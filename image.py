import discord
from redbot.core import commands
from redbot.core.data_manager import cog_data_path
from google_images_download import google_images_download
import os, shutil
class Image(commands.Cog):
	"""Cog that grabs images from Google."""
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def img(self, ctx, req : str):
		"""Grab the first image for any Google search."""
		image = google_images_download.googleimagesdownload().download({"keywords": req, "limit": 1, "output_directory": str(cog_data_path(self))})
		await ctx.send(file=discord.File(image[req][0]))
		folder = cog_data_path(self)
		for the_file in os.listdir(folder):
			file_path = os.path.join(folder, the_file)
			try:
				if os.path.isdir(file_path):
					shutil.rmtree(file_path)
			except Exception as e:
				await ctx.send(e)

	@commands.command(aliases=["mimg"])
	async def multiimg(self, ctx, req : str, amt : int = 2):
		"""
		Grabs as many images as you want from Google.

		Note: High values for "amt" can cause issues.
		"""
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
			except Exception as e:
				await ctx.send(e)