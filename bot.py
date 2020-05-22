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
    if member is None:
        mem = ctx.guild.get_member(ctx.author.id)
        embed = discord.Embed(title= ctx.author.name, color= 0x00ff00)
        embed.add_field(name= 'Joined the server at:', value = mem.joined_at, inline=False)
        embed.add_field(name= 'Is Bot:', value = mem.bot, inline=False)
        embed.add_field(name= "Username+Discrim:", value = ctx.author, inline=False)
        embed.add_field(name= "Highest role:", value = mem.top_role.name, inline=False)
        embed.add_field(name= "ID:", value = mem.id, inline= False)
        await ctx.send(embed=embed)
    else:
         users = []
       # for x in ctx.guild.members:
       #     if member in x.name:
       #         users.append(x.name)
         users.append(await ctx.guild.fetch_member(x.id))       
            if len(users) >= 2:
                embed = discord.Embed(title = "Multiple Users Found", color = 0xff0000)
                embed.add_field(name=f"Found {len(users)} users, try being more specific", value = '\n'.join(users), inline = False)
                await ctx.send(embed=embed)
                break

        mc = commands.MemberConverter()
        mem = await mc.convert(ctx, users[0])
        embed = discord.Embed(title= mem.name, color= 0x00ff00)
        embed.add_field(name= 'Joined at', value = mem.joined_at, inline=False)
        embed.add_field(name= 'Is Bot', value = mem.bot, inline=False)
        embed.add_field(name= "Username+Discrim", value = mem.name+mem.tag, inline=False)
        embed.add_field(name= "Highest role", value = mem.top_role.name, inline=False)
        embed.add_field(name= "ID", value = mem.id, inline= False)
        await ctx.send(embed=embed)

                


token = os.getenv('BOT_TOKEN')

bot.run('NzEzMTI5ODUxMDU3MzQwNDg3.XsboTw.b2c_QAprAh2IONu38aY-t6Giz64')
