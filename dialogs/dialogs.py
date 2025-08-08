from aiogram import Router
from aiogram.enums import ContentType
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Group,
    Next,
    NumberedPager,
    StubScroll,
    SwitchTo,
)
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from dialogs import getters
from dialogs.handlers import (
    check_passwd,
    right_passwd,
    to_gas_rooms,
    to_uzas_and_pumps,
    wrong_passwd,
)
from dialogs.states import AuthenSG, MainSG

start_router = Router()


@start_router.message(CommandStart())
async def bot_starter(msg: Message, dialog_manager: DialogManager):
    session: AsyncSession = dialog_manager.middleware_data["session"]
    user = await session.get(User, msg.from_user.id)
    await dialog_manager.start(
        state=MainSG.menu if user else AuthenSG.passwd, mode=StartMode.RESET_STACK
    )


authen_d = Dialog(
    Window(
        Const("Введите пароль"),
        TextInput(
            id="passwd_input",
            type_factory=check_passwd,
            on_success=right_passwd,
            on_error=wrong_passwd,
        ),
        state=AuthenSG.passwd,
    )
)

main_d = Dialog(
    Window(
        Const("Главное меню"),
        Button(Const("Датчики газа"), id="to_gas_rooms", on_click=to_gas_rooms),
        Button(Const("УЗА, насосы"), id="to_uza_pumps", on_click=to_uzas_and_pumps),
        # SwitchTo(""),
        state=MainSG.menu,
    ),
    Window(
        Const("Текущие показания датчиков газа:"),
        Format("{room}"),
        StaticMedia(path=Format("{path}"), type=ContentType.PHOTO),
        StubScroll(id="gs_rooms_scroll", pages="pages"),
        Group(NumberedPager(scroll="gs_rooms_scroll"), width=8),
        Button(Const("Архив"), id="to_gas_archive"),
        Back(Const("Назад")),
        state=MainSG.gas_sensors,
        getter=getters.gas_rooms_getter,
    ),
    Window(
        Const("УЗА, насосы"),
        StaticMedia(path=Format("{dialog_data[path]}"), type=ContentType.PHOTO),
        Button(Const("Архив насосов"), id="to_pumps_archive"),
        SwitchTo(Const("Назад"), id="to_main_menu", state=MainSG.menu),
        state=MainSG.pumps,
    ),
)
