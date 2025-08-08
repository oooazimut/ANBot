import logging
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, sessionmaker

from db.models import GasSensor, Pump
from service.modbus import poll_registers

logger = logging.getLogger(__name__)


async def save_data(db_pool: sessionmaker):
    data = await poll_registers()
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
