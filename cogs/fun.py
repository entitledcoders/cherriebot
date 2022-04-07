import discord
from discord.ext import commands

class fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="smile. ~superidol true for sound")
    async def superidol(self, ctx, sound=False):
        await ctx.message.delete()
        await ctx.send('https://tenor.com/view/super-idol-social-credits-gif-23422258')
        if sound==True:
            await ctx.send(file=discord.File(r'./materials/superidol.mp3'))
    
def setup(bot):
    bot.add_cog(fun(bot))
