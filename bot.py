import discord
import asyncio
import datetime
from datetime import datetime
from datetime import timezone
import youtube_dl
from discord.ext import commands
from util.pyutil import buildMultiMatchString, splitArgs
from util.discordutil import resolveMember, modActionLogEmbed
import os
import math
import random
desc= "Moderation bot engineered by CodeWritten, wakfi, and jedi3"
bot = commands.Bot(command_prefix='$', case_insensitive=True, description=desc)
bot.remove_command('help') #removing the default help cmd
#NO_MENTIONS = discord.AllowedMentions(everyone=False,users=False,roles=False) - add in d.py 1.4


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(f'{bot.command_prefix}help for commands'))
    print (f"Bot online")
    
@bot.event
async def on_command_error(ctx, error):
    await ctx.send("An error occured!\n```{}```".format(error))

@bot.command(desc="Gets information about a user and outputs it")
async def profile(ctx, *, member= None):
    if member is None: 
        #self profile
        mem = ctx.guild.get_member(ctx.author.id)
    else:
        #resolve argument to a member
        mem = await resolveMember(ctx, member)
        
    if mem is None:
        #return when input cannot be resolved
        await ctx.send(f'You must provide a valid user reference: "{member}" could not be resolved to a user')
        return
        
    
    #generate profile embed and send
    if(isinstance(mem, list)):
        usersFound = buildMultiMatchString(bot.command_prefix, 'profile', mem, member)
        await ctx.send(usersFound)
    else:
        embed = profileEmbed(ctx.message.author, mem)
        await ctx.send(embed=embed)

