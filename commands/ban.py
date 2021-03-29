from discord import Forbidden
from discord.ext import commands
from util.pyutil import buildMultiMatchString, splitArgs
from util.discordutil import resolveMember, modActionLogEmbed


class Ban(commands.Cog, name='Ban'):
    def __init__(self, bot):
        self.bot = bot
        self.modLogChannelID = 713131470625046549  # will be guild lookup for value in database

    @check_permissions(ban_members=True)
    @commands.command(description="Ban a member from the server", usage='<member> [-r <reason>]')
    async def ban(self, ctx, *, member=None, reason="No reason provided"):
        if member is None:
            mem = None
        else:
            args = splitArgs(member)
            if len(args) == 1:
                member = args[0]
            else:
                member = args[0][0]
            # resolve argument to a member
            mem = await resolveMember(ctx, member)

        if mem is None:
            # return when input cannot be resolved
            await ctx.send('You must provide a valid user reference{}'.format(
                f': "{member}" could not be resolved to a user' if member is not None else ''))
            return

        if isinstance(mem, list):
            usersFound = buildMultiMatchString(self.bot.command_prefix, 'ban', mem, member)
            await ctx.send(usersFound)
        else:
            indexReason = -1
            try:
                indexReason = args[1].index('r') + 1
            except Exception:
                pass
            if indexReason > -1:
                try:
                    if args[0][indexReason] != '':
                        reason = args[0][indexReason]
                except Exception:
                    await ctx.send('An error occurred while attempting to parse arguments')
                    return
            try:
                await ctx.guild.ban(mem, reason=reason)
                if self.modLogChannelID is not None:
                    await ctx.guild.get_channel(self.modLogChannelID).send(
                        embed=modActionLogEmbed('Banned', mem, reason, ctx.author))
            except Forbidden as e:
                errMessage = str(e)
                if 'error code: 50013' in errMessage:
                    await ctx.send("I don't have permission to do that!")
            except Exception as e:
                print('encountered an unknown error in kick command:')
                print(repr(e))
                await ctx.send('An unknown error occurred. Please try again later')


def setup(bot):
    bot.add_cog(Ban(bot))
