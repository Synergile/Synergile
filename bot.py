import discord
import asyncio
from discord.ext import commands
from datetime import datetime
import youtube_dl
import os
desc= "Moderation bot engineered by CodeWritten, wakfi, jedi3, and Napkins"
bot = commands.Bot(command_prefix='!', help_command=None, case_insensitive=True, description=desc)
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

#music
players = {}

@bot.command()
async def join(ctx):
	member = ctx.guild.get_member(ctx.author.id)
	vc = member.voice.channel
	await vc.connect()

	
@bot.command()
async def leave(ctx):
	vc = ctx.guild.voice_client   
	await vc.disconnect()

@bot.command(aliases=['p'])
async def play(ctx, url: str):
	song_there = os.path.isfile("song.mp3")
	try:
		if song_there:
			os.remove("song.mp3")
			print("Removed old song file")
	except PermissionError:
		print("Trying to delete song file, but it's being played")
		await ctx.send("ERROR: Music playing")
		return

	await ctx.send("Getting everything ready now")

	voice = get(bot.voice_clients, guild=ctx.guild)

	ydl_opts = {
		'format': 'bestaudio/best',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192',
		}],
	}

	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		print("Downloading audio now\n")
		ydl.download([url])

	for file in os.listdir("./"):
		if file.endswith(".mp3"):
			name = file
			print(f"Renamed File: {file}\n")
			os.rename(file, "song.mp3")

	voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print("Song done!"))
	voice.source = discord.PCMVolumeTransformer(voice.source)
	voice.source.volume = 0.07

	nname = name.rsplit("-", 2)
	await ctx.send(f"Playing: {nname[0]}")
	print("playing\n")
			
for cog in os.listdir(".\\commands"):#path
	if cog.endswith(".py"):
		try:
			cog = f"commands.{cog.replace('.py', '')}"
			bot.load_extension(cog)
		except Exception as e:
			print(f"{cog} cannot be loaded:")
			raise e

with open('config.config', 'r') as f:
	tok = f.readline()
	tok.replace('\n', "")
bot.run(tok)
