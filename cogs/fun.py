import discord
from discord.ext import commands
from rembg import remove
from PIL import Image
import aiohttp        
import aiofiles

async def discord_imgdl(message, output: str):
    if len(message.attachments) < 1:    
        parsed = str(message.content).split(" ")
        if len(parsed)<1:
            raise Exception("Please attach an image")
        url = parsed[1]
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(output, mode='wb')
                    await f.write(await resp.read())
                    await f.close()
    attachment = message.attachments[0]
    await attachment.save(output)
    

class HexGen:
    def __init__(self):
        self.counter = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        self.counter = 0 if self.counter > 16 else self.counter+1
        return hex(self.counter)[-1]


class fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hex = iter(HexGen())

    @commands.hybrid_command(help="smile. ~superidol true for sound")
    async def superidol(self, ctx, sound=False):
        await ctx.message.delete()
        await ctx.send('https://tenor.com/view/super-idol-social-credits-gif-23422258')
        if sound==True:
            await ctx.send(file=discord.File(r'./materials/superidol.mp3'))

    @commands.hybrid_command(
        aliases=['removebg', 'rembg'],
        help = f"~rembg (attach 1 image) [alpha=True/False (def:True)]",
        brief = "(AI) Removes background of an image.",
        description = ""
    )
    async def removebackground(self, ctx, alpha=False):
        try:
            msg = await ctx.message.reply("``` - - Downloading and processing image! - - ```")
            tag = next(self.hex)
            input_path = f'/temp/rembg/b{tag}-i.png'
            output_path = f'/temp/rembg/b{tag}-o.png'
            if len(ctx.message.attachments) < 1:    
                parsed = str(ctx.message.content).split(" ")
                if len(parsed)<1:
                    raise Exception("Please attach an image")
                url = parsed[1]
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            f = await aiofiles.open(input_path, mode='wb')
                            await f.write(await resp.read())
                            await f.close()
            else:
                attachment = ctx.message.attachments[0]
                await attachment.save(input_path)
            with open(input_path, 'rb') as i:
                with open(output_path, 'wb') as o:
                    input = i.read()
                    if alpha:
                        output = remove(
                            input,
                            alpha_matting = True,
                            alpha_matting_foreground_threshold = 240,
                            alpha_matting_background_threshold = 10,
                            alpha_matting_erode_size = 10
                        )
                    else:
                        output = remove(input)
                    o.write(output)
            input = Image.open(input_path)
            # if alpha:
            #     output = remove(
            #         input,
            #         alpha_matting = True,
            #         alpha_matting_foreground_threshold = 240,
            #         alpha_matting_background_threshold = 10,
            #         alpha_matting_erode_size = 10
            #     )
            # else:
            #     output = remove(input)
            # output.save(output_path)
            await msg.delete()
            await ctx.reply("Background removed!", file = discord.File(output_path))
        except Exception as e:
            await ctx.reply(f"```Error occured: {e}```")
            await msg.delete()
    
async def setup(bot):
    await bot.add_cog(fun(bot))
