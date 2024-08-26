import aiomysql
import logging as logger

import os
from dotenv import load_dotenv


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
        logger.critical(f'Pool hasn\'t been created!')
    

async def update_postings(pool ,posting: dict) -> None:
    try:
        async with pool.acquire() as connection:
            async with connection.transaction():

                # Delete existing postings
                delete_query = 'DELETE FROM postings'
                await connection.execute(delete_query)
                
                # Insert new postings
                insert_query = '''INSERT INTO postings (title, image, price, czynsz,
                                area, rooms_number, floor_number,
                                is_agency, city, address, date, link, platform)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                await connection.execute(insert_query, *posting.values())
    except Exception as ex:
        logger.critical(f"Error updating postings: {ex}")

async def get_postings(pool) -> list:
    try:
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                select_query = 'SELECT * FROM postings'
                await cursor.execute(select_query)
                rows = await cursor.fetchall()
                return rows
    except Exception as ex:
        logger.critical(f"Error retrieving postings: {ex}")
        return []

