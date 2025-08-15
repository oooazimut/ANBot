from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from db.models import User
from config import Alerts


async def send_message(bot: Bot, db_pool: sessionmaker, txt: str):
    async with db_pool() as session:
        userids = (await session.scalars(select(User.id))).all()
        for uid in userids:
            try:
                await bot.send_message(chat_id=uid, text=txt)
            except TelegramBadRequest:
                pass


async def handle_alerts(
    bot: Bot, db_pool: sessionmaker, alerts: list[tuple[str, dict]]
):
    for altype, al in alerts:
        match altype:
            case Alerts.GAS:
                txt = f"Датчик газа {al['name']}: концентрация {al['value']} %!"
            case Alerts.TANK:
                txt = f"Переполнение ёмкости {al['num']}!"
            case Alerts.BYPASS:
                txt = f"Насос {al['pump']} работает в обход УЗА!"
        await send_message(bot, db_pool, txt)


async def morning_message(bot: Bot, db_pool: sessionmaker):
    import service.modbus as mb

    txt = "Информация по дренажным ёмкостям: \n\n"
    for num, tank in enumerate(mb.Tanks, start=1):
        txt += f"Ёмкость {num}: {'полная!' if tank else 'норма.'}\n"
    await send_message(bot, db_pool, txt)
