import discord
import asyncio
import random
from .modules.microYT import Youtube, YoutubePlaylist, YoutubeSearch
from discord.ext import commands
from discord.ui import Button, View
from discord import ButtonStyle, Interaction

# - - - - - ( START VIEW COMPONENTS ) - - - - - #
class ChoiceBtn(Button['Choice']):
    def __init__(self, bot, i: int):
        if i == 5:
            super().__init__(style = ButtonStyle.danger, label = 'x')
        else:
            super().__init__(style = ButtonStyle.blurple, label = i+1)
        self.bot = bot
        self.i = i
    
    async def callback(self, interaction: Interaction):
        view: Choice = self.view
        if interaction.user == view.author:
            if self.i == 5:
                await interaction.response.send_message(f"Cancelled, stopping view..", ephemeral=True)
                self.bot.value = None
            else:
                await interaction.response.send_message(f"You chose number {self.label}", ephemeral=True)
                self.bot.value = self.i
            view.stop()
        else:
            await interaction.response.send_message("This belongs to other person!", ephemeral=True)

class Choice(View):
    def __init__(self, bot, author, *, timeout = 60):
        super().__init__(timeout=timeout)
        self.bot, self.author = bot, author
        for i in range(6):
            self.add_item(ChoiceBtn(bot, i))

    async def on_timeout(self):
        self.bot.value = random.randrange(5)
        self.stop()
        return await super().on_timeout()
# - - - - - ( END VIEW COMPONENTS ) - - - - - #


# - - - - - ( START INTERNAL COMPONENTS ) - - - - - #
class ytplayer(commands.Cog):
    song_queue = {}
    volume = {}
    loopMode = {}
    currentsong = {}
    idleMode = {}
    idleSong = {}

    # FFMPEGOPTIONS = {
    #                 'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
    #                 'options'       : '-vn'
    #                 }
    FFMPEGOPTIONS = {
                        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                        'options': '-vn -filter:a "volume=0.25"'
                    }

    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}
        self.retry = 0
        for guild in bot.guilds:
            self.song_queue[guild.id] = []
            self.currentsong[guild.id] = {}
            self.loopMode[guild.id] = 'off'
            self.volume[guild.id] = 25
            self.idleMode[guild.id] = False
            self.idleSong[guild.id] = ''

    async def play_next(self, ctx):
        queue = self.song_queue[ctx.guild.id]
        if ctx.voice_client is None:
            return await ctx.send("```Bot has left the channel```")

        loopMode = self.loopMode[ctx.guild.id]
        
        if loopMode == 'song':
            return await self.play_song(ctx, self.currentsong[ctx.guild.id])

        if len(queue) > 0:
            await self.play_song(ctx, queue[0])
            if loopMode == 'queue':
                queue.append(queue[0])
            queue.pop(0)
            
        else:
            if self.idleMode[ctx.guild.id]:
                await ctx.send(f'```Queue is empty! Playing idle music```')
                await self.play_song(ctx, self.idleSong[ctx.guild.id])
            else:
                await ctx.send(f'```Queue is empty!```')
                await self.leave(ctx)
        
        # print(self.loopMode)

    async def play_song(self, ctx, song):
        self.currentsong[ctx.guild.id] = song
        await ctx.send(f'```Now playing: {song.title}```')
        self.retry = 0
        # while 1:
        try:
            await song.dl()
        except Exception as e:
            self.retry += 1
            await ctx.send(f'```Error occured: {e} \nSkipping... (Retry: {self.retry})```')
            if self.retry > 2:
                return await self.play_next(ctx)
        try:
            ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.file, executable='C:\\ffmpeg\\bin\\ffmpeg.exe')), after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
        except Exception as e:
            await ctx.send(f'```Error fetching the audio stream!: {e} \nRetrying...```') 
            return await self.play_song(ctx, song)

        ctx.voice_client.source.volume = self.volume[ctx.guild.id]/100
# - - - - - ( END INTERNAL COMPONENTS ) - - - - - #


# - - - - - ( START COMMANDS COMPONENTS ) - - - - - #
# JOIN
    @commands.hybrid_command(
        help = "~join",
        brief = "Requests bot to enter your voice channel.",
        description = ""
    )
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send(f'You should join a voice channel first {ctx.author}!')
        else:
            try:
                voice_channel = ctx.author.voice.channel
                if ctx.voice_client is None:
                    await voice_channel.connect()
                else:
                    await ctx.voice_client.move_to(voice_channel)
                await ctx.send(f'```Joining {voice_channel}```')
            except Exception as e:
                await ctx.send(f'```Error occured: {e}```')

# LEAVE
    @commands.hybrid_command(
        help = "~leave",
        brief = "Requests bot to leave current voice channel.",
        description = ""
    )
    async def leave(self, ctx):
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("I am not connected to a voice channel.")

