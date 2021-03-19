import datetime, time
import discord
from discord.ext import commands
from util.pyutil import rreplace
from util.stringbuilder import StringBuilder


class Uptime(commands.Cog, name='Uptime'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        description='Amount of time the bot has been connected to Discord since establishing this connection')
    async def uptime(self, ctx: commands.Context):
        now = datetime.datetime.utcnow()
        delta = now - self.bot.readyAt
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        string_builder = StringBuilder()
        if days:
            string_builder.append(f'**{days}** {"day" if days == 1 else "days"}, ')
        if hours:
            string_builder.append(f'**{hours}** {"hour" if hours == 1 else "hours"}, ')
        if minutes:
            string_builder.append(f'**{minutes}** {"minute" if minutes == 1 else "minutes"}, ')
        if seconds:
            string_builder.append(f'**{seconds}** {"second" if seconds == 1 else "seconds"}, ')
        uptime_stamp = string_builder.to_string()
        uptime_stamp = rreplace(s=uptime_stamp, old=', ', new='', occurrence=1)
        if uptime_stamp.count(',') > 1:
            uptime_stamp = rreplace(s=uptime_stamp, old=', ', new=', and ', occurrence=1)
        elif uptime_stamp.count(',') == 1:
            uptime_stamp = rreplace(s=uptime_stamp, old=', ', new=' and ', occurrence=1)
        embed = discord.Embed(title='Uptime', description=f'I have been online for {uptime_stamp}')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Uptime(bot))
