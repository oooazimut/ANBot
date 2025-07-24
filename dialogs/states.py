from aiogram.fsm.state import StatesGroup, State


class MainSG(StatesGroup):
    menu = State()


class AuthenSG(StatesGroup):
    passwd = State()
