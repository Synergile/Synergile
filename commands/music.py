import asyncio
import functools
import itertools
import math
import random
import discord
import youtube_dl
from async_timeout import timeout
from discord.ext import commands
from util.discordutil import check_permissions

youtube_dl.utils.bug_reports_message = lambda: ''

class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass


class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '**{0.title}** by **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))

        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append('{} days'.format(days))
        if hours > 0:
            duration.append('{} hours'.format(hours))
        if minutes > 0:
            duration.append('{} minutes'.format(minutes))
        if seconds > 0:
            duration.append('{} seconds'.format(seconds))

        return ', '.join(duration)


class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    @property
    def title(self):
        return self.source.title

    def create_embed(self):
        embed = (discord.Embed(title='Now playing',
                               description='```\n{0.source.title}\n```'.format(self),
                               color=discord.Color.blurple())
                 .add_field(name='Duration', value=self.source.duration)
                 .add_field(name='Requested by', value=(f'{self.requester.name}#{self.requester.discriminator}' if self.requester.nick is None else f'{self.requester.nick} ({self.requester.name}#{self.requester.discriminator})'))
                 .add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
                 .add_field(name='URL', value='[Click]({0.source.url})'.format(self))
                 .set_thumbnail(url=self.source.thumbnail))

        return embed


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceStateContext(commands.Context):
    """Wrapper class for context object
    in a voice state
    """

    def __init__(self, ctx: commands.Context, music_cog):
        self._ctx = ctx
        self._music = music_cog

    @property
    def voice_state(self):
        return self._music.voice_states.get(self._ctx.guild.id)

    @property
    def voice_states(self):
        return self._music.voice_states

    @property
    def message(self):
        return self._ctx.message

    @property
    def bot(self):
        return self._ctx.bot

    @property
    def args(self):
        return self._ctx.args

    @property
    def kwargs(self):
        return self._ctx.kwargs

    @property
    def prefix(self):
        return self._ctx.prefix

    @property
    def command(self):
        return self._ctx.command

    @property
    def view(self):
        return self._ctx.view

    @property
    def invoked_with(self):
        return self._ctx.invoked_with

    @property
    def invoked_parents(self):
        return self._ctx.invoked_parents

    @property
    def invoked_subcommand(self):
        return self._ctx.invoked_subcommand

    @property
    def subcommand_passed(self):
        return self._ctx.subcommand_passed

    @property
    def command_failed(self):
        return self._ctx.command_failed

    @property
    def _state(self):
        return self._ctx._state

    async def invoke(self, *args, **kwargs):
        return await commands.Context.invoke(self, *args, **kwargs)

    async def reinvoke(self, *, call_hooks=False, restart=True):
        return await commands.Context.reinvoke(self, call_hooks=call_hooks, restart=restart)

    @property
    def valid(self):
        return self._ctx.valid

    @property
    def cog(self):
        return self._ctx.cog

    @property
    def guild(self):
        return self._ctx.guild

    @property
    def channel(self):
        return self._ctx.channel

    @property
    def author(self):
        return self._ctx.author

    @property
    def me(self):
        return self._ctx.me

    @property
    def voice_client(self):
        return self._ctx.voice_client

    async def send_help(self, *args):
        return await commands.Context.send_help(self, args=args)

    async def reply(self, content=None, **kwargs):
        return await commands.Context.reply(self, content=content, kwargs=kwargs)

class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: VoiceStateContext):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()

            if not self.loop:
                self.current = None
                # Try to get the next song within 3 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                try:
                    async with timeout(180):  # 3 minutes
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self._ctx.send('This channel has been marked inactive'))
                    self.bot.loop.create_task(self.stop())
                    return

            self.current.source.volume = self._volume
            self.voice.play(self.current.source, after=self.play_next_song)
            await self.current.source.channel.send(embed=self.current.create_embed())

            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self):

        if self.voice:
            await self._ctx.invoke(Music._leave, ctx=self._ctx)