#this should go in the Profile cog
def profileEmbed(author, mem):
    #avoiding magic numbers
    DISCORD_EPOCH = 1420070400000 #first second of 2015
    userMilliseconds = int(mem.id/math.pow(2,22) + DISCORD_EPOCH)
    embed = discord.Embed(title= mem.nick or mem.name, color= 0x00ff00, timestamp = datetime.now(timezone.utc))
    embed.set_thumbnail(url=mem.avatar_url)
    embed.add_field(name= "Username+Discrim:", value = f'{mem.name}#{mem.discriminator}', inline=False)
    embed.add_field(name= "Highest role:", value = mem.top_role.name, inline=False)
    embed.add_field(name= 'Is Bot?', value = 'Yes' if mem.bot else 'No', inline=False)
    embed.add_field(name= 'Joined Discord:', value = datetime.utcfromtimestamp(int(userMilliseconds//1000)).replace(microsecond=userMilliseconds%1000*1000), inline=False)
    embed.add_field(name= 'Joined the server at:', value = mem.joined_at, inline=False)
    embed.add_field(name= "ID:", value = mem.id, inline= False)
    embed.set_footer(text= f"Requested by {author}", icon_url=author.avatar_url)
    return embed

#Fun Catergory
@bot.command('8ball')
async def _8ball(ctx, *, question):
  response = ['Yes.', 'No.']
  await ctx.send(f'Question: {question} \nAnswer: {random.choice(response)}')

@bot.command()
async def choose(ctx, *choices: str):
    """Chooses between multiple choices."""
    await ctx.send(random.choice(choices))

#Moderation
@bot.command(desc="Purges a number of messages from the channel")
async def purge(ctx, amount):
    amount = int(amount)
    await ctx.channel.purge(limit=amount)
    
@bot.command(desc="Kick a member from the server")
async def kick(ctx,*, member=None, reason="No reason provided"):
    if member is None:
        mem = None
    else:
        args = splitArgs(member)
        if len(args)==1:
            member = args[0]
        else:
            member = args[0][0]
        #resolve argument to a member
        mem = await resolveMember(ctx, member)
    
    if mem is None:
        #return when input cannot be resolved
        await ctx.send(f'You must provide a valid user reference: "{member}" could not be resolved to a user')
        return
    
    if(isinstance(mem, list)):
        usersFound = buildMultiMatchString(bot.command_prefix, 'kick', mem, member)
        await ctx.send(usersFound)
    else:
        indexReason = -1
        try:
            indexReason = args[1].index('r') + 1
        except Exception:
            pass
        if indexReason > -1:
            try:
                if args[0][indexReason] is not None:
                    reason = args[0][indexReason]
            except Exception:
                await ctx.send('An error occurred while attempting to parse arguments')
                return
        try:
            await ctx.guild.kick(mem, reason=reason)
            await ctx.guild.get_channel(713131470625046549).send(embed=modActionLogEmbed('Kicked',mem,reason,ctx.author))
        except Exception:
            await ctx.send('An unknown error occured. Please try again later')

@bot.command(desc="Ban a member from the server")
async def ban(ctx,*, member=None, reason = "No reason provided"):
    if member is None:
        mem = None
    else:
        args = splitArgs(member)
        if len(args)==1:
            member = args[0]
        else:
            member = args[0][0]
        #resolve argument to a member
        mem = await resolveMember(ctx, member)
    
    if mem is None:
        #return when input cannot be resolved
        await ctx.send(f'You must provide a valid user reference: "{member}" could not be resolved to a user')
        return
    
    if(isinstance(mem, list)):
        usersFound = buildMultiMatchString(bot.command_prefix, 'ban', mem, member)
        await ctx.send(usersFound)
    else:
        indexReason = -1
        try:
            indexReason = args[1].index('r') + 1
        except Exception:
            pass
        if indexReason > -1:
            try:
                if args[0][indexReason] is not '':
                    reason = args[0][indexReason]
            except Exception:
                await ctx.send('An error occurred while attempting to parse arguments')
                return
        try:
            await ctx.guild.ban(mem, reason=reason)
            await ctx.guild.get_channel(713131470625046549).send(embed=modActionLogEmbed('Banned',mem,reason,ctx.author))
        except Exception:
            await ctx.send('An unknown error occured. Please try again later')


#music
players = {}

@bot.command()
async def join(ctx):
    member = ctx.guild.get_member(ctx.author.id)
    vc = member.voice.channel
    await vc.connect()

    
@bot.command()
async def leave(ctx):
    vc = ctx.guild.voice_client   
    await vc.disconnect()

@bot.command(aliases=['p'])
async def play(ctx, url: str):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send("ERROR: Music playing")
        return

    await ctx.send("Getting everything ready now")

    voice = get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}\n")
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print("Song done!"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07

    nname = name.rsplit("-", 2)
    await ctx.send(f"Playing: {nname[0]}")
    print("playing\n")
    
#help
@bot.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author
    embed = discord.Embed(colour = discord.Colour.orange(), title = 'Help', timestamp = datetime.now(timezone.utc))
    embed.add_field(name=f'{bot.command_prefix}ping', value='Returns Pong!', inline=False)
    embed.add_field(name=f'{bot.command_prefix}profile [@user | userID]', value='Display information about a given user', inline=False)
    embed.add_field(name=f'{bot.command_prefix}kick <@user | userID>', value='Kicks a member from the server', inline=False)
    embed.add_field(name=f'{bot.command_prefix}ban <@user | userID>', value='Bans a member from the server', inline=False)
    embed.set_footer(text= f"Requested by {author}", icon_url=author.avatar_url)    
    await ctx.send(embed=embed)

#other
@bot.command(desc="Says pong!")
async def ping(ctx):
    await ctx.send('Pong! {} ms'.format(bot.latency*1000))
    
@bot.command(desc="Displays build info")
async def build_info(ctx, file_override=None):
    if file_override is None:
        file= 'buildinfo.conf'
        with open(file, 'r') as f:
            await ctx.send(f.readlines())

    else:
        file = file_override
        with open(file, 'r') as f:
            await ctx.send(f.readlines())
            
for cog in os.listdir(".\\commands"):#path
	if cog.endswith(".py"):
		try:
			cog = f"commands.{cog.replace('.py', '')}"
			bot.load_extension(cog)
		except Exception as e:
			print(f"{cog} cannot be loaded:")
			raise e

with open('config.config', 'r') as f:
    tok = f.readline()
    tok.replace('\n', "")
bot.run(tok)
