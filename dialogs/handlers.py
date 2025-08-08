from pathlib import Path
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db.models import User
from db.repo import get_last_gassensors
from dialogs.states import MainSG
from service.draw import draw_gassensors, draw_uzas_and_pumps


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
    sensors = await get_last_gassensors(session)
    draw_gassensors(sensors)
    await manager.switch_to(state=MainSG.gas_sensors)


async def to_uzas_and_pumps(clb: CallbackQuery, button, manager: DialogManager):
    manager.dialog_data["path"] = str(Path("images/uza&pumps.png")
    draw_uzas_and_pumps(manager.dialog_data["path"])
    await manager.switch_to(state=MainSG.pumps)
