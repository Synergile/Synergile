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
        embed = discord.Embed(title= ctx.author.name, color= 0x00ff00)
        embed.add_field(name= 'Joined the server at:', value = mem.joined_at, inline=False)
        embed.add_field(name= 'Is Bot:', value = mem.bot, inline=False)
        embed.add_field(name= "Username+Discrim:", value = ctx.author, inline=False)
        embed.add_field(name= "Highest role:", value = mem.top_role.name, inline=False)
        embed.add_field(name= "ID:", value = mem.id, inline= False)
        await ctx.send(embed=embed)
    elif '@' in member:
        mem = await mc.convert(ctx, member)
        embed = discord.Embed(title= mem.name, color= 0x00ff00)
        embed.add_field(name= 'Joined the server at:', value = mem.joined_at, inline=False)
        embed.add_field(name= 'Is Bot:', value = mem.bot, inline=False)
        embed.add_field(name= "Username+Discrim:", value = mem.name, inline=False)
        embed.add_field(name= "Highest role:", value = mem.top_role.name, inline=False)
        embed.add_field(name= "ID:", value := mem.id, inline= False)
        await ctx.send(embed=embed)
                


with open('config.config', 'r') as f:
    tok = f.readline()
    tok.replace('\n', "")
bot.run(tok)
