import discord
import asyncio
import datetime
from datetime import datetime
from datetime import timezone
from discord.ext import commands
import re
SNOWFLAKE_REGEX = re.compile('\D') #compile regular expression matching all characters that aren't digits
MAX_MESSAGE_LENGTH = 2000
BASE_TRUNC_LENGTH = 200
MAX_TRUNC_LENGTH = 499


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

# send message to messageable target, automatically splitting into multiple messages as needed
# message and target are required args
async def split_send(message: str, target: discord.abc.Messageable, code_block=False, code_language=None, bookend=None, header=None, footer=None):
    if len(message) <= MAX_MESSAGE_LENGTH:
        # no split needed (considering base message)
        sent = await dress_message(message, target, code_block=code_block, code_language=code_language, bookend=bookend, header=header, footer=footer, first=True, last=True)
        if sent[0]:
            return [sent[1]]
    
    # auto splitting
    messages = []
    splitter = ''
    remaining_message = message
    split_more = True
    first = True
    last = False
    max_trunc = BASE_TRUNC_LENGTH
    pop_count = 1
    split_index = MAX_MESSAGE_LENGTH if len(message) > MAX_MESSAGE_LENGTH else len(message)
    while split_more:
        first_message = remaining_message[:split_index]
        remaining_message = remaining_message[split_index:]
        removed = ''
        if '\n' in first_message:
            print('line')
            splitter = '\n'
            first_message, removed = line_trunc(first_message, pop_count, max_trunc)
            if len(first_message) == 0:
                print('\tsentence')
                first_message = removed
                splitter = '. '
                if '. ' in first_message:
                    first_message, removed = sentence_trunc(first_message, pop_count, max_trunc)
                if len(first_message) == 0:
                    print('\t\tgeneral')
                    first_message = removed
                    splitter = ' '
                    first_message, removed = general_trunc(first_message, pop_count, max_trunc, max_trunc > MAX_TRUNC_LENGTH)
                    if len(first_message) == 0:
                        max_trunc = max_trunc + 100
        elif '. ' in first_message:
            print('sentence')
            splitter = '. '
            first_message, removed = sentence_trunc(first_message, pop_count, max_trunc)
            if len(first_message) == 0:
                print('\tgeneral')
                first_message = removed
                splitter = ' '
                first_message, removed = general_trunc(first_message, pop_count, max_trunc, max_trunc > MAX_TRUNC_LENGTH)
                if len(first_message) == 0:
                    max_trunc = max_trunc + 100
        else:
            print('general')
            splitter = ' '
            first_message, removed = general_trunc(first_message, pop_count, max_trunc, max_trunc > MAX_TRUNC_LENGTH)
            if len(first_message) == 0:
                max_trunc = max_trunc + 100
        remaining_message = f'{removed}{remaining_message}'
        if len(remaining_message.strip()) == 0:
            last = True
        if len(first_message) != 0:
            sent = await dress_message(first_message, target, code_block, code_language, bookend, header, footer, first, last)
        else:
            sent = (False, removed)
        if sent[0]:
            messages.append(sent[1])
            pop_count = 1
            max_trunc = BASE_TRUNC_LENGTH
            splitter = ''
            if first:
                header = None
                first = False
            split_more = len(remaining_message) > MAX_MESSAGE_LENGTH
        else:
            max_trunc += 20 + abs(len(sent[1]) - MAX_MESSAGE_LENGTH)
            pop_count += 1
            remaining_message = f'{first_message}{splitter}{remaining_message}'
    if last:
        return messages
    last = True
    sent = await dress_message(remaining_message, target, code_block, code_language, bookend, header, footer, first, last)
    if sent[0]:
        messages.append(sent[1])
        return messages
    if bookend is not None:
        if isinstance(bookend, list):
            if len(bookend) % 2 == 0:
                footer = ''.join(bookend[len(bookend)/2:])
            else:
                footer = ''.join(bookend)
        else:
                footer = ''.join(bookend)
        bookend = None
    split_sent = await split_send(remaining_message, target, code_block=code_block, code_language=code_language, bookend=bookend, header=header, footer=footer)
    messages.extend(split_sent)
    return messages

