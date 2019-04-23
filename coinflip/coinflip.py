from redbot.core import commands
from redbot.core.utils.chat_formatting import box
import discord, asyncio
from random import randint

class Coinflip(commands.Cog):
	"""Flips some coins."""
	def __init__(self, bot):
		self.bot = bot

	@commands.group()
	async def coinflip(self, ctx):
		"""
		Flips some coins.

		Type `[p]coinflip single` for a singular coinflip, or do `[p]coinflip multiple` for multiple coinflips.
		"""
		pass

	@coinflip.command()
	async def single(self, ctx):
		"""Flip a singular coin."""
		roll = ['\n\n\n - \n___','\n\n \ \n\n___','\n\n - \n\n___','\n / \n\n\n___',' - \n\n\n\n___',' \ \n\n\n\n___','\n - \n\n\n___','\n\n / \n\n___','\n\n\n - \n___']
		msg = "The coin landed on"
		check = lambda m: ctx.message.author == m.author and m.author.bot == False
		m = await ctx.send("\u200b")
		for x in range(9):
			await m.edit (content = box(roll[x]))
			await asyncio.sleep(0.5)
		coin = await ctx.send (msg)
		for x in range(3):
			msg += "."
			await asyncio.sleep (0.5)
			await coin.edit (content = msg)
		msg += f"{' Heads!' if randint(0,1) == 0 else ' Tails!'}"
		await coin.edit (content = msg)

	@coinflip.command()
	async def multiple(self, ctx, amt : int = 2):
		"""Flip multiple coins at once."""
		msg = "Flipping coins"
		heads, tails = 0, 0
		if amt < 2:
			return await ctx.send("Amount must be greater than or equal to 2 coins.")
		coin = await ctx.send (msg)
		for x in range(3):
			msg += "."
			await asyncio.sleep (0.5)
			await coin.edit (content = msg)
		for x in range(amt):
			if randint(0, 1) == 0:
				heads += 1
			else:
				tails += 1
		await ctx.send (box(f"Out of {str(amt)} coinflips:\n{str(heads)} {'coin' if heads == 1 else 'coins'} landed on heads.\n{str(tails)} {'coin' if tails == 1 else 'coins'} landed on tails."))
