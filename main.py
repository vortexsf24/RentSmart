import asyncio
from otodom import parse_otodom

import time
import logging as logger

import db

async def main():
    
    

    
    connection = await db.create_pool()
    
    for result in await asyncio.gather(asyncio.create_task(parse_otodom())):
        start_time = time.monotonic()
        await db.update_postings(connection,result)
    
    # for row in await db.get_postings(connection):
    #     print(row['image'])

    connection.close()

    # logger.info(f'Process of collecting postings took {round(time.monotonic() - start_time, 1)} seconds')

        
if __name__ == "__main__":
    asyncio.run(main())