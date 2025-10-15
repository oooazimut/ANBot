from typing import List, Sequence

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.orm import sessionmaker

from config import Alerts
from db.repo import get_all_userIDs


async def send_message(bot: Bot, userIDs: Sequence[int], txt: str):
    for uid in userIDs:
        try:
            await bot.send_message(chat_id=uid, text=txt)
        except TelegramBadRequest:
            pass


async def handle_alerts(
    bot: Bot, db_pool: sessionmaker, alerts: list[tuple[str, dict]]
):
    with db_pool() as session:
        user_ids = await get_all_userIDs(session)

    for altype, al in alerts:
        match altype:
            case Alerts.GAS:
                txt = f"Датчик газа {al['name']}: концентрация {al['value']} %!"
            case Alerts.TANK:
                txt = f"Переполнение ёмкости {al['num']}!"
            case Alerts.BYPASS:
                txt = f"Насос {al['pump']} работает в обход УЗА!"
        await send_message(bot, user_ids, txt)


def combine_text(tankFlags: List[int]):
    txt = "Информация по дренажным ёмкостям: \n\n"
    for num, tank in enumerate(tankFlags, start=1):
        txt += f"Ёмкость {num}: {'полная!' if tank else 'норма.'}\n"
    return txt


async def morning_message(bot: Bot, db_pool: sessionmaker):
    import service.modbus as mb

    async with db_pool() as session:
        user_ids = await get_all_userIDs(session)

    if mb.isConnected:
        txt = combine_text(mb.Tanks)
    else:
        txt = "нет связи со щитом управления!"

    await send_message(bot, user_ids, txt)
