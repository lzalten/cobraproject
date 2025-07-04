import random
from select import select

from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import SingleGame, User, MinesGame
from kbrds.inline import get_field_btns
from texts.game_texts import get_dice_game_text, update_dice_game_text, get_mines_text


async def validate_game(user, message):
    try:
        message.text.split()[1]
    except IndexError:
        return "Недостаточно параметров"
    if message.text.split()[0] in ["/dice", "/bdice", "/куб", "/бкуб", "/mines", "/мины"]:
        game_amount_str = message.text.split()[2]
    else:
        game_amount_str = message.text.split()[1]
    if message.text.split()[0] in ["/dice", "/bdice", "/куб", "/бкуб", "/mines", "/мины"] and len(message.text.split()) < 3 or len(message.text.split()) < 2:
        return "Недостаточно параметров"
    try:
        game_amount = float(game_amount_str)
    except ValueError:
        return "Введите валидное число"
    if game_amount > user.balance:
        return "Недостаточно средств"
    if message.text.split()[0] in ["/dice", "/bdice", "/куб", "/бкуб"]:
        try:
            dice_number = int(message.text.split()[1])
            if dice_number < 1 or dice_number > 6:
                raise ValueError
        except ValueError:
            return "Введите валидное число"
    if message.text.split()[0] in ["/mines", "/мины", "/mins"]:
        try:
            game_value = int(message.text.split()[1])
            if game_value < 1 or game_value > 24:
                raise ValueError
        except ValueError:
            return "Введите валидное число"
    return None


async def solo_game_creator(user, message, session):
    game_command = message.text.split()[0]
    game_amount = float(message.text.split()[1])
    game_value = int(message.text.split()[2]) if len(message.text.split()) == 3 else None
    user.balance -= game_amount
    game = SingleGame(
        user_id=user.user_id,
        amount=game_amount,
        game_type=game_command[1:],
        game_value=game_value,
        message_id=message.message_id,
    )
    session.add(game)
    if game_command in ["/dice", "/bdice", "/куб", "/бкуб", "/less", "/bless", "/more", "/bmore", "/меньше", "/бменьше", "/больше", "/ббольше"]:
        text = get_dice_game_text(game, game_value)
        game_message = await message.answer(text=text)
        game.message_id = game_message.message_id
    await session.commit()
    if message.text[1] in ["b", "б"]:
        dice = await game_message.reply_dice(emoji="🎲")
        await solo_game_doing(user, game, dice, session)


async def solo_game_doing(user: User, game: SingleGame, message: types.Message, session: AsyncSession):
    dice_value = message.dice.value
    original_text = message.reply_to_message.text
    if game.game_type in ["dice", "bdice", "куб", "бкуб"]:
        if dice_value == int(game.game_value):
            win_amount = game.amount*6
            user.balance += win_amount
            text = update_dice_game_text(original_text, True, win_amount)
            game.status = "WON"
        else:
            text = update_dice_game_text(original_text, False, game.amount)
            game.status = "LOST"
    elif game.game_type in ["less", "bless", "меньше", "бменьше"]:
        if dice_value < 3:
            win_amount = game.amount*2
            user.balance += win_amount
            text = update_dice_game_text(original_text, True, win_amount)
            game.status = "WON"
        else:
            text = update_dice_game_text(original_text, False, game.amount)
            game.status = "LOST"
    elif game.game_type in ["more", "bmore", "больше", "ббольше"]:
        if dice_value > 3:
            win_amount = game.amount*2
            user.balance += win_amount
            text = update_dice_game_text(original_text, True, win_amount)
            game.status = "WON"
        else:
            text = update_dice_game_text(original_text, False, game.amount)
            game.status = "LOST"
    await message.reply_to_message.edit_text(text=text)
    session.add(game)
    session.add(user)
    await session.commit()


