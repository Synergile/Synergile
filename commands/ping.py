import datetime
from time import time
import discord
from discord.ext import commands
from discord.utils import snowflake_time


class Ping(commands.Cog, name='Ping'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Displays connection speed info",
                      help='Calculates the latency of the client to the endpoint based on the time it takes for a response message to be sent to the command message. API latency information is provided by the websocket')
    async def ping(self, ctx):
        colors = {
            299: discord.Color.green(),
            300: 0xFFFF00,
            500: discord.Color.orange(),
            1000: discord.Color.red()
        }
        m = await ctx.send("Pinging...")
        clr = None
        latency = int((snowflake_time(m.id) - snowflake_time(ctx.message.id)).microseconds / 1000)
        for png, color in colors.items():
            if png == 299 and latency < png:
                clr = color
            elif latency > png:
                clr = color
            if clr is not None and latency > png:
                clr = color
        embed = discord.Embed(title="Pong! \U0001f3d3",
                              description=f"Message Latency: {latency}ms\nAPI Latency: {round(self.bot.latency*1000)}ms",
                              color=clr)
        await m.edit(content="", embed=embed)


def setup(bot):
    bot.add_cog(Ping(bot))
