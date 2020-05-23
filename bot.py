import discord
import asyncio
import datetime
import re
import youtube_dl
from discord.ext import commands
from discord.ext import tasks
import os
import math
desc= "Moderation bot engineered by CodeWritten, wakfi, and jedi3"
bot = commands.Bot(command_prefix='!', case_insensitive=True, description=desc)
bot.remove_command('help') #removing the default help cmd
SNOWFLAKE_REGEX = re.compile('\D'); #compile regular expression matching all characters that aren't digits


@bot.event
async def on_ready():
    print (f"Bot online")

@bot.command(desc="Gets information about a user and outputs it")
async def profile(ctx, member= None):
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
    embed = profileEmbed(mem)
    await ctx.send(embed=embed)

def profileEmbed(mem):
    #avoiding magic numbers
    DISCORD_EPOCH = 1420070400000 #first second of 2015
    userMilliseconds = int(mem.id/math.pow(2,22) + DISCORD_EPOCH)
    embed = discord.Embed(title= mem.nick or mem.name, color= 0x00ff00, timestamp = datetime.datetime.now(datetime.timezone.utc))
    embed.add_field(name= "Username+Discrim:", value = f'{mem.name}#{mem.discriminator}', inline=False)
    embed.add_field(name= "Highest role:", value = mem.top_role.name, inline=False)
    embed.add_field(name= 'Is Bot?', value = 'Yes' if mem.bot else 'No', inline=False)
    embed.add_field(name= 'Joined Discord:', value = datetime.datetime.utcfromtimestamp(int(userMilliseconds//1000)).replace(microsecond=userMilliseconds%1000*1000), inline=False)
    embed.add_field(name= 'Joined the server at:', value = mem.joined_at, inline=False)
    embed.add_field(name= "ID:", value = mem.id, inline= False)
    embed.set_footer(text='Admin Bot')
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
@bot.command(desc="Purges the channel")
async def purge(ctx, amount):
    amount = int(amount)
    await ctx.channel.purge(limit=amount)
    
@bot.command()
async def kick(ctx, member : discord.Member, *, reason="No reason provided"):
    guild = bot.get_guild(ctx.guild.id)
    await guild.kick(member, reason=reason)

@bot.command()
async def ban(ctx, member : discord.Member):
    await member.ban

#music
players = {}

@bot.command(pass_context=True)
async def join(ctx):
    channel = ctx.message.author.voice.voice_channel
    await bot.join_voice_channel(channel)
    
@bot.command(pass_context=True)
async def leave(ctx):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    await voice_bot.disconnect()
    
@bot.command(pass_context=True)
async def play(ctx, url):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    player = await voice_client.create_ytdl_player(url)
    players[server.id] = player
    player.start()
    
#help
@bot.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author
    
    embed = discord.Embed(colour = discord.Colour.orange(), title = 'Help', timestamp = datetime.datetime.now(datetime.timezone.utc))
    embed.set_footer(text='Admin Bot')
    embed.add_field(name=f'{bot.command_prefix}ping', value='Returns Pong!', inline=False)
    embed.add_field(name=f'{bot.command_prefix}profile [@user | userID]', value='Display information about a given user', inline=False)
    embed.add_field(name=f'{bot.command_prefix}kick [@user | userID]', value='Kicks a member from the server', inline=False)
    embed.add_field(name=f'{bot.command_prefix}ban [@user | userID]', value='Bans a member from the server', inline=False)
    
    await ctx.send(embed=embed)

#other
@bot.command(desc="Says pong!")
async def ping(ctx):
    await ctx.send('Pong! {} ms'.format(bot.latency*1000))

#resolve a string to a member object
async def resolveMember(ctx, stringToResolve):
    mc = commands.MemberConverter()
    if isSnowflake(stringToResolve): 
        #gave an number that may be an ID
        member = ctx.guild.get_member(int(stringToResolve)) #if stringToResolve is not a valid snowflake, mem=None
    elif '@' in stringToResolve:
        #mentioned a user
        member = await mc.convert(ctx, stringToResolve)
    else:
        #string cannot be resolved
        member = None
    return member

    
#helper
#returns true if a value only contains characters 0-9, false otherwise. does not check length. 
#a consequence of this is that is will return true on empty values
def isSnowflake(snowflake):
    return isinstance(snowflake,str) and not SNOWFLAKE_REGEX.search(snowflake)
    
    
with open('config.config', 'r') as f:
    tok = f.readline()
    tok.replace('\n', "")
bot.run(tok)
