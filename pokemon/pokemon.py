from redbot.core import commands
from redbot.core import Config
from redbot.core import checks
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core.data_manager import bundled_data_path
from redbot.core.utils.chat_formatting import box, pagify
import discord, json, time, asyncio
from random import randint

class Pokemon(commands.Cog):
	"""A worse version of Pokecord."""
	def __init__(self, bot):
		self.bot = bot
		self.config = Config.get_conf(self, identifier=99280384939814912)
		self.config.register_guild(
			whitelisted_channels = [],
			random_levels = 1,
			show_pokemon_amt = 25,
			ready = False,
			t = time.time(),
			spawntime = [180, 300]
		)
		self.config.register_member(
			caught_pokemon = [],
			held_pokemon = 1,
			levelamt = 1
		)

	async def fixready(self):
		for guild in self.bot.guilds:
			await self.config.guild(guild).ready.set(False)

	def __unload(self):
		self.bot.loop.create_task(self.fixready())

	async def levelup(self, author):
		held_pokemon = await self.config.member(author).held_pokemon()
		levelamt = await self.config.member(author).levelamt()
		async with self.config.member(author).caught_pokemon() as caught_pokemon:
			if len(caught_pokemon) > 0:
				if caught_pokemon[held_pokemon - 1]["level"] > 100:
					return
				goal = caught_pokemon[held_pokemon - 1]["level"] * 5
				if levelamt >= goal:
					caught_pokemon[held_pokemon - 1]["level"] += 1
					levelamt = 1
					await self.config.member(author).levelamt.set(levelamt)
				else:
					levelamt += 1
					await self.config.member(author).levelamt.set(levelamt)

	@commands.command(aliases=["pprint"])
	async def printpokemon(self, ctx, id : int = 1):
		"""Shows a pokemon's statistics based on its ID."""
		with open (str(bundled_data_path(self)) + "\\pokedex.json", encoding="utf8") as f:
			pokemon = json.load(f)
		try:
			await ctx.send(f"Pokemon's name is {pokemon[id - 1]['name']['english']}.")
		except:
			await ctx.send("Invalid ID!")
			return
		await ctx.send(f"{'Type is' if len(pokemon[id - 1]['type']) == 1 else 'Types are'}: " + str(", ".join(pokemon[id - 1]["type"])))
		await ctx.send(f"HP: {str(pokemon[id - 1]['base']['HP'])}\nAttack: {str(pokemon[id - 1]['base']['Attack'])}\nDefense: {str(pokemon[id - 1]['base']['Defense'])}\nSpecial Attack: {str(pokemon[id - 1]['base']['Sp. Attack'])}\nSpecial Defense: {str(pokemon[id - 1]['base']['Sp. Defense'])}\nSpeed: {str(pokemon[id - 1]['base']['Speed'])}")
		try:
			await ctx.send(file=discord.File(str(bundled_data_path(self)) + "\\images\\" + str(id).zfill(3) + str(pokemon[id - 1]["name"]["english"]) + ".png", filename="pokemon.png"))
		except:
			await ctx.send("No image avaliable!")
			return

	@commands.command(aliases=["pinfo"])
	async def pokemoninfo(self, ctx, sel : int = 0):
		"""
		Shows all the pokemon you have caught.

		You are also able to view detailed info about one particular pokemon by typing its ID after this command.
		"""
		caught_pokemon = await self.config.member(ctx.author).caught_pokemon()
		show_pokemon_amt = await self.config.guild(ctx.guild).show_pokemon_amt()
		levelamt = await self.config.member(ctx.author).levelamt()
		order = sorted(caught_pokemon, key = lambda p: p["id"])
		embeds = []
		run = True
		v = 0
		if sel != 0:
			if sel > len(caught_pokemon) or sel < 0:
				await ctx.send("Invalid value!")
				return
			goal = caught_pokemon[sel - 1]["level"] * 5
			embed = discord.Embed(
				title = caught_pokemon[sel - 1]["name"],
				description = (
					f"EXP: *{str(levelamt)}/{goal}* (Level {caught_pokemon[sel - 1]['level']})\n"
					f"Types: *{str(caught_pokemon[sel - 1]['type'])}*\n"
					f"HP: *{str(caught_pokemon[sel - 1]['hp'])}*\n"
					f"Attack: *{str(caught_pokemon[sel - 1]['atk'])}*\n"
					f"Defense: *{str(caught_pokemon[sel - 1]['def'])}*\n"
					f"Special Attack: *{str(caught_pokemon[sel - 1]['spatk'])}*\n"
					f"Special Defense: *{str(caught_pokemon[sel - 1]['spdef'])}*\n"
				),
				color = discord.Color(0).from_rgb(255,255,255)
			)
			try:
				img = discord.File(str(bundled_data_path(self) / "images" / (str(caught_pokemon[sel - 1]["trueid"]).zfill(3) + str(caught_pokemon[sel - 1]["name"]) + ".png")), filename="pokemon.jpg")
				embed.set_image(url="attachment://pokemon.jpg")
				await ctx.send(embed=embed, files=[img])
			except:
				embed.add_field(
					name = "\u200b",
					value = "No image avaliable!"
				)
				await ctx.send(embed=embed)
			return
		# if no pokemon
		if len(caught_pokemon) == 0:
			desc = "(No pokemon caught yet!)"
			showpokemon = discord.Embed(
				title = "Your pokémon:",
				description = (desc),
				color = await ctx.embed_color()
			)
			await ctx.send(embed=showpokemon)
		# if pokemon can be displayed in 1 page according to page #
		else:
			if len(caught_pokemon) <= show_pokemon_amt:
				desc = "*(out of " + str(len(caught_pokemon)) + " found)*\n\n"
				for x in range (len(caught_pokemon)):
					desc += "**" + str(caught_pokemon[x]["name"]) + "** | Level: *" + str(caught_pokemon[x]["level"]) + "*  | ID: *" + str(caught_pokemon[x]["id"]) + "*\n"
				showpokemon = discord.Embed(
					title = "Your pokémon:",
					description = (desc),
					color = await ctx.embed_color()
				)
				showpokemon.set_footer(text="To view more detailed information about your pokemon: [p]pokemoninfo (pokemon name)")
				await ctx.send(embed=showpokemon)
			# if multiple pages
			else:
				while run:
					desc = f"*(out of {str(len(caught_pokemon))} found)*\n\n"
					for x in range(show_pokemon_amt):
						desc += "**" + order[v]["name"] + "** | Level: *" + str(order[v]["level"]) + "*  | ID: *" + str(caught_pokemon[v]["id"]) + "*\n"
						v += 1
						if v > len(caught_pokemon) - 1:
							run = False
							break
					embed = discord.Embed(
						title = "Your pokémon:",
						description = (desc),
						color = await ctx.embed_color()
					)
					embed.set_footer(text="To view more detailed information about your pokemon: [p]pokemoninfo (pokemon name)")
					embeds.append(embed)
				await menu(ctx, pages=embeds, controls=DEFAULT_CONTROLS, message=None, timeout=20)

	@checks.guildowner()
	@commands.group(aliases=["pset"])
	async def pokemonset(self, ctx):
		"""All settings relating to pokemon. Settings are saved per guild."""
		pass

	@checks.guildowner()
	@commands.guild_only()
	@pokemonset.command()
	async def whitelist(self, ctx, *, list = ""):
		"""
		Add or remove a channel to the whitelist depending on context.

		To list all whitelisted channels, add 'list' after this command.
		"""
		async with self.config.guild(ctx.guild).whitelisted_channels() as whitelisted_channels:
			if list == "list":
				if len(whitelisted_channels) == 0:
					await ctx.send("There are no currently whitelisted channels at this time.")
					return
				raw = []
				for x in whitelisted_channels:
					raw.append(ctx.guild.get_channel(x))
				channels = [x.name for x in raw]
				desc = [x.topic for x in raw]
				msg = f"Whitelisted channels in {ctx.guild.name}:\n"
				cnt = 0
				for x in channels:
					if "\n" in str(desc[cnt]):
						msg += f"#{x}: \n{desc[cnt]}\n---\n"
					else:
						msg += f"#{x}: {desc[cnt]}\n---\n"
					cnt += 1
				await ctx.send(box(msg))
				return
			if ctx.channel.id in whitelisted_channels:
				await ctx.send (f"Removing {ctx.channel.name} from whitelist.")
				whitelisted_channels.remove(ctx.channel.id)
			else:
				await ctx.send (f"Adding {ctx.channel.name} to whitelist.")
				whitelisted_channels.append(ctx.channel.id)

	@checks.guildowner()
	@commands.guild_only()
	@pokemonset.command()
	async def randomlevels(self, ctx, val : bool = None):
		"""Turn on or off whether or not pokemon should be set to a random level when caught."""
		await self.config.guild(ctx.guild).random_levels.set(val)
		random_levels = await self.config.guild(ctx.guild).random_levels()
		await ctx.send (f"{'Turned on random level spawns.' if random_levels == 1 else 'Turned off random level spawns.'}")

	@checks.guildowner()
	@commands.guild_only()
	@pokemonset.command()
	async def spawntime(self, ctx, timeone : int = None, timetwo : int = None):
		"""
		Set the amount of time it should take to spawn a pokemon in seconds. Cannot be less than or equal to 0.

		Can either be one value or two, if the bot should pick a random time between these two values for every pokemon spawned.
		"""
		async with self.config.guild(ctx.guild).spawntime() as spawntime:
			if timeone == None and timetwo == None:
				return await ctx.send("Please input a number!")
			if timeone > 0:
				if timetwo == None:
					# only one time value
					for x in range(len(spawntime)):
						spawntime[x] = timeone
					await ctx.send(f"Time to spawn pokemon set to {timeone} seconds.")
				else:
					# two time values
					spawntime[0] = timeone
					spawntime[1] = timetwo
					await ctx.send(f"Time to spawn pokemon set to a random number between {timeone} and {timetwo} seconds.")
			else:
				await ctx.send("Please input a valid number!")

	@checks.guildowner()
	@commands.guild_only()
	@pokemonset.command()
	async def debug(self, ctx):
		"""Displays values relevant for debugging."""
		guild = self.bot.get_guild(ctx.guild)
		whitelisted_channels = await self.config.guild(ctx.guild).whitelisted_channels()
		random_levels = await self.config.guild(ctx.guild).random_levels()
		show_pokemon_amt = await self.config.guild(ctx.guild).show_pokemon_amt()
		caught_pokemon = await self.config.member(ctx.author).caught_pokemon()
		levelamt = await self.config.member(ctx.author).levelamt()
		held_pokemon = await self.config.member(ctx.author).held_pokemon()
		paged = pagify(json.JSONEncoder(indent=4).encode(caught_pokemon))
		channelslist = ""
		if len(caught_pokemon) > 0:
			goal = caught_pokemon[held_pokemon - 1]["level"] * 5
		else:
			goal = None
		for x in range (len(whitelisted_channels)):
			c = self.bot.get_channel(whitelisted_channels[x])
			channelslist += c.name + " "
		await ctx.send(f"**Debug:**\nWhitelisted channels: {channelslist}\nRandom level value: {str(random_levels)}\nAmount of pokemon shown: {str(show_pokemon_amt)}\nHeld pokemon: {str(held_pokemon)}\nEXP: {str(levelamt)}/{goal}")
		await ctx.send("Caught pokemon:")
		for page in paged:
			await ctx.send(box(page))

	@checks.is_owner()
	@pokemonset.command()
	async def resetdata(self, ctx, *, type = ""):
		"""Clear pokemon data either for all members of guilds or all guilds. **THIS IS IRREVERSIBLE!**"""
		check = lambda m: m.author.bot == False and (m.content.lower() == "y" or m.content.lower() == "n")
		if type == "" or (type != "member" and type != "guild"):
			return await ctx.send("Please specify the type of data to reset. Either `guild` or `member` is valid.")
		if type == "member":
			await ctx.send("Are you **SURE** you want to delete all *member* data? Please type Y/N in chat to confirm.")
			try:
				a = await self.bot.wait_for("message", check=check, timeout=20)
			except asyncio.TimeoutError:
				await ctx.send("No one responded in time. Cancelling request.")
			if a.content.lower() == "y":
				await self.config.clear_all_members()
				await ctx.send("All member data cleared successfully.")
			else:
				await ctx.send("Cancelling request to clear member data.")
		elif type == "guild":
			await ctx.send("Are you **SURE** you want to delete all *guild* data? Please type Y/N in chat to confirm.")
			try:
				a = await self.bot.wait_for("message", check=check, timeout=20)
			except asyncio.TimeoutError:
				await ctx.send("No one responded in time. Cancelling request.")
			if a.content.lower() == "y":
				await self.config.clear_all_guilds()
				await ctx.send("All guild data cleared successfully.")
			else:
				await ctx.send("Cancelling request to clear guild data.")

	@checks.guildowner()
	@commands.guild_only()
	@pokemonset.command()
	async def listamt(self, ctx, amt : int = 25):
		"""Amount of pokemon displayed on [p]pokemonlist. Cannot be set to higher than 50."""
		if amt <= 50 and amt >= 1:
			await self.config.guild(ctx.guild).show_pokemon_amt.set(amt)
			show_pokemon_amt = await self.config.guild(ctx.guild).show_pokemon_amt()
			await ctx.send(f"{str(amt)} pokemon will be displayed per page.")
		else:
			await ctx.send("Invalid value!")

	@commands.command(aliases=["pselect"])
	async def pokemonselect(self, ctx, sel : int = 1):
		"""
		Select a pokemon to receive XP by its ID.

		To retrieve an ID for your pokemon, do [p]pokemoninfo.
		"""
		caught_pokemon = await self.config.member(ctx.author).caught_pokemon()
		if sel >= 1 and sel <= len(caught_pokemon):
			await self.config.member(ctx.author).held_pokemon.set(sel)
			await ctx.send(f"Your selected pokemon is now {caught_pokemon[sel - 1]['name']}.")
		else:
			await ctx.send("Invalid value!")

	async def on_message(self, message):
		if isinstance(message.author, discord.User):
			return
		# levelup / exp
		await self.levelup(message.author)
		# spawning pokemon
		async with self.config.member(message.author).caught_pokemon() as caught_pokemon:
			t = await self.config.guild(message.guild).t()
			spawntime = await self.config.guild(message.guild).spawntime()
			if spawntime[0] == spawntime[1]:
				truespawn = spawntime[0]
			else:
				truespawn = randint(spawntime[0], spawntime[1])
			if time.time() - t >= truespawn:
				ready = await self.config.guild(message.guild).ready()
				if not ready:
					with open (str(bundled_data_path(self)) + "\\pokedex.json", encoding="utf8") as f:
						pokemon = json.load(f)
					id = randint(1, len(pokemon))
					name = str(pokemon[id - 1]["name"]["english"])
					check = lambda m: m.author.bot == False and m.content.lower() == name.lower()
					guess = ""
					random_levels = await self.config.guild(message.guild).random_levels()
					whitelisted_channels = await self.config.guild(message.guild).whitelisted_channels()
					if message.channel.id in whitelisted_channels:
						if len(whitelisted_channels) > 1:
							spawn = self.bot.get_channel(whitelisted_channels[randint(0, len(whitelisted_channels) - 1)])
						else:
							spawn = self.bot.get_channel(whitelisted_channels[0])
					else:
						if len(whitelisted_channels) == 0:
							return
						else:
							spawn = self.bot.get_channel(whitelisted_channels[0])
					if random_levels == 1:
						level = randint(1, 100)
					else:
						level = 1
					if not message.author.bot and isinstance(message.channel, discord.TextChannel):
						await self.config.guild(message.guild).ready.set(True)
						try:
							embed = discord.Embed(
								title = "A wild pokemon has appeared!",
								color = discord.Color(0).from_rgb(255,0,0)
							)
							img = discord.File(str(bundled_data_path(self) / "images" / (str(id).zfill(3) + str(pokemon[id - 1]["name"]["english"]) + ".png")), filename="pokemon.png")
							embed.set_image(url="attachment://pokemon.png")
							embed.set_footer(text="To catch the pokemon, type its name in chat!")
							await spawn.send(embed=embed, files=[img])
						except:
							embed = discord.Embed(
								title = "A wild pokemon has appeared!",
								description = ("No image avaliable!"),
								color = discord.Color(0).from_rgb(255,0,0)
							)
							embed.set_footer(text="To catch the pokemon, type its name in chat!")
							await spawn.send(embed=embed)
						await spawn.send(f"Pokemon is {name}.")
						try:
							guess = await self.bot.wait_for("message", check=check, timeout=20)
						except asyncio.TimeoutError:
							await spawn.send("No one responded in time!")
							await self.config.guild(message.guild).ready.set(False)
							await self.config.guild(message.guild).t.set(time.time())
							return
						await spawn.send(f"Good job {guess.author.mention}! You caught a level {str(level)} {str(name)}!")
						caught_pokemon.append({
							"level": level,
							"name": name,
							"id": len(caught_pokemon) + 1,
							"trueid": pokemon[id - 1]["id"],
							"type": str(pokemon[id - 1]["type"]).strip("[]"),
							"hp": pokemon[id - 1]["base"]["HP"],
							"atk": pokemon[id - 1]["base"]["Attack"],
							"def": pokemon[id - 1]["base"]["Defense"],
							"spatk": pokemon[id - 1]["base"]["Sp. Attack"],
							"spdef": pokemon[id - 1]["base"]["Sp. Defense"],
							"speed": pokemon[id - 1]["base"]["Speed"]
						})
						await self.config.guild(message.guild).ready.set(False)
						await self.config.guild(message.guild).t.set(time.time())
					else:
						return
				else:
					return
			else:
				return
