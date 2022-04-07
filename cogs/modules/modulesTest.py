# coding=utf-8

import asyncio
import sys, os
from microYT import *
from arsenic import get_session, keys, browsers, services, start_session, stop_session
import locale

def getpreferredencoding(do_setlocale = True):
   return "utf-8"


class Test(object):
    async def hello_world(self):
        service = services.Chromedriver()
        browser = browsers.Chrome()
        driver = await start_session(service, browser)
        self.driver = driver
        self.avail = True
        results = await YoutubeSearch().new(self, 'aimer', qty = 5)
        print(results)
        await stop_session(self.driver)
    
    def reserve(self):
        self.avail = False

    def release(self):
        self.avail = True

def main():
    locale.getpreferredencoding = getpreferredencoding
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Test().hello_world())


if __name__ == '__main__':
    main()