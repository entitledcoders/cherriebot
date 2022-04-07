import asyncio
import time
from pyppeteer import launch

async def hello_world():
    browser = await launch(headless = False)
    page = (await browser.pages())[0]
    starttime = time.time()
    await page.goto('https://www.youtube.com/watch?v=tLQLa6lM3Us&list=RDEM-pq0c1ZaSXRbQBZmXKqOzg')
    await page.waitForSelector("[class='style-scope ytd-thumbnail-overlay-time-status-renderer']", timeout = 1500)
    html = await page.content()
    results = await page.JJ('a[id=wc-endpoint]')
    for result in results[:20]:
        title = await result.Jeval('span[id=video-title]', '(e => e.innerText)')
        duration = (await result.Jeval("[class='style-scope ytd-thumbnail-overlay-time-status-renderer'][id=text]", '(e => e.innerText)')).replace('\n', '').replace(' ', '')
        url = (await (await result.getProperty('href')).jsonValue())[:43]
        print(url, duration, type(duration))
    print(time.time()-starttime)
    await page.goto('https://www.youtube.com/watch?v=UaZrspJ7eVY&list=RDUaZrspJ7eVY&start_radio=1&rv=UaZrspJ7eVY&t=2')
    await page.waitForSelector("[class='style-scope ytd-thumbnail-overlay-time-status-renderer']", timeout = 1500)
    results = await page.JJ('a[id=wc-endpoint]')
    for result in results[:20]:
        title = await result.Jeval('span[id=video-title]', '(e => e.title)')
        duration = (await result.Jeval("[class='style-scope ytd-thumbnail-overlay-time-status-renderer'][id=text]", '(e => e.innerText)')).replace('\n', '').replace(' ', '')
        url = (await (await result.getProperty('href')).jsonValue())[:43]
        print(title, url, duration, type(duration))
    print(time.time()-starttime)
def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(hello_world())


if __name__ == '__main__':
    main()