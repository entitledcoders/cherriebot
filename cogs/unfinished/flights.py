from discord.ext import commands
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs4
import asyncio

class wolframalpha(commands.Cog):
    convdict = {
        '%' : '%25',
        '!' : '%21',
        '@' : '%40',
        '#' : '%23',
        '$' : '%24',
        '^' : '%5E',
        '&' : '%26',
        '(' : '%28',
        ')' : '%29',
        '+' : '%2B',
        '=' : '%3D',
        '/' : '%2F',
        '[' : '%5B',
        ']' : '%5D',
        ' ' : '+'
    }

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['wa', 'walpha', 'wolfram'])
    async def wolframalpha(self, ctx, *, query: str):
        driver = self.bot.driver
        print(query)
        for key, value in self.convdict.items():
            query = query.replace(key, value)
        query = 'https://www.wolframalpha.com/input/?i=' + query
        print(query)
        driver.get(query)
        driver.implicitly_wait(10)
        driver.find_element(By.CLASS_NAME, 'Y4YRs')
        await asyncio.sleep(1)
        html = driver.page_source
        soup = bs4(html, 'lxml')
        boxes = soup.find_all(attrs={'class':'_2z545 q-8B0'})
        if boxes is None:
            return await ctx.send('```No results found!```')
        for box in boxes[:3]:
            text = box.find('h2').get_text()
            image = box.find('img')['src']
            await ctx.send(text)
            await ctx.send(image)

def setup(bot):
    bot.add_cog(wolframalpha(bot))
