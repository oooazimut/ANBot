import logging
from pathlib import Path
from typing import List

import aiosqlite
from aiologger import Logger
from dishka.async_container import AsyncContainer

from config import settings
from service.modbus import poll_registers

logger = logging.getLogger(__name__)


async def init_db(container: AsyncContainer):
    async with container() as nc:
        conn = await nc.get(aiosqlite.Connection)
        logger = await nc.get(Logger)
        await logger.info("инициируем бд...")
        with open(Path(settings.db_schema), "r", encoding="utf-8") as f:
            await conn.executescript(f.read())
        await conn.commit()
        await logger.info("бд инициирована")


async def get_userids(container: AsyncContainer) -> List[int]:
    async with container() as nc:
        conn = await nc.get(aiosqlite.Connection)
        cursor = await conn.execute("SELECT id FROM users")
        return [i["id"] for i in await cursor.fetchall()]


async def save_data(container: AsyncContainer, bot: Bot):
    data = await poll_registers(bot, container)
    if not data:
        return

    async with db_pool() as session:
        try:
            for pump in data["pumps"]:
                session.add(Pump(**pump))
            for sensor in data["sensors"]:
                session.add(GasSensor(**sensor))
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка сохранения данных: {e}")


# async def get_last_gassensors(session: AsyncSession) -> Sequence[GasSensor]:
#     substmt = (
#         select(GasSensor.name, func.max(GasSensor.timestamp).label("max_ts"))
#         .group_by(GasSensor.name)
#         .subquery()
#     )
#     GS = aliased(GasSensor)

#     stmt = select(GS).join(
#         substmt, (GS.name == substmt.c.name) & (GS.timestamp == substmt.c.max_ts)
#     )

#     return (await session.scalars(stmt)).all()


# async def get_last_pumps(session: AsyncSession) -> Sequence[Pump]:
#     subq = (
#         select(Pump.name, func.max(Pump.timestamp).label("max_ts"))
#         .group_by(Pump.name)
#         .subquery()
#     )
#     P = aliased(Pump)
#     stmt = select(P).join(
#         subq, (P.name == subq.c.name) & (P.timestamp == subq.c.max_ts)
#     )

#     return (await session.scalars(stmt)).all()


# def remove_old_data():
#     tables = [GasSensor.__tablename__, Pump.__tablename__]
#     interval = (date.today() - timedelta(days=90)).isoformat()

#     with sq.connect(settings.db_name) as conn:
#         for t in tables:
#             conn.execute(
#                 f"delete from {t} where DATE(timestamp) < ?",
#                 [interval],
#             )
#             print(t, "почищена")
#         conn.commit()
#         print("Все старые данные удалены")
