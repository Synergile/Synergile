import discord
from discord.ext import commands


class InviteCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command(name="invite")
    async def _invite(self, ctx: commands.Context):
        embed = discord.Embed(title="Invite link",
                              description="You can add me using [this link](https://synergile.xyz/invite)",
                              color=discord.Color.blurple())
        await ctx.send(embed=embed)


def setup(bot: commands.AutoShardedBot):
    bot.add_cog(InviteCog(bot))
