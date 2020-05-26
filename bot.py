import discord
import asyncio
import datetime
from datetime import datetime
from datetime import timezone
import re
import youtube_dl
from discord.ext import commands
from discord.ext import tasks
import os
import math
import random
desc= "Moderation bot engineered by CodeWritten, wakfi, and jedi3"
bot = commands.AutoShardedBot(command_prefix='$', case_insensitive=True, description=desc)
bot.remove_command('help') #removing the default help cmd
#NO_MENTIONS = discord.AllowedMentions(everyone=False,users=False,roles=False) - add in d.py 1.4
SNOWFLAKE_REGEX = re.compile('\D') #compile regular expression matching all characters that aren't digits


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
        usersFound = buildMultiMatchString('profile', mem, member)
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
        usersFound = buildMultiMatchString('kick', mem, member)
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
        usersFound = buildMultiMatchString('ban', mem, member)
        await ctx.send(usersFound)
    else:
        indexReason = -1
        try:
            indexReason = args[1].index('r') + 1
        except Exception:
            pass
        if indexReason > -1:
            try:
                if args[0][indexReason] != '':
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

#should be a util when cog setup
#resolve a string to a member object
async def resolveMember(ctx, stringToResolve):
    mc = commands.MemberConverter()
    stringToResolve = stringToResolve.strip()
    if isSnowflake(stringToResolve): 
        #gave an number that may be an ID
        member = ctx.guild.get_member(int(stringToResolve)) #if stringToResolve is not a valid snowflake, mem=None
    elif '@' in stringToResolve:
        #mentioned a user
        try:
            member = await mc.convert(ctx, stringToResolve)
        except Exception:
            member = None
    else:
        try:
            memList = await ctx.guild.query_members(query = stringToResolve)
        except Exception:
            memList = []
        if len(memList)==0:
            member = None
        elif len(memList)==1:
            member = memList[0]
        else:
            return memList
    return member

#should be a util when cog setup
def buildMultiMatchString(command,mem,member):
    strBuilder=f'Found {len(mem)} possible matches for "{member}":```'
    strBuilder=''.join([strBuilder, ''.join(f'\n{index+1}. {memMatch}' for index,memMatch in enumerate(mem))])
    strBuilder+=f'```'
    if len(mem)==5:
        strBuilder+=f'\n(number of matches shown is capped at 5, there may or may not be more)'
    strBuilder+=f'\nTry using the {bot.command_prefix}{command} command again with a more specific search term!'
    return strBuilder
    
#should be a util class when cog setup
def modActionLogEmbed(action,member,reason,issuer=bot):
    embed = discord.Embed(colour = discord.Colour.red(), description = f'{action} {member.mention} with reason: {reason}', timestamp = datetime.now(timezone.utc))
    embed.set_footer(text= f"Issued by {issuer}({issuer.id})", icon_url=issuer.avatar_url)
    return embed
    
#helper
#returns true if a value only contains characters 0-9, false otherwise. does not check length. 
#a consequence of this is that is will return true on empty values
def isSnowflake(snowflake):
    return isinstance(snowflake,str) and not SNOWFLAKE_REGEX.search(snowflake)

#do i even need to say that this is a util? this is a util
def splitArgs(input):
    optionRegex = re.compile(' -[a-zA-Z]+')
    if(not re.search(optionRegex, input)):
        return [input]
    spaceSplit = re.split(r' ', input)
    optionSplitArgs = optionRegex.split(input)
    optionSplitArgs = [arg.strip() for arg in optionSplitArgs]
    flagsRegex = re.compile('-')
    rawFlags = list(filter(flagsRegex.match, spaceSplit))
    joinedFlags = ''.join(rawFlags)
    rawFlags = re.split(flagsRegex, joinedFlags)
    joinedFlags = ''.join(rawFlags)
    flags = re.split(r'', joinedFlags)
    flags.pop()  # remove tailing empty string
    flags.pop(0) # remove leading empty string
    flags = [flag.lower() for flag in flags]
    return [optionSplitArgs, flags]
    
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

@bot.command(desc="Displays shard info")
async def sh_info(ctx):
    await ctx.send(f"Sent shard info to your DMs, <@{ctx.author.id}>")
    await ctx.author.send(f"Current Shard Latency: {bot.latency}\nShard IDs: {bot.shard_ids}\nAverage Shards Latency: {bot.latencies}")

with open('config.config', 'r') as f:
    tok = f.readline()
    tok.replace('\n', "")
bot.run(tok)
