from discord.ext import commands
from util.pyutil import buildMultiMatchString, splitArgs
from util.discordutil import resolveMember, modActionLogEmbed

class Kick(commands.Cog, name='Kick'):
	def __init__(self, bot):
		self.bot = bot
		self.modLogChannelID=713131470625046549 #will be guild lookup for value in database
	
	@commands.command(desc="Kick a member from the server")
	async def kick(self, ctx,*, member=None, reason="No reason provided"):
		if member is None:
			mem = None
		else:
			args = splitArgs(member)
			if len(args)==1:
				member = args[0]
			else:
				member = args[0][0]
			#resolve argument to a member
			mem = await resolveMember(ctx, member)
		
		if mem is None:
			#return when input cannot be resolved
			await ctx.send('You must provide a valid user reference{}'.format(f': "{member}" could not be resolved to a user' if member is not None else ''))
			return
		
		if(isinstance(mem, list)):
			usersFound = buildMultiMatchString(self.bot.command_prefix, 'kick', mem, member)
			await ctx.send(usersFound)
		else:
			indexReason = -1
			try:
				indexReason = args[1].index('r') + 1
			except Exception:
				pass
			if indexReason > -1:
				try:
					if args[0][indexReason] is not None:
						reason = args[0][indexReason]
				except Exception:
					await ctx.send('An error occurred while attempting to parse arguments')
					return
			try:
				await ctx.guild.kick(mem, reason=reason)
				if self.modLogChannelID is not None:
					await ctx.guild.get_channel(self.modLogChannelID).send(embed=modActionLogEmbed('Kicked',mem,reason,ctx.author))
			except Exception:
				await ctx.send('An unknown error occured. Please try again later')

def setup(bot):
	bot.add_cog(Kick(bot))
