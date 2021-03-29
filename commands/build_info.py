import discord
from discord.ext import commands


class Build_info(commands.Cog, name='Build_info'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Displays build info")
    async def build_info(self, ctx, file_override=None):
        if file_override is None:
            file = 'buildinfo.conf'
            with open(file, 'r') as f:
                await ctx.send(''.join(f.readlines()))

        else:
            file = file_override
            with open(file, 'r') as f:
                await ctx.send(''.join(f.readlines()))


def setup(bot):
    bot.add_cog(Build_info(bot))
