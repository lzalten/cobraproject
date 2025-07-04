#
# import asyncio
# import re
#
# import aiofiles
# import zipfile
# import os
# import random
# import string
# import subprocess
# import time
# from datetime import datetime
#
# from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
#
# from aiogram import types, Router, F
# from aiogram.filters import CommandStart, Command, or_f, StateFilter
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import StatesGroup, State
# from aiogram.types import Message
# from aiogram.utils.keyboard import InlineKeyboardBuilder
# from bs4 import BeautifulSoup
# from dotenv import find_dotenv, load_dotenv
# from sqlalchemy.ext.asyncio import AsyncSession
#
#
# import config
# from common.chat_text import get_category_text
# from database.models import User, Purchase, Sms, Country
# from database.orm_query import orm_get_user, orm_add_user, orm_update_user, get_objects_by_name, get_obj_by_name_and_id, \
#     get_balance_by_username, add_balance_by_username, get_cupon_price, delete_cupon, orm_add_object, get_user_purchases, \
#     get_purchase, get_countries_orm, get_services_orm, get_countries_by_multiservice, check_user_balance, \
#     orm_get_user_by_username, get_balance_by_id
# from kbrds.inline import profile_kb, deposite_kb, get_inlineMix_btns, get_shop_btns, get_cryptobot_btns, \
#     shop_kb, get_callback_btns, info_btn_kb, get_sms_btns, get_sms_countries_btns, get_multiservice_btns, \
#     get_multiservice_countries_btns, get_cryptomus_btns
# from kbrds.reply import menu_markup, sms_shop_markup, pokupka_sms_kb
# from services.cryptomus_service import create_invoice, get_invoice_mus, get_rub_course
# from services.lolz_service import check_payment_lolz, get_history
# from services.main_service import get_invoice, invoice_by_id, check_invoice, delete_invoice, pagination, \
#     send_message_via_telegram_api, send_photomessage_via_telegram_api, give_strings, clear_trash, append_to_file, \
#     pagination_dict, \
#     get_avaliables, generate_random_string
#
# from smsactivate.api import SMSActivateAPI
#
# from services.sms_activate_service import pagination_sms, get_countries_by_service, get_sms_number, \
#     get_activation_status, cancel_activation, get_multi_numbers, get_price_with_markup, \
#     get_price_by_service_and_country
#
# load_dotenv(find_dotenv())
#
#
# user_private_router = Router()
#
#
# # ------------------------------MAIN MENU---------------------------------
#
# @user_private_router.message(F.text.startswith('/start'))
# async def start_cmd(message: types.Message, session: AsyncSession):
#     if message.from_user.username == None:
#         username = 'None'
#     else:
#         username = message.from_user.username
#     if message.chat.type == 'private':
#         if not await orm_get_user(session=session, user_id=message.from_user.id):
#             referrer_id = str(message.text[7:])
#             if referrer_id != '':
#                 if referrer_id != str(message.from_user.id):
#                     user = User(
#                         username = username,
#                         user_id = message.from_user.id,
#                         ref_id = int(referrer_id)
#                     )
#                     await message.bot.send_message(chat_id=int(referrer_id), text=f"<b>У вас новый реферал - @{username}</b>")
#                     await orm_add_user(session, user)
#                 else:
#                     user = User(
#                         username=username,
#                         user_id=message.from_user.id,
#                     )
#                     await orm_add_user(session, user)
#             else:
#                 user = User(
#                     username=username,
#                     user_id=message.from_user.id,
#                 )
#                 await orm_add_user(session, user)
#         await message.answer(f'''<b>🙋‍♂️@{username} Добро пожаловать
#  в бота 𝐏𝐔𝐍𝐂𝐇𝐌𝐀𝐃𝐄 SHOP!
#
# 👇 Для управления воспользуйся кнопками ниже</b>
#         ''', reply_markup=menu_markup)
#         # await message.answer('Главное меню', reply_markup=menu_kb.as_markup())
#         await message.delete()
#         return
#
#
# @user_private_router.message(F.text == 'ℹ️Информация')
# async def menu_query1(message: types.Message, state: FSMContext):
#     await state.clear()
#     await message.answer_photo(photo=FSInputFile('assets/info.png'), reply_markup=info_btn_kb.as_markup())
#     await message.delete()
#     return
#
# @user_private_router.callback_query(F.data == 'rules')
# async def menu_query2(callback: types.CallbackQuery, state: FSMContext):
#     await state.clear()
#     async with aiofiles.open('rules.txt', 'r', encoding='utf-8') as f:
#         info_text = await f.read()
#     await callback.message.answer(f'<b>{info_text}</b>')
#     await callback.message.delete()
#     return
#
#
# @user_private_router.callback_query(F.data == 'referal')
# async def shop_query(call: types.CallbackQuery, state: FSMContext):
#     await state.clear()
#     text = f'''<b>В боте включена реферальная система.
# Приглашайте друзей и зарабатывайте на этом!
# Вы будете получать 5% с каждого пополнения вашего реферала
#
# 🛍️Ваша реферальная ссылка: {'https://t.me/ ' +config.BOT_NAM E +'?start= ' +str(call.from_user.id)}
# </b>
#     '''
#     await call.message.answer(text)
#     await call.message.delete()
#     return
#
#
# # @user_private_router.callback_query(F.data == 'shop')
# # async def shop_query(call: types.CallbackQuery, state: FSMContext):
# #     await state.clear()
# #     text = '''
# # 🛍️Магазин цифровых товаров
# #
# # 📕Выберите категорию:
# #
# #     '''
# #     await call.message.answer(text, reply_markup=shop_kb.as_markup())
# #     await call.message.delete()
# #     return
#
#
# @user_private_router.message(F.text == '🛍️Каталог товаров')
# async def shop_query(message: types.Message, state: FSMContext):
#     await state.clear()
#     text = '''<b>🛍️Магазин цифровых товаров
#
# 📕Выберите категорию:</b>
#     '''
#     await message.answer_photo(photo=FSInputFile('assets/categories.png'), caption=text, reply_markup=shop_kb.as_markup())
#     await message.delete()
#     return
#
#
# @user_private_router.message(F.text == '👤Профиль')
# async def profile_query(message: types.Message, session: AsyncSession):
#     user_id = message.from_user.id
#     user = await orm_get_user(session=session, user_id=int(user_id))
#     text = f'''<b>👤User ID: <code>{user.user_id}</code>
#
# 👨‍💻Username: @{user.username}
#
# 💰Баланс: {user.balance} ₽
#
# 🛒Кол-во купленных товаров: {user.items_count}
#
# 🛍Сумма купленных товаров: {user.items_prices_sum} ₽</b>
#             '''
#     await message.answer_photo(photo=FSInputFile('assets/profile.jpg'), caption=text, reply_markup=profile_kb.as_markup())
#     await message.delete()
#     return
#
#
# class CuponGroup(StatesGroup):
#     cupon_name = State()
#
#     async def clear(self) -> None:
#         await self.set_state(state=None)
#         await self.set_data({})
#
#
# @user_private_router.callback_query(F.data == 'cupon')
# async def cupon_query(callback: types.CallbackQuery, state: FSMContext):
#     text = f'''<b>Введите купон</b>'''
#     await state.set_state(CuponGroup.cupon_name)
#     await callback.message.answer(text=text)
#     await callback.message.delete()
#     return
#
#
# @user_private_router.callback_query(F.data == 'history')
# async def history_query(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
#     text = f'''<b>Ваши покупки:\n</b>'''
#     purchases = await get_user_purchases(session=session, user_id=callback.from_user.id)
#     btns ={}
#     for purchase in purchases:
#         btns.update({f"<b>Заказ#{purchase.purchase_tag[1:]} - {purchase.item_name}": f"btnhistoty_{purchase.id}</b>"})
#
#     await callback.message.answer(text=text, reply_markup=get_callback_btns(btns=btns, sizes=(1,)))
#     await callback.message.delete()
#     return
#
#
# @user_private_router.callback_query(F.data.startswith('btnhistoty_'))  # VPN_3 (page 3)
# async def btnshistory_callback(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
#     await state.clear()
#     purchase_id = int(callback.data.split("_")[-1])
#     purchase = await get_purchase(session=session, purchase_id=purchase_id)
#     await callback.message.answer(text=f'''<b>Заказ{purchase.purchase_tag}:
#
# Название товара: {purchase.item_name}
# Количетсво товара: {purchase.items_count}
# Цена за один товар: {purchase.item_price}
# Цена за все товары: {purchase.items_prices_sum}
#
# Дата покупки: {purchase.date}</b>
# ''')
#
#
# @user_private_router.message(StateFilter(CuponGroup.cupon_name), F.text)
# async def cupon_message(message: types.Message, session: AsyncSession, state: FSMContext):
#     await state.update_data(cupon_name=message.text)
#     cupon = await get_cupon_price(session=session, cupon_name=message.text)
#     if cupon:
#         user = await orm_get_user(session=session, user_id=message.from_user.id)
#         user.balance += cupon.cupon_price
#         await orm_update_user(session=session, user_id=user.user_id, data={"balance": user.balance})
#         await message.answer(text=f"<b>На ваш баланс зачислено {cupon.cupon_price}</b>")
#         await delete_cupon(session=session, cupon_name=cupon.name)
#         await state.clear()
#     else:
#         await message.answer(text=f"<b>Купона не существует</b>")
#         await state.clear()
#     await message.delete()
#     return
#
#
# # --------------------------------------SHOP---------------------------------------
#
#
# @user_private_router.callback_query(
#     F.data.startswith('vpn_') | F.data.startswith('phys_') | F.data.startswith('chatgpt_') | F.data.startswith(
#         'subs_') | F.data.startswith('steampoints_') | F.data.startswith('gift_') | F.data.startswith(
#         'discordnitro_') | F.data.startswith('soc_') | F.data.startswith('mails_'))  # VPN_3 (page 3)
# async def items_callback(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
#     await state.clear()
#     print(callback.data)
#     pagination_page = int(callback.data.split("_")[-1])
#     obj_name = callback.data.split("_")[-2]
#     # print(pagination_page)
#     print(obj_name)
#     objects = await get_objects_by_name(name=obj_name, session=session)
#     paginated_objects = pagination(objects=objects, page=pagination_page)
#     # print(objects)
#     total_pages = 1
#     if len(objects) > 5:
#         if len(objects) % 5 == 0:
#             total_pages = len(objects) // 5
#         else:
#             total_pages = len(objects) // 5 + 1
#     else:
#         total_pages = 1
#     keyboard = await get_shop_btns(paginated_objects, pagination_page, total_pages, False)
#     text = "<b>" + get_category_text(obj_name) + "</b>"
#     print(f'assets/{obj_name}.png')
#     await send_photomessage_via_telegram_api(chat_id=callback.from_user.id, caption=text,
#                                              photo_path=f'assets/{obj_name}.png', reply_markup=keyboard)
#     await callback.message.delete()
#     return
#
#
# class BuyingItem(StatesGroup):
#     items_count = State()
#     items_payment = State()
#
#     async def clear(self) -> None:
#         await self.set_state(state=None)
#         await self.set_data({})
#
#
# @user_private_router.callback_query(StateFilter(None), F.data.startswith('buy_'))  # VPN_3 (page 3)
# async def buy_callback(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
#     obj_name = callback.data.split("_")[-2]
#     obj_id = float(callback.data.split("_")[-1])
#     obj = await get_obj_by_name_and_id(id=obj_id, name=obj_name, session=session)
#     count = await get_avaliables(obj)
#     if count == 0:
#         await callback.bot.send_message(callback.from_user.id, text=f"<b>Товара нет в наличии!</b>")
#     else:
#         await state.update_data(item=obj)
#         text = f'''<b>
# 🛒Товар: {obj.name}
#
# 📃Описание:
# {obj.description}
#
# Укажите количество товара</b>
#     '''
#         tovarkb_list = [
#             [
#                 InlineKeyboardButton(text="1️⃣", callback_data='1'),
#                 InlineKeyboardButton(text="2️⃣", callback_data='2'),
#                 InlineKeyboardButton(text="3️⃣", callback_data='3'),
#                 InlineKeyboardButton(text="4️⃣", callback_data='4'),
#                 InlineKeyboardButton(text="5️⃣", callback_data='5')],
#             [
#                 InlineKeyboardButton(text="🔢Укажите свое количество", callback_data='your')
#             ],
#             [
#                 InlineKeyboardButton(text="Назад", callback_data=f"{type(obj).__name__.lower()}_1")
#             ]
#         ]
#         tovar_kb = InlineKeyboardBuilder(tovarkb_list)
#         await callback.bot.send_message(callback.from_user.id, text=text, reply_markup=tovar_kb.as_markup())
#         await state.set_state(BuyingItem.items_count)
#     await callback.message.delete()
#     return
#
#
# @user_private_router.message(BuyingItem.items_count, F.text)
# async def count_chosen(message: Message, state: FSMContext, session: AsyncSession):
#     item_counts = int(message.text)
#     state_data = await state.get_data()
#     item = state_data["item"]
#     object_name = type(item).__name__.lower()
#     print(object_name)
#
#     if object_name not in ['phys', 'discordnitro', 'gift']:
#         source_directory = f"sources/{object_name}/{item.file_name}.txt"
#         if not os.path.exists(source_directory):
#             await message.answer(
#                 text=f"<b>Файл '{source_directory}' не существует. Обратитесь в поддержку @punchmade_support.</b>")
#             await state.clear()
#             return
#
#         async with aiofiles.open(source_directory, mode='r') as f:
#             lines = await f.readlines()
#             lines = [line.strip() for line in lines if line.strip()]
#
#         available_lines = len(lines)
#
#         if available_lines == 0:
#             await message.answer(text=f"<b>Товара нет в наличии!</b>")
#             return
#
#         if item_counts > available_lines:
#             await message.answer(
#                 text=f"<b>Доступно только {available_lines} строк. Пожалуйста, введите меньшее количество.</b>")
#             return
#     else:
#         if item.count == 0:
#             await message.answer(text=f"<b>Товара нет в наличии!</b>")
#             return
#
#         if item_counts > item.count:
#             await message.answer(text=f"<b>Доступно только {item.count}. Пожалуйста, введите меньшее количество.</b>")
#             return
#
#     tag_item = "#" + str(random.randint(10000000, 99999999))
#     await state.update_data(item_counts=item_counts, tag_item=tag_item)
#     item_name = item.name
#     item_price = item.price
#     items_sum = item_counts * item_price
#     user_balance = await get_balance_by_id(user_id=message.from_user.id, session=session)
#     text = f'''<b>➖➖➖➖➖➖➖➖➖➖➖➖
# 📦 Товар: ⭐️ {item_name}
# 📝 Описание: {item.description}
# 💵 Цена: {items_sum}
# 🧮  Кол-во: {item_counts}
# ✉️ Заказ: {tag_item}
# ⏰ Время заказа: {datetime.now()}
# 💸 Способ оплаты: Баланс бота
# 👤 Покупатель ID: {message.from_user.id}
# 👤 Покупатель: @{message.from_user.username if message.from_user.username else 'None'}
# {'📄 Инструкция: Обратитесь в Тех.Поддержку - @punchmade_support для получения товара' if item_name in ['discordnitro', 'phys', 'gift'] else ''}
# ➖➖➖➖➖➖➖➖➖➖➖➖</b>
# '''
#     btns = {"Оплатить": f"oplatit_{float(message.text) * item_price}"} if user_balance >= items_sum else {
#         "Пополнить баланс": f"deposite"}
#     await message.answer(
#         text=text,
#         reply_markup=get_inlineMix_btns(btns=btns)
#     )
#     await state.set_state(BuyingItem.items_payment)
#
#
# @user_private_router.callback_query(BuyingItem.items_count, F.data)
# async def count_chosen(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
#     if call.data not in ['1', '2', '3', '4', '5', 'your']:
#         return
#     if call.data == 'your':
#         await call.message.answer(text='<B>Укажите желаемое количество товара</b>')
#         return
#     item_counts = int(call.data)
#     state_data = await state.get_data()
#     item = state_data["item"]
#     object_name = type(item).__name__.lower()
#     print(object_name + 'tut')
#     if object_name not in ['phys', 'discordnitro', 'gift']:
#         source_directory = f"sources/{object_name}/{item.file_name}.txt"
#         if not os.path.exists(source_directory):
#             await call.message.answer(
#                 text=f"<b>Файл '{source_directory}' не существует. Обратитесь в поддержку @punchmade_support.</b>")
#             await state.clear()
#             return
#
#         async with aiofiles.open(source_directory, mode='r') as f:
#             lines = await f.readlines()
#             lines = [line.strip() for line in lines if line.strip()]
#
#         available_lines = len(lines)
#
#         if available_lines == 0:
#             await call.message.answer(text=f"<b>Товара нет в наличии!</b>")
#             return
#
#         if item_counts > available_lines:
#             await call.message.answer(
#                 text=f"<b>Доступно только {available_lines} строк. Пожалуйста, введите меньшее количество.</b>")
#             return
#     else:
#         if item.count == 0:
#             await call.message.answer(text=f"<b>Товара нет в наличии!</b>")
#             return
#
#         if item_counts > item.count:
#             await call.message.answer(
#                 text=f"<b>Доступно только {item.count}. Пожалуйста, введите меньшее количество.</b>")
#             return
#
#     tag_item = "#" + str(random.randint(10000000, 99999999))
#     await state.update_data(item_counts=item_counts, tag_item=tag_item)
#     item_name = item.name
#     item_price = item.price
#     items_sum = item_counts * item_price
#     user = await orm_get_user(user_id=call.from_user.id, session=session)
#     user_balance = await get_balance_by_id(user_id=call.from_user.id, session=session)
#     text = f'''<b>➖➖➖➖➖➖➖➖➖➖➖➖
# 📦 Товар: ⭐️ {item_name}
# 📝 Описание: {item.description}
# 💵 Цена: {items_sum}
# 🧮  Кол-во: {item_counts}
# ✉️ Заказ: {tag_item}
# ⏰ Время заказа: {datetime.now()}
# 💸 Способ оплаты: Баланс бота
# 👤 Покупатель ID: {call.from_user.id}
# 👤 Покупатель: @{call.from_user.username if call.from_user.username else 'None'}
# {'📄 Инструкция: Обратитесь в Тех.Поддержку - @punchmade_support для получения товара' if item_name in ['discordnitro', 'phys', 'gift'] else ''}
# ➖➖➖➖➖➖➖➖➖➖➖➖</b>
# '''
#     btns = {"Оплатить": f"oplatit_{float(call.data) * item_price}"} if user.balance >= items_sum else {
#         "Пополнить баланс": f"deposite"}
#     await call.message.answer(
#         text=text,
#         reply_markup=get_inlineMix_btns(btns=btns)
#     )
#     await state.set_state(BuyingItem.items_payment)
#
#
# @user_private_router.callback_query(BuyingItem.items_payment, F.data.startswith('oplatit_'))  # VPN_3 (page 3)
# async def oplatit_callback(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
#     state_data = await state.get_data()
#     item = state_data["item"]
#     item_counts = state_data["item_counts"]
#     tag_item = state_data["tag_item"]
#     items_price = float(callback.data.split("_")[-1])
#     user = await orm_get_user(user_id=callback.from_user.id, session=session)
#     object_name = type(item).__name__.lower()
#     if user.balance >= items_price and item_counts <= item.count:
#         user.balance -= items_price
#         user.items_count += 1
#         user.items_prices_sum += items_price
#         item.count -= item_counts
#         purchase = Purchase(
#             user_id=user.user_id,
#             item_name=item.name,
#             purchase_tag=tag_item,
#             item_price=item.price,
#             items_count=item_counts,
#             items_prices_sum=item_counts * item.price,
#         )
#         await orm_add_object(purchase, session=session)
#         log_text = f"[{datetime.now()}] {tag_item} - {user.username} - {item.name} - {item.price} - {item_counts} - {item_counts * item.price}"
#         await orm_add_user(session=session, user=user)
#         await append_to_file(log_text)
#         await state.clear()
#         document = await give_strings(object_name, item.name, item.file_name, item_counts)
#         if document:
#             if type(document) is list:
#                 await callback.bot.send_document(chat_id=callback.from_user.id,
#                                                  document=FSInputFile(document[0], document[1]))
#                 await clear_trash(document[0])
#             elif type(document) is str:
#                 await callback.message.answer(text=document)
#         else:
#             await callback.message.answer(
#                 text="<b>Произошла ошибка при получении товара. Обратитесь в Тех.Поддержку.</b>")
#     else:
#         await state.clear()
#         await deposite_query(callback)
#         await callback.message.delete()
#     await state.clear()
#     return
#
#
# # ---------------------DEPOSITS------------------------------
#
# class DepositeFSM(StatesGroup):
#     popolnenie = State()
#
#     async def clear(self) -> None:
#         await self.set_state(state=None)
#         await self.set_data({})
#
#
# class CryptomusFSM(StatesGroup):
#     popolnenie = State()
#
#     async def clear(self) -> None:
#         await self.set_state(state=None)
#         await self.set_data({})
#
#
# class ZelenkaFSM(StatesGroup):
#     popolnenie = State()
#
#     async def clear(self) -> None:
#         await self.set_state(state=None)
#         await self.set_data({})
#
#
# @user_private_router.callback_query(F.data == 'deposite')
# async def deposite_query(callback: types.CallbackQuery):
#     text = f'''
# 💸Выберите способ пополнения
#
# #
# '''
#     await callback.message.answer(text=text, reply_markup=deposite_kb.as_markup())
#     await callback.message.delete()
#     return
#
#
# @user_private_router.callback_query(F.data == 'cryptobot_sum')
# async def deposite_sum_query(callback: types.CallbackQuery, state: FSMContext):
#     text = f'''<b>Введите желаемую сумму пополнения</b>'''
#     await state.set_state(DepositeFSM.popolnenie)
#     await callback.message.answer(text=text)
#     await callback.message.delete()
#     return
#
#
# @user_private_router.message(DepositeFSM.popolnenie, F.text)
# async def deposite_sum_query(message: types.Message, state: FSMContext):
#     await state.update_data(sum=int(message.text))
#     await crypto_bot_pay_query(
#         callback=types.CallbackQuery(id=str(random.randint(1000000, 5000000)),  # Произвольное значение
#                                      data='cryptoBot',
#                                      from_user=message.from_user,  # Информация о пользователе, отправившем сообщение
#                                      chat_instance=str(message.chat.id)), state=state)
#     return
#
#
# # при нажатии
# @user_private_router.callback_query(DepositeFSM.popolnenie, F.data == 'cryptoBot')
# async def crypto_bot_pay_query(callback: types.CallbackQuery, state: FSMContext):
#     text = f'''<b>Пополните счет</b>'''
#     sum = await state.get_data()
#     sum = sum["sum"]
#     invoice = await get_invoice(sum)
#     link = invoice.bot_invoice_url
#     keyboard = get_cryptobot_btns(link=link, invoice=invoice)
#     await send_message_via_telegram_api(chat_id=callback.from_user.id, text=text,
#                                         reply_markup=keyboard)
#     return
#
#
# @user_private_router.callback_query(F.data == 'cryptomus_sum')
# async def deposite_sum_query(callback: types.CallbackQuery, state: FSMContext):
#     text = f'''<b>Введите желаемую сумму пополнения</b>'''
#     await state.set_state(CryptomusFSM.popolnenie)
#     await callback.message.answer(text=text)
#     await callback.message.delete()
#     return
#
#
# @user_private_router.message(CryptomusFSM.popolnenie, F.text)
# async def deposite_mus_sum_query(message: types.Message, state: FSMContext):
#     sum = float(message.text) / (await get_rub_course())
#     print(sum)
#     await state.update_data(sum=sum)
#     text = f'''<b>Пополните счет</b>'''
#     sum = await state.get_data()
#     sum = sum["sum"]
#     comment = generate_random_string()
#     await state.update_data(comment=comment)
#     invoice = await create_invoice(user_id=message.from_user.id, amount=sum, comment=comment)
#     print(invoice)
#     link = invoice['result']['url']
#     keyboard = get_cryptomus_btns(link=link, invoice=invoice)
#     await send_message_via_telegram_api(chat_id=message.from_user.id, text=text,
#                                         reply_markup=keyboard)
#     return
#
#
# @user_private_router.callback_query(F.data == 'zelenka_sum')
# async def deposite_sum_query(callback: types.CallbackQuery, state: FSMContext):
#     text = f'''<b>Введите желаемую сумму пополнения</b>'''
#     await state.set_state(ZelenkaFSM.popolnenie)
#     await callback.message.answer(text=text)
#     await callback.message.delete()
#     return
#
#
# # при нажатии на кнопку оплата зеленкой
# @user_private_router.message(ZelenkaFSM.popolnenie)
# async def zelenka_payment_query(message: types.Message, state: FSMContext):
#     try:
#         sum = int(message.text)
#         print(sum)
#         await state.update_data(sum=sum)
#     except:
#         await message.answer(text='Введите целое число')
#         return
#     comment = message.from_user.id
#     text = f'''
# Для оплаты перейдите по ссылке!
# ❗️Нельзя изменять:
# -Сумму перевода
# -Комментарий к переводу
# -Получателя
# -Замораживать платеж
#
# После оплаты нажмите на кнопку "Проверить оплату" '''
#     link = f'https://lzt.market/balance/transfer?redirect=https%3A%2F%2Fapi.bot-t.com%2Fpayment%2Flolz%2Fsuccess%2F{comment}&username={config.LOLZ_USERNAME}&comment={comment}&amount={sum * 1.07}'
#     await message.answer(text=text, reply_markup=get_inlineMix_btns(btns={"Оплатить": f"{link}",
#                                                                           "Проверить оплату": f"checkPaymentZelenka_{comment}",
#                                                                           "Назад": "deposite"}))
#     await message.delete()
#     return
#
#
# @user_private_router.callback_query(F.data.startswith("checkPaymentZelenka_"))
# async def check_payment_zelenka_query(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
#     comment_id = int(callback.data.split("_")[-1])
#     state_data = await state.get_data()
#     sum = state_data['sum']
#     print(comment_id)
#     response = await get_history(comment=comment_id)
#     print(response)
#     result = await check_payment_lolz(response, sum)
#     print(result)
#     if result is None:
#         await callback.answer(text="Ожидайте", show_alert=True)
#         return
#
#     # await callback.message.delete()
#     user_id = callback.from_user.id
#
#     user = await orm_get_user(session=session, user_id=int(user_id))
#     if user.ref_id != 0:
#         try:
#             refer = await orm_get_user(session=session, user_id=user.ref_id)
#             await add_balance_by_username(session=session, username=refer.username, amount=result * 0.05)
#             await callback.bot.send_message(user.ref_id, f"Ваш реферал пополнил счет, вам начислено {result * 0.05}")
#         except Exception as e:
#             print(e)
#     await callback.answer(text="Платеж найден,деньги зачислены на ваш счет.", show_alert=True)
#     user.balance += result
#     await orm_update_user(session=session, user_id=user_id, data={"balance": user.balance})
#     await callback.message.delete()
#     # await menu_msg(callback.message)
#
#
# # при нажатии на кнопку "Проверить" под оплатой криптоботом
# def menu_query(callback):
#     pass
#
#
# @user_private_router.callback_query(DepositeFSM.popolnenie, F.data.startswith("checkPaymentCrypto_"))
# async def check_payment_crypto_query(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
#     invoice_id = int(callback.data.split("_")[-1])
#     invoice = await invoice_by_id(invoice_id)
#     result = await check_invoice(invoice_id)
#     if result == 'active':
#         await callback.answer(text="Ожидайте", show_alert=True)
#     if result == 'paid':
#         user = await orm_get_user(user_id=callback.from_user.id, session=session)
#         if user.ref_id != 0:
#             try:
#                 refer = await orm_get_user(session=session, user_id=user.ref_id)
#                 await add_balance_by_username(session=session, username=refer.username, amount=invoice.amount * 0.05)
#                 await callback.bot.send_message(user.ref_id,
#                                                 f"Ваш реферал пополнил счет, вам начислено {invoice.amount * 0.05}")
#             except:
#                 ...
#         await state.clear()
#         user_id = callback.from_user.id
#         await callback.message.answer(text=f"<b>💸На ваш баланс зачислено {invoice.amount}₽</b>")
#         user.balance += invoice.amount
#         await orm_update_user(session=session, user_id=user_id, data={"balance": user.balance})
#         await delete_invoice(invoice_id)
#         # await menu_query(callback)
#         await callback.message.delete()
#
#
# @user_private_router.callback_query(CryptomusFSM.popolnenie, F.data.startswith("checkPaymentMus_"))
# async def check_payment_crypto_query(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
#     invoice = await get_invoice_mus(callback.data.split("_")[-1])
#     status = invoice['result']['status']
#     print(status)
#     if status == 'paid' or status == 'paid_over':
#         amount = float(invoice['result']['amount']) * (await get_rub_course())
#         user = await orm_get_user(user_id=callback.from_user.id, session=session)
#         if user.ref_id != 0:
#             try:
#                 refer = await orm_get_user(session=session, user_id=user.ref_id)
#                 await add_balance_by_username(session=session, username=refer.username, amount=amount * 0.05)
#                 await callback.bot.send_message(user.ref_id,
#                                                 f"Ваш реферал пополнил счет, вам начислено {amount * 0.05}")
#             except:
#                 ...
#         await state.clear()
#         user_id = callback.from_user.id
#         await callback.message.answer(text=f"<b>💸На ваш баланс зачислено {amount}₽</b>")
#         user.balance += amount
#         await orm_update_user(session=session, user_id=user_id, data={"balance": user.balance})
#         # await menu_query(callback)
#         await callback.message.delete()
#     else:
#         await callback.answer(text="Ожидайте", show_alert=True)
#
#
# # @user_private_router.message(F.text == 'test')
# # async def test(message: types.Message, state: FSMContext):
# #     await get_rub_course()
# # ----------------------------------------------SMS-----------------------------------------
# # для будущего кодера
# # если будут вопросы по коду, напиши мне в тг, я помогу разобраться
# # @cncntrated
# # там админку допилить нужно еще под товар
#
# class SMSShop(StatesGroup):
#     kupit_sms = State()
#     multiservice_chose = State()
#     multiservice_country = State()
#     search_service = State()
#     ojidanie_sms = State()
#
#     async def clear(self) -> None:
#         await self.set_state(state=None)
#         await self.set_data({})
#
#
# # await state.update_data(item_counts=item_counts, tag_item=tag_item)
# #     state_data = await state.get_data()
# #     item = state_data["item"]
# #     item_name = item.name
# #     item_price = item.price
# #     items_sum = item_counts*item_price
#
#
# @user_private_router.message(F.text == '📩Sms shop')
# async def vhod_v_sms_shop_msg(message: types.Message, state: FSMContext, session: AsyncSession):
#     await message.answer_photo(photo=FSInputFile('assets/sms.png'), caption=f"<b>🤚Добро пожаловать в SMS SHOP!</b>",
#                                reply_markup=sms_shop_markup)
#     await message.delete()
#
#
# @user_private_router.message(F.text == "👊Меню")
# async def menu_from_sms_shop(message: types.Message, state: FSMContext, session: AsyncSession):
#     await state.clear()
#     await message.answer(f'''<b>👊Главное меню:</b>
#             ''', reply_markup=menu_markup)
#     await message.delete()
#
#
# # ПОКУПКА СМС
#
#
# @user_private_router.message(F.text.contains('Купить'))
# async def sms_kupit_msg(message: types.Message, state: FSMContext, session: AsyncSession):
#     await state.set_state(SMSShop.kupit_sms)
#     pagination_page = 1
#     objects = await get_services_orm(session=session)
#     paginated_objects = pagination_sms(objects=objects, page=pagination_page)
#     print(objects)
#     total_pages = 1
#     if len(objects) > 18:
#         if len(objects) % 18 == 0:
#             total_pages = len(objects) // 18
#         else:
#             total_pages = len(objects) // 18 + 1
#     else:
#         total_pages = 1
#     keyboard = get_sms_btns(paginated_objects, pagination_page, total_pages)
#     await send_message_via_telegram_api(chat_id=message.from_user.id, text="Выберите сервис:", reply_markup=keyboard)
#     await message.delete()
#     return
#
#
# # кнопка переключения страницы шопа покупки смс
# @user_private_router.callback_query(F.data.startswith('sms_'))
# async def sms_shop_query(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
#     if await state.get_state() != SMSShop.kupit_sms.state:
#         await state.set_state(SMSShop.kupit_sms)
#
#     pagination_page = int(call.data.split("_")[-1])
#     objects = await get_services_orm(session=session)
#     paginated_objects = pagination_sms(objects=objects, page=pagination_page)
#     print(objects)
#     total_pages = 1
#     if len(objects) > 18:
#         if len(objects) % 18 == 0:
#             total_pages = len(objects) // 18
#         else:
#             total_pages = len(objects) // 18 + 1
#     else:
#         total_pages = 1
#     keyboard = get_sms_btns(paginated_objects, pagination_page, total_pages)
#     await send_message_via_telegram_api(chat_id=call.from_user.id, text="Выберите сервис:", reply_markup=keyboard)
#     await call.message.delete()
#     return
#
#
# @user_private_router.callback_query(SMSShop.kupit_sms, F.data.startswith('smsservice_'))  # smsservice_tg_2
# async def sms_service_query(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
#     service_tag = call.data.split("_")[-2]
#     country_page = int(call.data.split("_")[-1])
#
#     await state.update_data(service_tag=service_tag)
#
#     countries = get_countries_by_service(service=service_tag)
#
#     paginated_objects = pagination_dict(countries, page=country_page, paginate=5)
#
#     total_pages = 1
#     if len(countries) > 5:
#         if len(countries) % 5 == 0:
#             total_pages = len(countries) // 5
#         else:
#             total_pages = len(countries) // 5 + 1
#     else:
#         total_pages = 1
#
#     sms_countries = await get_sms_countries_btns(countries_dict=paginated_objects,
#                                                  current_page=country_page,
#                                                  total_pages=total_pages,
#                                                  service_tag=service_tag,
#                                                  session=session)
#
#     if sms_countries:
#         await send_message_via_telegram_api(chat_id=call.from_user.id, text='🇲🇽Выберите страну номера',
#                                             reply_markup=sms_countries)
#     else:
#         await send_message_via_telegram_api(chat_id=call.from_user.id, text='❌Товара нет в наличии')
#
#     await call.message.delete()
#     return
#
#
# #  f"buysms_{service_tag}_{country_id}"
#
# @user_private_router.callback_query(SMSShop.kupit_sms, F.data.startswith("buysms_"))
# async def buy_sms_query(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
#     service_tag = call.data.split("_")[-2]
#     country_id = int(call.data.split("_")[-1])
#     await state.update_data(country_id=country_id)
#
#     price_data = get_price_by_service_and_country(service=service_tag, country_id=country_id)
#     if not price_data:
#         await call.message.answer(text="Сервис временно недоступен. Попробуйте позже.")
#         return
#
#     price = float(price_data[f'{country_id}'][service_tag]['cost'])
#     price_with_markup = get_price_with_markup(price)
#
#     if not await check_user_balance(call.from_user.id, session, price_with_markup):
#         await call.message.answer(text="Недостаточно средств на балансе для совершения покупки.")
#         return
#
#     await state.update_data(total_price=price_with_markup)
#     activation = get_sms_number(service_tag=service_tag, country_id=country_id)
#     activation_id = int(activation['activationId'])
#     await state.update_data(activation_id=activation_id, activation=activation)
#     user = await orm_get_user(session=session, user_id=call.from_user.id)
#     user.balance -= price_with_markup
#     await orm_add_user(session=session, user=user)
#     # await add_balance_by_username(username=call.from_user.username, session=session, amount=-price_with_markup)
#
#     await call.message.answer(text=f'''
# 📱 Ваш номер: +{activation['phoneNumber']}
# 📱 Номер без кода страны: <code>{activation['phoneNumber']}</code>
# ⏳ Время на активацию: 20 минут.
#
# ❓ FAQ:
# - Попался заблокированный номер и на него НЕ приходил СМС код? Отмените его, баланс вернется в бот.
# - Номер автоматически
# и отменяется, если не пришел код в течении 20 минут.
# - Если отменяете номер, то выходите с окна ввода кода только после полной отмены номера. Код может прийти во время отмены из-за задержки.
# - Код придет автоматически!
# - Столкнулись с проблемой после получения СМС кода? Пиши @Punchmade_Support,
# обязательно со скринами.
#
# <u>Телеграм нужно регистрировать с телефона через официальное приложение Telegram. Иначе код может не приходить. Если код идет на другое устройство, то отменяйте номер.</u>
# ''', reply_markup=pokupka_sms_kb)
#     await state.set_state(SMSShop.ojidanie_sms)
#     while True:
#         status = get_activation_status(activation_id)
#         print(status)
#         if 'canceled' in status:
#             break
#         if 'STATUS_OK' in status:
#             result = status.split(":")[-1]
#             await call.message.answer(text=f'''Ваш код: {result}''', reply_markup=menu_markup)
#             status.clear()
#             print("УСПЕХ")
#             break
#         await asyncio.sleep(5)
#
#
# @user_private_router.message(SMSShop.ojidanie_sms, F.text == '❌Отменить покупку')
# async def sms_shop_msg(message: types.Message, state: FSMContext, session: AsyncSession):
#     state_data = await state.get_data()
#     activation_id = state_data['activation_id']
#     print(activation_id)
#     status = get_activation_status(activation_id)
#
#     print(status)
#     price_with_markup = state_data['total_price']
#     if 'Current activation canceled and no longer' in status:
#         await message.answer(text=f'''✅Покупка отменена''', reply_markup=menu_markup)
#         user = await orm_get_user(session=session, user_id=message.from_user.id)
#         user.balance += price_with_markup
#         await orm_add_user(session=session, user=user)
#         await state.clear()
#         return
#     if 'STATUS_OK' not in status:
#         cancel = cancel_activation(activation_id)
#         print(cancel)
#         if 'ACCESS_CANCEL' in cancel:
#             await message.answer(text=f'''✅Покупка отменена''', reply_markup=menu_markup)
#             user = await orm_get_user(session=session, user_id=message.from_user.id)
#             user.balance += price_with_markup
#             await orm_add_user(session=session, user=user)
#             await state.clear()
#             return
#         if 'EARLY_CANCEL_DENIED' in cancel:
#             await message.answer(text=f'''
# ⚡️В первые 2 минуты после покупки вы не можете отменить покупку, подождите
# ''')
#     await message.delete()
#     return
#
#
# @user_private_router.message(F.text.contains('Мультисервис'))
# async def sms_multiservice_msg(message: types.Message, state: FSMContext, session: AsyncSession):
#     await state.set_state(SMSShop.multiservice_chose)
#     pagination_page = 1
#     objects = await get_services_orm(session=session)
#     paginated_objects = pagination_sms(objects=objects, page=pagination_page)
#     await state.update_data(chosen_services=[])
#     total_pages = 1
#     if len(objects) > 18:
#         if len(objects) % 18 == 0:
#             total_pages = len(objects) // 18
#         else:
#             total_pages = len(objects) // 18 + 1
#     else:
#         total_pages = 1
#     keyboard = get_multiservice_btns(objects=paginated_objects, current_page=pagination_page, total_pages=total_pages,
#                                      chosen_objects=[])
#     await send_message_via_telegram_api(chat_id=message.from_user.id, text="Выберите до 5 сервисов:",
#                                         reply_markup=keyboard)
#     await message.delete()
#     return
#
#
# # отвечает за переключение страниц смс сервисов
# @user_private_router.callback_query(F.data.startswith('smsmulti_'))
# async def sms_shop_query(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
#     if await state.get_state() != SMSShop.multiservice_chose.state:
#         await state.set_state(SMSShop.multiservice_chose)
#
#     pagination_page = int(call.data.split("_")[-1])
#     objects = await get_services_orm(session=session)
#     paginated_objects = pagination_sms(objects=objects, page=pagination_page)
#     fsmdata = await state.get_data()
#     chosen_services = fsmdata["chosen_services"]
#     print(objects)
#     total_pages = 1
#     if len(objects) > 18:
#         if len(objects) % 18 == 0:
#             total_pages = len(objects) // 18
#         else:
#             total_pages = len(objects) // 18 + 1
#     else:
#         total_pages = 1
#     keyboard = get_multiservice_btns(objects=paginated_objects, current_page=pagination_page,
#                                      total_pages=total_pages, chosen_objects=chosen_services)
#     await send_message_via_telegram_api(chat_id=call.from_user.id, text='Выберите до 5 сервисов:',
#                                         reply_markup=keyboard)
#     await call.message.delete()
#     return
#
#
# # отвечает за добавление выбранного сервиса к мультисервисам
# @user_private_router.callback_query(SMSShop.multiservice_chose, F.data.startswith('multiadd_'))
# async def sms_shop_query(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
#     fsmdata = await state.get_data()
#     chosen_services = fsmdata["chosen_services"]
#     if len(chosen_services) == 5:
#         await call.answer(text='Вы уже выбрали 5 сервисов, переходите к следующему шагу, либо сбросьте сервисы',
#                           show_alert=True)
#         return
#     else:
#         await call.message.delete()
#         service_tag = call.data.split("_")[-1]
#         chosen_services.append(service_tag)
#         print(chosen_services)
#         await state.update_data(chosen_services=chosen_services)
#         pagination_page = 1
#         objects = await get_services_orm(session=session)
#         paginated_objects = pagination_sms(objects=objects, page=pagination_page)
#         total_pages = 1
#         if len(objects) > 18:
#             if len(objects) % 18 == 0:
#                 total_pages = len(objects) // 18
#             else:
#                 total_pages = len(objects) // 18 + 1
#         else:
#             total_pages = 1
#         keyboard = get_multiservice_btns(objects=paginated_objects, current_page=pagination_page,
#                                          total_pages=total_pages, chosen_objects=chosen_services)
#         await send_message_via_telegram_api(chat_id=call.from_user.id, text="Мультисервис",
#                                             reply_markup=keyboard)
#
#         return
#
#
# # очищает массив от всех выбранных элементов
# @user_private_router.callback_query(SMSShop.multiservice_chose, F.data.startswith('clearmulti_'))
# async def sms_shop_query(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
#     await state.update_data(chosen_services=[])
#     chosen_services = []
#     pagination_page = 1
#     objects = await get_services_orm(session=session)
#     paginated_objects = pagination_sms(objects=objects, page=pagination_page)
#     total_pages = 1
#     if len(objects) > 18:
#         if len(objects) % 18 == 0:
#             total_pages = len(objects) // 18
#         else:
#             total_pages = len(objects) // 18 + 1
#     else:
#         total_pages = 1
#     keyboard = get_multiservice_btns(objects=paginated_objects, current_page=pagination_page,
#                                      total_pages=total_pages, chosen_objects=chosen_services)
#     await send_message_via_telegram_api(chat_id=call.from_user.id, text="Мультисервис",
#                                         reply_markup=keyboard)
#     await call.message.delete()
#     return
#
#     # countries = await get_countries_by_multiservice(session=session)
#     #
#     # paginated_objects = pagination(countries, page=1, paginate=5)
#     #
#     # total_pages = 1
#     # if len(countries) > 5:
#     #     if len(countries) % 5 == 0:
#     #         total_pages = len(countries) // 5
#     #     else:
#     #         total_pages = len(countries) // 5 + 1
#     # else:
#     #     total_pages = 1
#     #
#     # await send_message_via_telegram_api(chat_id=call.from_user.id, text='страны по сервису',
#     #                                     reply_markup=await get_sms_countries_btns(countries_dict=paginated_objects,
#     #                                                                               # уже отпагинированные страницы
#     #                                                                               current_page=country_page,
#     #                                                                               # стартует с 1, нет страницы 0
#     #                                                                               total_pages=total_pages,
#     #                                                                               service_tag=service_tag,
#     #                                                                               session=session))
#
#
# # отвечает за выбор страны для мультисервисов
# @user_private_router.callback_query(SMSShop.multiservice_chose, F.data.startswith('choosecountrymultisms_'))
# async def sms_shop_query(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
#     fsmdata = await state.get_data()
#     chosen_services = fsmdata["chosen_services"]
#     country_page = int(call.data.split("_")[-1])
#
#     countries = await get_countries_by_multiservice(session)
#
#     paginated_objects = pagination(countries, page=country_page, paginate=5)
#
#     total_pages = 1
#     if len(countries) > 5:
#         if len(countries) % 5 == 0:
#             total_pages = len(countries) // 5
#         else:
#             total_pages = len(countries) // 5 + 1
#     else:
#         total_pages = 1
#
#     multiservices = await get_multiservice_countries_btns(countries_objects=paginated_objects,
#                                                           chosen_services=chosen_services, current_page=country_page,
#                                                           total_pages=total_pages)
#     if multiservices:
#         await send_message_via_telegram_api(chat_id=call.from_user.id, text='Страны по мультисервисам',
#                                             reply_markup=multiservices)
#     else:
#         await send_message_via_telegram_api(chat_id=call.from_user.id, text='❌Товара нет в наличии')
#
#
# @user_private_router.callback_query(SMSShop.multiservice_chose, F.data.startswith('buymultisms_'))
# async def sms_shop_query(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
#     country_id = int(call.data.split("_")[-1])
#     await state.update_data(country_id=country_id)
#     fsmdata = await state.get_data()
#     chosen_services = fsmdata["chosen_services"]
#
#     total_price = 0
#     for service in chosen_services:
#         price_data = get_price_by_service_and_country(service=service, country_id=country_id)
#         if not price_data:
#             await call.message.answer(text="Один из выбранных сервисов временно недоступен. Попробуйте позже.")
#             return
#         price = float(price_data[f'{country_id}'][service]['cost'])
#         total_price += get_price_with_markup(price)
#
#     if not await check_user_balance(call.from_user.id, session, total_price):
#         await call.message.answer(text="Недостаточно средств на балансе для совершения покупки.")
#         return
#
#     resp = get_multi_numbers(chosen_services, country_id)
#     print(resp)
#     if isinstance(resp, str):
#         await call.message.answer(text=resp)
#     elif isinstance(resp, dict):
#         activation_id = resp['activationId']
#         await state.update_data(activation_id=activation_id, activation=resp)
#
#         user = await orm_get_user(session=session, user_id=call.from_user.id)
#         user.balance -= total_price
#         await orm_add_user(session=session, user=user)
#
#         await call.message.answer(text=f'''
# номер активации: {resp['phoneNumber']}
# дата активации: {resp['activationTime']}
# ''', reply_markup=pokupka_sms_kb)
#         await state.set_state(SMSShop.ojidanie_sms)
#         while True:
#             status = get_activation_status(activation_id)
#             if 'canceled' in status:
#                 break
#             if 'STATUS_OK' in status:
#                 await call.message.answer(text=f'''Ваш код: {status['STATUS_OK']}''', reply_markup=menu_markup)
#                 status.clear()
#                 print("УСПЕХ")
#                 break
#             await asyncio.sleep(5)
#     else:
#         print(type(resp))
#         await call.message.answer(text='Произошла ошибка при получении номера')
#
#
# @user_private_router.callback_query(SMSShop.kupit_sms, F.data == "search_sms_service")
# async def search_sms_service(call: types.CallbackQuery, state: FSMContext):
#     await call.message.answer("Введите название сервиса для поиска:")
#     await state.set_state(SMSShop.search_service)
#
#
# @user_private_router.message(SMSShop.search_service, F.text)
# async def search_service_result(message: types.Message, state: FSMContext, session: AsyncSession):
#     search_query = message.text.lower()
#     services = await get_services_orm(session=session)
#
#     matched_services = [service for service in services if search_query in service.name.lower()]
#
#     if matched_services:
#         keyboard = get_sms_btns(matched_services, current_page=1, total_pages=1)
#         await send_message_via_telegram_api(chat_id=message.from_user.id, text="Результаты поиска:",
#                                             reply_markup=keyboard)
#     else:
#         await message.answer("Сервис не найден. Попробуйте другой запрос.")
#
#     await state.set_state(SMSShop.kupit_sms)
#
#
# @user_private_router.message(F.text.contains('Мануалы'))
# async def search_service_result(message: types.Message, state: FSMContext, session: AsyncSession):
#     await message.answer(text=f'''
# 📚<b>МАНУАЛЫ</b> - @PUNCHMADEBIO
# ''')
#
#
# class PerevodFSM(StatesGroup):
#     sum = State()
#     username = State()
#     confirmation = State()
#
#     async def clear(self) -> None:
#         await self.set_state(state=None)
#         await self.set_data({})
#
#
# @user_private_router.callback_query(F.data.contains('perevesti'))
# async def search_service_result(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
#     await state.set_state(PerevodFSM.sum)
#     await call.message.answer(text='<b>Введите сумму перевода</b>')
#
#
# @user_private_router.message(PerevodFSM.sum)
# async def search_service_result(message: types.Message, state: FSMContext, session: AsyncSession):
#     try:
#         amount = int(message.text)
#     except:
#         await state.clear()
#         await message.answer(text='<b>Неправильная сума перевода</b>')
#         return
#     sender = await orm_get_user(session=session, user_id=message.from_user.id)
#     if sender.balance < amount:
#         await state.clear()
#         await message.answer("Недостаточно средств для перевода")
#         return
#
#     await state.update_data(sender_user_id=message.from_user.id, amount=amount)
#     await message.answer("<b>Введите тег пользователя который получит перевод</b>")
#     await state.set_state(PerevodFSM.username)
#
#
# @user_private_router.message(PerevodFSM.username)
# async def search_service_result(message: types.Message, state: FSMContext, session: AsyncSession):
#     username = message.text
#     # Если юзер начинается с @, удаляем символ @
#     if username.startswith('@'):
#         username = username[1:]
#     # Получаем пользователя из базы данных
#     user = await orm_get_user_by_username(session, username)
#
#     if not user or username == 'None':
#         await state.clear()
#         await message.answer("<b>Пользователь не найден</b>")
#         return
#
#     await state.update_data(geter_user_id=user.user_id)
#     state_data = await state.get_data()
#     await message.answer(text=f'''<b>
# Пользователь: @{username}
# Сумма: {state_data['amount']}
# Верно?
# </b>''', reply_markup=get_callback_btns(btns={'✅Да': 'yes',
#                                               '❌Нет': 'no'}, sizes=(2,)))
#     await state.set_state(PerevodFSM.confirmation)
#
#
# @user_private_router.callback_query(PerevodFSM.confirmation)
# async def search_sms_service(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
#     try:
#         if call.data == 'yes':
#             state_data = await state.get_data()
#             sender_user_id = state_data['sender_user_id']
#             geter_user_id = state_data['geter_user_id']
#             amount = state_data['amount']
#
#             sender = await orm_get_user(session=session, user_id=sender_user_id)
#             if sender.balance < amount:
#                 await state.clear()
#                 await call.message.answer(text="Перевод отменен", reply_markup=menu_markup)
#
#             sender.balance -= amount
#             await orm_add_user(session=session, user=sender)
#             geter = await orm_get_user(session=session, user_id=geter_user_id)
#             geter.balance += amount
#             await orm_add_user(session=session, user=geter)
#             await state.clear()
#             await call.message.answer(text="💛Перевод успешно выполнен", reply_markup=menu_markup)
#             await call.bot.send_message(chat_id=geter.user_id,
#                                         text=f'💵Вам пришел перевод {amount}руб. от @{sender.username}')
#
#         else:
#             await state.clear()
#             await call.message.answer(text="Перевод отменен", reply_markup=menu_markup)
#     except:
#         await state.clear()
#         await call.message.answer(text="Перевод отменен", reply_markup=menu_markup)
#
#
# @user_private_router.callback_query(F.data)
# async def else_cbck(callback: types.CallbackQuery, session: AsyncSession):
#     print(callback.data)
