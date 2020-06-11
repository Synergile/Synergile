import discord
from discord.ext import commands
import random

class Choose(commands.Cog, name='Choose'):
	def __init__(self, bot):
		self.bot = bot
		self.response = ['Yes', 'No']
	
	@commands.command(name='choose',desc="Chooses between multiple choices.")
	async def choose(self, ctx, *choices: str):
		if(choices is not None and len(choices) > 1):
			await ctx.send(random.choice(choices))
		else:
			await ctx.send("You need to give me at least 2 options to choose from!",delete_after=12)

def setup(bot):
	bot.add_cog(Choose(bot))
