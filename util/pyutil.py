import asyncio
import re
OPTION_REGEX = re.compile(' -[a-zA-Z]+')
FLAGS_REGEX = re.compile('-')
SPACE_REGEX = re.compile(' ')
EMPTY_REGEX = re.compile('')

#replace occurances of a substring from the back
def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

#efficiently build a string of variable length when multiple members are found following a query
def buildMultiMatchString(command_prefix,command,mem,member):
    strBuilder=f'Found {len(mem)} possible matches for "{member}":```'
    strBuilder=''.join([strBuilder, ''.join(f'\n{index+1}. {memMatch}' for index,memMatch in enumerate(mem))])
    strBuilder+=f'```'
    if len(mem)==5:
        strBuilder+=f'\n(number of matches shown is capped at 5, there may or may not be more)'
    strBuilder+=f'\nTry using the {command_prefix}{command} command again with a more specific search term!'
    return strBuilder

#split arguments into seperate (-x) flags where x can be any letter or sequence of letters
#each flag will be seperated even if given as a single string and returned as a list
#non-flag arguments are returned in a list in the order they appear, seperated by flag occurances
#returns values in the form: [[arg0,arg1,arg2,...],[flag0,flag1,...]]
#positional flags and non-positional flags should not be mixed in the same syntax; only accept one per command
def splitArgs(input):
    if(not re.search(OPTION_REGEX, input)):
        return [input]
    spaceSplit = re.split(SPACE_REGEX, input)
    optionSplitArgs = OPTION_REGEX.split(input)
    optionSplitArgs = [arg.strip() for arg in optionSplitArgs]
    rawFlags = list(filter(FLAGS_REGEX.match, spaceSplit))
    joinedFlags = ''.join(rawFlags)
    rawFlags = re.split(FLAGS_REGEX, joinedFlags)
    joinedFlags = ''.join(rawFlags)
    flags = re.split(EMPTY_REGEX, joinedFlags)
    flags.pop()  # remove tailing empty string
    flags.pop(0) # remove leading empty string
    flags = [flag.lower() for flag in flags]
    return [optionSplitArgs, flags]