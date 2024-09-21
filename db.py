import os
import config
import aiomysql

from log import logger


class Db:
    def __init__(self):
        self.pool: aiomysql.Pool
        self.host = os.getenv('HOST')
        self.port = int(os.getenv('PORT'))
        self.user = os.getenv('USERNAME')
        self.password = os.getenv('PASSWORD')
        self.db = os.getenv('DATABASE')

    async def create_pool(self):
        self.pool = await aiomysql.create_pool(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.db,
            autocommit=True,
            maxsize=10
        )

    async def insert_posting(self, posting_data):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                sql = '''
                INSERT INTO postings
                (title, image, price, czynsz, area, rooms_number, floor_number, is_agency, city, address, date, link, platform)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    title=VALUES(title),
                    image=VALUES(image),
                    price=VALUES(price),
                    czynsz=VALUES(czynsz),
                    area=VALUES(area),
                    rooms_number=VALUES(rooms_number),
                    floor_number=VALUES(floor_number),
                    is_agency=VALUES(is_agency),
                    city=VALUES(city),
                    address=VALUES(address),
                    date=VALUES(date),
                    platform=VALUES(platform)
                '''
                params = (
                    posting_data['title'],
                    posting_data['image'],
                    posting_data['price'],
                    posting_data['czynsz'],
                    posting_data['area'],
                    posting_data['rooms_number'],
                    posting_data['floor_number'],
                    posting_data['is_agency'],
                    posting_data['city'],
                    posting_data['address'],
                    posting_data['date'],
                    posting_data['link'],
                    posting_data['platform'],
                )

                await cursor.execute(sql, params)

    async def remove_deleted_postings(self, current_links: list):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                sql = '''
                DELETE FROM postings
                WHERE link NOT IN (%s)
                ''' % ','.join(['%s'] * len(current_links))

                await cursor.execute(sql, current_links)

    async def close_pool(self):
        self.pool.close()
        await self.pool.wait_closed()
