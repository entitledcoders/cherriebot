import discord
from discord.ext import commands
from discord.ui import View, Select

class Dropdown(Select):
    def __init__(self, cogs, hover=None):
        options = [
            discord.SelectOption(
                label=cog, 
                emoji='⭕', 
                default=True if cog == hover else False
            ) for cog in cogs if cog is not None
        ]
        super().__init__(placeholder='Choose a category', min_values=1, max_values=1, options=options, row=1)
        self.cogs = cogs
        
    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f'CherriePy Help', description="COG: " + self.values[0])
        commands = self.cogs[self.values[0]].get_commands()
        for command in commands:
            aliases = ''.join(f'{alias}, ' for alias in command.aliases) 
            guide = command.help if command.help is not None else "not available!"
            description = command.brief if command.brief is not None else "description needed!"
            embed.add_field(
                name=command.name + f" ({aliases[:-2] if aliases != '' else '-'})",
                value=f'''
                `{guide}`
                {description}
                ''',
                inline=False
            )
        view = View()
        view.add_item(Dropdown(self.cogs, hover=self.values[0]))
        self.view.stop()
        await interaction.message.edit(embed=embed, view=view)

class helpcommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def helpdefault(self, ctx):
        self.bot.help_command = commands.DefaultHelpCommand()   
        await ctx.send('```Set to default help menu```')
    
    @commands.command()
    async def helpcustom(self, ctx):
        self.bot.help_command = custommenu()
        await ctx.send('```Set to custom help menu```')

def setup(bot):
    bot.add_cog(helpcommand(bot))

class custommenu(commands.HelpCommand):
    def __init__(self, **options):
        super().__init__(**options)
    
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title='CherriePy Help', description=' ')
        embed.description += '''
        Welcome to CherriePy Help menu
        Choose a category in the dropdown below to get started
        '''

        try:
            cogs = {cog.qualified_name:cog for cog in mapping if cog is not None}
            view = View()
            view.add_item(Dropdown(cogs))
        except Exception as e:
            await self.get_destination().send(e)

        await self.get_destination().send(embed = embed, view = view)