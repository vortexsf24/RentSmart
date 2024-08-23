# line 50 сделать так чтобы ретерн не None
# сделать success если все все правильно в бд записалось, Error елси не все, critical если ничего
# добавить прокси и при 403 их менять
# поменять названия ключей и сделать условия через isinstance()

import time
import json
import random
import asyncio

import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from loguru import logger
from log import logger_setup

PAGE_URL = 'https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/cala-polska'
BASE_JSON_URL = 'https://www.otodom.pl/_next/data/%s/pl/wyniki/wynajem/mieszkanie/cala-polska.json'
MAX_REQUESTS_ATTEMPTS = 5

dynamic_json_link_part = ''
final_json_url = BASE_JSON_URL % dynamic_json_link_part

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


async def fetch(session: aiohttp.ClientSession, url: str, params: dict, request_attempt: int = 1) -> str | None:
    try:
        async with session.get(url, params=params, headers=headers) as response:
            html = await response.text()
            return html

    except aiohttp.ClientResponseError as _failed_request:
        if _failed_request.status == 403:
            logger.critical(_failed_request)

        elif _failed_request.status == 404:
            global final_json_url
            global dynamic_json_link_part

            logger.info('JSON link is expired, finding a new one...')

            html = await fetch(session, PAGE_URL, params)
            soup = BeautifulSoup(html, 'lxml')

            dynamic_json_link_part = json.loads(soup.find('script', id='__NEXT_DATA__').text)['buildId']
            final_json_url = BASE_JSON_URL % dynamic_json_link_part

            return 1

        elif _failed_request.status == 429:
            if request_attempt == MAX_REQUESTS_ATTEMPTS:
                logger.error(_failed_request)
                return

            logger.warning(_failed_request)

            awaiting_time = 1 * 2 ** request_attempt + round(random.uniform(0, 1, ), 3)
            request_attempt += 1

            await asyncio.sleep(awaiting_time)

            loop = asyncio.get_event_loop()
            return await loop.create_task(fetch(session, url, params, request_attempt))

        else:
            logger.critical(_failed_request)

    except Exception as _ex:
        logger.critical(_ex)


async def get_postings() -> int:
    try:
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=20, ttl_dns_cache=300),
            raise_for_status=True
        ) as session:
            html = await fetch(session, PAGE_URL, params)
            soup = BeautifulSoup(html, 'lxml')

            page_quantity = int(
                soup.find('ul', attrs={'data-cy': 'frontend.search.base-pagination.nexus-pagination'}).find_all('li')[-2].text
            )

            # if 404 occurs it will make a new link
            assert await fetch(session, final_json_url, params)

            tasks = []
            for page_number in range(1, page_quantity + 1):
                tasks.append(asyncio.create_task(fetch(session, final_json_url, params | {'page': page_number})))

            exceptions_count = 0
            a = 1
            posts = []
            for page in await asyncio.gather(*tasks):
                print(a)
                a+=1

                page = json.loads(page)
                page_postings = page['pageProps']['data']['searchAds']['items']

                for posting in page_postings:
                    posting_data = {
                        
                        'price': posting['totalPrice']['value'] if posting['totalPrice'] is not None else 'Zapytaj',
                        'czynsz': posting['rentPrice']['value'] if posting['rentPrice'] is not None else 'Zapytaj',
                        'image': posting['images'][0]['large'] if len(posting['images']) != 0 else 'Zapytaj',
                        'area': posting[''],
                        'square_meters': posting['areaInSquareMeters'],
                        'number_of_rooms': posting['roomsNumber'],
                    }

                    posts.append(posting_data)

            print(posts)
            print(len(posts))

            return 1 if exceptions_count else 0

    except AssertionError:
        logger.critical('404 is not resolved!')

    except Exception as _ex:
        logger.critical(_ex)


async def parse_otodom():
    start_time = time.monotonic()
    logger_setup(logger)
    execution_status = await asyncio.gather(asyncio.create_task(get_postings()))

    if execution_status[0]:
        logger.critical(f'Otodom hasn\'t been analyzed and the execution took {round(time.monotonic() - start_time, 1)} seconds!')
    else:
        logger.success(f'Otodom has been successfully analyzed in {round(time.monotonic() - start_time, 1)} seconds!')