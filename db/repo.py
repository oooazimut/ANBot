import sqlite3 as sq
from datetime import date, timedelta
import logging
from typing import Sequence

from aiogram import Bot
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, sessionmaker

from config import settings
from db.models import GasSensor, Pump, User
from service.modbus import poll_registers

logger = logging.getLogger(__name__)


async def save_data(db_pool: sessionmaker, bot: Bot):
    data = await poll_registers(bot, db_pool)
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


async def get_last_gassensors(session: AsyncSession) -> Sequence[GasSensor]:
    substmt = (
        select(GasSensor.name, func.max(GasSensor.timestamp).label("max_ts"))
        .group_by(GasSensor.name)
        .subquery()
    )
    GS = aliased(GasSensor)

    stmt = select(GS).join(
        substmt, (GS.name == substmt.c.name) & (GS.timestamp == substmt.c.max_ts)
    )

    return (await session.scalars(stmt)).all()


async def get_last_pumps(session: AsyncSession) -> Sequence[Pump]:
    subq = (
        select(Pump.name, func.max(Pump.timestamp).label("max_ts"))
        .group_by(Pump.name)
        .subquery()
    )
    P = aliased(Pump)
    stmt = select(P).join(
        subq, (P.name == subq.c.name) & (P.timestamp == subq.c.max_ts)
    )

    return (await session.scalars(stmt)).all()


def remove_old_data():
    tables = [GasSensor.__tablename__, Pump.__tablename__]
    interval = (date.today() - timedelta(days=90)).isoformat()

    with sq.connect(settings.db_name) as conn:
        for t in tables:
            conn.execute(
                f"delete from {t} where DATE(timestamp) < ?",
                [interval],
            )
            print(t, "почищена")
        conn.commit()
        print("Все старые данные удалены")


async def get_all_userIDs(session: AsyncSession):
    return (await session.scalars(select(User.id))).all()
