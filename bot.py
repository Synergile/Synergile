import discord
import asyncio
import datetime
import youtube_dl
from discord.ext import commands
from discord.ext import tasks
import os
desc= "Moderation bot engineered by CodeWritten, wakfi, and jedi3"
bot = commands.Bot(command_prefix='!', case_insensitive=True, description=desc)
bot.remove_command('help') #removing the default help cmd

@bot.event
async def on_ready():
    print (f"Bot online")

@bot.command(desc="Gets information about a user and outputs it")
async def profile(ctx, member= None):
    mc = commands.MemberConverter()
    if member is None:
        mem = ctx.guild.get_member(ctx.author.id)
    elif '@' in member:
        mem = await mc.convert(ctx, member)
    embed = profileEmbed(mem)
    await ctx.send(embed=embed)

def profileEmbed(mem)
    #avoiding magic numbers
    DISCORD_EPOCH = 1420070400000 #first second of 2015
    userMilliseconds = mem.id/math.pow(2,22) + DISCORD_EPOCH
    embed = discord.Embed(title= mem.name, color= 0x00ff00)
    embed.add_field(name= 'Joined the server at:', value = mem.joined_at, inline=False)
    embed.add_field(name= 'Joined Discord:', value = datetime.utcfromtimestamp(userMilliseconds//1000).replace(microsecond=userMilliseconds%1000*1000), inline=False)
    embed.add_field(name= 'Is Bot:', value = mem.bot, inline=False)
    embed.add_field(name= "Username+Discrim:", value = f'{mem.name}#{mem.discriminator}', inline=False)
    embed.add_field(name= "Highest role:", value = mem.top_role.name, inline=False)
    embed.add_field(name= "ID:", value = mem.id, inline= False)
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
@bot.command()
async def purge(ctx, amount-3):
    await ctx.channel.purge(limit=amount)
    
@bot.command()
async def kick(ctx, member : discord.Member):
    await member.kick

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
    
    embed = discord.Embed(colour = discord.Colour.orange())
    embed.set_author(name='Help') 
    embed.add_field(name='ping', value='Returns Pong!', inline=False)
    embed.add_field(name='kick', value='Kicks a member from the server', inline=False)
    embed.add_field(name='ban', value='Bans a member from the server', inline=False)
    
    await bot.send_message(channel, embed=embed)

#other
@bot.event
async def ping():
    await client.say('Pong!')
    
with open('config.config', 'r') as f:
    tok = f.readline()
    tok.replace('\n', "")
bot.run(tok)
