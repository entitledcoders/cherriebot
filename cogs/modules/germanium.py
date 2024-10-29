from typing import Awaitable
from pyppeteer import launch

class GermaniumElement(object):
    async def new(self):
        self = GermaniumElement()
        self.avail = True
        self.browser = await launch(autoClose = True)
        self.driver = (await self.browser.pages())[0]
        return self
    
    def reserve(self):
        self.avail = False

    def release(self):
        self.avail = True

class Germanium():
    def __init__(self):
        self.sessions = []

    async def next(self):
        while True:
            for session in self.sessions:
                if session.avail is True:
                    return session
            
            self.sessions.append(await GermaniumElement().new())

    async def close(self):
        for session in self.sessions:
            await session.browser.close()
        
        self.sessions = []