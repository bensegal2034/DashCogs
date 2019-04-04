from .selfmessage import SelfMessage
def setup(bot):
    bot.add_cog(SelfMessage(bot))
