"""
1. Create transaction with delete statement and execute it only once and then insert posting_data in cycle then end transaction (OR integrate update
algorythm saving old data for still existing posts)

2. добавить прокси и при 403 их менять
3. docstrings
"""
import time
import json
import random
import asyncio

import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

import db

from loguru import logger
from log import logger_setup

from misc.utils import otodom_format_rooms_number
from misc.utils import otodom_format_floor_number

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


async def fetch(session: aiohttp.ClientSession, url: str, params: dict, request_attempt: int = 1) -> str | int:
    try:
        async with session.get(url, params=params, headers=headers) as response:
            return await response.text()

    except aiohttp.ClientResponseError as _failed_request:
        if _failed_request.status == 403:
            logger.critical(_failed_request)
            return 0

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
                return 0

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
            raise_for_status=True,
        ) as session:
            
            tasks = []
            exceptions_count = 0

            html = await fetch(session, PAGE_URL, params)
            soup = BeautifulSoup(html, 'lxml')

            page_quantity = int(
                soup.find('ul', attrs={'data-cy': 'frontend.search.base-pagination.nexus-pagination'}).find_all('li')[-2].text
            )

            # if 404 occurs it will make a new link
            assert await fetch(session, final_json_url, params)

            for page_number in range(1, page_quantity + 1):
                tasks.append(asyncio.create_task(fetch(session, final_json_url, params | {'page': page_number})))
            
            for page in await asyncio.gather(*tasks):
                if page in (0, None):
                    exceptions_count += 1
                    continue

                page = json.loads(page)
                postings = page['pageProps']['data']['searchAds']['items']

                for posting in postings:
                    posting_data = {
                        'title': posting['title'],
                        'image': posting['images'][0]['large'] if len(posting['images']) > 0 else 'Zapytaj',
                        'price': posting['totalPrice']['value'] if posting['totalPrice'] is not None else 'Zapytaj',
                        'czynsz': posting['rentPrice']['value'] if posting['rentPrice'] is not None else 'Zapytaj',
                        'area': posting['areaInSquareMeters'],
                        'rooms_number': otodom_format_rooms_number(posting['roomsNumber']),
                        'floor_number': otodom_format_floor_number(posting['floorNumber']),
                        'is_agency': False if posting['agency'] == 'null' else True,
                        'city': posting['location']['address']['city']['name'],
                        'address': posting['location']['address']['street']['name'] if posting['location']['address'][
                            'street'] is not None else 'Zapytaj',
                        'date': posting['dateCreatedFirst'],
                        'link': f'https://www.otodom.pl/pl/oferta/{posting['slug']}',
                        'platform': 'otodom',
                    }
                    
            return 2 if exceptions_count else 1

    except AssertionError:
        logger.critical('404 is not resolved!')
        return 0

    except Exception as _ex:
        logger.critical(_ex)


async def parse_otodom():
    start_time = time.monotonic()
    logger_setup(logger)

    match await get_postings():
        case 0:
            logger.critical(
                f'Otodom hasn\'t been analyzed! '
                f'Execution took {(time.monotonic() - start_time):.1f} seconds. '
            )

        case 1:
            logger.success(
                f'Otodom has been successfully analyzed! '
                f'Execution took {(time.monotonic() - start_time):.1f} seconds. '
            )

        case 2:
            logger.warning(
                f'Otodom has been analyzed but some errors occurred during execution! '
                f'Execution took {(time.monotonic() - start_time):.1f} seconds.'
            )