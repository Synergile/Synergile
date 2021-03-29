from discord.ext import commands


class ShInfo(commands.Cog, name='Sh_info'):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command(description="Displays shard info", hidden=True)
    async def shinfo(self, ctx: commands.Context):
        cshard = round(self.bot.latency*1000)
        shids = ", ".join(self.bot.shard_ids)
        nlatencies = []
        for latency in self.bot.latencies:
            nlatencies.append(round(latency*1000))
        nlatencies = ", ".join(nlatencies)
        await ctx.author.send(
            f"Current Shard Latency: {cshard}\nShard IDs: {shids}\nAverage Shards Latency: {nlatencies}")
        await ctx.send(f"Sent shard info to your DMs, {ctx.author.mention}")


def setup(bot):
    bot.add_cog(ShInfo(bot))
