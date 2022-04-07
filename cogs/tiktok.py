import aiohttp        
import aiofiles
import discord
from pyupload.uploader.catbox import CatboxUploader as Catbox
from discord.ext import commands
from discord.ui import View, Button
from discord import ButtonStyle, Interaction

class Cancel(Button):
    def __init__(self, message, author):
        super().__init__(style = ButtonStyle.danger, label = 'DELETE')
        self.message = message
        self.author = author

    async def callback(self, interaction: Interaction):
        if interaction.user.id == self.author:
            await self.message.delete()

class HexGen:
    def __init__(self):
        self.counter = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        self.counter = 0 if self.counter > 16 else self.counter+1
        return hex(self.counter)[-1]

class tiktok(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hex = iter(HexGen())

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if ('http' in message.content) and ('tiktok.com' in message.content):
            try:
                tiktok = message.content.split(' ')[0]
                say = message.content[len(tiktok)+1:]
                tiktok = message.content.split('?')[0][:-1]
                sess = await self.bot.sessions.next()
                sess.reserve()
                driver = sess.driver
                await driver.goto(tiktok)
                await driver.waitForSelector('video', timeout = 30000)
                url = await driver.Jeval('video', '(e => e.src)')
                desc = await driver.Jeval('div[data-e2e=video-desc]', '(e => e.innerText)')
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            embed = discord.Embed(title="Tiktok Video", description=f"[source]({tiktok})")
                            embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
                            if len(desc)>0:
                                embed.add_field(name='Description', value=desc)
                            embed.set_footer(text=f'Message: {say}')
                            tempfile = f'/temp/tiktok-b{next(self.hex)}.mp4'
                            f = await aiofiles.open(tempfile, mode='wb')
                            await f.write(await resp.read())
                            await f.close()
                            try:
                                video = await message.reply(embed = embed, file = discord.File(tempfile))
                            except Exception as e:
                                temp = await message.reply(content = '```Video exceeds limit size, uploading to Catbox...```')
                                uploader = Catbox(tempfile)
                                link = uploader.execute()
                                await temp.delete()
                                video = await message.reply(
                                    content = f"{link} \nsource: {tiktok} \nsent by {message.author.mention}: {say}"
                                )
                            view = View()
                            view.add_item(Cancel(message=video, author=message.author.id))
                            await video.edit(view=view)
                            await message.delete()
            except Exception as e:
                await message.reply(e)
            sess.release()

def setup(bot):
    bot.add_cog(tiktok(bot))