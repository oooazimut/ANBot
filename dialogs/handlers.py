from datetime import date
from pathlib import Path
from typing import Callable, Sequence, Type

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
from service.plot import plot_gs, plot_pumps


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


def check_connection() -> bool:
    import service.modbus as mb

    return mb.isConnected


def reset_sensors_values(sensors: Sequence[GasSensor]) -> None:
    for sensor in sensors:
        sensor.value = -999


async def to_gas_rooms(clb: CallbackQuery, button, manager: DialogManager):
    session: AsyncSession = manager.middleware_data["session"]
    sensors = await get_last_gassensors(session)

    if not check_connection():
        reset_sensors_values(sensors)

    draw_gassensors(sensors)
    await manager.next()


def reset_pump_metrics(pumps: Sequence[Pump]):
    for pump in pumps:
        pump.pressure = -999
        pump.temperature = -999
        pump.work = -999


async def to_uzas_and_pumps(clb: CallbackQuery, button, manager: DialogManager):
    manager.dialog_data["path"] = str(Path("images/uza&pumps.png"))
    session = manager.middleware_data["session"]
    pumps = await get_last_pumps(session)

    if not check_connection():
        reset_pump_metrics(pumps)

    draw_uzas_and_pumps(manager.dialog_data["path"], pumps)
    await manager.switch_to(state=MainSG.pumps)


async def to_archive(clb, button: Button, manager: DialogManager):
    manager.dialog_data["archive"] = button.widget_id
    await manager.switch_to(MainSG.calendar)


async def on_date(event: CallbackQuery, widget, manager: DialogManager, date: date):
    await manager.find("archive_scroll").set_page(0)

    async def get_and_plot(
        session: AsyncSession, m: Type, date, plot_f: Callable
    ) -> bool:
        r = (
            await session.scalars(select(m).where(func.date(m.timestamp) == date))
        ).all()
        if not r:
            return False
        plot_f(r)
        return True

    session: AsyncSession = manager.middleware_data["session"]
    data_map = [("pump", Pump, plot_pumps), ("gs", GasSensor, plot_gs)]

    for key, model, fnc in data_map:
        if key in manager.dialog_data["archive"]:
            has_data = await get_and_plot(session, model, date, fnc)
            if not has_data:
                await event.answer("Данных нет", show_alert=True)
                return
            await manager.next()
            return
