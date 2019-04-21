import discord
from redbot.core import commands
from redbot.core import checks
from redbot.core import Config
from redbot.core.data_manager import cog_data_path
from redbot.core.utils.chat_formatting import box
from typing import Optional
from google_images_download import google_images_download
import os, shutil

class GImage(commands.Cog):
	"""Cog that grabs images from Google."""
	def __init__(self, bot):
		self.bot = bot
		self.config = Config.get_conf(self, identifier=99280384939814912)
		self.config.register_guild(
			blocked_members = []
		)
	@commands.command()
	async def img(self, ctx, req : str):
		"""Grab the first image for any Google search."""
		blocked_members = await self.config.guild(ctx.guild).blocked_members()
		if ctx.author.id in blocked_members:
			return
		image = google_images_download.googleimagesdownload().download({"keywords": req, "limit": 1, "output_directory": str(cog_data_path(self))})
		await ctx.send(file=discord.File(image[req][0]))
		folder = cog_data_path(self)
		for the_file in os.listdir(folder):
			file_path = os.path.join(folder, the_file)
			try:
				if os.path.isdir(file_path):
					shutil.rmtree(file_path)
			except:
				raise

	@commands.command(aliases=["mimg"])
	async def multiimg(self, ctx, req : str, amt : int = 2):
		"""
		Grabs as many images as you want from Google.

		Note: High values for "amt" can cause issues.
		"""
		blocked_members = await self.config.guild(ctx.guild).blocked_members()
		if ctx.author.id in blocked_members:
			return
		image = google_images_download.googleimagesdownload().download({"keywords": req, "limit": amt, "output_directory": str(cog_data_path(self))})
		for x in range(amt):
			try:
				await ctx.send(file=discord.File(image[req][x]))
			except:
				await ctx.send("**Error uploading file!**")
		folder = cog_data_path(self)
		for the_file in os.listdir(folder):
			file_path = os.path.join(folder, the_file)
			try:
				if os.path.isdir(file_path):
					shutil.rmtree(file_path)
			except:
				raise

	@checks.guildowner()
	@commands.guild_only()
	@commands.group(aliases=["imgset"])
	async def gimageset(self, ctx):
		"""All settings relating to GImage. Settings are saved per guild."""
		pass

	@checks.guildowner()
	@commands.guild_only()
	@gimageset.group(invoke_without_command=True)
	async def block(self, ctx, *, mem : Optional[discord.Member] = None):
		"""Add or remove a person to the blocked list of people not allowed to use GImage."""
		async with self.config.guild(ctx.guild).blocked_members() as blocked_members:
			if mem is None:
				return await ctx.send("Please specify a person to block.")
			if mem.id in blocked_members:
				blocked_members.remove(mem.id)
				await ctx.send(f"{mem.display_name} removed from block list.")
			else:
				blocked_members.append(mem.id)
				await ctx.send(f"{mem.display_name} added to block list.")

	@checks.guildowner()
	@commands.guild_only()
	@block.command()
	async def list(self, ctx):
		"""Displays all people blocked from using GImage."""
		blocked_members = await self.config.guild(ctx.guild).blocked_members()
		list = ""
		for x in range(len(blocked_members)):
			try:
				member = ctx.guild.get_member(blocked_members[x])
				list += member.display_name + "\n"
			except:
				list += "<Removed member>\n"
		await ctx.send(box(list))
