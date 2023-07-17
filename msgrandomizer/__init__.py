from .msgrandomizer import MsgRandomizer

async def setup(bot):
    await bot.add_cog(MsgRandomizer(bot))