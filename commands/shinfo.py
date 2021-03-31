import discord
from discord.ext import commands


class ShInfo(commands.Cog, name='Sh_info'):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command(description="Displays shard info", hidden=True)
    async def shinfo(self, ctx: commands.Context):
        colors = {
            299: discord.Color.green(),
            300: 0xFFFF00,
            500: discord.Color.orange(),
            1000: discord.Color.red()
        }
        shard_ids = ", ".join([str(key) for key in self.bot.shards.keys()])
        shard_count = len(self.bot.shards)
        this_shard = str(round(self.bot.latency*1000))
        clr = None
        for ping, color in colors.items():
            if ping == 299 and int(this_shard) < ping:
                clr = color
            elif int(this_shard) > ping:
                clr = color
            if clr is not None and int(this_shard) > ping:
                clr = color
        all_shards = ", ".join([str(round(latency[1]*1000))+"ms" for latency in self.bot.latencies])
        if shard_count >= 10:
            all_shards = "Too Many Shards ({})".format(shard_count)
            shard_ids = "Too Many Shards ({})".format(shard_count)
        form = f"Shard IDs: ({shard_ids})\nShard Count: {shard_count}\nThis Shard's Latency: {this_shard}ms\nAll Shard Latencies: ({all_shards})"
        embed = discord.Embed(title="Shard Info", description=form, color=clr)
        await ctx.author.send(embed=embed)
        await ctx.send(f"Sent shard info to your DMs, {ctx.author.mention}")


def setup(bot):
    bot.add_cog(ShInfo(bot))
