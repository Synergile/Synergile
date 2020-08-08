import os
import asyncio
import discord
from discord.ext import commands
from util.listutil import listFind, listFindAll
from util.parseFlags import parseFlags
from util.discordutil import resolveChannel, buildMultiMatchString

DENY_SEND = discord.PermissionOverwrite()
DENY_SEND.send_messages = False
DENY_SEND.speak = False
DENY_SEND.stream = False #this is the video permission
NULL_SEND = discord.PermissionOverwrite()
NULL_SEND.send_messages = None
NULL_SEND.speak = None
NULL_SEND.stream = None
ALLOW_SEND = discord.PermissionOverwrite()
ALLOW_SEND.send_messages = True
ALLOW_SEND.speak = True
ALLOW_SEND.stream = True

#load channel categories k/v

class Lockdown(commands.Cog, name='lockdown'):
	
	def __init__(self,bot):
		self.bot = bot

	@commands.command(aliases=['lockdown'], description='Lockdown a channel or group of channels. In locked channels, non-elevated users cannot send messages',
	  help='Specify a channel or a group of channels to lock. If no channel is specified, the current channel will be locked', usage='[channelResolvable]')
	async def lock(self,ctx,*,channelResolvable=None):
		result = await self.toggleLockdown(ctx,channelResolvable,DENY_SEND,'lockdown')
		if(result['success']):
			channel = result['channel']
			oldPerms = result['oldPerms']
			[ await ch.send('🚨🚨 This channel is on lockdown 🚨🚨' if oldPerms[f'{ch.id}'] else '🚨 This channel is on lockdown 🚨') for ch in channel ] if result["category"] else await channel.send('🚨🚨 This channel is on lockdown 🚨🚨' if oldPerms else '🚨 This channel is on lockdown 🚨')
			#results in either "Lockdown of category something initiated" or "Lockdown of <#1234566959119249> initiated", with the second result resolving to a channel mention
			return await ctx.send(f'Lockdown of {f"{channelResolvable} category" if result["category"] else f"<#{channel.id}>"} initiated')
		else:
			return await ctx.send(result['reply'])
		
	@commands.command(description='Unlock a locked channel or group of channels',
	  help='Specify a channel or a group of channels to unlock. If no channel is specified, the current channel will be unlocked', usage='[channelResolvable]')
	async def unlock(self,ctx,*,channelResolvable=None):
		result = await self.toggleLockdown(ctx,channelResolvable,NULL_SEND,'unlock')
		if(result['success']):
			channel = result['channel']
			[ await ch.send('Channel lockdown has ended') for ch in channel ] if result["category"] else await channel.send('Channel lockdown has ended')
			return await ctx.send(f'Unlocked {f"{channelResolvable} category" if result["category"] else f"<#{channel.id}>"}')
		else:
			return await ctx.send(result['reply'])
		
	async def toggleLockdown(self,ctx,channelResolvable,permissions,action):
		if(channelResolvable):
			args = parseFlags(args=channelResolvable,flags={'strict':'-s','stricts':'--strict'},truthy=True,disableAutoPrefix=True,allowDoublePrefix=True)
			channelResolvable = ' '.join(args['args'])
			strict = args['strict'] or args['stricts']
			channelName = channelResolvable
			channel = resolveChannel(ctx,channelResolvable,strict=strict)
		else:
			channel = ctx.channel
		if(not channel):
			return { 'success':False, 'reply':f'Could not resolve {channelResolvable} to a channel' }
		elif(isinstance(channel,tuple)):
			return { 'success':False, 'reply':buildMultiMatchString(self.bot.command_prefix, action, [*channel], channelResolvable) }
			
		atEveryone = ctx.guild.default_role
		if(isinstance(channel,discord.abc.GuildChannel)):
			category = False
			channelID = channel.id
			channelName = channel.name
			channelPerm = channel.overwrites_for(atEveryone)
			if(action is 'unlock'):
				if(channelPerm.send_messages == False):
					oldPerms = {}
					lockMsg = listFind([c async for c in channel.history()], lambda msg: '🚨' in msg.content)
					lights = len(listFindAll([*lockMsg.content], lambda c: c == '🚨'))
					channelPerm.send_messages = True if lights == 4 else None
			else:
				if(channelPerm.send_messages != False):
					oldPerms = channelPerm.send_messages
					channelPerm.send_messages = permissions.send_messages
			await channel.set_permissions(atEveryone,overwrite=channelPerm,reason=f'Manual {action} request by: {ctx.author}({ctx.author.id})')
		else:
			category = True
			channelID = None
			oldPerms = {}
			for ch in channel:
				channelPerm = ch.overwrites_for(atEveryone)
				if(action is 'unlock'):
					if(channelPerm.send_messages == False):
						oldPerms = {}
						lockMsg = listFind([c async for c in ch.history()], lambda msg: '🚨' in msg.content)
						lights = len(listFindAll([*lockMsg.content]), lambda c: c == '🚨')
						channelPerm.send_messages = True if lights == 4 else None
				else:
					if(channelPerm.send_messages != False):
						oldPerms[f'{ch.id}'] = channelPerm.send_messages
						channelPerm.send_messages = permissions.send_messages
				await ch.set_permissions(atEveryone,overwrite=channelPerm,reason=f'Manual {action} request as part of {channelName} by: {ctx.author}({ctx.author.id})')
			
		return { 'success':True, 'channelID':channelID, 'channelName':channelName, 'category':category, 'channel':channel, 'oldPerms':oldPerms }

def setup(bot):
	bot.add_cog(Lockdown(bot))