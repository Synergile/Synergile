import discord
from discord.ext import commands
import random

class __8ball(commands.Cog, name='8ball'):
	def __init__(self, bot):
		self.bot = bot
		self.response = ['Yes', 'No']
	
	@commands.command(name='8ball',desc="Answers a yes or no question")
	async def _8ball(self,ctx,*,question=None):
		if(question is not None):
			await ctx.send(f'Question: {question} \nAnswer: {random.choice(self.response)}')
		else:
			await ctx.send("You didn't ask me a question!",delete_after=12)

def setup(bot):
	bot.add_cog(__8ball(bot))
