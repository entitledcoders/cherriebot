from discord.ext import commands
from jishaku.features.python import PythonFeature
from jishaku.features.root_command import RootCommand

class jishaku(PythonFeature, RootCommand):
    pass

def setup(bot: commands.Bot):
    bot.add_cog(jishaku(bot=bot))
