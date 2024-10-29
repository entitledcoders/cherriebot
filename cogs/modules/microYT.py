from pytube import YouTube
from os.path import exists
from youtubesearchpython import VideosSearch, Playlist
from threading import Thread
import concurrent.futures
import asyncio
import os
import yt_dlp

executor = concurrent.futures.ProcessPoolExecutor(max_workers=5)

def ytdlp_download(url: str):
    try:
        destination = "/temp/music"
        # Define options for yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{destination}/%(id)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        # Create a new yt-dlp object
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Download the audio
            ydl.download([url])
        print("Audio downloaded successfully!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def download(url: str):
    destination = "/temp/music"
    _id = url[-11:]
    if exists(f"{destination}/{_id}.mp3"):
        print(f"{_id} exists, skipping...")
        return
    yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
    video = yt.streams.filter(only_audio=True).first()
    print(f"downloading {_id}...")
    out_file = video.download(output_path=destination, filename=_id)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    try:
        os.rename(out_file, new_file)
    except:
        os.remove(out_file)
    return
        
class Youtube():
    def __init__(self, url, title=None, duration=None, thumbnail=None, file=None):
        self.url = url
        self.title = title
        self.duration = duration
        self.thumbnail = thumbnail
        self.file = f'/temp/music/{url[-11:]}.mp3' if file is None else file

    def update_metadata(self):
        results = YoutubeSearch(self.url)
        if results == []:
            raise ValueError('Failed to fetch data!')
        else:
            result = results[0]
        self = result

    def length(self):
        total = 0
        for i in self.duration.split(':'):
            total = total + int(i)*60
        total = total/60
    
    async def dl(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, download, self.url)

class YoutubePlaylist(list):
    async def new(self, url):
        self = YoutubePlaylist()
        pl = Playlist(url)
        pl.getNextVideos()
        for video in pl.videos:
            title = video['title']
            link = f"https://www.youtube.com/watch?v={video['id']}"
            duration = video['duration']
            thumbnail = f"https://img.youtube.com/vi/{video['id']}/0.jpg"
            self.append(Youtube(url=link, title=title, duration=duration, thumbnail=thumbnail))

        return self
    
    async def new_legacy(self, session, url):
        self = YoutubePlaylist()

        session.reserve()
        driver = session.driver

        await driver.goto(url)
        await driver.waitForSelector("[class='style-scope ytd-thumbnail-overlay-time-status-renderer']", timeout = 0)
        
        videos = await driver.JJ('a[id=wc-endpoint]')

        for video in videos:
            link = (await (await video.getProperty('href')).jsonValue())[:43]
            title = await video.Jeval('span[id=video-title]', '(e => e.title)')
            duration = await video.Jeval("[class='style-scope ytd-thumbnail-overlay-time-status-renderer'][id=text]", '(e => e.innerText)')
            duration = duration.replace('\n', '').replace(' ', '')
            thumbnail = f'https://img.youtube.com/vi/{link[-11::]}/0.jpg'
            self.append(Youtube(url=link, title=title, duration=duration, thumbnail=thumbnail))

        session.release()
        tasks = [download(video.url) for video in self]
        await asyncio.gather(*tasks)
        return self
            
    def get_urls(self):
        urls = []
        if self == []:
            raise Exception("Playlist is empty!")
        
        for video in self.videos:
            urls.append(video.url)
        
        return urls

class YoutubeSearch(list):
    async def new(self, query : str, qty = 1):
        self = YoutubeSearch()
        
        results = VideosSearch(query=query, limit=11).result()['result']
        for video in results:
            if len(self) == qty:
                break
            duration = video['duration']
            secs = sum(int(x) * 60 ** i for i, x in enumerate(reversed(duration.split(':'))))
            if (secs > 600) and (qty != 1):
                continue
            title = video['title']
            link = f"https://www.youtube.com/watch?v={video['id']}"
            thumbnail = f"https://img.youtube.com/vi/{video['id']}/0.jpg"
            # Thread(target=download, args=[link]).start()
            self.append(Youtube(url=link, title=title, duration=duration, thumbnail=thumbnail))
            
        return self

    async def new_legacy(self, session, query : str, qty = 1):
        self = YoutubeSearch()

        query = query.replace('%', '%25')
        query = query.replace(':', '%3A')
        query = query.replace('/', '%2F')
        query = query.replace('?', '%3F')
        query = query.replace('=', '%3D')
        query = query.replace('@', '%40')
        query = query.replace('#', '%23')
        query = query.replace('$', '%24')
        query = query.replace('&', '%26')
        query = query.replace('+', '%2B')
        query = query.replace(' ', '+')

        search = 'https://www.youtube.com/results?search_query=' + query

        session.reserve()
        driver = session.driver

        await driver.goto(search)
        await driver.waitForSelector("[class='style-scope ytd-thumbnail-overlay-time-status-renderer']", timeout = 0)
        
        results = await driver.JJ('[id=dismissible]')

        for result in results:
            if len(self) == qty:
                break
            try:
                duration = await result.Jeval("[class='style-scope ytd-thumbnail-overlay-time-status-renderer'][id=text]", '(e => e.innerText)')
                duration = duration.replace('\n', '').replace(' ', '')
            except:
                continue
            if duration == 'PREMIERE':
                continue
            title = await result.Jeval('[id=video-title]', '(e => e.title)')
            link = await result.Jeval('[id=video-title]', '(e => e.href)')
            secs = sum(int(x) * 60 ** i for i, x in enumerate(reversed(duration.split(':'))))
            if (secs > 600) and (qty != 1):
                continue
            thumbnail = f'https://img.youtube.com/vi/{link[-11::]}/0.jpg'
            print("starting new dl task")
            await loop.run_in_executor(executor, download, (link,))
            self.append(Youtube(url=link, title=title, duration=duration, thumbnail=thumbnail))
        
        session.release()
        return self

    def get_urls(self):
        urls = []
        for video in self:
            urls.append(video.url)
        return urls