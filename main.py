import asyncio

from dishka.async_container import make_async_container

from config import settings
from db.repo import init_db
from providers import AioLoggerProvider, DatabaseProvider


async def main():
    container = make_async_container(
        DatabaseProvider(settings.db_name),
        AioLoggerProvider(),
    )
    await init_db(container)


if __name__ == "__main__":
    asyncio.run(main())
