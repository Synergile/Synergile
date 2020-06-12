import discord
from discord.ext import commands
from datetime import datetime
from datetime import timezone

class Help(commands.Cog, name='Help'):
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command(desc="Display help information for the bot")
	async def help(self,ctx):
		author = ctx.message.author
		embed = discord.Embed(colour = discord.Colour.orange(), title = 'Help', timestamp = datetime.now(timezone.utc),
			description='Syntax note: A "member resolvable" is a user mention, user ID, or a username fragment that can be resolved to a single user in the server (which can be an entire username)')
		embed.add_field(name=f'{self.bot.command_prefix}ping', value='Returns Pong!', inline=False)
		embed.add_field(name=f'{self.bot.command_prefix}profile [member resolvable]', value='Display information about a given user', inline=False)
		embed.add_field(name=f'{self.bot.command_prefix}kick <member resolvable>', value='Kicks a member from the server', inline=False)
		embed.add_field(name=f'{self.bot.command_prefix}ban <member resolvable>', value='Bans a member from the server', inline=False)
		embed.set_footer(text= f"Requested by {author}", icon_url=author.avatar_url)	
		await ctx.send(embed=embed) #change to ctx.author.send

def setup(bot):
	bot.add_cog(Help(bot))
