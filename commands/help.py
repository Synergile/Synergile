import discord
from discord.ext import commands
from datetime import datetime
from datetime import timezone
from util.stringbuilder import StringBuilder

class Help(commands.Cog, name='Help'):
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command(description="Displays help information for the bot",
		help='Displays a list of commands with descriptions when used without an argument, or display specific help information for a command when a command name or alias is given as an argument. \n*Syntax notes:* In command usages, `<arg>` is a required argument and `[arg]` is an optional argument. Any commands that take a member or user as an argument will accept a member or user resolvable, respectively. A "user resolvable" is a user mention or user ID that can be resolved to a specific Discord User. A "member resolvable" is a user resolvable or a username fragment (which can be an entire username), that can be resolved to a single user in the server')
	async def help(self,ctx,*,commandName=None):
		if(commandName is None):
			cmds = list(set([*(self.bot.walk_commands())]))
			author = ctx.message.author
			embeds = [discord.Embed(colour = discord.Colour.orange(), title = 'Help', timestamp = datetime.now(timezone.utc)).set_thumbnail(url='https://i.imgur.com/0NR5nbD.png').set_footer(text= f"Requested by {author}", icon_url=author.avatar_url)]
			count=0
			for cmd in cmds:
				if(count==25):
					embeds.append(discord.Embed(colour = discord.Colour.orange(), timestamp = datetime.now(timezone.utc)).set_thumbnail(url='https://i.imgur.com/0NR5nbD.png').set_footer(text= f"Requested by {author}", icon_url=author.avatar_url))
					count = 0
				count += 1
			count = 0
			index = 0
			for command in cmds:
				if(command.hidden):
					continue
				if(count==25):
					index+=1
					count = 0
				fieldstr = 'No description' if command.description == '' else command.description
				embeds[index].add_field(name=f'{self.bot.command_prefix}{command.name}', value=fieldstr, inline=False)
				count+=1
			for embed in embeds:
				await self.send_help(ctx,embed=embed)
		else:
			command = self.bot.get_command(commandName)
			if(command is None):
				await self.send_help(ctx, content=f'Could not find command or alias `{commandName}`')
				return
			author = ctx.message.author
			embed = discord.Embed(colour = discord.Colour.orange(), title = command.name, timestamp = datetime.now(timezone.utc))
			fieldstr = StringBuilder()
			if(command.aliases):
				fieldstr.append(f'**Aliases:** {", ".join(command.aliases)}\n')
			fieldstr.append('**Description:** ').append(command.description if command.description else 'No description').append('\n')
			fieldstr.append(f'**Usage:** {self.bot.command_prefix}{command.name} ').append(command.usage if command.usage else command.signature).append('\n')
			if(command.help):
				fieldstr.append(f'**Help:** {command.help}\n')
			elif(command.brief):
				fieldstr.append(f'**Help:** {command.brief}\n')
			if(not command.enabled):
				fieldstr.append('*Command is disabled*\n')
			if(command.hidden):
				fieldstr.append('*Hidden*\n')
			#'Command Help' is a placeholder for permission notes with proper permissions
			embed.add_field(name='Command Help', value=fieldstr.to_string(), inline=False)
			embed.set_footer(text= f"Requested by {author}", icon_url=author.avatar_url)	
			await self.send_help(ctx,embed=embed)
			
	#used to unify changes to how reply is sent. If changing reply to send to DMs for example, would only need to change here
	async def send_help(self, ctx, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None):
		return await ctx.send(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce)

def setup(bot):
	bot.add_cog(Help(bot))