# SEARCH
    @commands.hybrid_command(
        help = "~search [title]",
        brief = "Searches for title in Youtube and users can choose between 5 results.",
        description = ""
    )
    async def search(self, ctx, *, song=None):
        
        if song is None:
            return await ctx.send(f"Include a song {ctx.author.mention}")
        await ctx.send("Searching for songs!")
        
        try:
            songs = await YoutubeSearch().new(query=song, qty=5)
        except Exception as error:
            await ctx.send(f'```diff\n- {error} \n```')

        embed = discord.Embed(title=f"Results for '{song}':\n", description="")
        view = Choice(bot=self.bot, author=ctx.message.author)
        amount = 0
        for song in songs:
            amount += 1
            embed.description += f"**{amount})** [{song.title}]({song.url}) ({song.duration})\n"
            
        embed.set_footer(text=f"Displaying the first {amount} results.")   
        message = await ctx.send(embed=embed, view=view)
        await view.wait()
        await message.edit(view=None)
        if self.bot.value is not None:
            song = songs[int(self.bot.value)]
            await self.play(ctx, song=song)

# PLAY
    @commands.hybrid_command(
        aliases=['p'], 
        help = "~p [title / yt url / mp3]", 
        brief = "Plays / queues the song into queue",
        description = ""
    )
    async def play(self, ctx, *, song=None, pn=False):
        if ctx.voice_client is None:
            await self.join(ctx)
        
        attachments = ctx.message.attachments
        if (song is None) and (len(attachments) == 0) :
            return await ctx.send(f'```Please include a song or attach an MP3 file {ctx.author.mention}```')

        for attachment in attachments:
            if not attachment.filename.endswith('mp3'):
                return await ctx.send(f'```The bot can only accept MP3 audio files```')
            try:
                fp = 'music/' + attachment.filename
                await attachment.save(fp)
                song = Youtube(
                    url = "mp3", 
                    title = attachment.filename[:-4].replace('_', ' '), 
                    duration = "NA",
                    file = fp
                )
                await ctx.send(f'```Music file is downloaded, {song.url}```')
                break
            except Exception as e:
                await ctx.send(e)

        if not hasattr(song, 'url'):
            if "&list" in song:
                # print("COMMAND PLAYLIST CALLED")
                return await self.playlist(ctx, song=song)

            try:
                # print("START SEARCH")
                song = await YoutubeSearch().new(query=song)
                song = song[0]
            except Exception as error:
                return await ctx.send(f'```diff\n- {error} \n```')
            
            if song is None:
                return await ctx.send("Song could not be found, try using ~search")
            
        queue_len = len(self.song_queue[ctx.guild.id])

        if ctx.voice_client.source is not None:
            if queue_len < 200:
                if pn:
                    self.song_queue[ctx.guild.id].insert(0, song)
                    return await ctx.send(f'```{song.title} has been scheduled to play after current song```')
                else:
                    self.song_queue[ctx.guild.id].append(song)
                    return await ctx.send(f'```{song.title} has been added to queue, position: {queue_len+1}```\n')

            else:
                return await ctx.send("```The queue is full!```")
        # print("CALL PLAY SONG")
        await self.play_song(ctx, song)

# PLAY NEXT
    @commands.hybrid_command(
        aliases=['pn'],
        help = "~pn [title / yt url / mp3]",
        brief = "Forces song to be played after current song.",
        description = ""
    )
    async def playnext(self, ctx, *, song=None):
        await self.play(ctx, song=song, pn=True)

# PLAYLIST
    @commands.hybrid_command(
        aliases=['pl', 'list'], 
        help = "~pl [yt url] (start index) (stop index).",
        brief = "Queues songs from playlist from start to stop index (Max 200). By default, first 100. ",
        description = ""
    )
    async def playlist(self, ctx, song=None, start=0, end=100):
        if song is None:
            return await ctx.send(f'Include a playlist link {ctx.author.mention}')
        
        p = await YoutubePlaylist().new(url=song)
        queue = self.song_queue[ctx.guild.id]
        quota = 200 - len(queue)

        if (start+len(p)) > quota:
            end = start + quota
        
        if (end-start) > len(p):
            end = -1

        song = p[start]
        await self.play(ctx, song=song)
        queue.extend(p[start+1:end])
        await ctx.send(f'```and another {len(p[start+1:end])} songs to the queue```')

# FORCE SKIP
    @commands.hybrid_command(
        aliases=['fs'],
        help = "~fs",
        brief = "Forcefully skips currently playing song.",
        description = ""
    )
    async def forceskip(self, ctx):
        await ctx.send("```Current song has been skipped!```")
        ctx.voice_client.stop()

# SET VOLUME
    @commands.hybrid_command(
        aliases = ['volume', 'v', 'vol'], 
        help = "~vol [0-200]",
        brief = "Sets bot audio volume. Default: 25",
        description = ""
    )
    async def setvolume(self, ctx, volume = 25):
        self.volume[ctx.guild.id] = 25
        await ctx.send(f"```Volume has been set to: {volume}%```")
        ctx.voice_client.source.volume = volume/100

