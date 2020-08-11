import discord
from discord.ext import commands
from beta_utils import tester
class beta(commands.Cog, name='Beta'):
	def __init__(self, bot):
		self.bot = bot

    @commands.command(discription='Pushes a DM to all testers about a new release')
    async def release(self, ctx, *, message):
        path = os.getcwd