def line_trunc(first_message, pop_count, max_trunc):
    split_pattern = '\n'
    removed = first_message[0-max_trunc:]
    first_message = first_message[:0-max_trunc]
    restoring = removed.split(split_pattern)
    popped = []
    for i in range(pop_count):
        if len(restoring) == 0:
            break
        popped.insert(0, restoring.pop())
    if len(split_pattern.join(restoring).strip()) > 0:
        first_message = f'{first_message}{split_pattern.join(restoring)}'
        removed = split_pattern.join(popped)
    else:
        restoring.extend(popped)
        removed = split_pattern.join(restoring)
        removed = f'{first_message}{removed}'
        first_message = ''
    return first_message, removed

# attempt truncation at the last complete sentence
def sentence_trunc(first_message, pop_count, max_trunc):
    split_pattern = r'. '
    removed = first_message[0-max_trunc:]
    first_message = first_message[:0-max_trunc]
    restoring = removed.split(split_pattern)
    popped = []
    for i in range(pop_count):
        if len(restoring) == 0:
            break
        popped.insert(0, restoring.pop())
    if len(split_pattern.join(restoring).strip()) > 0:
        first_message = f'{first_message}{split_pattern.join(restoring)}.'
        removed = split_pattern.join(popped)
    else:
        restoring.extend(popped)
        removed = split_pattern.join(restoring)
        removed = f'{first_message}{removed}'
        first_message = ''
    return first_message, removed

# attempt truncation at the last complete word in the final <max_trunc> characters
def general_trunc(first_message, pop_count, max_trunc, forced=False, split_pattern=' '):
    if forced:
        max_trunc = BASE_TRUNC_LENGTH
        print('fix up')
    removed = first_message[0-max_trunc:]
    first_message = first_message[:0-max_trunc]
    if not forced:
        restoring = removed.split(split_pattern)
        popped = []
        for i in range(pop_count):
            if len(restoring) == 0:
                break
            popped.insert(0, restoring.pop())
        if len(split_pattern.join(restoring).strip()) > 0:
            first_message = f'{first_message}{split_pattern.join(restoring)}'
            removed = split_pattern.join(popped)
        else:
            restoring.extend(popped)
            removed = split_pattern.join(restoring)
            removed = f'{first_message}{removed}'
            first_message = ''
    return first_message, removed

# helper function to manage application of split_send arguments on messages
async def dress_message(message, target, code_block=False, code_language=None, bookend=None, header=None, footer=None, first=False, last=False):
    msg = message
    if code_block:
       lang = code_language if code_language is not None else ''
       msg = f'```{lang}\n{msg}```'
    if bookend is not None and (first or last):
        if isinstance(bookend, list):
            if len(bookend) % 2 == 0:
                bookend_length = len(bookend)
                fbkend = ''.join(bookend[:bookend_length/2])
                bbkend = ''.join(bookend[bookend_length/2:])
                if first:
                    msg = f'{fbkend}{msg}'
                if last:
                    msg = f'{msg}{bbkend}'
                    
            else:
                bookend = ''.join(bookend)
                if first:
                    msg = f'{bookend}{msg}'
                if last:
                    msg = f'{msg}{bookend}'
        else:
            if first:
                msg = f'{bookend}{msg}'
            if last:
                msg = f'{msg}{bookend}'
    if first and header is not None:
        msg = f'{header}{msg}'
    if last and footer is not None:
        msg = f'{msg}{footer}'
    # check if splitting is needed after applying arguments
    if len(msg) <= MAX_MESSAGE_LENGTH:
        sent = await target.send(msg)
        return (True, sent)
    else:
        return (False, msg)

