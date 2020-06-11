import datetime
from time import time
import discord
from discord.ext import commands
from discord.utils import snowflake_time

class Ping(commands.Cog, name='Ping'):
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command(desc="Displays connection speed info")
	async def ping(self,ctx):
		await ctx.send('Pong! {} ms'.format(self.bot.latency*1000))

def setup(bot):
	bot.add_cog(Ping(bot))
