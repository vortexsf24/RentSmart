import asyncio
# import logging
# import time

import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

URL = {
    'otodom': 'https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/cala-polska?ownerTypeSingleSelect=ALL&viewType=listing',
}

headers = {'User-Agent': UserAgent().chrome}


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url, headers=headers) as response:
        response = await response.text()
        return response


async def parse_otodom() -> tuple:
    # try:
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, URL.get('otodom'))
        soup = BeautifulSoup(html, 'lxml')

        ul = soup.find('ul', class_='css-rqwdxd e127mklk0')

        # links = tuple(elem.get('href') for elem in
        #               soup.find('ol', class_='media-item-list media-item-list--timestamps').findAll('a',
        #                                                                                             class_='js-tealium-tracking'))
        # articles = tuple(elem.text for elem in
        #                  soup.find('ol', class_='media-item-list media-item-list--timestamps').findAll('a',
        #                                                                                                class_='js-tealium-tracking'))

        photoes = tuple(div.find('img', class_='css-uwwqev ed99okv5') for div in
                        ul.find_all('div', attrs={'class': 'css-17rb9mp', 'aria-selected': 'true'}))

        # descriptions = tuple(elem.text for elem in
        #                  soup.find('ol', class_='media-item-list media-item-list--timestamps').findAll('a',
        #                                                                                                class_='js-tealium-tracking'))

        print(photoes)

    # except Exception as _ex:
    #     logging.error(_ex)


# config: Config
async def start_parsing() -> None:
    while True:
        # start_time = time.monotonic()
        tasks = [
            asyncio.create_task(parse_otodom()),

        ]

        # connection = BotDB(config)
        # await connection.create_pool()

        # for result in await asyncio.gather(*tasks):
        #     await connection.update_news(paper_name=result[0], news=result[1])

        # connection.pool.close()
        # logging.info(f'Process of collecting news took {round(time.monotonic() - start_time, 1)} seconds')

        await asyncio.sleep(300)


asyncio.run(parse_otodom())