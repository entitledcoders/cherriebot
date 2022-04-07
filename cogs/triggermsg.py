import discord
from discord.ext import commands
from random import randrange

class triggermsg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['.'])
    async def settriggermsg(self, ctx, trigger, url = None):
        if url is not None:
            if 'http' not in url:
                return await ctx.send('```Trigger word should not contain spaces!```')
            self.bot.db.reference('attachments').update({trigger:url})
        else:
            try:
                attachment = ctx.message.attachments[0]
                fp = 'attachments/' + hex(randrange(0, 4096)) + attachment.filename[-4:]
                await attachment.save(fp)
                self.bot.db.reference('attachments').update({trigger:fp})
            except Exception as e:
                return await ctx.send(e)
        return await ctx.send('```Trigger message has been set!```')
    
    @commands.command(aliases=['..'])
    async def gettriggermsg(self, ctx, trigger):
        try:
            attach = self.bot.db.reference('attachments/'+trigger).get()
        except Exception as e:
            await ctx.send(e)
        if 'http' in attach:
            return await ctx.send(attach)
        attach = discord.File(attach)
        await ctx.send(file = attach)

    @commands.command(aliases=['.,'])
    async def listtriggermsg(self, ctx):
        await ctx.send(f"```{self.bot.db.reference('attachments').get().keys()}```")
    
    @commands.command(aliases=[',,'])
    async def deltriggermsg(self, ctx, trigger):
        self.bot.db.reference('attachments/'+trigger).delete()
        await ctx.send(f'```Deleted!```')

def setup(bot):
    bot.add_cog(triggermsg(bot))
