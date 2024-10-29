from discord.ext import commands
import base64
import discord

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
    
    async def _query(self, driver, query):
        dict = {}
        for key, value in self.convdict.items():
            query = query.replace(key, value)

        query = 'https://www.wolframalpha.com/input/?i=' + query

        await driver.goto(query)
        await driver.waitForSelector('h2._3OpX', timeout = 10000)
        boxes = await driver.JJ("section")

        print(boxes)
        if boxes is None:
            return None
        
        for box in boxes[2:5]:
            text = await box.Jeval('h2', '(e => e.innerText)')
            image = await box.Jeval('img', '(e => e.src)')

            dict[text] = image
            print(text, image)

        return dict
        
    @commands.command(aliases=['wa', 'walpha', 'wolfram'])
    async def wolframalpha(self, ctx, *, query: str):
        msg = await ctx.send(f'```WolframAlpha querying \'{query}\'...\nMay take up to 60 seconds.```')
        

        session = await self.bot.sessions.next()
        session.reserve()
        driver = session.driver

        try:
            dict = await self._query(driver, query)
        except Exception as e:
            await ctx.send(e)

        session.release()
        await msg.delete()

        for text, image in dict.items():
            await ctx.send(f'```{text}```')
            if 'base64' in image:
                image = image.split(',')[1]
                print(image)
                with open('/temp/wolfram/image.jpg', 'wb') as f:
                    decoded_image_data = base64.b64decode(image)
                    f.write(decoded_image_data)
                image = discord.File('/temp/wolfram/image.jpg')
                await ctx.send(file=image)
            else:
                await ctx.send(image)

async def setup(bot):
    await bot.add_cog(wolframalpha(bot))