# DISPLAY QUEUE
    @commands.hybrid_command(
        aliases=['q'],
        help = "~q",
        brief = "Displays all songs in queue.",
        description = ""
    )
    async def queue(self, ctx):
        queue = self.song_queue[ctx.guild.id]
        if len(queue) == 0:
            return await ctx.send("```No songs are in the queue```")
        embed = discord.Embed(title="Song Queue", description=f"")
        message = await ctx.send(embed=embed)
        i = 0
        for song in queue:
            i += 1
            embed.description += f"{i}. [{song.title}]({song.url}) ({song.duration})\n"
            if i%10 == 0:
                embed.set_footer(text = f"Songs in queue: {len(queue)}. Automatic paging ({i-9}-{i}). [10s to next page]")
                await message.edit(embed=embed)
                embed.description=''
                await asyncio.sleep(10)

        embed.set_footer(text = f"Songs in queue: {len(queue)}. Automatic paging ({int(i/10)*10+1}-{i}).")
        await message.edit(embed=embed)

# REMOVE FROM QUEUE
    @commands.hybrid_command(
        aliases=['rem', 'remove'],
        help = "~rem [index]",
        brief = "Removes song in the queue at specified index",
        description = ""
    )
    async def removequeue(self, ctx, i=1):
        queue = self.song_queue[ctx.guild.id]
        song = queue[i-1]
        await ctx.send(f'```{song.title} has been removed from the queue.```')
        queue.pop(i-1)

# CLEAR QUEUE
    @commands.hybrid_command(
        aliases=['clear'],
        help = f"~clear",
        brief = "Removes all songs in the queue.",
        description = ""
    )
    async def clearqueue(self, ctx):
        self.song_queue[ctx.guild.id] = []
        await ctx.send("```Song queue have been cleared!```")

# SAVE QUEUE
    @commands.hybrid_command(
        aliases=['saveq'],
        help = f"~saveq",
        brief = "Not yet implemented (WIP)",
        description = ""
    )
    async def savequeue(self, ctx):
        pass

# LOAD QUEUE
    @commands.hybrid_command(
        aliases=['loadq'],
        help = f"~loadq",
        brief = "Not yet implemented (WIP)",
        description = ""
    )
    async def loadqueue(self, ctx):
        pass

# NOW PLAYING
    @commands.hybrid_command(
        aliases=['np'],
        help = "~np",
        brief = "Displays currently playing song title and duration",
        description = ""
    )
    async def nowplaying(self, ctx):
        song = self.currentsong[ctx.guild.id]
        embed = discord.Embed(
            title=f"Currently playing: {song.title}",
            description=f"{song.duration}"
        )
        await ctx.send(embed = embed)

# PAUSE
    @commands.hybrid_command(
        help = "~pause",
        brief = "Pauses audio from bot.",
        description = ""
    )
    async def pause(self, ctx):
        if ctx.voice_client.is_paused():
            return await ctx.send("```I am already paused.```")

        ctx.voice_client.pause()
        return await ctx.send("```The current song has been paused.```")

# RESUME
    @commands.hybrid_command(
        help = "~resume",
        brief = "Resumes from pausing audio.",
        description = ""
    )
    async def resume(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("```I am not connected to a voice channel.```")

        if not ctx.voice_client.is_paused():
            return await ctx.send("```I am already playing a song.```")
        
        ctx.voice_client.resume()
        return await ctx.send("```The current song has been resumed.```")

# SHUFFLE
    @commands.hybrid_command(
        help = "~shuffle",
        brief = "Shuffles order of song in queue.",
        description = ""
    )
    async def shuffle(self, ctx):
        random.shuffle(self.song_queue[ctx.guild.id])
        return await ctx.send('Queue have been shuffled!')

# IDLE MODE
    @commands.hybrid_command(
        help = "~idle [True / False]",
        brief = "When queue is empty, plays specified idle song if idle mode is True.",
        description = ""
    )
    async def idle(self, ctx, mode):
        if self.idleSong[ctx.guild.id] == '':
            return await ctx.send(f'Please set up idle song before turning on idle mode. `~idlesong [title / yt url]`')
        self.idleMode[ctx.guild.id] = mode
        return await ctx.send(f'Idle mode has set to {mode}. Make sure you have idleSong applied')

# IDLE SONG
    @commands.hybrid_command(
        help="~idlesong [title / yt url]",
        brief = "Sets the idle song for idle mode.",
        description = ""
    )
    async def idlesong(self, ctx, song):
        self.idleSong[ctx.guild.id] = (await YoutubeSearch().new(query=song))[0]
        return await ctx.send('Idle song has updated!')

# LOOP SETTING
    @commands.hybrid_command(
        help = "~loop [off / song / queue]",
        brief = "Changes loop settings on playlist to repeat song, queue or off.",
        description = ""
    )
    async def loop(self, ctx, mode=None):
        modeList = ['song', 'queue', 'off']
        if mode in modeList:
            self.loopMode[ctx.guild.id] = mode
            await ctx.send(f"```Looping has been set to: {mode}```")
        else:
            await ctx.send("```Change loop modes to song/queue/off```")
    
# - - - - - ( END COMMAND COMPONENTS ) - - - - - #

async def setup(bot):
    await bot.add_cog(ytplayer(bot))