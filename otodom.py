import time
import random
import asyncio

import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from loguru import logger
from log import logger_setup

URL = 'https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/cala-polska'
params = {
    'ownerTypeSingleSelect': 'ALL',
    'viewType': 'listing',
    'limit': '72',
}
headers = {
    'User-Agent': UserAgent().chrome,
}

MAX_REQUESTS_ATTEMPTS = 8


async def fetch(session: aiohttp.ClientSession, params: dict = params, request_attempt: int = 1) -> str:
    try:
        async with session.get(URL, params=params, headers=headers) as response:
            await asyncio.sleep(1)
            html = await response.text()
            await asyncio.sleep(1)
            return html

    except aiohttp.ClientResponseError as _failed_request:
        if _failed_request.status == 403:
            logger.critical(_failed_request)

        elif _failed_request.status == 404:
            logger.critical(_failed_request)

        elif _failed_request.status == 429:
            if request_attempt == MAX_REQUESTS_ATTEMPTS:
                logger.error(_failed_request)
                return

            logger.warning(_failed_request)

            awaiting_time = 1 * 2 ** request_attempt + round(random.uniform(0, 1, ), 2)
            request_attempt += 1

            await asyncio.sleep(awaiting_time)

            loop = asyncio.get_event_loop()
            await loop.create_task(fetch(session, params, request_attempt))

        else:
            logger.critical(_failed_request)

    except Exception as _ex:
        logger.critical(_ex)


async def get_postings() -> tuple:
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(limit=20, ttl_dns_cache=518),
        raise_for_status=True
    ) as session:
        html = await fetch(session, params)
        with open('html.html', 'w', encoding="utf-8") as file:
            file.write(html)
        soup = BeautifulSoup(html, 'lxml')

        page_quantity = int(
            soup.find('ul', attrs={'data-cy': 'frontend.search.base-pagination.nexus-pagination'}).find_all('li')[-2].text
        )

        tasks = []
        for page_number in range(1, page_quantity + 1):
            tasks.append(asyncio.create_task(fetch(session, params | {'page': page_number})))
        a = 0
        for page in await asyncio.gather(*tasks):
            soup = BeautifulSoup(page, 'lxml')
            pictures_promoted = soup.find('ul', attrs={'class': 'css-rqwdxd e127mklk0'}).find_all('li')[0].find('img')
            # pictures_first_group = soup.find('div', attrs={'data-cy': 'search.listing.organic'}).find_all('ul')
            # location = soup.find_all('p', class_='css-42r2ms eejmx80')
            a+=1
            print(pictures_promoted, a)

        return 0,


async def parse_otodom():
    start_time = time.monotonic()
    logger_setup(logger)
    result = await asyncio.gather(asyncio.create_task(get_postings()))

    logger.success(f'Otodom has been successfully analyzed in {round(time.monotonic() - start_time, 1)} seconds!')

    return result
