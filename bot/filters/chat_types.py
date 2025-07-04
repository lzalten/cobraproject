import os

from aiogram import Bot, types
from aiogram.filters import Filter

import config as config


class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message:types.Message) -> bool:
        return message.chat.type in self.chat_types


class IsAdmin(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        return message.from_user.id == config.ADMIN_ID


class IsAdminCallback(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, callback: types.CallbackQuery, bot: Bot) -> bool:
        return callback.from_user.id == config.ADMIN_ID


