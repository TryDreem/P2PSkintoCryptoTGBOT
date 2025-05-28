import asyncio
from config import bot
from services.tasks import clean_up_codes
from aiogram.types import BotCommand
from aiogram import Dispatcher

from handlers import start, profile, deals, history, disputes, guide, policy


async def main():
    """Bot initialization and startup"""
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(deals.router)
    dp.include_router(history.router)
    dp.include_router(disputes.router)
    dp.include_router(guide.router)
    dp.include_router(policy.router)

    await bot.set_my_commands([
        BotCommand(command='start', description="Start")
    ])
    asyncio.create_task(clean_up_codes()) # Background task for expired deals
    await dp.start_polling(bot)


asyncio.run(main())