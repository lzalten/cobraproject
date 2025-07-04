from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ChatMemberMember, ChatMemberAdministrator, ChatMemberOwner

import config


async def is_user_subscribed(bot: Bot, user_id: int, channel_username: str = config.CHANNEL_USERNAME) -> bool:
    """
    Проверяет, подписан ли пользователь на канал.
    :param bot: Экземпляр бота
    :param user_id: ID пользователя
    :param channel_username: Юзернейм канала (например, "@my_channel")
    :return: True, если подписан, иначе False
    """
    try:
        chat_member = await bot.get_chat_member(chat_id=config.CHANNEL_ID, user_id=user_id)
        print(chat_member)
        return isinstance(chat_member, (ChatMemberMember, ChatMemberAdministrator, ChatMemberOwner))
    except TelegramBadRequest as e:
        return False