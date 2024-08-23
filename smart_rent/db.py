import aiomysql
import logging

from smart_rent.config import Config

logging.basicConfig(
    level=logging.INFO,
    format=u'%(filename)s:%(lineno)d #%(levelname)-1s [%(asctime)s]  ----->  %(message)s'
)

class BotDB:
    """
    Class for interaction with the database.
    Allows writing parsed news and retrieving them when required.

    Args:
        config (Config): The configuration object containing database connection settings.

    Attributes:
        pool (aiomysql.Pool):  The connection pool for executing database queries.
        config (Config): The configuration object containing database connection settings.
    """

    def __init__(self, config: Config):
        self.pool: aiomysql.Pool = None
        self.config: Config = config

    async def create_pool(self) -> None:
        """
        Creates a connection pool to the database.
        """
        try:
            self.pool = await aiomysql.create_pool(
                host=self.config.db.HOST,
                port=self.config.db.PORT,
                user=self.config.db.USER,
                password=self.config.db.PASSWORD,
                db=self.config.db.DATABASE,
                cursorclass=aiomysql.cursors.DictCursor,
                minsize=1,
                maxsize=10
            )

        except Exception as _ex:
            logging.error(_ex)

    async def update_news(self, postings:dict) -> None:
        """
        Replaces all news of a certain paper with the relevant news.
        Method is called everytime when the news web-page is parsed.
        Args:
            paper_name (str): The name of the table where news will be updated.
            news (list): The list of news to update in the table.
        Returns:
            None
        """

        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor() as cursor:

                    # Create the TRUNCATE query
                    delete_query = f'TRUNCATE TABLE otodom'
                    await cursor.execute(delete_query)
                    await connection.commit()

                    for section in postings:
                        # Create the INSERT query
                        columns = ", ".join(section.keys())
                        values = ", ".join(["%s"] * len(section))
                        insert_query = f"INSERT INTO postings ({columns}) VALUES ({values});"
                        await cursor.execute(insert_query)

                    await connection.commit()
        except Exception as _ex:
            logging.error(_ex)

    async def get_news(self) -> list[dict, ...]:
        """
        Retrieves news from the table of a paper which you choose.
        Args:
            paper_name (str): The name of the table containing the news to retrieve.
        Returns:
            rows: List of news retrieved from the specified table.
        """

        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    select_query = f'SELECT * FROM postings'
                    await cursor.execute(select_query)
                    rows = await cursor.fetchall()
                    return rows
                
        except Exception as _ex:
            logging.error(_ex)


