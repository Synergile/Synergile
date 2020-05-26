import discord, datetime, time
from discord.ext import commands

start_time = time.time()
start_time = datetime.datetime.utcnow()

class Uptime(commands.Cog, name='Uptime'):
	def __init__(self, bot):
		self.bot = bot
	
    #replace occurances of a substring from the back
	def rreplace(self, s, old, new, occurrence):
		li = s.rsplit(old, occurrence)
		return new.join(li)
    
	@commands.command(desc='uptime')
	async def uptime(self, ctx : commands.Context):
		now = datetime.datetime.utcnow()
		delta = now - start_time
		hours, remainder = divmod(int(delta.total_seconds()), 3600)
		minutes, seconds = divmod(remainder, 60)
		days, hours = divmod(hours, 24)
		uptime_stamp = ''
		if days:
			uptime_stamp += f'**{days}** {"day" if days==1 else "days"}, '
		if hours:
			uptime_stamp += f'**{hours}** {"hour" if hours==1 else "hours"}, '
		if minutes:
			uptime_stamp += f'**{minutes}** {"minute" if minutes==1 else "minutes"}, '
		if seconds:
			uptime_stamp += f'**{seconds}** {"second" if seconds==1 else "seconds"}, '
		uptime_stamp=self.rreplace(s=uptime_stamp, old=', ', new='', occurrence=1)
		if uptime_stamp.count(',') > 1:
			uptime_stamp=self.rreplace(s=uptime_stamp, old=', ', new=', and ', occurrence=1)
		elif uptime_stamp.count(',')==1:
			uptime_stamp=self.rreplace(s=uptime_stamp, old=', ', new=' and ', occurrence=1)
		embed = discord.Embed(title='Uptime', description=f'The bot, {self.bot.user.name}, has been online for {uptime_stamp}')
		await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(Uptime(bot))
