import re
from .stringbuilder import StringBuilder

OPTION_REGEX = re.compile(' -[a-zA-Z]+')
FLAGS_REGEX = re.compile('-')
SPACE_REGEX = re.compile(' ')
EMPTY_REGEX = re.compile('')
NUMERIC_REGEX = re.compile('\d+(?:\.\d+)?')


# replace occurances of a substring from the back
def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


def isNaN(value):
    return not NUMERIC_REGEX.fullmatch(value)


# efficiently build a string of variable length when multiple members are found following a query
def buildMultiMatchString(command_prefix, command, mem, member):
    strBuilder = StringBuilder(f'Found {len(mem)} possible matches for "{member}":```')
    for index, memMatch in enumerate(mem):
        strBuilder.append(f'\n{index + 1}. {memMatch}')
    strBuilder.append(f'```')
    if len(mem) == 5:
        strBuilder.append(f'\n(number of matches shown is capped at 5, there may or may not be more)')
    strBuilder.append(f'\nTry using the {command_prefix}{command} command again with a more specific search term!')
    return strBuilder.to_string()


# split arguments into seperate (-x) flags where x can be any letter or sequence of letters
# each flag will be seperated even if given as a single string and returned as a list
# non-flag arguments are returned in a list in the order they appear, seperated by flag occurances
# returns values in the form: [[arg0,arg1,arg2,...],[flag0,flag1,...]]
# positional flags and non-positional flags should not be mixed in the same syntax; only accept one per command
def splitArgs(input):
    if not re.search(OPTION_REGEX, input):
        return [input]
    space_split = re.split(SPACE_REGEX, input)
    option_split_args = OPTION_REGEX.split(input)
    option_split_args = [arg.strip() for arg in option_split_args]
    raw_flags = list(filter(FLAGS_REGEX.match, space_split))
    joined_flags = ''.join(raw_flags)
    raw_flags = re.split(FLAGS_REGEX, joined_flags)
    joined_flags = ''.join(raw_flags)
    flags = re.split(EMPTY_REGEX, joined_flags)
    flags.pop()  # remove tailing empty string
    flags.pop(0)  # remove leading empty string
    flags = [flag.lower() for flag in flags]
    return [option_split_args, flags]