class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, VoiceStateContext(ctx, self))
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage('This command can\'t be used in DM channels')

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('An error occurred: {}'.format(str(error)))
		
    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

    @commands.command(name='join', aliases=['j'], invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        """Joins a voice channel."""

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send('You are not connected to any voice channel')

        if ctx.voice_client and ctx.voice_client.channel == ctx.author.voice.channel:
            return await ctx.send('I am already in your voice channel')

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
        else:
            ctx.voice_state.voice = await destination.connect()
        await ctx.send(f'Joined **{destination.name}**')

    @commands.command(name='summon')
    @check_permissions(manage_guild=True)
    async def _summon(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        """Summons the bot to a voice channel.
        If no channel was specified, it joins your channel.
        """

        if not channel:
            if not ctx.author.voice:
                return await ctx.send('You are neither connected to a voice channel nor specified a channel to join')
            return await ctx.invoke(self._join)

        if ctx.voice_state.voice:
            if(channel == ctx.voice_state.voice.channel):
                return await ctx.send('I am already in your voice channel')
            await ctx.voice_state.voice.move_to(channel)
        else:
            ctx.voice_state.voice = await channel.connect()
        await ctx.send(f'Connected to **{channel.name}**')

    @commands.command(name='leave', aliases=['disconnect', 'quit'])
    @check_permissions(move_members=True)
    async def _leave(self, ctx: commands.Context):
        """Clears the queue and leaves the voice channel."""

        if not ctx.voice_state.voice:
            return await ctx.send('Not connected to any voice channel')

        channel = ctx.voice_client.channel

        try:
            await ctx.voice_client.disconnect()
        except AttributeError:
            pass
        else:
            await ctx.send(f'Left **{channel.name}**')
        del self.voice_states[ctx.guild.id]

    @commands.command(name='now', aliases=['current', 'playing', 'nowplaying'])
    async def _now(self, ctx: commands.Context):	           
        """Displays the currently playing song."""
        if(not ctx.voice_state.current):
            return await ctx.send('Not playing anything')
        await ctx.send(embed=ctx.voice_state.current.create_embed())

    @commands.command(name='pause')
    async def pause_(self, ctx):
        """Pause the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            return await ctx.send('I am not currently playing anything!')
        if vc.is_paused():
            return

        vc.pause()
        #await ctx.send(f'**`{ctx.author}:`** paused the song!')
        await ctx.send('⏸ Paused')

    @commands.command(name='resume')
    async def resume_(self, ctx):
        """Resume the currently paused song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!')
        if not vc.is_paused():
            return await ctx.send('I am not paused')

        vc.resume()
        #await ctx.send(f'**`{ctx.author}:`** resumed the song!')
        await ctx.send('▶ Resumed playing')

    @commands.command(name='stop')
    async def stop_(self, ctx):
        """Stop the currently playing song and destroy the player.       
            This will destroy the player assigned to your guild, also deleting any queued songs and settings.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected() or not ctx.voice_state.is_playing:
            return await ctx.send('I am not currently playing anything!')

        ctx.voice_state.songs.clear()
        ctx.voice_state.skip()
        await ctx.send('⏹ Stopped playing')

    @commands.command(name='skip')
    async def _skip(self, ctx: commands.Context):
        """Vote to skip a song. The requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('Not playing any music right now...')

        voter = ctx.message.author
        if voter == ctx.voice_state.current.requester:
            await ctx.send(f'⏭ Skipped **{ctx.voice_state.current.title}**')
            ctx.voice_state.skip()

        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)

            if total_votes >= 3:
                await ctx.send(f'⏭ Skipped **{ctx.voice_state.current.title}**')
                ctx.voice_state.skip()
            else:
                await ctx.send('Skip vote added, currently at **{}/3**'.format(total_votes))

        else:
            await ctx.send('You have already voted to skip this song.')

    @commands.command(name='queue', aliases=['q'])
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        """Shows the player's queue.
        You can optionally specify the page to show. Each page contains 10 elements.
        """

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(description='**{} tracks:**\n\n{}'.format(len(ctx.voice_state.songs), queue))
                 .set_footer(text='Viewing page {}/{}'.format(page, pages)))
        await ctx.send(embed=embed)

    @commands.command(name='shuffle')
    async def _shuffle(self, ctx: commands.Context):
        """Shuffles the queue."""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')

        ctx.voice_state.songs.shuffle()
        await ctx.send(f'🔀 Queue shuffled')

    @commands.command(name='remove')
    async def _remove(self, ctx: commands.Context, *, position=None):
        """Removes a song from the queue at a given index."""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')

        if position is None:
            return await ctx.send('Must provide the position number of the item to be removed from the queue')
        else:
            try:
                position = int(position)
            except(ValueError):
                return await ctx.send('Position must be a number')

        if position < 1:
            return await ctx.send('Must provide the position number of the item to be removed from the queue')
        if position > len(ctx.voice_state.songs):
            return await ctx.send(f'The last song in the queue is at position **{len(ctx.voice_state.songs)}**. There is no item at position `{position}`')

        song = ctx.voice_state.songs[position - 1]
        ctx.voice_state.songs.remove(position - 1)
        await ctx.send(f'✅ Removed **{position}. {song.title}** from the queue')

    @commands.command(name='loop')
    async def _loop(self, ctx: commands.Context):
        """Loops the currently playing song.
        Invoke this command again to unloop the song.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('Nothing being played at the momen.')

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        if ctx.voice_state.loop:
            await ctx.send('🔁 Song looping enabled')
        else:
            await ctx.send('➡ Song looping disabled')

    @commands.command(name='play')
    async def _play(self, ctx: commands.Context, *, search=None):
        """Plays a song.
        If there are songs in the queue, this will be queued until the
        other songs finished playing.
        This command automatically searches from various sites if no URL is provided.
        A list of these sites can be found here: https://rg3.github.io/youtube-dl/supportedsites.html
        """

        if ctx.voice_client and ctx.voice_client.is_connected() and ctx.voice_client.is_paused():
            return await ctx.invoke(self.resume_)

        if search is None:
            return await ctx.send('Must provide link or search query')

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send('You are not connected to any voice channel')

        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)

        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
            else:
                song = Song(source)

                await ctx.voice_state.songs.put(song)
                await ctx.send('Enqueued {}'.format(str(source)))



def setup(bot):
	bot.add_cog(Music(bot))
