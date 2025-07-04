from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

import config as config
from database.orm_query import get_used_bonuses_for_user


def get_callback_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (3,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


def get_url_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (3,)):
    keyboard = InlineKeyboardBuilder()

    for text, url in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, url=url))

    return keyboard.adjust(*sizes).as_markup()


# Создать микс из CallBack и URL кнопок
def get_inlineMix_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (3,)):
    keyboard = InlineKeyboardBuilder()

    for text, value in btns.items():
        if '://' in value:
            keyboard.add(InlineKeyboardButton(text=text, url=value))
        else:
            keyboard.add(InlineKeyboardButton(text=text, callback_data=value))

    return keyboard.adjust(*sizes).as_markup()


info_btn_kb = InlineKeyboardBuilder()
info_btn_kb.add(InlineKeyboardButton(text="👨‍💻Тех.Поддержка", url="https://t.me/punchmade_support"))
info_btn_kb.add(InlineKeyboardButton(text="📕Правила", callback_data="rules"))
info_btn_kb.add(InlineKeyboardButton(text="⚙️Наши проекты", url='https://t.me/punchmadeprojects'))
info_btn_kb.adjust(1)


main_menu_inline = InlineKeyboardBuilder()
main_menu_inline.add(InlineKeyboardButton(text="💳 Пополнить баланс", callback_data="balance_up"))
main_menu_inline.add(InlineKeyboardButton(text="⚡ Вывести деньги", callback_data="balance_out"))
main_menu_inline.add(InlineKeyboardButton(text="👨‍💻Тех.Поддержка", url=config.SUP_URL))
main_menu_inline.adjust(2, 1)


games_menu_url = InlineKeyboardBuilder()
games_menu_url.add(InlineKeyboardButton(text="💳 Пополнить баланс", callback_data="balance_up"))
games_menu_url.add(InlineKeyboardButton(text="⚡ Вывести деньги", callback_data="balance_out"))
games_menu_url.add(InlineKeyboardButton(text="🎮Игры", web_app=WebAppInfo(url=config.WEBAPP_URL)))
games_menu_url.adjust(2, 1)


sup_inline = InlineKeyboardBuilder()
sup_inline.add(InlineKeyboardButton(text="💳ПОПОЛНЕНИЯ/ВЫВОДЫ", url=config.SUP_MONEY))
sup_inline.add(InlineKeyboardButton(text="❗ОШИБКИ/БАГИ", url=config.SUP_ERROR))
sup_inline.add(InlineKeyboardButton(text="📝ПРЕДЛОЖЕНИЯ", url=config.SUP_REPORT))
sup_inline.add(InlineKeyboardButton(text="💼 СОТРУДНИЧЕСТВО", url=config.SUP_URL))
sup_inline.adjust(1)


async def get_bonuses_inline_kb(user_id: int, session: AsyncSession):
    bonuses_inline = InlineKeyboardBuilder()
    used_bonuses_for_user = await get_used_bonuses_for_user(session=session, user_id=user_id)
    if 0 not in used_bonuses_for_user:
        bonuses_inline.add(InlineKeyboardButton(text="📢ПОДПИСАТЬСЯ НА КАНАЛ С НОВОСТЯМИ [10р]", callback_data="bonus_0"))
    if 1 not in used_bonuses_for_user:
        bonuses_inline.add(InlineKeyboardButton(text="💰ПОПОЛНИТЬ БАЛАНС НА 500р ОДНИМ ПЛАТЕЖОМ [20р]", callback_data="bonus_1"))
    if 2 not in used_bonuses_for_user:
        bonuses_inline.add(InlineKeyboardButton(text="⚡💰ВЫВЕСТИ 1000р ОДНИМ ПЛАТЕЖОМ [20р]", callback_data="bonus_2"))
    if 3 not in used_bonuses_for_user:
        bonuses_inline.add(InlineKeyboardButton(text="🔃[МЕС]СЫГРАТЬ 500 ИГР [50р]", callback_data="bonus_3"))
    if 4 not in used_bonuses_for_user:
        bonuses_inline.add(InlineKeyboardButton(text="🔃[ДЕНЬ]СЫГРАТЬ 100 ИГР [10р]", callback_data="bonus_4"))
    if 5 not in used_bonuses_for_user:
        bonuses_inline.add(InlineKeyboardButton(text="🔃[ДЕНЬ]СЫГРАТЬ СТАВКУ ALL-IN [5р]", callback_data="bonus_5"))
    if 6 not in used_bonuses_for_user:
        bonuses_inline.add(InlineKeyboardButton(text="🔃[ДЕНЬ]ВЫИГРАТЬ ПОЛЕ С 24 МИНАМИ [20р]", callback_data="bonus_6"))
    if 7 not in used_bonuses_for_user:
        bonuses_inline.add(InlineKeyboardButton(text="🪙ЗАКРЫТЬ КРЕСТ НА 10 МИН [2000 руб.]", callback_data="bonus_7"))
    bonuses_inline.adjust(1,)
    return bonuses_inline


# MINES
def get_field_btns(clicked_btns_array, game):
    keyboard = InlineKeyboardBuilder()

    try:
        for i in range(0, 5):
            row = []
            for j in range(1, 6):
                current_btn_number = i * 5 + j
                if current_btn_number in clicked_btns_array:
                    if current_btn_number not in game.mines_array:
                        button = types.InlineKeyboardButton(text="🟩", callback_data=f"minepass_{i * 5 + j}")
                    else:
                        button = types.InlineKeyboardButton(text="💥", callback_data=f"minepass_{i * 5 + j}")
                else:
                    button = types.InlineKeyboardButton(text="ᅠ ᅠ ", callback_data=f"mine_{game.id}_{i * 5 + j}")
                row.append(button)
            keyboard.row(*row)

        if game.status in ["LOSE", "WON"]:
            keyboard = InlineKeyboardBuilder()
            try:
                for i in range(0, 5):
                    row = []
                    for j in range(1, 6):
                        current_btn_number = i * 5 + j
                        if current_btn_number in clicked_btns_array:
                            if current_btn_number not in game.mines_array:
                                button = types.InlineKeyboardButton(text="🟩", callback_data=f"minepass_{i * 5 + j}")
                            else:
                                button = types.InlineKeyboardButton(text="💥", callback_data=f"minepass_{i * 5 + j}")
                        else:
                            if current_btn_number in game.mines_array:
                                button = types.InlineKeyboardButton(text="💢", callback_data=f"minepass_{i * 5 + j}")
                            else:
                                button = types.InlineKeyboardButton(text="ᅠ ᅠ ",
                                                                    callback_data=f"mine_{game.id}_{i * 5 + j}")
                        row.append(button)
                    keyboard.row(*row)
                return keyboard.as_markup()
            except Exception as e:
                print(f"An error occurred: {e}")
                return None

        keyboard.row(
            types.InlineKeyboardButton(
                text=f"Забрать выигрыш {game.current_prize} | x{round(game.current_prize/game.amount, 2)}",
                callback_data=f"takeprizemins_{game.id}"
            )
        )

        return keyboard.as_markup()  # Возвращаем в правильном формате

    except Exception as e:
        print(f"An error occurred: {e}")
        return None