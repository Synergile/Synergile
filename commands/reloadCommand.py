import discord
from discord.ext import commands
from util.discordutil import find_command


class ReloadCommand(commands.Cog, name='ReloadCommand'):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_any_role(713125578773102603, 766100975382953984)
    @commands.command(description="Reload a Command", aliases=['rlc'], usage='<commandName>')
    async def reloadCommand(self, ctx, *, input=None):
        if input is None:
            await ctx.send('You must provide a command name or alias')
            return
        commandName = find_command(self.bot, input)
        if commandName is None:
            return await ctx.send(f'Reload failed: Could not find command or alias `{input}`')
        try:
            self.bot.reload_extension(f'commands.{commandName}')
            await ctx.send(f'Successfully reloaded `{commandName}`')
        except Exception as e:
            await ctx.send(f'Reload failed with exception: `{e}`')


def setup(bot):
    bot.add_cog(ReloadCommand(bot))
