import asyncio
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time

URL = {
    'otodom': 'https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/cala-polska?ownerTypeSingleSelect=ALL&viewType=listing',
}

headers = {'User-Agent': UserAgent().random}
params = {}

a = 0
async def fetch(session: aiohttp.ClientSession, url: str, params: dict) -> str:
    async with session.get(url, headers={'User-Agent': UserAgent().random}, params=params) as response:
        global a
        a += 1
        print(response.status, a)
        response = await response.text()
        return response


async def parse_otodom() -> tuple:
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, URL.get('otodom'), {})
        soup = BeautifulSoup(html, 'lxml')

        page_quantity = int(
            soup.find('ul', class_='e1h66krm4 css-iiviho').find_all('li', class_='css-1lclt1h')[-1].text)

        tasks = []
        for page_number in range(1, page_quantity + 1):
            tasks.append(asyncio.create_task(fetch(session, URL.get('otodom'), {'page': page_number})))


        for result in await asyncio.gather(*tasks):
            soup = BeautifulSoup(result, 'lxml')


start_time = time.monotonic()
asyncio.run(parse_otodom())
print(round(time.monotonic() - start_time, 1))
