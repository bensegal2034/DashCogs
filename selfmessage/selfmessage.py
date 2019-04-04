import discord
from redbot.core import commands
from redbot.core import checks
from redbot.core import Config

class SelfMessage(commands.Cog):
	"""Allows the bot owner to send messages from the bot's account."""
	def __init__(self, bot):
		self.bot = bot
		self.config = Config.get_conf(self, identifier=99280384939814912)
		self.config.register_global(
			server = [x.id for x in self.bot.guilds][0],
			chn = None,
			enabled = True
		)

	@checks.is_owner()
	@commands.command()
	async def server(self, ctx, *, srv):
		"""
		Defines what server the bot should send messages to.

		Both full server names and ID will work to set the server.
		"""
		ids = [x.id for x in self.bot.guilds]
		names = [x.name for x in self.bot.guilds]
		if srv.isdigit() == False:
			if srv in names:
				await self.config.server.set(ids[names.index(srv)])
				await ctx.send("Server set.")
			else:
				await ctx.send("Can't find server!")
		else:
			srvi = int(srv)
			if srvi in ids:
				await self.config.server.set(ids[ids.index(srvi)])
				await ctx.send("Server set.")
			else:
				await ctx.send("Can't find server!")
	@checks.is_owner()
	@commands.command()
	async def channel(self, ctx, *, ch : discord.TextChannel):
		"""
		Defines what channel in the selected server the bot should send messages to.

		Both full channel names and ID will work to set the channel.
		"""
		g = self.bot.get_guild(await self.config.server())
		if ch is None:
			await ctx.send("Please specify a channel!")
			return
		await self.config.chn.set(ch.id)
		await ctx.send("Channel updated.")

	@checks.is_owner()
	@commands.command()
	async def enabled(self, ctx):
		"""Toggle if sending PMs to the bot as owner will send a message to the server & text channel specified."""
		if await self.config.enabled() == True:
			await self.config.enabled.set(False)
			await ctx.send("Toggled off.")
		else:
			await self.config.enabled.set(True)
			await ctx.send("Toggled on.")

	async def on_message(self, message):
		if not message.author.bot and not isinstance(message.channel, discord.TextChannel) and message.author.id == self.bot.owner_id and await self.config.enabled() == True:
			channel = self.bot.get_channel(await self.config.chn())
			await channel.send(message.content)
