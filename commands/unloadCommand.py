import discord
from discord.ext import commands
from util.discordutil import find_command


class UnloadCommand(commands.Cog, name='UnloadCommand'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Unload a command", aliases=['ulc'], usage='<commandName>')
    async def unloadCommand(self, ctx, *, input=None):
        if input is None:
            await ctx.send('You must provide a command name or alias')
            return
        commandName = find_command(self.bot, input)
        try:
            self.bot.unload_extension(f'commands.{commandName}')
            await ctx.send(f'Successfully unloaded `{commandName}`')
        except Exception as e:
            await ctx.send(f'Unload failed with exception: `{e}`')


def setup(bot):
    bot.add_cog(UnloadCommand(bot))
