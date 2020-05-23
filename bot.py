import discord
import asyncio
import datetime
from discord.ext import commands
from discord.ext import tasks
import os
desc= "Moderation bot engineered by CodeWritten, wakfi, and jedi3"
bot = commands.Bot(command_prefix='!', case_insensitive=True, description=desc)
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
    ms = mem.id/math.pow(2,22) + DISCORD_EPOCH
    embed = discord.Embed(title= mem.name, color= 0x00ff00)
    embed.add_field(name= 'Joined the server at:', value = mem.joined_at, inline=False)
    embed.add_field(name= 'Joined Discord:', value = datetime.utcfromtimestamp(ms//1000).replace(microsecond=ms%1000*1000), inline=False)
    embed.add_field(name= 'Is Bot:', value = mem.bot, inline=False)
    embed.add_field(name= "Username+Discrim:", value = f'{mem.name}#{mem.discriminator}', inline=False)
    embed.add_field(name= "Highest role:", value = mem.top_role.name, inline=False)
    embed.add_field(name= "ID:", value = mem.id, inline= False)
    return embed

with open('config.config', 'r') as f:
    tok = f.readline()
    tok.replace('\n', "")
bot.run(tok)
