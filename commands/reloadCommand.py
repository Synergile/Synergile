import discord
from discord.ext import commands
from util.discordutil import find_command
from util.parseFlags import parseFlags

class ReloadCommand(commands.Cog, name='ReloadCommand'):
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command(description="Reload a Command", aliases=['rlc'],usage='<commandName>')
	async def reloadCommand(self,ctx,*,input=None):
		if(input is None):
			await ctx.send('You must provide a command name or alias')
			return
		pargs = parseFlags(input,{'force':'f','forced':'-force'},truthy=True,allowDoublePrefix=True)
		cmd = ' '.join(pargs['args'])
		force = pargs['force'] or pargs['forced']
		commandName = find_command(self.bot,cmd) if not force else cmd
		if(commandName is None):
			return await ctx.send(f'Reload failed: Could not find command or alias `{cmd}`')
		try:
			self.bot.reload_extension(f'commands.{commandName}')
			await ctx.send(f'Successfully reloaded `{commandName}`')
		except Exception as e:
			await ctx.send(f'Reload failed with exception: `{e}`')

def setup(bot):
	bot.add_cog(ReloadCommand(bot))
