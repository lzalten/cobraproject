from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

import bot.config as config
from kbrds.inline import get_callback_btns
from services.chanel_service import is_user_subscribed


async def get_profile_text(user, user_games):

    text = f'''
<b>🧑‍✈️Ваш профиль</b>
<b>🆔Ваш ID:</b> {user.user_id}
<b>💰Ваш баланс:</b> {user.balance}

<b>🎲Количество игр: </b> {user_games.get('total', 0)}

<b>🫅Пригласивший вас игрок: </b> {user.referrer_id or '-'}
<b>♻️Ваша реферальная ссылка:</b> https://t.me/{config.BOT_NAME}?start=ref_{user.user_id}
    '''
    return text


def get_games_text():
    text = f'''
🎲 <b>Доступные игры:</b>

🎲 <b>КУБИК</b>
▫️ Использование: <code>/dice &lt;сумма&gt; &lt;число&gt;</code>
▫️ Доступные команды: <b>/dice</b>, <b>/кубик</b>, 🚀<b>/bdice</b>, 🚀<b>/бкубик</b>

🪙 <b>МОНЕТКА</b>
▫️ Использование: <code>/orel &lt;сумма&gt;</code>
▫️ Доступные команды: <b>/orel</b>, <b>/reshka</b>, <b>/орел</b>, <b>/решка</b>

📉 <b>БОЛЬШЕ/МЕНЬШЕ</b>
▫️ Использование: <code>/less &lt;сумма&gt;</code>
▫️ Доступные команды: <b>/less</b>, <b>/меньше</b>, <b>/more</b>, <b>/больше</b>, 🚀<b>/bmore</b>, 🚀<b>/бменьше</b>, 🚀<b>/bless</b>, 🚀<b>/больше</b>

🎰 <b>СЛОТЫ</b>
▫️ Использование: <code>/slots &lt;сумма&gt;</code>
▫️ Доступные команды: <b>/slots</b>, <b>/слоты</b>, 🚀<b>/bslots</b>, 🚀<b>/бслоты</b>

💣 <b>МИНЫ</b>
▫️ Использование: <code>/mines &lt;мины&gt; &lt;сумма&gt;</code>
▫️ Доступные команды: <b>/mines</b>, <b>/мины</b>, <b>/mins</b>

🎡 <b>РУЛЕТКА</b>
▫️ Использование: <code>/roulette &lt;сумма&gt;</code>
▫️ Доступные команды: <b>/roulette</b>, <b>/рулетка</b>,

⚡ <b>Быстрые команды</b> для игр "Больше/Меньше" и "Кубик":
▫️ <b>/бкубик</b> — бот сам бросит кубик за вас.
▫️ <b>/ббольше</b> — быстрая игра на "Больше".

    '''
    return text


def get_ref_text(ref_count, current_percent, earned_from_ref, ref_link):
    text = f"""
🎉 <b>Зарабатывай на рефералах!</b> 🎉  

Приглашай друзей и получай <b>% с их пополнений</b>! 💰  

📊 <b>Таблица начислений:</b>  
▫️ <b>1 - 5</b> рефералов → <i>1% с пополнений</i>  
▫️ <b>6 - 10</b> рефералов → <i>2% с пополнений</i>  
▫️ <b>11 - 15</b> рефералов → <i>3% с пополнений</i>  
▫️ <b>16 - 20</b> рефералов → <i>4% с пополнений</i>  
▫️ <b>21+</b> рефералов → <i>5% с пополнений</i>  

⚠️ <b>Важно!</b>  
Реферал засчитывается, если <b>зарегистрировался</b> в боте по вашей ссылке и сделал <b>ставок на 300₽</b>.  

👥 <b>Ваши рефералы:</b> <code>{ref_count}</code>  
📈 <b>Текущий процент с пополнений:</b> <code>{current_percent}%</code>  
💸 <b>Заработано с рефералов:</b> <code>{earned_from_ref}₽</code>  

🔗 <b>Ваша реферальная ссылка:</b>  
👉 <code>{ref_link}</code>
        """

    return text


def get_user_balance_text(user, transactions):
    text = f'''
💰 <b>Баланс:</b> <code>{user.balance}₽</code>

📥 <b>Пополнения:</b>
▫️ <b>Всего:</b> <code>{transactions["deposits"]["total"]}₽</code>
▫️ <b>За неделю:</b> <code>{transactions["deposits"]["week"]}₽</code>
▫️ <b>За месяц:</b> <code>{transactions["deposits"]["month"]}₽</code>

📤 <b>Выводы:</b>
▫️ <b>Всего:</b> <code>{transactions["withdrawals"]["total"]}₽</code>
▫️ <b>За неделю:</b> <code>{transactions["withdrawals"]["week"]}₽</code>
▫️ <b>За месяц:</b> <code>{transactions["withdrawals"]["month"]}₽</code>

💡 <b>Чтобы пополнить баланс или вывести деньги, используйте кнопки ниже.</b>
    '''
    return text

