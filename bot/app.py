import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import config
from database.orm_query import create_bonus_objects_from_0_to_7
from handlers.admin_private import admin_router
from handlers.game_private import game_private_router
from handlers.user_private import user_private_router
from middlewares.db import DataBaseSession

from database.engine import create_db, session_maker, drop_db, reset_db

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

dp.include_router(admin_router)
dp.include_router(user_private_router)
dp.include_router(game_private_router)


async def on_startup():
    # await drop_db()
    #await reset_db()
    await create_db()
    async with session_maker() as session:
        await create_bonus_objects_from_0_to_7(session)


async def on_shutdown():
    print('bot leg')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    # await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot)


asyncio.run(main())
