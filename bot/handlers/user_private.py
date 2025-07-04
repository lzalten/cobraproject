from typing import Union

from aiogram import Router, types, F, Bot
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

import config as config
from database.models import User
from database.orm_query import orm_get_user, get_user_transaction_sums, orm_get_bonus, get_bonus1_deposit, \
    get_bonus2_withdraw, get_games_for_user, get_earned_money_from_referral, get_valid_referrals_count
from kbrds.inline import main_menu_inline, sup_inline, get_bonuses_inline_kb, get_callback_btns, get_inlineMix_btns, \
    games_menu_url
from kbrds.reply import main_markup
from services.chanel_service import is_user_subscribed
from services.others_service import get_percent_by_count_of_referrals
from texts.user_big_texts import get_profile_text, get_games_text, get_ref_text, get_user_balance_text

user_private_router = Router()


async def send_main_menu(message: types.Message):
    await message.answer_sticker(sticker=config.START_STICKER, reply_markup=main_markup)
    await message.answer("Добро пожаловать в казино CobraCash!", reply_markup=main_menu_inline.as_markup())


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    args = message.text.split(" ", 1)
    if len(args) > 1:
        args = args[1]  # Получаем только аргументы после /start
    else:
        args = ""
    user_id = message.from_user.id

    # Проверяем, есть ли пользователь в базе
    user = await orm_get_user(session=session, user_id=user_id)

    if user is None:  # Новый пользователь
        referrer_id = None
        if args.startswith("ref_"):
            str_referrer_id = args.split("_")[1]
            try:
                referrer_id = int(str_referrer_id)
                if referrer_id == user_id:  # Запрещаем приглашать себя
                    raise ValueError
            except ValueError:
                pass

        user = User(
            user_id=user_id,
            referrer_id=referrer_id
        )
        session.add(user)
        await session.commit()

    await send_main_menu(message=message)


