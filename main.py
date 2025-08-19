import asyncio
import sys

from dishka.async_container import make_async_container

from db.repo import init_db
from providers import AioLoggerProvider, DatabaseProvider
from config import settings


async def main():
    container = make_async_container(
        DatabaseProvider(settings.db_name),
        AioLoggerProvider(),
    )
    await init_db(container)
    print("all_good")
    # try:
    #     pass
    # finally:
    #     await container.close()


if __name__ == "__main__":
    asyncio.run(main())
