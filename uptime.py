import discord, datetime, time
from discord.ext import commands

start_time = time.time()
start_time = datetime.datetime.utcnow()

class Uptime(commands.Cog, name='Uptime'):
	def __init__(self, bot):
		self.bot = bot

    @commands.command()
	async def uptime(self, ctx):
		now = datetime.datetime.utcnow()
		delta = now - start_time
		hours, remainder = divmod(int(delta.total_seconds()), 3600)
		minutes, seconds = divmod(remainder, 60)
		days, hours = divmod(hours, 24)
		if days:
			time_format = "**{d}** days, **{h}** hours, **{m}** minutes, and **{s}** seconds."
		else:
			time_format = "**{h}** hours, **{m}** minutes, and **{s}** seconds."
		uptime_stamp = time_format.format(d=days, h=hours, m=minutes, s=seconds)
		embed = discord.Embed(title="Uptime")
		embed.add_field(name="The bot, ", value="{} has been online for {}".format(client.user.name, uptime_stamp))
		await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Uptime(bot))
