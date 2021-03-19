import discord
from discord.ext import commands


class Purge(commands.Cog, name='Purge'):
    def __init__(self, bot):
        self.bot = bot
        self.response = ['Yes', 'No']

    @commands.command(name='purge', description="Purges a number of messages from the channel", usage='<amount>')
    async def purge(self, ctx, amount=None):
        if amount is not None:
            amount = int(amount) + 1
            if amount > 100:
                await ctx.send("Number of messages to purge must be less than 100", delete_after=12)
                return
            deleted = await ctx.channel.purge(limit=amount)
        else:
            await ctx.send("You must provide a number of messages to purge", delete_after=12)


def setup(bot):
    bot.add_cog(Purge(bot))
