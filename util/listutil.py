def listSplice(target,start,deleteCount=None,*items):
	if deleteCount == None:
		deleteCount = len(target) - start
	total = start + deleteCount
	removed = target[start:total]
	target[start:total] = items
	return removed
	
def listIncludes(target,value):
	try:
		target.index(value)
		return True
	except ValueError:
		return False
		
def listIndexOf(target,value):
	try:
		return target.index(value)
	except ValueError:
		return -1
		
def listFindIndex(target,function):
	for index,value in enumerate(target):
		if function(value):
			return index
	return -1
	
def listFind(target,function):
	for value in target:
		if function(value):
			return value
	return None

def listFindAll(target,function):
	found = []
	for value in target:
		if function(value):
			found.append(value)
	return found

def listFindSome(target,function,*,limit=None):
	if(limit is None):
		return listFindAll(target,function)
	found = []
	for value in target:
		if function(value):
			found.append(value)
			if limit and len(found) == limit:
				break
	return found