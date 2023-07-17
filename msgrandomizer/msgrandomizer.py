from redbot.core import commands
from redbot.core import Config
import discord, pprint

class MsgRandomizer(commands.Cog):
    """Display messages containing media in a random order from a given channel."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=49502314239500134)
        self.config.register_guild(
            cachedChannels = {
                123 : {
                    312 : ["url1, url2"]
                }
            }
        )

    @commands.command()
    async def randomize(self, ctx, channel : discord.TextChannel):
        """
        Display messages from a given channel in random order.
        """

        cachedChannels = await self.config.guild(ctx.guild).cachedChannels()

        # Check if the passed channel is cached, if it is, check if there are new URLs to cache
        if str(channel.id) in cachedChannels.keys():
            async with ctx.typing():
                async for message in channel.history(after=list(cachedChannels[channel.id].keys())[-1], limit=None):
                    if message.embeds:
                        cachedChannels[str(channel.id)].update({str(message.id) : [embed.url for embed in message.embeds]})
            await ctx.send("Successfully updated channel cache!")

        else:
            # We have not cached this channel yet, go through it from oldest to newest and add all the messages with embeds to the dict of cached channels
            async with ctx.typing():
                cachedChannels.update({str(channel.id) : {}})

                async for message in channel.history(oldest_first=True, limit=None):
                    if message.embeds:
                        cachedChannels[str(channel.id)].update({str(message.id) : [embed.url for embed in message.embeds]})
            await ctx.send("Successfully added channel to cached channels list!")
        
        await self.config.guild(ctx.guild).cachedChannels.set(cachedChannels)

    @commands.command()
    async def displaycached(self, ctx):
        cachedChannels = await self.config.guild(ctx.guild).cachedChannels()

        await ctx.send(pprint.pformat(cachedChannels))

    @commands.command()
    async def clearcached(self, ctx):
        await self.config.clear_all_guilds()