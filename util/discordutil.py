import discord
import asyncio
import datetime
from datetime import datetime
from datetime import timezone
from discord.ext import commands
import re

SNOWFLAKE_REGEX = re.compile('\D')  # compile regular expression matching all characters that aren't digits

#decorator to check user permissions for command
def check_permissions(**perms):
    def predicate(ctx):
        return ((discord.Permissions(**perms).value | 0x8) & ctx.message.author.permissions_in(ctx.channel).value) > 0x0
    return commands.check(predicate)

#should be a util when cog setup
#resolve a string to a member object
async def resolveMember(ctx, stringToResolve):
	mc = commands.MemberConverter()
	stringToResolve = stringToResolve.strip()
	if isSnowflake(stringToResolve): 
		#gave an number that may be an ID
		member = ctx.guild.get_member(int(stringToResolve)) #if stringToResolve is not a valid snowflake, mem=None
	elif '@' in stringToResolve:
		#mentioned a user
		try:
			member = await mc.convert(ctx, stringToResolve)
		except Exception:
			member = None
	else:
		try:
			memList = await ctx.guild.query_members(query = stringToResolve)
		except Exception:
			memList = []
		if len(memList)==0:
			member = None
		elif len(memList)==1:
			member = memList[0]
		else:
			return memList
	return member
	
#returns true if a value only contains characters 0-9, false otherwise. does not check length. 
#a consequence of this is that is will return true on empty values
def isSnowflake(snowflake):
    return isinstance(snowflake, str) and not SNOWFLAKE_REGEX.search(snowflake)


# should be a util class when cog setup
def modActionLogEmbed(action, member, reason, issuer):
    embed = discord.Embed(colour=discord.Colour.red(), description=f'{action} {member.mention} with reason: {reason}',
                          timestamp=datetime.now(timezone.utc))
    embed.set_footer(text=f"Issued by {issuer}({issuer.id})", icon_url=issuer.avatar_url)
    return embed


def find_command(bot, commandName):
    if commandName is not None:
        for command in bot.walk_commands():
            if command.name == commandName:
                return command.name
            if command.aliases is not None:
                for alias in command.aliases:
                    if alias == commandName:
                        return command.name
    return None


async def author_reply(ctx, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None,
                       nonce=None):
    if not isinstance(ctx, commands.Context):
        raise TypeError('ctx must be a Context object')
    if isinstance(content, discord.Embed):
        embed = content
        content = None
    try:
        sent = await ctx.author.send(content=content, tts=tts, embed=embed, file=file, files=files,
                                     delete_after=delete_after, nonce=nonce)
        return sent
    except discord.errors.Forbidden as e:
        if e.code != 50007:
            raise
        await ctx.send(f"{ctx.author.mention}, I can't DM you! Make sure your DMs are open, and try that again!",
                       delete_after=20)
        return
    except discord.errors.HTTPException as e:
        if e.code != 50006:
            raise
        raise RuntimeError('content or embed must be defined') from e
