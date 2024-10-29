import os
import discord
from cogs.helpcommand import custommenu
from cogs.admin import admin
from dotenv import load_dotenv
from discord.ext import commands
from discord import Intents
from typing import Optional, Literal

load_dotenv('token.env')

botToken = os.getenv("botToken")
intents = Intents.all()
intents.members = True
intents.guild_messages = True

# - - - SERVER CONFIGURATION - - - #
def get_prefix(bot, message):
    try: 
        return bot.db.reference(f'prefix/{str(message.guild.id)}').get()
    except Exception as e:
        print(f"WARNING: {e}")
        return '~'

bot = commands.Bot(command_prefix=get_prefix, intents=intents)

# - - - DISCORD EVENTS - - - #
@bot.event
async def on_guild_join(guild):
    try:
        bot.db.reference('prefix').update({guild.id:"~"})
    except Exception as e:
        print("MAIN: ERROR OCCURED: ", guild.id, e)

@bot.event
async def on_guild_leave(guild):
    bot.db.reference('prefix').remove(str(guild.id))

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game('nothing'))
    print("bot is online")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('```Error: missing arguments```')

    if isinstance(error, commands.MissingPermissions):
        await ctx.send('```Error: you do not have the permissions```')

# - - - BASIC BOT COMMANDS - - - #
@bot.command(description="Change command prefixes (default '~')")
@commands.has_permissions(administrator=True)
async def cherrieprefix(ctx, prefix):
    try:
        bot.db.reference('prefix').update({ctx.guild.id:prefix})
        await ctx.send(f"The server prefix has been updated to '{prefix}'")
    except Exception as e:
        await ctx.send("Failed to update the prefix due to an error!")
        print(ctx.guild.id, prefix, e)

@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    await bot.load_extension(f'cogs.{extension}')
    await ctx.message.delete()
    await ctx.send(f'```{ctx.author} turned on {extension}```')

@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    await bot.unload_extension(f'cogs.{extension}')
    for vc in bot.voice_clients:
        await vc.disconnect()
        await vc.cleanup()
    await ctx.message.delete()
    await ctx.send(f'```{ctx.author} turned off {extension}```')

@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    await bot.unload_extension(f'cogs.{extension}')
    await ctx.message.delete()
    await bot.load_extension(f'cogs.{extension}')
    await ctx.send(f'```{extension} have been reloaded```')

@bot.command()
@commands.is_owner()
async def maintenance(ctx):
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Game('under maintenance'))
    await ctx.send('I\'m going to sleep :sleeping::zzz:')
    for filename in os.listdir('./cogs'):
        print(filename)

@bot.command()
@commands.is_owner()
async def start(ctx):
    i = 0
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game('nothing'))
    await ctx.send('```Initiating all extensions...```')
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                i+=1
            except Exception as e:
                await ctx.send(f'```Exception occured: {e}```')        
    await ctx.send(f'```Loaded ({i}) extensions!```')
    try:
        bot.help_command = custommenu()
    except Exception as e:
        print(e)

@bot.command()
@commands.is_owner()
async def kill(ctx):
    raise SystemExit

@bot.hybrid_command(name="invite")
async def invite(ctx):
    view = discord.ui.View()
    style = discord.ButtonStyle.url
    button = discord.ui.Button(style=style, label=f"Invite me to your server", url='https://discord.com/api/oauth2/authorize?client_id=898387806068543488&permissions=413394069569&scope=bot%20applications.commands')
    view.add_item(button)
    await ctx.send("Click the button below!", view=view)

@bot.command()
async def sync(ctx, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None):
    try:
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")
    except Exception as e:
        await ctx.send(f"```Error occured: {e}.```")

bot.run(botToken)