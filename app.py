# app.py
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
import logging

from handlers import start_handler, game_handler, profile_handler
from db import init_db
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

async def main():
    # DB init
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Register handlers (each module will attach to dp inside)
    start_handler.register(dp)
    game_handler.register(dp)
    profile_handler.register(dp)

    # Optional: set bot commands
    await bot.set_my_commands([
        BotCommand(command="start", description="Boshlash"),
    ])

    try:
        print("Bot ishga tushmoqda...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
