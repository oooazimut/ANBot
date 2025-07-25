from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import GasSensor


def get_last_gassensors(session: AsyncSession) -> List[GasSensor]:
    pass
