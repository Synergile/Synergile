import discord
from discord.ext import commands

class Sh_info(commands.Cog, name='Sh_info'):
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command(description="Displays shard info")
	async def sh_info(self,ctx):
		await ctx.author.send(f"Current Shard Latency: {self.bot.latency}\nShard IDs: {self.bot.shard_ids}\nAverage Shards Latency: {self.bot.latencies}")
		await ctx.send(f"Sent shard info to your DMs, <@{ctx.author.id}>")

def setup(bot):
	bot.add_cog(Sh_info(bot))
