from aiogram.fsm.state import StatesGroup, State


class MainSG(StatesGroup):
    menu = State()
    gas_sensors = State()
    pumps = State()


class AuthenSG(StatesGroup):
    passwd = State()
