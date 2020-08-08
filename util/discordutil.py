import re
import discord
import asyncio
import datetime
from datetime import datetime
from datetime import timezone
from discord.ext import commands
from discord import CategoryChannel
from util.stringbuilder import StringBuilder
from util.listutil import listFindAll, listFindSome
SNOWFLAKE_REGEX = re.compile('\D') #compile regular expression matching all characters that aren't digits
CHANNEL_SNOWFLAKE_REGEX = re.compile('<#(\d{17,21})>') 

#resolve a string to a member object
async def resolveMember(ctx, stringToResolve,*,sensitive=False,strict=False):
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
			if(sensitive):
				search = lambda m: m.name.startswith(stringToResolve) or m.nick and m.nick.startswith(stringToResolve)
			elif(strict):
				search = lambda m: m.name == stringToResolve or m.nick == stringToResolve
			else:
				r = re.compile(f'^{stringToResolve}.*', re.I)
				search = lambda m: True if r.match(m.name) or r.match(m.nick) else False
			memList = listFindSome(ctx.guild.members, search, limit=5)
		except Exception:
			memList = []
		print(memList)
		if len(memList)==0:
			member = None
		elif len(memList)==1:
			member = memList[0]
		else:
			return memList
	return member

def resolveChannel(ctx,channelResolvable,*,strict=False,resolveCategoryChannels=True):
	#attempt to resolve as pure ID
	if isSnowflake(channelResolvable):
		channel = ctx.guild.get_channel(int(channelResolvable))
		if(not isinstance(channel,CategoryChannel)):
			return channel
		channelResolvable = channel.name
		strict = True
	#attempt to resolve as mention (extract ID from mention)
	#elif match := CHANNEL_SNOWFLAKE_REGEX.fullmatch(str(channelResolvable)): python 3.8 syntax
	else:
		match = CHANNEL_SNOWFLAKE_REGEX.fullmatch(str(channelResolvable))
		if match:
			channel =  ctx.guild.get_channel(int(match[1]))
			if(not isinstance(channel,CategoryChannel)):
				return channel
			channelResolvable = channel.name
			strict = True
	#attempt to resolve as channel name or partial name
	searchFunc = (lambda ch: ch.name.startswith(channelResolvable)) if not strict else (lambda ch: ch.name == channelResolvable)
	channelList = tuple(listFindAll(ctx.guild.channels,searchFunc))
	if len(channelList)==0:
		#check k/v of defined category names
		#if found in k/v:
		#	retrieve and resolve list of channels for that group
		#else:
		return None
	elif len(channelList)==1:
		channel = channelList[0]
	else:
		return channelList
	if(resolveCategoryChannels and isinstance(channel,CategoryChannel)):
		return channel.text_channels
	return channel
	
	
#returns true if a value only contains characters 0-9, false otherwise. does not check length. 
#a consequence of this is that is will return true on empty values
def isSnowflake(snowflake):
	return isinstance(snowflake,str) and not SNOWFLAKE_REGEX.search(snowflake)
	
#should be a util class when cog setup
def modActionLogEmbed(action,member,reason,issuer):
	embed = discord.Embed(colour = discord.Colour.red(), description = f'{action} {member.mention} with reason: {reason}', timestamp = datetime.now(timezone.utc))
	embed.set_footer(text= f"Issued by {issuer}({issuer.id})", icon_url=issuer.avatar_url)
	return embed
	
#efficiently build a string of variable length when multiple members are found following a query
def buildMultiMatchString(command_prefix,command,mem,member): 
    strBuilder = StringBuilder(f'Found {len(mem)} possible matches for "{member}":```')
    for index,memMatch in enumerate(mem):
        strBuilder.append(f'\n{index+1}. {memMatch}')
    strBuilder.append(f'```')
    if len(mem)==5:
        strBuilder.append(f'\n(number of matches shown is capped at 5, there may or may not be more)')
    strBuilder.append(f'\nTry using the `{command_prefix}{command}` command again with a more specific search term!')
    return strBuilder.to_string()
	
def find_command(bot,commandName):
	if(commandName is not None):
		for command in bot.walk_commands():
			if(command.name == commandName):
				return command.name
			if(command.aliases is not None):
				for alias in command.aliases:
					if(alias == commandName):
						return command.name
	return None

async def author_reply(ctx, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None):
	if(not isinstance(ctx,commands.Context)):
		raise TypeError('ctx must be a Context object')
	if(isinstance(content, discord.Embed)):
		embed = content
		content = None
	try:
		sent = await ctx.author.send(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce)
		return sent
	except discord.errors.Forbidden as e:
		if(e.code != 50007):
			raise
		await ctx.send(f"{ctx.author.mention}, I can't DM you! Make sure your DMs are open, and try that again!", delete_after=20)
		return
	except discord.errors.HTTPException as e:
		if(e.code != 50006):
			raise
		raise RuntimeError('content or embed must be defined') from e
