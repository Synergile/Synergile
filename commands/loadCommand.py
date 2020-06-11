import discord
from discord.ext import commands

class LoadCommand(commands.Cog, name='LoadCommand'):
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command(desc="Load a command", aliases=['ldc'])
	async def loadCommand(self,ctx,*,commandName):
		if(commandName is None):
			await ctx.send('You must provide a command name or alias')
			return
		try:
			self.bot.load_extension(f'commands.{commandName}')
			await ctx.send(f'Successfully loaded `{commandName}`')
		except Exception as e:
			await ctx.send(f'Load failed with exception: `{e}`')

def setup(bot):
	bot.add_cog(LoadCommand(bot))
