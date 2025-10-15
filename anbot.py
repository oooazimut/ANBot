import asyncio
import logging

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import ErrorEvent
from aiogram_dialog import DialogManager, StartMode, setup_dialogs
from aiogram_dialog.api.exceptions import OutdatedIntent, UnknownIntent
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import settings
from custom.media_storage import MediaIdStorage
from db.repo import remove_old_data, save_data
from dialogs.dialogs import start_router, authen_d, main_d
from dialogs.states import MainSG
from middlewares import DbSessionMiddleware
from service.message import morning_message


async def ui_error_handler(event: ErrorEvent, dialog_manager: DialogManager):
    logging.warning("Сброс ошибки")
    await dialog_manager.start(MainSG.menu, mode=StartMode.RESET_STACK)


async def main():
    logging.basicConfig(
        level=logging.WARNING, format="%(asctime)s %(levelname)s %(message)s"
    )
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    engine = create_async_engine(settings.sqlite_async_dsn, echo=False)
    db_pool = async_sessionmaker(engine, expire_on_commit=False)
    bot = Bot(
        token=settings.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        save_data,
        trigger="interval",
        seconds=5,
        id="polling",
        args=[db_pool, bot],
        replace_existing=True,
    )
    scheduler.add_job(
        morning_message,
        trigger="cron",
        day_of_week="mon-fri",
        hour=9,
        id="morn_mail",
        args=[bot, db_pool],
        replace_existing=True,
    )
    scheduler.add_job(
        remove_old_data,
        trigger="cron",
        day=1,
        id="rmv_old",
        replace_existing=True,
    )
    scheduler.start()
    storage = RedisStorage(
        Redis(), key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True)
    )
    dp = Dispatcher(storage=storage)
    dp.include_routers(start_router, authen_d, main_d)
    setup_dialogs(dp, media_id_storage=MediaIdStorage())
    dp.update.outer_middleware(DbSessionMiddleware(db_pool))
    dp.errors.register(
        ui_error_handler,
        ExceptionTypeFilter(UnknownIntent, OutdatedIntent),
    )
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
