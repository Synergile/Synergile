import re
from util.listutil import listFindIndex,listIncludes,listIndexOf,listSplice

DASHFLAG = '-'
DASHFLAG_REGEX = re.compile('(?:(?<=\s)|(?<=^))(-[a-zA-Z]+)(?:(?=\s)|(?=$))')
DOUBLE_DASHFLAG_REGEX = re.compile('(?:(?<=\s)|(?<=^))(--[a-zA-Z\-_]+)(?:(?=\s)|(?=$))')

__all__ = (
	'parseFlags',
	'parsePositionalFlags',
	'parseTruthyFlags',
)

# parse args that designate the location of arguments when specifying inputs, such as 'mycommand some other text -t title -i some information' (these can be flipped and  still work)
def parsePositionalFlags(args,flags,*,flagPrefix=None,flagMatching=None,flagRegex=None,singlePosition=False,disableAutoPrefix=False):
	flagPrefix = flagPrefix or DASHFLAG
	flagRegex = flagRegex or re.compile(f'((?<=\\s)|(?<=^)){flagPrefix}{flagMatching}((?=\\s)|(?=$))') if flagMatching else DASHFLAG_REGEX
	if not isinstance(flagRegex,re.Pattern):
		raise TypeError('flagRegex must be a Regular Expression')
	originalFlags = flags
	if not disableAutoPrefix:
		flags = { key:''.join([flagPrefix,aFlag]) for key,aFlag in originalFlags.items() }
	obj = {}
	for key,flag in flags.items():
		if listIncludes(args,flag):
			indexKey = listIndexOf(args,flag)
			nextFlagIndex = 1 if singlePosition else listFindIndex(args[indexKey+1:], lambda arg: flagRegex.fullmatch(arg))
			val = ' '.join(listSplice(args, indexKey+1, len(args) if nextFlagIndex==-1 else nextFlagIndex))
			obj[key] = val
			listSplice(args,indexKey,1)
		else:
			obj[key] = None
	obj['args'] = args
	return obj

# parse args that are used to designate conditions as true or false, such as -f (commonly used as force) or -h (help); Supports combining individual flags such as -vE (verbose + extended syntax, flags from bash globbing)
def parseTruthyFlags(args,flags,*,flagPrefix=None,flagMatching=None,flagRegex=None,disableAutoPrefix=False,allowDoublePrefix=True,doublePrefix=None,doubleMatching=None,doubleRegex=None):
	flagPrefix = flagPrefix or DASHFLAG
	flagRegex = flagRegex or re.compile(f'((?<=\\s)|(?<=^)){flagPrefix}{flagMatching}((?=\\s)|(?=$))') if flagMatching else DASHFLAG_REGEX
	if not isinstance(flagRegex,re.Pattern):
		raise TypeError('flagRegex must be a Regular Expression')
	originalFlags = flags
	if not disableAutoPrefix:
		flags = { key:''.join([flagPrefix,aFlag]) for key,aFlag in originalFlags.items() }
	obj = {}
	if allowDoublePrefix:
		doublePrefix = doublePrefix or ''.join([flagPrefix,flagPrefix])
		doubleRegex = doubleRegex or re.compile(f'((?<=\\s)|(?<=^)){doublePrefix}{doubleMatching}((?=\\s)|(?=$))') if doubleMatching else DOUBLE_DASHFLAG_REGEX
		found = doubleRegex.findall(' '.join(args)) 
	else:
		found = []
	found = [ *found, *[ ''.join([flagPrefix,foundItem]) for foundItem in ''.join(''.join([ string if len(tupple) is not 2 else found.append(''.join(tupple)) or '' if string is '-' else '' for tupple in flagRegex.findall(' '.join(args)) for string in tupple ]).split(flagPrefix))] ]
	count = 0
	for key,flag in flags.items():
		if listIncludes(found,flag):
			listSplice(found,listIndexOf(found,flag),1)
			if flag.startswith(doublePrefix):
				resultOfFind = { 'index':listIndexOf(args,flag), 'remainingFlags':'' }
			else:
				resultOfFind = listFindMatchingFlagIndex(args,flag,flagPrefix,flagRegex)
			remainingFlags = resultOfFind['remainingFlags']
			listSplice(args,resultOfFind['index'],1,remainingFlags) if remainingFlags else listSplice(args,resultOfFind['index'],1)
			obj[key] = True
			count = count + 1
		else:
			obj[key] = False
	obj['args'] = args
	obj['count'] = count
	return obj

# specialized version of listFind() used in parseTruthyFlags
def listFindMatchingFlagIndex(target,flag,prefix,regex):
	for index,value in enumerate(target):
		if(regex.fullmatch(value)):
			if len(value) == 2:
				if value == flag:
					return { 'index':index, 'remainingFlags':'' }
			else:
				flagsInVal = [ ''.join([prefix,flagV]) for flagV in ''.join(value.split(prefix)) ]
				if listIncludes(flagsInVal,flag):
					listSplice(flagsInVal,listIndexOf(flagsInVal,flag),1)
					remainingFlags = ''.join([prefix,''.join(''.join(flagsInVal).split(prefix))])
					return { 'index':index, 'remainingFlags':remainingFlags }
	return { index:-1,remainingFlags:None }

# convenience unified function
def parseFlags(args,flags,*,positional=None,truthy=False,flagPrefix=None,flagMatching=None,flagRegex=None,singlePosition=False,disableAutoPrefix=False,allowDoublePrefix=True,doublePrefix=None,doubleMatching=None,doubleRegex=None):
	if isinstance(args,str):
		args = args.split(' ') #this causes strings to be valid which is convenient
	if truthy:
		if positional:
			raise ValueError('optional arguments "truthy" and "positional" are mutually exclusive')
		return parseTruthyFlags(args,flags,flagPrefix=flagPrefix,flagMatching=flagMatching,flagRegex=flagRegex,disableAutoPrefix=disableAutoPrefix,allowDoublePrefix=allowDoublePrefix,doublePrefix=doublePrefix,doubleMatching=doubleMatching,doubleRegex=doubleRegex)
	return parsePositionalFlags(args,flags,flagPrefix=flagPrefix,flagMatching=flagMatching,flagRegex=flagRegex,singlePosition=singlePosition,disableAutoPrefix=disableAutoPrefix)