from discord.ext import commands


class BuildInfo(commands.Cog, name='Build Info'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Displays build info")
    async def buildinfo(self, ctx):
        file = 'buildinfo.conf'
        with open(file, 'r') as f:
            await ctx.send(''.join(f.readlines()))


def setup(bot):
    bot.add_cog(BuildInfo(bot))
