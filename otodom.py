import time
import random
import asyncio

import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from loguru import logger
from log import logger_setup

PAGE_URL = 'https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/cala-polska'
JSON_URL = 'https://www.otodom.pl/_next/data/91ZnsW0yvz8l1VBrd30i0/pl/wyniki/wynajem/mieszkanie/cala-polska.json'
params = {
    'limit': '72',
    'viewType': 'listing',
    'ownerTypeSingleSelect': 'ALL',
    'searchingCriteria': [
        'wynajem',
        'mieszkanie',
        'cala-polska',
    ],
}
headers = {
    'User-Agent': UserAgent().chrome,
}

MAX_REQUESTS_ATTEMPTS = 4


async def fetch(session: aiohttp.ClientSession, url: str, params: dict, request_attempt: int = 1) -> str | None:
    try:
        async with session.get(url, params=params, headers=headers) as response:
            html = await response.text()
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
            await loop.create_task(fetch(session, JSON_URL, params, request_attempt))

        else:
            logger.critical(_failed_request)

    except Exception as _ex:
        logger.critical(_ex)


async def get_postings() -> int:
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(limit=20, ttl_dns_cache=300),
        raise_for_status=True
    ) as session:
        html = await fetch(session, PAGE_URL, params)
        soup = BeautifulSoup(html, 'lxml')

        page_quantity = int(
            soup.find('ul', attrs={'data-cy': 'frontend.search.base-pagination.nexus-pagination'}).find_all('li')[-2].text
        )

        tasks = []
        for page_number in range(1, page_quantity + 1):
            tasks.append(asyncio.create_task(fetch(session, JSON_URL, params | {'page': page_number})))

        exceptions_count = 0
        a = 0
        for page in await asyncio.gather(*tasks):
            a+=1
            print(page, f'ASDASD {a}')

        return 1 if exceptions_count else 0


async def parse_otodom():
    start_time = time.monotonic()
    logger_setup(logger)
    execution_status = await asyncio.gather(asyncio.create_task(get_postings()))

    if execution_status[0]:
        logger.critical(f'Otodom hasn\'t been analyzed and the execution took {round(time.monotonic() - start_time, 1)} seconds!')
    else:
        logger.success(f'Otodom has been successfully analyzed in {round(time.monotonic() - start_time, 1)} seconds!')

    raise AttributeError
