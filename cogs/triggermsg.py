import discord
import aiofiles
import aiohttp
from discord.ext import commands
from random import randrange

class triggermsg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(aliases=['.'])
    async def settriggermsg(self, ctx, trigger, url = None):
        try:
            if url is not None:
                if 'http' not in url:
                    return await ctx.send('```Trigger word should not contain spaces!```')
                fp = 'attachments/' + trigger + '.' + str(url.split('.')[-1]).split('?')[0]
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            f = await aiofiles.open(fp, mode='wb')
                            await f.write(await resp.read())
                            await f.close()
            else:
                attachment = ctx.message.attachments[0]
                fp = 'attachments/' + trigger + '.' + str(attachment.filename).split('.')[-1]
                await attachment.save(fp)
        except Exception as e:
            return await ctx.send(e)
        self.bot.db.reference('attachments').update({trigger:fp})
            
        return await ctx.send('```Trigger message has been set!```')
    
    @commands.hybrid_command(aliases=['..'])
    async def gettriggermsg(self, ctx, trigger):
        try:
            attach = self.bot.db.reference('attachments/'+trigger).get()
        except Exception as e:
            await ctx.send(e)
        if 'http' in attach:
            return await ctx.send(attach)
        attach = discord.File(attach)
        await ctx.send(file = attach)

    @commands.hybrid_command(aliases=['.,'])
    async def listtriggermsg(self, ctx):
        await ctx.send(f"```{self.bot.db.reference('attachments').get().keys()}```")
    
    @commands.hybrid_command(aliases=[',,'])
    async def deltriggermsg(self, ctx, trigger):
        self.bot.db.reference('attachments/'+trigger).delete()
        await ctx.send(f'```Deleted!```')

async def setup(bot):
    await bot.add_cog(triggermsg(bot))
