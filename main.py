import asyncio
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

URL = {
    'otodom': 'https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/cala-polska?ownerTypeSingleSelect=ALL&viewType=listing',
}

headers = {'User-Agent': UserAgent().chrome}
params = {}

async def fetch(session: aiohttp.ClientSession, url: str, params: dict) -> str:
    async with session.get(url, headers=headers, params=params) as response:
        response = await response.text()
        return response


async def parse_otodom() -> tuple:
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, URL.get('otodom'), {})
        soup = BeautifulSoup(html, 'lxml')

        # page_quantity = int(
        #     soup.find('ul', class_='e1h66krm4 css-iiviho').find_all('li', class_='css-1lclt1h')[-1].text)
        page_quantity = 609
        tasks = []
        for page_number in range(1, page_quantity + 1):
            tasks.append(asyncio.create_task(fetch(session, URL.get('otodom'), {'page': page_number})))

        print(123)
        # Запускаем задачи и собираем результаты
        results = await asyncio.gather(*tasks)
        print(123)
        # Обработка результатов
        asd=[]
        a = 1
        for result in results:
            soup = BeautifulSoup(result, 'lxml').text
            asd.append(soup + '\n' + str(a))
            a+=1
        print(asd)




asyncio.run(parse_otodom())
