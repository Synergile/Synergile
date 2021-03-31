from discord.ext import commands


class ShInfo(commands.Cog, name='Sh_info'):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command(description="Displays shard info", hidden=True)
    async def shinfo(self, ctx: commands.Context):
        cshard = round(self.bot.latency*1000)
        shids = ", ".join([str(key) for key in self.bot.shards.keys()])
        if len(self.bot.shards.keys()) >= 10:
            shids = "Too Many Shards ({})".format(len(self.bot.shards.keys()))
        nlatencies = []
        for latency in self.bot.latencies:
            nlatencies.append(str(round(latency[1]*1000)))
        nlatencies = ", ".join(nlatencies)
        if len(self.bot.latencies) >= 10:
            nlatencies = shids
        await ctx.author.send(
            f"Current Shard Latency: {cshard}\nShard IDs or Shard Count: {shids}\nShards Latency: {nlatencies if len(nlatencies) <= 10 else 'Too Many Shards'}")
        await ctx.send(f"Sent shard info to your DMs, {ctx.author.mention}")


def setup(bot):
    bot.add_cog(ShInfo(bot))
