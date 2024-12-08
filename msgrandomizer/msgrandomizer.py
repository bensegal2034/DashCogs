from redbot.core import commands, app_commands
from redbot.core import Config
from redbot.core import utils
import discord, random, itertools, pprint

class MsgRandomizer(commands.Cog):
    """Display messages containing media in a random order from a given channel."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=49502314239500134)
        self.config.register_guild(
            cachedChannels = {}
        )
    
    async def processMessage(self, message, channel, cachedChannels):

        if str(message.id) != cachedChannels[str(channel.id)]["lastCheckedMsg"]:
            cachedChannels[str(channel.id)].update({"lastCheckedMsg" : str(message.id)})

        if message.embeds or message.attachments:
            tmpCachedMedia = []
            for embed, attachment in itertools.zip_longest(message.embeds, message.attachments):
                if embed is not None:
                    tmpCachedMedia.append(embed.url)
                if attachment is not None:
                    tmpCachedMedia.append(attachment.url)
            cachedChannels[str(channel.id)].update({str(message.id) : tmpCachedMedia})

        return cachedChannels

    @app_commands.command()
    async def randomize(self, intr: discord.Interaction, channel : discord.TextChannel):
        """
        Display messages from a given channel in random order.
        """

        cachedChannels = await self.config.guild(intr.guild).cachedChannels()

        # Check if the passed channel is cached, if it is, check if there are new URLs to cache
        if str(channel.id) in cachedChannels:
            async with intr.channel.typing():
                async for message in channel.history(after=await channel.fetch_message(list(cachedChannels[str(channel.id)].keys())[-2]), limit=None):
                    cachedChannels = await self.processMessage(message, channel, cachedChannels)
            await intr.response.send_message("Successfully updated channel cache!", ephemeral=True)

        else:
            # We have not cached this channel yet, go through it from oldest to newest and add all the messages with embeds to the dict of cached channels
            async with intr.channel.typing():
                cachedChannels.update({str(channel.id) : {"lastCheckedMsg" : ""}})

                async for message in channel.history(oldest_first=True, limit=None):
                    cachedChannels = await self.processMessage(message, channel, cachedChannels)
            await intr.response.send_message("Successfully added channel to cached channels list!", ephemeral=True)
        
        # Update the cache with our new data if it exists (if not, no problem in just setting the dict to its existing value)
        await self.config.guild(intr.guild).cachedChannels.set(cachedChannels)

        # Form our list of embeds and randomize them
        mediaEmbeds = []

        for messageId, messageData in cachedChannels[str(channel.id)].items():
            if messageId == "lastCheckedMsg":
                continue
            for data in messageData:
                embed = discord.Embed()
                print(f"Data: {data}")
                if "jpg" in data or "png" in data or "gif" in data:
                    print("Interpreting as image")
                    embed.set_image(url=data)
                elif "youtube" in data:
                    print("Interpreting as video")
                    embed.video.url = data
                else:
                    print(f"Unknown type, skipping")
                mediaEmbeds.append(embed)

        # Create a menu of the embeds and display it
        await utils.menus.menu(intr.context, mediaEmbeds)

    @commands.command()
    async def showcached(self, ctx):
        cachedChannels = await self.config.guild(ctx.guild).cachedChannels()

        pprint.pprint(cachedChannels)

    @commands.command()
    async def clearcached(self, ctx):
        await self.config.clear_all_guilds()
        await ctx.send("Cache cleared from all guilds.")

    @commands.command()
    async def test(self, ctx):
        """
        msg = await [channel for channel in ctx.guild.channels if channel.name == "general"][0].fetch_message(1130604776988618937)
        await ctx.send(msg.attachments)
        """
        return