import discord
from redbot.core import commands
from redbot.core import checks
from redbot.core import Config
from redbot.core.data_manager import cog_data_path
import os

class SelfMessage(commands.Cog):
	"""Allows the bot owner to send messages from the bot's account."""
	def __init__(self, bot):
		self.bot = bot
		self.config = Config.get_conf(self, identifier=99280384939814912)
		self.config.register_global(
			server = [x.id for x in self.bot.guilds][0],
			chn = None,
			enabled = True,
			access = []
		)

	@checks.is_owner()
	@commands.group(aliases=["selfset"])
	async def selfmessageset(self, ctx):
		"""All settings relating to SelfMessage. Settings are saved globally."""
		pass

	@checks.is_owner()
	@selfmessageset.command()
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
				name = self.bot.get_guild(ids[names.index(srv)]).name
				await ctx.send(f"Server set to {name}.")
			else:
				await ctx.send("Can't find server!")
		else:
			srvi = int(srv)
			if srvi in ids:
				await self.config.server.set(ids[ids.index(srvi)])
				name = self.bot.get_guild(srvi).name
				await ctx.send(f"Server set to {name}.")
			else:
				await ctx.send("Can't find server!")

	@checks.is_owner()
	@selfmessageset.command()
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
		await ctx.send(f"Channel set to #{ch.name}.")

	@checks.is_owner()
	@selfmessageset.command()
	async def enabled(self, ctx):
		"""Toggle if sending PMs to the bot as owner (or any other authorized user) will send a message to the server & text channel specified."""
		if await self.config.enabled() == True:
			await self.config.enabled.set(False)
			await ctx.send("Toggled off.")
		else:
			await self.config.enabled.set(True)
			await ctx.send("Toggled on.")

	@checks.is_owner()
	@selfmessageset.command()
	async def toggleuser(self, ctx, *, mem : discord.Member = None):
		"""Add or remove a person to the list of people allowed to use SelfMessage."""
		async with self.config.access() as access:
			if mem is None:
				await ctx.send("Please specify a person to add.")
				return
			if mem.id in access:
				access.remove(mem.id)
				await ctx.send(f"{mem.display_name} is now disallowed from using SelfMessage.")
			else:
				access.append(mem.id)
				await ctx.send(f"{mem.display_name} is now allowed to use SelfMessage.")

	@checks.is_owner()
	@selfmessageset.command()
	async def listusers(self, ctx):
		"""Show all users allowed to use SelfMessage."""
		access = await self.config.access()
		list = "```\n" + ctx.guild.get_member(self.bot.owner_id).display_name + " (Owner)\n"
		for x in range(len(access)):
			try:
				member = ctx.guild.get_member(access[x])
				list += member.display_name + "\n"
			except:
				list += "<Removed member>\n"
		list += "```"
		await ctx.send(list)

	async def on_message(self, message):
		enabled = await self.config.enabled()
		access = await self.config.access()
		if (
		    not message.author.bot
		    and not isinstance(message.channel, discord.TextChannel)
		    and enabled
		    and (message.author.id in access or message.author.id == self.bot.owner_id)
		):
			if message.attachments == []:
				channel = self.bot.get_channel(await self.config.chn())
				await channel.send(message.content)
			else:
				channel = self.bot.get_channel(await self.config.chn())
				files = message.attachments
				for x in range(len(files)):
					try:
						await files[x].save(str(cog_data_path(self)) + "\\attachment.png")
						await channel.send(file=discord.File(str(cog_data_path(self)) + "\\attachment.png"))
					except:
						raise
