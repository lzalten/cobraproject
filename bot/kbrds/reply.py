from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, WebAppInfo

import config

main_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
          KeyboardButton(text="Играть🥷", web_app=WebAppInfo(url=config.WEBAPP_URL)),
        ],
        [
          KeyboardButton(text="Играть🎰"),
        ],
        [
            KeyboardButton(text="Кабинет💼"),
            KeyboardButton(text="Баланс💵"),
        ],
        [
            KeyboardButton(text="Рефералка👯"),
            KeyboardButton(text="Бонусы🎁"),
        ],
        [
            KeyboardButton(text="Тех.Поддержка👨‍💻"),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите действие'
)

cancel_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отмена❌"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите действие'
)
