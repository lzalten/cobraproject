import re

from aiogram import Router, types, F
from aiogram.types import Dice
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.orm_query import orm_get_user, get_game_by_message_id, orm_get_active_mines_game_for_user, \
    orm_get_mines_game_by_id
from kbrds.inline import get_field_btns
from services.game_service import validate_game, solo_game_creator, solo_game_doing, solo_mines_creator, \
    validate_mines_click, solo_mines_click
from texts.game_texts import get_mines_text

game_private_router = Router()


@game_private_router.message(F.text.startswith("/less"))
@game_private_router.message(F.text.startswith("/more"))
@game_private_router.message(F.text.startswith("/dice"))
@game_private_router.message(F.text.startswith("/orel"))
@game_private_router.message(F.text.startswith("/reshka"))
@game_private_router.message(F.text.startswith("/slots"))
@game_private_router.message(F.text.startswith("/roulette"))
@game_private_router.message(F.text.startswith("/больше"))
@game_private_router.message(F.text.startswith("/меньше"))
@game_private_router.message(F.text.startswith("/куб"))
@game_private_router.message(F.text.startswith("/орел"))
@game_private_router.message(F.text.startswith("/решка"))
@game_private_router.message(F.text.startswith("/слоты"))
@game_private_router.message(F.text.startswith("/рулетка"))
@game_private_router.message(F.text.startswith("/bless"))
@game_private_router.message(F.text.startswith("/bmore"))
@game_private_router.message(F.text.startswith("/bdice"))
@game_private_router.message(F.text.startswith("/borel"))
@game_private_router.message(F.text.startswith("/breshka"))
@game_private_router.message(F.text.startswith("/ббольше"))
@game_private_router.message(F.text.startswith("/бменьше"))
@game_private_router.message(F.text.startswith("/бкуб"))
@game_private_router.message(F.text.startswith("/борел"))
@game_private_router.message(F.text.startswith("/брешка"))
async def game_start_msg(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    user = await orm_get_user(session=session, user_id=user_id)
    validation_text = await validate_game(user, message)
    if validation_text:
        await message.answer(text=validation_text)
        return
    await solo_game_creator(user=user, message=message, session=session)


@game_private_router.message(F.dice & F.reply_to_message)
async def dice_msg(message: types.Message, session: AsyncSession):
    message_id = message.reply_to_message.message_id
    game = await get_game_by_message_id(session=session, message_id=message_id)
    if game is None:
        await message.answer(text="Сообщение не является игрой")
        return
    if game.user_id != message.from_user.id:
        await message.answer(text="Это не твоя игра")
        return
    if game.status != "CREATED":
        await message.answer(text="Игра уже сыграна")
        return
    user = await orm_get_user(session=session, user_id=game.user_id)
    await solo_game_doing(user, game, message, session)


# MINES
@game_private_router.message(F.text.startswith("/мины"))
@game_private_router.message(F.text.startswith("/mins"))
@game_private_router.message(F.text.startswith("/mines"))
async def mines_msg(message: types.Message, session: AsyncSession):
    user = await orm_get_user(session=session, user_id=message.from_user.id)
    validation_text = await validate_game(user, message)
    if validation_text:
        await message.answer(text=validation_text)
        return
    await solo_mines_creator(user=user, message=message, session=session)


@game_private_router.callback_query(F.data.startswith("mine_"))
async def mine_click(callback: types.CallbackQuery, session: AsyncSession):
    pattern = r"mine_(\d+)_(\d+)"
    match = re.match(pattern, callback.data)

    game_id = int(match.group(1))
    kletka = int(match.group(2))
    mins = await orm_get_mines_game_by_id(mines_id=game_id, session=session)
    validation_text = await validate_mines_click(mins, callback.from_user.id, kletka)
    if validation_text:
        await callback.answer(text=validation_text)
        return
    await solo_mines_click(kletka, mins, callback, session)



@game_private_router.callback_query(F.data.startswith("takeprizemins_"))
async def takeprize_click(callback: types.CallbackQuery, session: AsyncSession):
    pattern = r"takeprizemins_(\d+)"
    match = re.match(pattern, callback.data)
    game_id = int(match.group(1))
    mins = await orm_get_mines_game_by_id(mines_id=game_id, session=session)
    if mins is None or mins.status in ["LOSE", "WON"] or mins.user_id != callback.from_user.id:
        return
    if mins is not None and mins.id == game_id:
        mins.status = "WON"
        session.add(mins)
        user = await orm_get_user(session=session, user_id=callback.from_user.id)
        text = get_mines_text(gamer=callback.from_user.id, price=mins.amount, count_mins=len(mins.mines_array), next_hod_x=0,
                              status="WON", prize=mins.current_prize)
        await callback.bot.edit_message_text(chat_id=callback.message.chat.id,
                                             message_id=callback.message.message_id, text=text,
                                             reply_markup=get_field_btns(mins.clicked_array, game=mins))
        user.balance = user.balance + mins.current_prize
        session.add(user)
    await session.commit()


@game_private_router.message()
async def any_msg(message: types.Message):
    print(message.text)
