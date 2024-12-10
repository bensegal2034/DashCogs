from redbot.core import commands, app_commands
from redbot.core import Config
from redbot.core.utils.views import SimpleMenu
import discord, random, itertools, re, pprint

class MsgRandomizer(commands.GroupCog, group_name="msgrandom"):
    """Display messages containing media in a random order from a given channel."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=49502314239500134)
        self.config.register_guild(
            cachedChannels = {}
        )
    
    async def processMessageHelper(self, message, channel, cachedChannels):
        """
        Code to extract the real gif url from a Tenor gif using requests.
        Removed as this is no longer necessary with current functionality
        pageContent = requests.get(tmpUrl).text
        # Regex to find the URL on the media1.tenor.com domain that ends with .gif
        regex = r"(?i)\b((https?://media1[.]tenor[.]com/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))[.]gif)"
        cachedMedia.append(re.findall(regex, pageContent)[0][0])
        """

        # Check if the current message we are processing is NOT the last checked message,
        # if it isn't, update the last checked message appropriately
        if str(message.id) != cachedChannels[str(channel.id)]["lastCheckedMsg"]:
            cachedChannels[str(channel.id)].update({"lastCheckedMsg" : str(message.id)})

        # Set up our dict for our message data
        # We must do things this way because full objects (such as a Member) cannot be serialized
        # So we only save the parts of these objects that we care about
        messageDict = {
            "author": {
                "id": message.author.id,
                "name": message.author.name,
                "mention": message.author.mention
            },
            "created_at_timestamp": message.created_at.timestamp(),
            "content": message.content,
            "jump_url": message.jump_url
        }

        if message.embeds or message.attachments:
            # mediaTypes contains the list of valid substrings we are looking for in the URL
            # If none are found in the url, we do not care about it and toss it out
            tmpCachedMedia = []
            cachedMedia = []
            mediaTypes = [
                "tenor",
                "jpg",
                "png",
                "webm",
                "gif",
                "youtube",
                "mp4"
            ]
            for embed, attachment in itertools.zip_longest(message.embeds, message.attachments):
                if embed is not None and embed.url is not None:
                    tmpCachedMedia.append(embed.url)
                if attachment is not None and attachment.url is not None:
                    tmpCachedMedia.append(attachment.url)
            if tmpCachedMedia:
                for tmpUrl in tmpCachedMedia:
                    if any(mediaType in tmpUrl for mediaType in mediaTypes):
                        cachedMedia.append(tmpUrl)
                    else:
                        continue
                cachedChannels[str(channel.id)].update({
                    message.id : {
                        "messageDict": messageDict,
                        "cachedMedia": cachedMedia
                    }
                })

        return cachedChannels

    async def processChannelHelper(self, intr, msg, channel):
        cachedChannels = await self.config.guild(intr.guild).cachedChannels()
        msgCounter = 0

        # Check if the passed channel is cached, if it is, check if there are new messages to cache
        if str(channel.id) in cachedChannels:
            async for message in channel.history(after=await channel.fetch_message(cachedChannels[str(channel.id)]["lastCheckedMsg"]), limit=None):
                cachedChannels = await self.processMessageHelper(message, channel, cachedChannels)
                await msg.edit(content=f"Processing messages... {msgCounter} messages processed")
                msgCounter = msgCounter + 1
        else:
            # We have not cached this channel yet, go through it from oldest to newest and add all the messages with embeds to the dict of cached channels
            cachedChannels.update({str(channel.id) : {"lastCheckedMsg" : ""}})

            async for message in channel.history(oldest_first=True, limit=None):
                cachedChannels = await self.processMessageHelper(message, channel, cachedChannels)
                await msg.edit(content=f"Adding {channel.name} to the cache... {msgCounter} messages processed. Last processed message was sent <t:{int(message.created_at.timestamp())}:R>.")
                msgCounter = msgCounter + 1
        
        # Update the cache with our new data if it exists (if not, no problem in just setting the dict to its existing value)
        await self.config.guild(intr.guild).cachedChannels.set(cachedChannels)
        return msgCounter

    @app_commands.command(name="media", description="Randomize media from a text channel")
    @app_commands.describe(channel="The channel to randomize media from")
    async def randomizeMedia(self, intr: discord.Interaction, channel: discord.TextChannel):
        # Defer so that the command doesn't time out
        await intr.response.defer(ephemeral=True)
        # Create our message obj so that we can edit it later without sending a new message every time
        followupMsg = await intr.followup.send(content=f"Processing messages...", ephemeral=True, wait=True, allowed_mentions=discord.AllowedMentions.none())
        await self.processChannelHelper(intr, followupMsg, channel)
        cachedChannels = await self.config.guild(intr.guild).cachedChannels()

        # Form our list of strings by randomly sorting through the cachedChannels dict structure
        mediaCounter = 1
        mediaStrings = []

        for messageId, messageData in sorted(cachedChannels[str(channel.id)].items(), key=lambda x: random.random()):
            if type(messageData) is not dict:
                continue
            for url in messageData["cachedMedia"]:
                urlCounter = 1
                messageDetailText = f"**Sent <t:{int(messageData['messageDict']['created_at_timestamp'])}:R> by {messageData['messageDict']['author']['mention']}**"
                jumpText = f"*[Click to jump to original message!]({messageData['messageDict']['jump_url']})*"

                mediaString = f"{messageDetailText}\n{jumpText}\n\n"
                if messageData['messageDict']['content'] and messageData['messageDict']['content'] != url and "tenor.com" not in messageData['messageDict']['content']:
                    mediaString = f"{mediaString}\"{messageData['messageDict']['content']}\"\n"
                mediaString = f"{mediaString}{url}"
                mediaStrings.append(mediaString)

                await followupMsg.edit(content=f"Setting up display for {mediaCounter}/{len(cachedChannels[str(channel.id)]) - 1} messages...")
                urlCounter = urlCounter + 1
            mediaCounter = mediaCounter + 1

        # Create a menu of the strings and display it
        menu = SimpleMenu(mediaStrings)
        menu.author = intr.user
        menuKwargs = await menu.get_page(menu.current_page)
        menu.message = await intr.followup.send(**menuKwargs, ephemeral=True, wait=True, allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="processchannel", description="Process and cache a channel for MsgRandomizer")
    async def processChannel(self, intr: discord.Interaction, channel: discord.TextChannel):
        await intr.response.defer(ephemeral=False)
        followupMsg = await intr.followup.send(content=f"Processing messages...", ephemeral=False, wait=True, allowed_mentions=discord.AllowedMentions.none())
        initialTimestamp = followupMsg.created_at.timestamp()
        msgCounter = await self.processChannelHelper(intr, followupMsg, channel)
        await followupMsg.edit(content=f"Channel {channel.name} successfully cached! {msgCounter - 1} messages were processed. Processing started <t:{int(initialTimestamp)}:R>.")

    @app_commands.command(name="displaycached", description="Display channels cached by MsgRandomizer")
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
    async def clearcached(self, intr: discord.Interaction):
        await self.config.guild(intr.guild).clear()
        await intr.response.send_message(f"Cleared cache for server {intr.guild.name}.", ephemeral=True)