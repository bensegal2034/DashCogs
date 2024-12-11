from redbot.core import commands, app_commands
from redbot.core import Config
from redbot.core.utils.views import SimpleMenu
import discord, random, pprint, datetime

class MsgRandomizer(commands.GroupCog, group_name="msgrand"):
    """Display messages in a random order from a given channel."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=49502314239500134)
        self.config.register_guild(
            cachedChannels = {}
        )
    
    async def processMessageHelper(self, message, channel, cachedChannels):
        # Check if the current message we are processing is NOT the last checked message,
        # if it isn't, update the last checked message appropriately
        if str(message.id) != cachedChannels[str(channel.id)]["lastCheckedMsg"]:
            cachedChannels[str(channel.id)].update({"lastCheckedMsg" : str(message.id)})

        # Grab all links and throw them in a list
        links = []
        for embed in message.embeds:
            if embed.url:
                links.append(embed.url)
        for attachment in message.attachments:
            if attachment.url:
                links.append(attachment.url)

        # Set up our dict for our message data
        # We must do things this way because full objects (such as a Member) cannot be serialized
        # So we only save the parts of these objects that we care about
        cachedChannels[str(channel.id)].update({
            message.id : {
                "author": {
                    "id": message.author.id,
                    "name": message.author.name,
                    "mention": message.author.mention
                },
                "content": message.content,
                "links": links,
                "jump_url": message.jump_url,
                "created_at_timestamp": message.created_at.timestamp()
            }
        })

        return cachedChannels

    async def processChannelHelper(self, intr, channel):
        cachedChannels = await self.config.guild(intr.guild).cachedChannels()
        msgCounter = 0
        
        msg = await intr.followup.send(content=f"Processing messages...", ephemeral=True, wait=True, allowed_mentions=discord.AllowedMentions.none())
        # Check if the passed channel is cached, if it is, check if there are new messages to cache
        if str(channel.id) in cachedChannels:
            async for message in channel.history(after=await channel.fetch_message(cachedChannels[str(channel.id)]["lastCheckedMsg"]), limit=None):
                cachedChannels = await self.processMessageHelper(message, channel, cachedChannels)
        else:
            # We have not cached this channel yet, go through it from oldest to newest and add all the messages with embeds to the dict of cached channels
            cachedChannels.update({str(channel.id) : {"lastCheckedMsg" : ""}})

            async for message in channel.history(oldest_first=True, limit=None):
                cachedChannels = await self.processMessageHelper(message, channel, cachedChannels)
                if msgCounter % 200 == 0:
                    await msg.edit(content=f"Adding {channel.name} to the cache... {msgCounter} messages processed.")
                msgCounter = msgCounter + 1
        
        await msg.delete()
        # Update the cache with our new data if it exists (if not, no problem in just setting the dict to its existing value)
        await self.config.guild(intr.guild).cachedChannels.set(cachedChannels)
        return msgCounter

    @app_commands.command(name="media", description="Randomize media from a text channel")
    @app_commands.describe(channel="The channel to randomize media from", mediatype="What types of media should be shown?")
    @app_commands.choices(mediatype = [
        app_commands.Choice(name="Both", value = "both"),
        app_commands.Choice(name="Pictures", value = "pictures"),
        app_commands.Choice(name="Videos", value = "videos")
    ])
    @app_commands.guild_only()
    async def randomMedia(self, intr: discord.Interaction, channel: discord.TextChannel, mediatype: app_commands.Choice[str]):
        # Defer so that the command doesn't time out
        await intr.response.defer(ephemeral=True)
        await self.processChannelHelper(intr, channel)
        cachedChannels = await self.config.guild(intr.guild).cachedChannels()

        # Form our list of strings by randomly sorting through the cachedChannels dict structure
        allUrlTypes = [
            "tenor",
            "jpg",
            "png",
            "webm",
            "gif",
            "youtube",
            "mp4"
        ]
        videoUrlTypes = [
            "youtube",
            "mp4"
        ]
        pictureUrlTypes = [
            "tenor",
            "jpg",
            "png",
            'webm',
            "gif"
        ]
        mediaStrings = []

        for messageData in cachedChannels[str(channel.id)].values():
            if type(messageData) is not dict:
                continue
            author = messageData["author"]
            content = messageData["content"]
            links = messageData["links"]
            jump_url = messageData["jump_url"]
            created_at_timestamp = messageData["created_at_timestamp"]
            for link in links:
                if any(urlType in link for urlType in allUrlTypes):
                    if mediatype.value == "pictures" and any(urlType in link for urlType in videoUrlTypes):
                        continue
                    if mediatype.value == "videos" and any(urlType in link for urlType in pictureUrlTypes):
                        continue
                    messageDetailText = f"**Sent <t:{int(created_at_timestamp)}:R> by {author['mention']}**"
                    jumpText = f"*[Click to jump to original message!]({jump_url})*"

                    mediaString = f"{messageDetailText}\n{jumpText}\n\n"
                    if content and content != link:
                        mediaString = f"{mediaString}\"{content}\"\n"
                    mediaString = f"{mediaString}{link}"
                    mediaStrings.append(mediaString)

        # Create a menu of the strings and display it
        if not mediaStrings:
            await intr.followup.send(content="No valid media found.", ephemeral=True)
            return
        random.shuffle(mediaStrings)
        menu = SimpleMenu(pages=mediaStrings)
        menu.author = intr.user
        menuKwargs = await menu.get_page(menu.current_page)
        menu.message = await intr.followup.send(**menuKwargs, ephemeral=True, wait=True, allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="text", description="Randomize all messages from a text channel")
    @app_commands.describe(channel="The channel to randomize messages from")
    async def randomText(self, intr: discord.Interaction, channel: discord.TextChannel):
        # Defer so that the command doesn't time out
        await intr.response.defer(ephemeral=True)
        await self.processChannelHelper(intr, channel)
        cachedChannels = await self.config.guild(intr.guild).cachedChannels()

        messageStrings = []

        for messageData in cachedChannels[str(channel.id)].values():
            if type(messageData) is not dict:
                continue
            author = messageData["author"]
            content = messageData["content"]
            links = messageData["links"]
            jump_url = messageData["jump_url"]
            created_at_timestamp = messageData["created_at_timestamp"]

            messageDetailText = f"**Sent <t:{int(created_at_timestamp)}:R> by {author['mention']}**"
            jumpText = f"*[Click to jump to original message!]({jump_url})*"

            messageString = f"{messageDetailText}\n{jumpText}\n\n"
            if content and content not in links:
                messageString = f"{messageString }\"{content}\"\n"
            if links:
                for link in links:
                    messageString  = f"{messageString}{link}\n"
            messageStrings.append(messageString)

        # Create a menu of the strings and display it
        if not messageStrings:
            await intr.followup.send(content="No valid messages found.", ephemeral=True)
            return
        random.shuffle(messageStrings)
        menu = SimpleMenu(pages=messageStrings)
        menu.author = intr.user
        menuKwargs = await menu.get_page(menu.current_page)
        menu.message = await intr.followup.send(**menuKwargs, ephemeral=True, wait=True, allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="processchannel", description="Process and cache a channel for MsgRandomizer")
    @app_commands.guild_only()
    async def processChannel(self, intr: discord.Interaction, channel: discord.TextChannel):
        # This sucks but I couldn't figure out any other way of making the interaction not fail or time out so whatever
        await intr.response.send_message(content="‎", silent=True, ephemeral=True, delete_after=0)
        initialTimestamp = datetime.datetime.now().timestamp()
        msgCounter = await self.processChannelHelper(intr, channel)
        await intr.followup.send(content=f"Channel {channel.name} successfully cached! {msgCounter - 1} messages were processed. Processing started <t:{int(initialTimestamp)}:R>.", ephemeral=True)

    @app_commands.command(name="displaycached", description="Display channels cached by MsgRandomizer")
    @app_commands.guild_only()
    async def showCachedChannels(self, intr: discord.Interaction):
        cachedChannels = await self.config.guild(intr.guild).cachedChannels()
        pprint.pprint(cachedChannels)
        cachedChannelsText = ""
        if not cachedChannels:
            await intr.response.send_message(f"No messages cached in server {intr.guild.name}.")
            return
        for channelId, channelData in cachedChannels.items():
            channelObj = self.bot.get_channel(int(channelId))
            cachedChannelsText = f"{cachedChannelsText}{channelObj.name}: {len(channelData) - 1} messages cached\n"
        await intr.response.send_message(content=cachedChannelsText, ephemeral=True)

    @app_commands.command(name="clearcached", description="Clear MsgRandomizer's cache for the current server")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def clearcached(self, intr: discord.Interaction):
        await self.config.guild(intr.guild).clear()
        await intr.response.send_message(f"Cleared cache for server {intr.guild.name}.", ephemeral=True)