@user_private_router.message(F.text == "/ref")
@user_private_router.message(F.text == "Рефералка👯")
async def ref_msg(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    user = await orm_get_user(session=session, user_id=user_id)
    ref_link = f"https://t.me/{config.BOT_NAME}?start=ref_{user_id}"

    # Подсчет количества валидных рефералов
    ref_count = await get_valid_referrals_count(session=session, user_id=user_id)

    # Определение процента вознаграждения
    currrent_percent = get_percent_by_count_of_referrals(ref_count=ref_count)

    # Подсчет заработанных денег с рефералов
    earned_from_ref = await get_earned_money_from_referral(session=session, user_id=user_id)

    text = get_ref_text(ref_count, currrent_percent, earned_from_ref, ref_link)
    await message.answer_photo(photo=config.REF_PHOTO, caption=text)


@user_private_router.message(F.text == "Тех.Поддержка👨‍💻")
async def sup_msg(message: types.Message, session: AsyncSession):
    text = f"🛟<b>Контакты тех.поддержки</b>"
    await message.answer_photo(photo=config.SUP_PHOTO, caption=text, reply_markup=sup_inline.as_markup())


@user_private_router.message(F.text == "/balance")
@user_private_router.message(F.text == "Баланс💵")
async def balance_msg(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    user = await orm_get_user(session=session, user_id=user_id)
    transactions = await get_user_transaction_sums(session=session, user_id=user_id)
    text = get_user_balance_text(user=user, transactions=transactions)
    await message.answer_photo(photo=config.BALANCE_PHOTO, caption=text, reply_markup=main_menu_inline.as_markup())


@user_private_router.message(F.text == "/cabinet")
@user_private_router.message(F.text == "Кабинет")
@user_private_router.message(F.text == "/profile")
@user_private_router.message(F.text == "Кабинет💼")
async def cabinet_msg(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    user = await orm_get_user(session=session, user_id=user_id)
    user_games = await get_games_for_user(session=session, user_id=user_id)
    text = await get_profile_text(user=user, user_games=user_games)
    await message.answer_photo(photo=config.CABINET_PHOTO ,caption=text, reply_markup=main_menu_inline.as_markup())


@user_private_router.message(F.text == "Играть🎰")
async def games_msg(message: types.Message):
    text = get_games_text()
    await message.answer(text, reply_markup=games_menu_url.as_markup())


@user_private_router.callback_query(F.data == "bonuses")
@user_private_router.message(F.text == "Бонусы🎁")
async def bonuses_msg(call_or_message: Union[types.CallbackQuery, types.Message], session: AsyncSession):
    user_id = call_or_message.from_user.id
    user = await orm_get_user(session=session, user_id=user_id)
    text = f'''
Выполняйте задания, получайте бабулет
'''
    reply_markup = await get_bonuses_inline_kb(user_id=user_id, session=session)
    if isinstance(call_or_message, types.CallbackQuery):
        await call_or_message.message.edit_caption(caption=text, reply_markup=reply_markup.as_markup())
    else:
        await call_or_message.answer_photo(photo=config.BONUS_PHOTO, caption=text, reply_markup=reply_markup.as_markup())


@user_private_router.callback_query(F.data.startswith("bonus_"))
async def bonus_call(call: types.CallbackQuery, session: AsyncSession):
    user_id = call.from_user.id
    user = await orm_get_user(session=session, user_id=user_id)
    try:  # валидация номера бонуса
        bonus_number = int(call.data.split("_")[1])
        if bonus_number < 0 or bonus_number > 7:
            raise ValueError
    except ValueError:
        return
    bonus = await orm_get_bonus(session=session, bonus_id=bonus_number)
    if user_id in bonus.users_ids:  # проверка на наличие бонуса у юзера
        return
    if bonus_number == 0:
        if await is_user_subscribed(bot=call.bot, user_id=user_id):
            text = '''
🎉Поздравляем, Вы выполнили задание!

Для получения приза, нажмите кнопку ниже.
'''
            reply_markup = get_callback_btns(btns={"✅ ЗАБРАТЬ ПРИЗ": "getprizefrombonus_0"})

        else:
            if len(call.data.split("_")) > 2 and call.data.split("_")[2] == "check":
                await call.answer("Вы не выполнили задание, попробуйте позже")
                return
            text = '''
❕Для получения бонуса, подпишитесь на канал и нажмите кнопку ниже.
'''
            reply_markup = get_inlineMix_btns(btns={"👁️‍🗨️ПОДПИСАТЬСЯ": f"https://t.me/{config.CHANNEL_USERNAME}",
                                                    "🔍ПРОВЕРИТЬ": "bonus_0_check",
                                                    "🔙 Назад": "bonuses"}, sizes=(1,))
        await call.message.edit_caption(caption=text, reply_markup=reply_markup)
    elif bonus_number == 1:
        if not await get_bonus1_deposit(session=session, user_id=user_id):
            text = '''
❕Для получения бонуса, пополните баланс на сумму от 500р любым удобным для вас способом.
            '''
            reply_markup = get_callback_btns(btns={"💳 Пополнить баланс": "balance_up",
                                                   "🔙 Назад": "bonuses"}, sizes=(1,))
        else:
            text = '''
🎉Поздравляем, Вы выполнили задание!

Для получения приза, нажмите кнопку ниже.
'''
            reply_markup = get_callback_btns(btns={"✅ ЗАБРАТЬ ПРИЗ": "getprizefrombonus_1"})

        await call.message.edit_caption(caption=text, reply_markup=reply_markup)
    elif bonus_number == 2:
        if not await get_bonus2_withdraw(session=session, user_id=user_id):
            text = '''
❕Для получения бонуса, выведите сумму от 1000р.
            '''
            reply_markup = get_callback_btns(btns={"⚡ Вывести деньги": "balance_out",
                                                   "🔙 Назад": "bonuses"}, sizes=(1,))
        else:
            text = '''
🎉Поздравляем, Вы выполнили задание!

Для получения приза, нажмите кнопку ниже.
'''
            reply_markup = get_callback_btns(btns={"✅ ЗАБРАТЬ ПРИЗ": "getprizefrombonus_2"})

        await call.message.edit_caption(caption=text, reply_markup=reply_markup)
    elif bonus_number == 3:
        games_for_month = (await get_games_for_user(session=session, user_id=user_id)).get("month")
        if games_for_month < 500:
            text = f'''
❕Для получения бонуса, вы должны сыграть 500 игр за этот месяц

Сыграно: {games_for_month}/500
            '''
            reply_markup = get_callback_btns(btns={"🔙 Назад": "bonuses"})
        else:
            text = '''
🎉Поздравляем, Вы выполнили задание!

Для получения приза, нажмите кнопку ниже.
'''
            reply_markup = get_callback_btns(btns={"✅ ЗАБРАТЬ ПРИЗ": "getprizefrombonus_3"})

        await call.message.edit_caption(caption=text, reply_markup=reply_markup)
    elif bonus_number == 4:
        games_for_day = (await get_games_for_user(session=session, user_id=user_id)).get("day")
        if games_for_day < 100:
            text = f'''
❕Для получения бонуса, вы должны сыграть 100 игр за этот день

Сыграно: {games_for_day}/100
                    '''
            reply_markup = get_callback_btns(btns={"🔙 Назад": "bonuses"})
        else:
            text = '''
🎉Поздравляем, Вы выполнили задание!

Для получения приза, нажмите кнопку ниже.
        '''
            reply_markup = get_callback_btns(btns={"✅ ЗАБРАТЬ ПРИЗ": "getprizefrombonus_4"})

        await call.message.edit_caption(caption=text, reply_markup=reply_markup)
    elif bonus_number == 5:
        text = '''
🎉Поздравляем, Вы выполнили задание!

Для получения приза, нажмите кнопку ниже.
        '''
        reply_markup = get_callback_btns(btns={"✅ ЗАБРАТЬ ПРИЗ": "getprizefrombonus_5"})

        await call.message.edit_caption(caption=text, reply_markup=reply_markup)


@user_private_router.callback_query(F.data.startswith("getprizefrombonus_"))
async def get_prize_from_bonus_call(call: types.CallbackQuery, session: AsyncSession):
    user_id = call.from_user.id
    user = await orm_get_user(session=session, user_id=user_id)
    try:  # валидация номера бонуса
        bonus_number = int(call.data.split("_")[1])
        if bonus_number < 0 or bonus_number > 7:
            raise ValueError
    except ValueError:
        return
    bonus = await orm_get_bonus(session=session, bonus_id=bonus_number)
    if user_id in bonus.users_ids:  # проверка на наличие бонуса у юзера
        return

    user.balance += bonus.amount
    current_bonus_users = bonus.users_ids
    new_bonus_users = current_bonus_users + [user_id]
    bonus.users_ids = new_bonus_users
    await session.commit()

    await call.message.answer(f"💰Вы получили бонус в размере {bonus.amount}₽")
    await call.message.delete()


@user_private_router.message(F.text == '/deposite')
async def get_deposite(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    user = await orm_get_user(session=session, user_id=user_id)
    user.balance += 1000
    await session.commit()
    await message.answer(f"💰Вы получили 1000₽")



@user_private_router.message(F.content_type == types.ContentType.PHOTO)
async def get_file_id(message: types.Message):
    file_id = message.photo[-1].file_id  # Берем фото в наивысшем разрешении
    print(f"File ID: {file_id}")
    await message.answer(f"Вот ваш file_id:\n`{file_id}`", parse_mode="Markdown")