from pathlib import Path
from typing import AsyncIterable

import aiosqlite
from aiologger import Logger
from aiologger.levels import LogLevel
from aiologger.logger import Formatter
from dishka.entities.component import Component
from dishka.entities.scope import BaseScope, Scope
from dishka.provider import Provider, provide

from config import settings


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


class DatabaseProvider(Provider):
    def __init__(
        self,
        db_path: str,
        scope: BaseScope | None = None,
        component: Component | None = None,
    ):
        super().__init__(scope, component)
        self.db_path = db_path

    @provide(scope=Scope.REQUEST)
    async def get_connection(self) -> AsyncIterable[aiosqlite.Connection]:
        conn = await aiosqlite.connect(Path(self.db_path))
        conn.row_factory = dict_factory
        try:
            yield conn
        finally:
            await conn.close()


class AioLoggerProvider(Provider):
    # def __init__(self, name: str = "bot"):
    #     self.name = name

    @provide(scope=Scope.APP)
    async def get_logger(self) -> AsyncIterable[Logger]:
        logger = Logger.with_default_handlers(
            name="bot",
            level=LogLevel.INFO,
            formatter=Formatter("%(asctime)s %(levelname)s %(message)s"),
        )
        try:
            yield logger
        finally:
            await logger.shutdown()
