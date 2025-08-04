from datetime import datetime
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

timestamp = Annotated[datetime, mapped_column(default=datetime.now)]
base_id = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[base_id]
    name: Mapped[str]

    def __repr__(self):
        cols = ", ".join(
            f"{k}={getattr(self, k)!r}" for k in self.__mapper__.columns.keys()
        )
        return f"<{self.__class__.__name__}({cols}) > "

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class Pump(Base):
    __tablename__ = "pumps"

    pressure: Mapped[float]
    temperature: Mapped[float] = mapped_column(nullable=True)
    work: Mapped[int]
    enable: Mapped[bool]
    permission: Mapped[bool]
    timestamp: Mapped[timestamp]


class GasSensor(Base):
    __tablename__ = "gas_sensors"

    value: Mapped[float]
    timestamp: Mapped[timestamp]
