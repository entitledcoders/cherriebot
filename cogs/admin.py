import time
import firebase_admin
from firebase_admin import credentials, db
from discord.ext import commands
from .modules.germanium import Germanium

class admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        aliases=['dm'], 
        description = "~dm [lines]. Deletes lines of messages."
    )
    @commands.has_permissions(administrator=True)
    async def deletemessages(self, ctx, lines=5):
        await ctx.channel.purge(limit=lines+1)
        await ctx.send("Deleted")
    
    @commands.is_owner()
    @commands.hybrid_command()
    async def startdriver(self, ctx):
        starttime = time.time()
        self.bot.sessions = Germanium()
        await self.bot.sessions.next()
        await ctx.send(f'```Driver has established (Elapsed: {int(time.time()-starttime)}s)```')
    
    @commands.is_owner()
    @commands.hybrid_command()
    async def listdriver(self, ctx):
        await ctx.send(f'```{self.bot.sessions.sessions}```')
    
    @commands.is_owner()
    @commands.hybrid_command()
    async def closedriver(self, ctx):
        await self.bot.sessions.close()

    @commands.is_owner()
    @commands.hybrid_command()
    async def connectdb(self, ctx):
        try:
            cred = credentials.Certificate("./key.json")
            self.bot.firebase = firebase_admin.initialize_app(cred, {'databaseURL':'https://cherrie-electronics-default-rtdb.asia-southeast1.firebasedatabase.app/'})
            self.bot.db = db
        except Exception as e:
            return await ctx.send(e)
        await ctx.send('```Database connected```')

    @commands.hybrid_command()
    async def disconnectdb(self, ctx):
        firebase_admin.delete_app(self.bot.firebase)
        await ctx.send('```Database disconnected```')
    
async def setup(bot):
    await bot.add_cog(admin(bot))