import discord
import asyncio
import datetime
from datetime import datetime
from datetime import timezone
from discord.ext import commands
import re
SNOWFLAKE_REGEX = re.compile('\D') #compile regular expression matching all characters that aren't digits
MAX_MESSAGE_LENGTH = 2000
BASE_TRUNC_AMMOUNT = 200

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
async def split_send(message=None, target=None, *, code_block=False, code_language=None, bookend=None, header=None, footer=None, *args=None, **kwargs=None):
    if args is not None:
        if not isinstance(args, list):
            raise TypeError('args must be a list of arguments')
        args_length = len(args)
        if args_length < 2:
            raise ValueError('args must at least contain items for message text and target')
        if args_length > 7:
            raise ValueError('too many arguments provided')
        message = args[0]
        target = args[1]
        try:
            code_block = args[2]
            code_language = args[3]
            bookend = args[4]
            header = args[5]
            footer = args[6]
        except IndexError as e:
            pass
    if kwargs is not None:
        if not isinstance(kwargs, dict):
            raise TypeError('kwargs must be a dict of arguments by keyword')
        message = kwargs['message']
        target = kwargs['target']
        if 'code_block' in kwargs:
            code_block = kwargs['code_block']
        if 'code_language' in kwargs:
            code_language = kwargs['code_language']
        if 'bookend' in kwargs:
            bookend = kwargs['bookend']
        if 'header' in kwargs:
            header = kwargs['header']
        if 'footer' in kwargs:
            footer = kwargs['footer']
    if message is None or target is None:
        raise ValueError('message and target are required arguments')
    if not isinstance(target, discord.abc.Messageable):
        raise ValueError('target must be a messageble object (i.e. derived from discord.abc.Messageble)')
    if not isinstance(message, str):
        message = str(message)
        
    if len(message) <= MAX_MESSAGE_LENGTH:
        # not splitting
        sent = dress_message(message, target, code_block=code_block, code_language=code_language, bookend=bookend, header=header, footer=footer, first=True, last=True)
        if sent[0]:
            return [sent[1]]
        """
        # going to try just advancing with the original message at this point instead of updating message
        else:
            message = sent[1]
            bookend = None
            header = None
            footer = None
            # problem: a codeblock that goes over the char limit at this stage
        """
    
    # auto splitting
    messsages = []
    remaining_message = message
    split_more = True
    first = True
    last = False
    aggressive_split = False
    max_trunc = BASE_TRUNC_AMMOUNT
    pop_count = 1
    split_index = len(message) > MAX_MESSAGE_LENGTH ? MAX_MESSAGE_LENGTH + 1 : len(message)
    while split_more:
        first_message = remaining_message[:split_index]
        remaining_message = remaining_message[split_index:]
        popped = []
        removed = ''
        if '\n' in first_message:
            for i in range(pop_count):
                msg_split = first_message.split('\n')
                popped.append(msg_split.pop())
                if len('\n'.join(popped)) > max_trunc:
                    msg_split.extend(popped)
                    break
            first_message = '\n'.join(msg_split)
            removed = '\n'.join(popped)
            if len(first_message) == MAX_MESSAGE_LENGTH:
                if '. ' in first_message:
                    first_message, removed = sentence_trunc(first_message, pop_count, max_trunc)
                if len(first_message) == MAX_MESSAGE_LENGTH:
                    first_message, removed = general_trunc(first_message, max_trunc, max_trunc > 400)
                    if len(first_message) === MAX_MESSAGE_LENGTH:
                        max_trunc = max_trunc + 200
                        aggressive_split = True
        elif '. ' in first_message:
            first_message, removed = sentence_trunc(first_message, pop_count, max_trunc)
            if len(first_message) == MAX_MESSAGE_LENGTH:
                first_message, removed = general_trunc(first_message, max_trunc, max_trunc > 400)
                if len(first_message) === MAX_MESSAGE_LENGTH:
                    max_trunc = max_trunc + 200
                    aggressive_split = True
        else:
            first_message, removed = general_trunc(first_message, max_trunc, max_trunc > 400)
                if len(first_message) === MAX_MESSAGE_LENGTH:
                    max_trunc = max_trunc + 100
                    aggressive_split = True
        remaining_message = f'{removed}{remaining_message}'
        if len(remaining_message.strip()) == 0:
            last = True
        sent = dress_message(first_message, target, code_block=code_block, code_language=code_language, bookend=bookend, header=header, footer=footer, first=frist, last=last)
        if sent[0]:
            messages.append(sent[1])
            aggressive_split = False
            pop_count = 1
            max_trunc = BASE_TRUNC_AMMOUNT
            if first:
                header = None
                first = False
            split_more = len(remaining_message) > MAX_MESSAGE_LENGTH
        else:
            aggressive_split = True
            max_trunc += len(sent[1]) - MAX_MESSAGE_LENGTH
            pop_count += 1
    if last:
        return messages
    last = True
    sent = dress_message(remaining_message, target, code_block=code_block, code_language=code_language, bookend=bookend, header=header, footer=footer, first=frist, last=last)
    if sent[0]:
        messages.append(sent[1])
        return messages
    if bookend is not None:
        if isinstance(bookend, list):
            if len(bookend) % 2 == 0:
                footer = ''.(bookend[len(bookend)/2:])
            else:
                footer = ''.join(bookend)
        else:
                footer = ''.join(bookend)
        bookend = None
    split_sent = await split_send(remaining_message, target, code_block=code_block, code_language=code_language, bookend=bookend, header=header, footer=footer)
    messages.extend(split_sent)
    return messages

# attempt truncation at the last complete sentence
def sentence_trunc(first_message, pop_count, max_trunc):
    for i in range(pop_count):
        msg_split = first_message.split('. ')
        popped.append(msg_split.pop())
        if len('. '.join(popped)) > max_trunc:
            msg_split.extend(popped)
            break
    first_message = '. '.join(msg_split)
    removed = '. '.join(popped)
    return first_message, removed

# attempt truncation after the last complete word in the final <max_trunc> characters
def general_trunc(first_message, max_trunc, forced):
    if forced:
        max_trunc = BASE_TRUNC_AMMOUNT
    removed = first_message[0-max_trunc:]
    first_message = first_message[:0-max_trunc]
    if not forced:
        second_split = removed.split(' ')
        restoring = second_split.pop()
        if len(''.join(second_split)) > 0:
            first_message = f'{first_message}{restoring}'
        else:
            second_split.append(restoring)
        removed = ' '.join(second_split)
    return first_message, removed

# helper function to manage application of split_send arguments on messages
def dress_message(message, target, *, code_block=False, code_language=None, bookend=None, header=None, footer=None, first=False, last=False):
    msg = message
    if code_block:
       lang = code_language if code_language is not None else ''
       msg = f'```{lang}\n{msg}```'
    if bookend is not None and (first or last):
        if isinstance(bookend, list):
            if len(bookend) % 2 == 0:
                bookend_length = len(bookend)
                fbkend = ''.join(bookend[:bookend_length/2])
                bbkend = ''.(bookend[bookend_length/2:])
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
    if header is not None:
        msg = f'{header}{msg}'
    if footer is not None:
        msg = f'{msg}{footer}'
    if len(msg) <= MAX_MESSAGE_LENGTH:
        # not splitting needed (recheck after applying arguments)
        sent = await target.send(msg)
        return (True, sent)
    else:
        return (False, msg)

