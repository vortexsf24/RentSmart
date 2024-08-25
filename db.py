import aiomysql
import logging as logger

import os
from dotenv import load_dotenv

logger.basicConfig(
    level=logger.INFO,
    format=u'%(filename)s:%(lineno)d #%(levelname)-1s [%(asctime)s]  ----->  %(message)s'
)

pool = None
load_dotenv()

async def create_pool():
    
    try:
        pool = await aiomysql.create_pool(
            host=os.getenv('HOST'),
            port=int(os.getenv('PORT')),
            user=os.getenv('USER'),
            password=os.getenv('PASSWORD'),
            db=os.getenv('DATABASE'),
            cursorclass=aiomysql.cursors.DictCursor,
            minsize=1,
            maxsize=10
        )
        return pool

    except Exception as _ex:
        logger.error(_ex)
    

async def update_postings(pool ,postings: dict) -> None:
    try:
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                delete_query = 'DELETE FROM postings'
                await cursor.execute(delete_query)
                
                for section in postings:
                    
                    columns = ", ".join(section.keys())
                    values = ", ".join(["%s"] * len(section))
                    insert_query = f"INSERT INTO postings ({columns}) VALUES ({values});"
                    await cursor.execute(insert_query, list(section.values()))
                
                await connection.commit()
    except Exception as _ex:
        
        logger.error(_ex)

async def get_postings(pool) -> list:
    try:
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                select_query = 'SELECT * FROM postings'
                await cursor.execute(select_query)
                rows = await cursor.fetchall()
                return rows
    except Exception as _ex:
        logger.error(_ex)
        return []

