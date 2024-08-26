import asyncio
from otodom import parse_otodom

import asyncio
from otodom import parse_otodom


async def main():
    while True:
        await asyncio.gather(asyncio.create_task(parse_otodom()))
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())