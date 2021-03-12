import discord
from redbot.core import commands
from redbot.core import checks
from redbot.core import Config
from redbot.core.data_manager import cog_data_path
from redbot.core.utils.chat_formatting import box
from typing import Optional
from google_images_search import GoogleImagesSearch
import os, shutil

class gimage(commands.Cog):
	"""Cog that grabs images from Google."""
	def __init__(self, bot):
		self.bot = bot
		self.config = Config.get_conf(self, identifier=99280384939814912)
		self.config.register_global(
			googleAPIKey = "",
			projectCX = ""
		)
		self.config.register_guild(
			blocked_members = []
		)

	@commands.command(aliases=["img"])
	async def image(self, ctx, keyword : str, amount : Optional[int] = 1):
		"""
		Get images from Google.
		Keyword is the search term, amount is the number of images you want to be displayed.
		"""
		blocked_members = await self.config.guild(ctx.guild).blocked_members()
		if ctx.author.id in blocked_members:
			return

		googleAPIKey = await self.config.googleAPIKey()
		projectCX = await self.config.projectCX()
		gis = GoogleImagesSearch(googleAPIKey, projectCX)
		path = str(cog_data_path(self))
		_search_params = {
		    "q": keyword,
		    "num": amount,
		    'fileType': "jpg|png|gif",
		}

		try:
			gis.search(search_params=_search_params, path_to_dir=path)
		except:
			return await ctx.send("Invalid credentials provided! Check your input.")
		for file in os.listdir(path):
			if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".gif"):
				image = os.path.join(path, file)
				await ctx.send(file=discord.File(image))
				os.remove(image)

	@checks.is_owner()
	@commands.group(aliases=["imgset"])
	async def gimageset(self, ctx):
		"""
		All settings relating to gimage.
		Blocked members are saved per server. API key and Project CX are saved globally.
		If you do not know how to get your own API key or Project CX, please view the README section inside the DashCogs repo.
		"""
		pass

	@checks.is_owner()
	@gimageset.group(invoke_without_command=True)
	async def apikey(self, ctx, *, key : Optional[str] = None):
		"""Input your API key."""
		if key is None:
			return await ctx.send("Please specify a key.")
		await self.config.googleAPIKey.set(key)
		await ctx.send("API key set!")

	@checks.is_owner()
	@gimageset.group(invoke_without_command=True)
	async def projectCX(self, ctx, *, id : Optional[str] = None):
		"""Input your Project CX."""
		if id is None:
			return await ctx.send("Please specify an ID.")
		await self.config.projectCX.set(id)
		await ctx.send("Project CX set!")

	@checks.is_owner()
	@gimageset.group(invoke_without_command=True)
	async def checkCredentials(self, ctx):
		"""Check to make sure your API key and Project CX are properly set."""
		googleAPIKey = await self.config.googleAPIKey()
		projectCX = await self.config.projectCX()
		gis = GoogleImagesSearch(googleAPIKey, projectCX)
		_search_params = {
		    "q": "test",
		    "num": 1,
		    'fileType': "jpg|png|gif",
		}
		try:
			gis.search(search_params=_search_params)
		except:
			return await ctx.send("Invalid credentials provided! Check your input.")
		return await ctx.send("Valid credentials provided. You are ready to use gimage.")

	@checks.is_owner()
	@gimageset.group(invoke_without_command=True)
	async def block(self, ctx, *, member : Optional[discord.Member] = None):
		"""Add or remove a person to the blocked list of people not allowed to use gimage."""
		async with self.config.guild(ctx.guild).blocked_members() as blocked_members:
			if member is None:
				return await ctx.send("Please specify a person to block.")
			if member.id in blocked_members:
				blocked_members.remove(member.id)
				await ctx.send(f"{member.display_name} removed from block list.")
			else:
				blocked_members.append(member.id)
				await ctx.send(f"{member.display_name} added to block list.")

	@checks.is_owner()
	@block.command()
	async def list(self, ctx):
		"""Displays all people blocked from using gimage."""
		blocked_members = await self.config.guild(ctx.guild).blocked_members()
		list = ""
		if len(blocked_members) == 0:
			return await ctx.send("No blocked members!")
		for x in range(len(blocked_members)):
			try:
				member = ctx.guild.get_member(blocked_members[x])
				list += f"{member.display_name}\n"
			except:
				list += "<Removed member>\n"
		await ctx.send(box(list))
