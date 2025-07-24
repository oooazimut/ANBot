from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Start, SwitchTo
from aiogram_dialog.widgets.text import Const
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from dialogs.handlers import right_passwd, wrong_passwd, check_passwd
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
        state=AuthenSG.passwd
    )
)

main_d = Dialog(
    Window(
        SwitchTo(Const("Датчики газа")),
        SwitchTo(Const("УЗА, насосы")),
        SwitchTo(""),
        state=,
    ),

)
