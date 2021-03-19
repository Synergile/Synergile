import sys
import discord
from discord.ext import commands

'''
You must use a process manager for this command to work fully; I reccomend pm2 (surprisingly it works with python scripts)
'''


class Restart(commands.Cog, name='Restart'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Restart the bot")
    async def restart(self, ctx):
        await self.bot.change_presence(status=discord.Status.offline)
        await ctx.send(f"Restarting...")
        sys.exit(0)


def setup(bot):
    bot.add_cog(Restart(bot))
