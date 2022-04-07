import asyncio
import sys, os
from arsenic import keys, browsers, services, start_session, stop_session

async def hello_world():
    dict = {}
    query = 'expand (x+1)(x-5)'
    service = services.Chromedriver()
    browser = browsers.Chrome()
    sys.stdout = open(os.devnull, "w")
    session = await start_session(service, browser)
    await session.get('https://www.wolframalpha.com/input/?i=1%2B1')
    await session.wait_for_element(15, 'h2[class=zcOOf]')
    boxes = await session.get_elements("[class='_2z545 q-8B0']")
    sys.stdout = sys.__stdout__
    print(len(boxes))
    for box in boxes[:3]:
        dict[await (await box.get_element('h2')).get_text()] = await (await box.get_element('img')).get_attribute('src')
        
    await stop_session(session)
    for text, image in dict.items():
        print(text, image)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(hello_world())


if __name__ == '__main__':
    main()