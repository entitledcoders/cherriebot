class Youtube():
    def __init__(self, url, title=None, duration=None, thumbnail=None):
        self.url = url
        self.title = title
        self.duration = duration
        self.thumbnail = thumbnail

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

class YoutubePlaylist(list):
    async def new(self, session, url):
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
        return self
            
    def get_urls(self):
        urls = []
        if self == []:
            raise Exception("Playlist is empty!")
        
        for video in self.videos:
            urls.append(video.url)
        
        return urls

class YoutubeSearch(list):
    async def new(self, session, query : str, qty = 1):
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
            title = await result.Jeval('[id=video-title]', '(e => e.title)')
            link = await result.Jeval('[id=video-title]', '(e => e.href)')
            try:
                duration = await result.Jeval("[class='style-scope ytd-thumbnail-overlay-time-status-renderer'][id=text]", '(e => e.innerText)')
                duration = duration.replace('\n', '').replace(' ', '')
            except:
                continue
            if duration == 'PREMIERE':
                continue
            thumbnail = f'https://img.youtube.com/vi/{link[-11::]}/0.jpg'
            self.append(Youtube(url=link, title=title, duration=duration, thumbnail=thumbnail))
        
        session.release()
        return self

    def get_urls(self):
        urls = []
        for video in self:
            urls.append(video.url)
        return urls