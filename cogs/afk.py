from discord.ext import commands

class pingmsg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.afkmembers = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        msg = ''
        for member in message.mentions:
            if member.id in self.bot.afkmembers.keys():
                msg = msg + member.name + ': ' + self.bot.afkmembers[member.id] + '\n'
        if len(msg)>0:
            await message.reply(msg)

    @commands.command(aliases=['afk', 'away'], help="~afk ~away [message]. Sends your away message if pinged")
    async def setawaymsg(self, ctx, *, msg=None):
        await ctx.message.delete()

        usermessages = self.bot.afkmembers
        user = ctx.author
        
        if user.id in usermessages.keys():
            usermessages.pop(user.id)
            await user.send('You turned off your away message.')
        else:
            if msg is None:
                msg = 'currently away (default message)'
            self.bot.afkmembers[user.id] = msg
            await user.send(f'You have set your away message to {msg}.')
        print(usermessages)

def setup(bot):
    bot.add_cog(pingmsg(bot))