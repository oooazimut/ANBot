from datetime import date
from pathlib import Path
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db.models import GasSensor, Pump, User
from db.repo import get_last_gassensors, get_last_pumps
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
    await manager.next()


async def to_uzas_and_pumps(clb: CallbackQuery, button, manager: DialogManager):
    manager.dialog_data["path"] = str(Path("images/uza&pumps.png"))
    session = manager.middleware_data["session"]
    pumps = await get_last_pumps(session)
    draw_uzas_and_pumps(manager.dialog_data["path"], pumps)
    await manager.switch_to(state=MainSG.pumps)


async def to_archive(clb, button: Button, manager: DialogManager):
    manager.dialog_data["archive"] = button.widget_id
    print(button.widget_id)
    await manager.switch_to(MainSG.calendar)


async def on_date(event, widget, manager: DialogManager, date: date):
    session: AsyncSession = manager.middleware_data["session"]
    if "pump" in manager.dialog_data["archive"]:
        pumps = (
            await session.scalars(select(Pump).where(func.date(Pump.timestamp) == date))
        ).all()
    else:
        gs = (
            await session.scalars(
                select(GasSensor).where(func.date(GasSensor.timestamp) == date)
            )
        ).all()
    # await manager.next()
