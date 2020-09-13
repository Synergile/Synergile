import discord
import asyncio
from discord.ext import commands
from datetime import datetime
import os
cfgInDir = False
foundPrefix = False
for i in os.listdir():
	if i == "config.config":
		cfgInDir = True
		with open('config.config', 'r') as config:
			for line in config:
				splitline = line.split(':')
				if splitline[0].lower() == "prefix":
					prefix = splitline[1]
					foundPrefix = True
if not cfgInDir:
	os.chdir("Synergile")
	with open('config.config', 'r') as config:
		for line in config:
			splitline = line.split(':')
			if splitline[0].lower() == "prefix":
				prefix = splitline[1]
				foundPrefix = True
if not foundPrefix:
	print ("Couldn't find a prefix")
	raise LookupError("Tried to find 'prefix' in config.config, failed to do so")

desc= "Moderation bot engineered by CodeWritten, wakfi, jedi3, and Napkins"
bot = commands.AutoShardedBot(command_prefix=prefix, help_command=None, case_insensitive=True, description=desc)
#NO_MENTIONS = discord.AllowedMentions(everyone=False,users=False,roles=False) - add in d.py 1.4

#add readyAt property to bot class
def readyAtGetter(self):
	return self._readyAt
def readyAtSetter(self,value):
	self._readyAt = value
commands.Bot.readyAt = property(readyAtGetter, readyAtSetter)
@bot.event
async def on_ready():
	await bot.change_presence(status=discord.Status.online, activity=discord.Game(f'{bot.command_prefix}help for commands'))
	bot.readyAt = datetime.utcnow()
	print (f"Bot online")
	
'''
#kind of not a fan of this
@bot.event
async def on_command_error(ctx, error):
	if isinstance(error,commands.errors.CommandNotFound):
		return
	await ctx.send("An error occured!\n```{}```".format(error))
'''

curdir = os.getcwd()
curdir.split('\\')
if "Synergile" not in curdir:
	os.chdir("Synergile")
else:
	pass
for cog in os.listdir(f"{os.getcwd()}{os.path.sep}commands"):#path
	if cog.endswith(".py"):
		try:
			cog = f"commands.{cog.replace('.py', '')}"
			bot.load_extension(cog)
		except Exception as e:
			print(f"{cog} cannot be loaded:")
			raise e

with open('config.config', 'r') as f:
	for i in f:
		splitted = i.split(':')
		if splitted[0].lower() == "token":
			token = splitted[1]
bot.run(token)
