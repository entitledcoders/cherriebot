import discord
import time
from random import randrange
from discord.ext import commands
from .modules.microYT import YoutubePlaylist, YoutubeSearch
from pyppeteer import launch

class test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.store = {}
        self.attachments = {}

    @commands.command()
    async def embed(self, ctx, title = None, description = None, image = None, thumbnail = None, fields = None):
        if title is None or description is None:
            return await ctx.send('Please include a title and description')
        embed = discord.Embed(title=title, description=description)
        if image is not None:
            embed.set_image(image)
        if thumbnail is not None:
            embed.set_thumbnail(thumbnail)
        if fields is not None:
            for field in fields:
                embed.add_field(field)
        await ctx.message.delete()
        await ctx.send(embed = embed)

    @commands.command()
    async def copy(self, ctx, *, text):
        self.store[ctx.author.id] = text
        print(self.store)
    
    @commands.command()
    async def paste(self, ctx):
        await ctx.send(self.store[ctx.author.id])

    @commands.command()
    async def benchytsearch(self, ctx, *, query):
        starttime = time.time()
        await ctx.send('Processing! Benchmarking performance fpr `ytsearch`!')
        try:
            results = await YoutubeSearch().new(session=await self.bot.sessions.next(), query = query, qty = 10)
        except Exception as e:
            return await ctx.send(e)
        await ctx.send(f'type: {type(results)}, length: {len(results)}')
        delta = int(time.time()-starttime)
        await ctx.send(f'That took {delta} seconds!')
        embed = discord.Embed(title='Search results!', description=f'Search contains {len(results)} songs!')
        for result in results[:10]:
            embed.add_field(name=result.title, value=f'link: {result.url}\nduration: {result.duration}\nthumbnail: {result.thumbnail}', inline=False)
        await ctx.send(f'Type is {type(results[0])}' ,embed=embed)
    
    @commands.command()
    async def benchytpl(self, ctx, url):
        starttime = time.time()
        await ctx.send('Processing! Benchmarking performance for `ytplaylist`!')
        try:
            videos = await YoutubePlaylist().new(session=await self.bot.sessions.next(), url = url)
        except Exception as e:
            return await ctx.send(e)
        await ctx.send(f'type: {type(videos)}, length: {len(videos)}')
        delta = int(time.time()-starttime)
        await ctx.send(f'That took {delta} seconds!')
        embed = discord.Embed(title='Playlist results!', description=f'Playlist contains {len(videos)} songs!')
        for result in videos[:10]:
            embed.add_field(name=result.title, value=f'link: {result.url}\nduration: {result.duration}\nthumbnail: {result.thumbnail}', inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def germnew(self, ctx):
        await ctx.send(await self.bot.sessions.next())
    
    @commands.command()
    async def germtest(self, ctx):
        session = await self.bot.sessions.next()
        session.open()
        await ctx.send(session.avail)
        session.close()
        await ctx.send(session.avail)
        await ctx.send(session.driver)

    @commands.command()
    async def pyppetest(self, ctx):
        browser = await launch(headless = False)
        page = (await browser.pages())[0]
        await page.goto('https://www.youtube.com/results?search_query=aimer')
        await page.waitForSelector("[class='style-scope ytd-thumbnail-overlay-time-status-renderer']", timeout = 1500)
        results = await page.JJ('[id=dismissible]')
        for result in results[:1]:
            title = await result.J('[id=video-title]')
            text = await (await title.getProperty('title')).jsonValue()
            await ctx.send(text)
        await browser.close()

async def setup(bot):
    await bot.add_cog(test(bot))
