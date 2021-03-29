import discord
from discord.ext import commands


class InviteCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command(name="invite", aliases=["server", "link", "website"])
    async def _invite(self, ctx: commands.Context):
        embed = discord.Embed(title="Synergile Invite Link",
                              description="You can add me to your server using [my invite](https://synergile.xyz/invite)",
                              color=discord.Color.blurple())
        embed.add_field(name="Come visit us!", value="Visit us in our [support server](https://synergile.xyz/server)", inline=False)
        embed.add_field(name="Take a peek at our website", value="Find it [here](https://synergile.xyz)")
        embed.set_thumbnail(url="https://synergile.xyz/images/synergile_logo.png")
        await ctx.send(embed=embed)


def setup(bot: commands.AutoShardedBot):
    bot.add_cog(InviteCog(bot))
