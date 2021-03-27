import discord
import asyncio
from discord.ext import commands
from datetime import datetime
import os
from util import configuration
from util import ensure_path
import traceback
if os.getcwd() != ensure_path.send_path():
    os.chdir(ensure_path.send_path())
token, prefix = configuration.configuration()

intents = discord.Intents()
intents.value = 0x378b
desc = "Moderation bot engineered by CodeWritten, wakfi, jedi3, and Napkins"
bot = commands.AutoShardedBot(command_prefix=prefix, help_command=None, case_insensitive=True, description=desc, intents=intents)
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


@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.errors.CommandNotFound):
        return
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        err_emb = discord.Embed(title=f"Missing the '{str(error.param).rstrip(': str')}' arg",
                                description=f"Usage: {bot.command_prefix}{ctx.command.qualified_name} {ctx.command.signature}",
                                color=discord.Color.red())
        await ctx.send(embed=err_emb)
    else:
        channel = bot.get_channel(817127799256252437)
        with open("error.log", "w") as err:
            err.write("".join(traceback.format_exception(type(error), error, error.__traceback__)))
        with open("error.log", "rb") as err:
            file = discord.File(err)
        log_form = "=====ERROR====\nTime: {0}\nCommand: {1}\nError:\n```{2}```"
        await channel.send(log_form.format(datetime.utcnow(), ctx.message.content, error), file=file)
        embed = discord.Embed(title="Something unknown happened!",
                              description="The issue has been reported",
                              color=discord.Color.red())
        await ctx.send(embed=embed)
        traceback.print_exception(type(error), error, error.__traceback__)


for cog in os.listdir(f"{os.getcwd()}{os.path.sep}commands"):#path
    if cog.endswith(".py"):
        try:
            cog = f"commands.{cog.replace('.py', '')}"
            bot.load_extension(cog)
        except Exception as e:
            print(f"{cog} cannot be loaded:")
            raise e

bot.run(token)
