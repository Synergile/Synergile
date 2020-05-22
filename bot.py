import discord
import asyncio
import datetime
from discord.ext import commands
from discord.ext import tasks
desc= "Moderation bot engineered by CodeWritten, wakfi, and jedi3"
bot = commands.Bot(command_prefix='!', case_insensitive=True, description=desc)
@bot.event
async def on_ready():
    print (f"Bot online")

@bot.command(desc="Gets information about a user and outputs it")
async def profile(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.guild.get_member(ctx.author.id)
        embed = discord.Embed(title= ctx.author.name, color= 0x00ff00)
        embed.add_field(name= 'Joined at', value = member.joined_at, inline=False)
        embed.add_field(name= 'Is Bot', value = member.bot, inline=False)
        embed.add_field(name= "Username+Discrim", value = ctx.author, inline=False)
        embed.add_field(name= "Highest role", value = member.top_role.name, inline=False)
        
        await ctx.send(embed=embed)


bot.run("NzEzMTI5ODUxMDU3MzQwNDg3.XsboTw.b2c_QAprAh2IONu38aY-t6Giz64")