# MINES
mines_chanses = {
    '2': [1.05, 1.15, 1.26, 1.39, 1.53, 1.7, 1.9, 2.14, 2.42, 2.77, 3.2, 3.73, 4.41, 5.29, 6.47, 8.08, 10.39, 13.86, 19.4, 29.1, 48.5, 97, 200],
    '3': [1.08, 1.24, 1.42, 1.63, 1.94, 2.28, 2.69, 3.22, 3.93, 4.85, 6.08, 7.75, 10.10, 13.12, 15.40, 22.03, 29.05, 47.98, 65.98, 93.33, 236.56, 540],
    '4': [1.15, 1.39, 1.68, 2.05, 2.53, 3.17, 4.01, 5.16, 6.74, 8.99, 11, 15, 20, 30, 45, 70, 100, 150, 300, 700, 1000],
    '5': [1.21, 1.53, 1.96, 2.53, 3.32, 4.43, 5.89, 7.65, 9.4, 13.6, 18.54, 34.09, 45.12, 67.09, 93.51, 122.02, 234.29, 545, 5590, 12940],
    '6': [1.25, 1.5, 2, 3, 4, 6, 9, 13, 18, 30, 50, 100, 150, 300, 450, 900, 1500, 3000, 10000],
    '7': [1.35, 1.9, 2.53, 3.01, 5.01, 7.25, 14.65, 23.98, 34.76, 46.46, 67.86, 90.72, 145.74, 1010, 1597, 3450, 4588, 15000],
    '8': [1.43, 2.14, 3.28, 5.16, 8.33, 13.88, 23.98, 40, 50, 100, 250, 350, 1000, 3000, 9000, 14000, 30000],
    '9': [1.51, 2.42, 3.98, 6.74, 11.8, 16.45, 28.76, 56.52, 86.22, 164.94, 190.85, 1300, 3400, 9634, 16790, 34000],
    '10': [1.62, 2.77, 4.9, 8.99, 17.16, 34.32, 72.46, 100, 300, 900, 1500, 3000, 7000, 15000, 48888],
    '11': [1.73, 3.2, 6.13, 12.26, 25.74, 35.2, 79.86, 123.09, 345, 950, 1605, 3405, 7800, 17695],
    '12': [1.86, 3.73, 7.8, 17.16, 40.04, 100.11, 271.72, 815.17, 2770, 1190, 5540, 9940, 18000],
    '13': [2.02, 4.41, 10.14, 24.79, 55.07, 125.92, 331.74, 891, 2980, 12005, 14050, 18950],
    '14': [2, 5, 10, 20, 55.55, 111.20, 166.78, 998.4, 1988.3, 3767.45, 10000],
    '15': [2.42, 6.47, 18.59, 58.43, 135.51, 295.03, 1503, 2503, 3534, 5607],
    '16': [2.69, 8.08, 26.56, 97.38, 409.02, 2050, 12950, 15600, 45000],
    '17': [3.03, 10.39, 39.84, 145.29, 554.29, 3530, 7689, 16670],
    '18': [3.46, 13.86, 63.74, 350.58, 2450, 24540, 35000],
    '19': [4.04, 19.4, 111.55, 818.03, 8590, 14000],
    '20': [4.85, 29.1, 223.1, 2450, 7000],
    '21': [6.06, 48.5, 557.75, 12270],
    '22': [8.08, 97, 2230],
    '23': [12.13, 291],
    '24': [24.25]
}

def generate_random_numbers(count):
    random_numbers = random.sample(range(1, 26), count)
    return random_numbers


async def solo_mines_creator(user: User, message: types.Message, session: AsyncSession):
    msg_args = message.text.split()
    if msg_args[-1] == 'all' or msg_args[-1] == 'алын':
        price = int(user.balance)
    else:
        price = int(msg_args[-1])
    count_mins = int(msg_args[-2])
    current_hod = -1
    next_hod_x = mines_chanses[f'{count_mins}'][current_hod + 1]
    mins_array = generate_random_numbers(count_mins)
    current_prize = int(price * 0.9)
    if user.balance < price:
        await message.answer(text='''🚫 Недостаточно средств!''')
        return
    user.balance = user.balance - price
    session.add(user)
    mines_game = MinesGame(
        user_id=user.user_id,
        amount=price,
        game_type="mines",
        message_id=message.message_id,
        mines_array=mins_array,
        clicked_array=[],
        current_prize=current_prize,
    )
    session.add(mines_game)
    await session.commit()
    text = get_mines_text(user.user_id, price, count_mins, next_hod_x)
    reply_markup = get_field_btns(clicked_btns_array=[], game=mines_game)
    await message.answer(text=text, reply_markup=reply_markup)


async def solo_mines_click(kletka: int, mins: MinesGame, callback: types.CallbackQuery, session: AsyncSession):
    clicked_btns = mins.clicked_array + [kletka]
    if kletka in mins.mines_array:
        mins.clicked_array = mins.clicked_array + [kletka]
        mins.status = "LOSE"
        text = get_mines_text(callback.from_user.id, mins.amount, len(mins.mines_array), 0, "LOSE")
        await callback.bot.edit_message_text(chat_id=callback.message.chat.id,
                                             message_id=callback.message.message_id, text=text,
                                             reply_markup=get_field_btns(clicked_btns, game=mins))
    else:
        mins.clicked_array = clicked_btns
        mins.current_prize = int(mines_chanses[f'{len(mins.mines_array)}'][len(clicked_btns)-1] * mins.amount)
        if 25 - len(mins.mines_array) == len(clicked_btns):
            mins.status = "WON"
            query = select(User).where(User.user_id == callback.from_user.id)
            result = await session.execute(query)
            user = result.scalar()
            user.balance = user.balance + mins.current_prize
            session.add(user)
            text = get_mines_text(callback.from_user.id, mins.amount, len(mins.mines_array), "WIN")
            await callback.bot.edit_message_text(chat_id=callback.message.chat.id,
                                                 message_id=callback.message.message_id, text=text,
                                                 reply_markup=get_field_btns(clicked_btns, game=mins))
        else:
            next_hod_x = mines_chanses[f'{len(mins.mines_array)}'][len(mins.clicked_array)]
            text = text = get_mines_text(callback.from_user.id, mins.amount, len(mins.mines_array), next_hod_x)
            await callback.bot.edit_message_text(chat_id=callback.message.chat.id,
                                                 message_id=callback.message.message_id, text=text,
                                                 reply_markup=get_field_btns(clicked_btns, game=mins))

    session.add(mins)
    await session.commit()


async def validate_mines_click(mins: MinesGame, user_id: int, kletka: int):
    if mins is None or mins.status == "LOSE" or mins.status == "WON" or kletka in mins.clicked_array:
        return "huy"