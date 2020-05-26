import discord
import asyncio
import datetime
from datetime import datetime
from datetime import timezone
from discord.ext import commands
import re
SNOWFLAKE_REGEX = re.compile('\D') #compile regular expression matching all characters that aren't digits

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
    return isinstance(snowflake,str) and not SNOWFLAKE_REGEX.search(snowflake)
    
#should be a util class when cog setup
def modActionLogEmbed(action,member,reason,issuer):
    embed = discord.Embed(colour = discord.Colour.red(), description = f'{action} {member.mention} with reason: {reason}', timestamp = datetime.now(timezone.utc))
    embed.set_footer(text= f"Issued by {issuer}({issuer.id})", icon_url=issuer.avatar_url)
    return embed