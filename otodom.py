import asyncio
import random
import time

import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

URL = 'https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/cala-polska'
params = {
    'ownerTypeSingleSelect': 'ALL',
    'viewType': 'listing',
    'limit': '72'
}
headers = {
    'User-Agent': UserAgent().chrome
}

results_number = 0
a = 0
all_requests = -1


async def fetch(session: aiohttp.ClientSession, params: dict = params, attempt: int = 1) -> str:
    try:
        global all_requests
        global a
        global results_number
        all_requests+=1
        async with session.get(URL, params=params, headers=headers) as response:
            a += 1
            print(f"Request {a}: {response.status}")

            html = await response.text()
            results_number += 1

            return html

    except aiohttp.ClientResponseError as _failed_request:
        if _failed_request.status == 429:
            loop = asyncio.get_event_loop()
            waitting = 1 * 2 ** attempt + round(random.uniform(0, 1, ), 2)
            print(f'429 код, попытка номер {attempt}, жду {waitting}')
            attempt += 1
            await asyncio.sleep(waitting) # + рандом(0, 1)
            await loop.create_task(fetch(session, params=params, attempt=attempt))

        elif _failed_request.status == 403:
            print(_failed_request.args)

        else:
            print(_failed_request.args)  # логировать в файл log и в консоль

    except Exception as _ex:
        print(_ex)  # логировать в файл log и в консоль


async def parse_otodom() -> tuple:
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(limit=50, ttl_dns_cache=300),
        raise_for_status=True
    ) as session:
        html = await fetch(session, {})
        soup = BeautifulSoup(html, 'lxml')

        page_quantity = int(
            soup.find('ul', class_='e1h66krm4 css-iiviho').find_all('li', class_='css-43nhzf')[-1].text
        )

        tasks = []
        for page_number in range(1, page_quantity + 1):
            tasks.append(asyncio.create_task(fetch(session, {'page': page_number}))) # params + {'page': page_number}

        global results_number
        results = await asyncio.gather(*tasks)





start_time = time.monotonic()
asyncio.run(parse_otodom())
print(round(time.monotonic() - start_time, 1))
print(f'успешных запросов{results_number}')
print(f'всего зпросов{all_requests}')
