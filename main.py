import asyncio
import random
import time

import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

URL = {
    'otodom': 'https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/cala-polska?ownerTypeSingleSelect=ALL&viewType=listing',
}
headers = {
    'User-Agent': UserAgent().chrome
}
params = {}

tasks = []
results_number = 0
a = 0


async def timeout(attemp, session, params, page_number):
    await asyncio.sleep(1* 2**attemp + 0.1)


async def fetch(session: aiohttp.ClientSession, url: str, params: dict = params, headers: dict = headers, page_number: int = None, attemp: int = 1) -> str:
    try:
        global a
        global results_number

        async with session.get(url, params=params, headers=headers) as response:
            a += 1
            print(f"Request {a}: {response.status}")

            html = await response.text()
            results_number += 1
            # await asyncio.sleep(0.1)
            return html

    except aiohttp.ClientResponseError as _failed_request:
        if _failed_request.status == 429:
            global tasks

            print(attemp)
            attemp+=1
            tasks.append(asyncio.ensure_future(timeout(attemp, session, params, page_number)))
            await asyncio.sleep(1 * 2 ** attemp)
            tasks.append(asyncio.ensure_future(
                fetch(session, URL.get('otodom'), {'page': page_number}, page_number=page_number, attemp=attemp)))


        elif _failed_request.status == 403:
            print(_failed_request.args)

        else:
            print(_failed_request.args)  # логировать в файл log и в консоль

    except Exception as _ex:
        print(_ex)  # логировать в файл log и в консоль


async def parse_otodom() -> tuple:
    async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=30, ttl_dns_cache=300),
            raise_for_status=True
    ) as session:
        html = await fetch(session, URL.get('otodom'), {})
        soup = BeautifulSoup(html, 'lxml')

        page_quantity = int(
            soup.find('ul', class_='e1h66krm4 css-iiviho').find_all('li', class_='css-43nhzf')[-1].text)

        global tasks
        for page_number in range(1, page_quantity + 1):
            tasks.append(asyncio.create_task(fetch(session, URL.get('otodom'), {'page': page_number}, page_number=page_number))) # params + {'page': page_number}

        global results_number
        results = await asyncio.gather(*tasks)




start_time = time.monotonic()
asyncio.run(parse_otodom())
print(round(time.monotonic() - start_time, 1))
print(results_number)
