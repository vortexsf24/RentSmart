import asyncio
from otodom import parse_otodom
import db

async def main():
    while True:
        connection = db.DbConnection()
        await connection.create_pool()

        for result in await asyncio.gather(asyncio.create_task(parse_otodom())):
            await connection.update_news(paper_name=result[0], news=result[1])
        
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())