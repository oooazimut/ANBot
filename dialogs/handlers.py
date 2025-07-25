from datetime import date
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db.models import GasSensor, User
from dialogs.states import MainSG


def check_passwd(passwd: str) -> str:
    if passwd == settings.passwd.get_secret_value():
        return passwd
    raise ValueError


async def right_passwd(
    msg: Message, widget: ManagedTextInput, manager: DialogManager, *args, **kwargs
):
    session: AsyncSession = manager.middleware_data["session"]
    session.add(User(id=msg.from_user.id, name=msg.from_user.full_name))
    await session.commit()
    await manager.start(state=MainSG.menu, mode=StartMode.RESET_STACK)


async def wrong_passwd(msg: Message, *args, **kwargs):
    await msg.answer("Пароль неверный!")


async def to_gas_rooms(clb: CallbackQuery, button, manager: DialogManager):
    session: AsyncSession = manager.middleware_data["session"]
    stmt = select(GasSensor).where(func.date(GasSensor.timestamp) == date.today())
    sensors = await session.scalars(stmt)
    sensors = sensors.all()
