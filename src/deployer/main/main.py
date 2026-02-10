import asyncio
import logging
import os
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs
from dishka.integrations.aiogram import setup_dishka

from deployer.database.mapper import start_db_mapping
from deployer.main.providers.build import build_container
from deployer.presentators.tg import (
    deployment_router,
    entry_router,
    error_router,
    project_router,
    user_router,
)

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='{asctime} - [{levelname}] - {funcName}:{lineno} - {message}',
        style='{',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    logging.getLogger('aiogram').setLevel(logging.ERROR)


def build_dispatcher() -> Dispatcher:
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(entry_router)
    dp.include_router(user_router)
    dp.include_router(project_router)
    dp.include_router(deployment_router)
    dp.include_router(error_router)
    setup_dialogs(dp)
    return dp


async def main() -> None:
    dp = build_dispatcher()
    container = build_container()

    setup_dishka(container=container, router=dp, auto_inject=True)
    start_db_mapping()
    setup_logging()

    bot = Bot(os.environ['BOT_TOKEN'])
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info(f'Bot started {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())
