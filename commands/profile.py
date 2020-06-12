import math
import discord
from discord.ext import commands
from datetime import datetime
from datetime import timezone
from util.pyutil import buildMultiMatchString
from util.discordutil import resolveMember

class Profile(commands.Cog, name='Profile'):
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command(description="Gets information about a user and outputs it",usage='[user]')
	async def profile(self, ctx, *, member=None):
		if member is None: 
			#self profile
			mem = ctx.guild.get_member(ctx.author.id)
		else:
			#resolve argument to a member
			mem = await resolveMember(ctx, member)
			
		if mem is None:
			#return when input cannot be resolved
			await ctx.send(f'You must provide a valid user reference: "{member}" could not be resolved to a user')
			return
			
		
		#generate profile embed and send
		if(isinstance(mem, list)):
			usersFound = buildMultiMatchString(self.bot.command_prefix, 'profile', mem, member)
			await ctx.send(usersFound)
		else:
			embed = self.profileEmbed(ctx.message.author, mem)
			await ctx.send(embed=embed)

	#this should go in the Profile cog
	def profileEmbed(self, author, mem):
		#avoiding magic numbers
		DISCORD_EPOCH = 1420070400000 #first second of 2015
		userMilliseconds = int(mem.id/math.pow(2,22) + DISCORD_EPOCH)
		embed = discord.Embed(title= mem.nick or mem.name, color= 0x00ff00, timestamp = datetime.now(timezone.utc))
		embed.set_thumbnail(url=mem.avatar_url)
		embed.add_field(name= "Username+Discrim:", value = f'{mem.name}#{mem.discriminator}', inline=False)
		embed.add_field(name= "Highest role:", value = mem.top_role.name, inline=False)
		embed.add_field(name= 'Is Bot?', value = 'Yes' if mem.bot else 'No', inline=False)
		embed.add_field(name= 'Joined Discord:', value = datetime.utcfromtimestamp(int(userMilliseconds//1000)), inline=False)
		embed.add_field(name= 'Joined the server at:', value = mem.joined_at.replace(microsecond=0), inline=False)
		embed.add_field(name= "ID:", value = mem.id, inline= False)
		embed.set_footer(text= f"Requested by {author}", icon_url=author.avatar_url)
		return embed

def setup(bot):
	bot.add_cog(Profile(bot))
