def get_dice_game_text(game, game_value):
    if game.game_type in ["dice", "bdice", "куб", "бкуб"]:
        text = f'''
🎲 <b>Кубик</b> 🎲

🔢Вы выбрали число: <code>{game_value}</code>
'''
    if game.game_type in ["больше", "ббольше", "more", "bmore"]:
        text = f'''
↗️ <b>Больше</b> ↖️

'''
    if game.game_type in ["меньше", "бменьше", "less", "bless"]:
        text = f'''
↘️ <b>Меньше</b> ↙️

'''
    text += f'''
💰Ставка: <b>{game.amount}₽</b>

'''
    if game.game_type[0] not in ["b", "б"]:
        text += f'''
<blockquote>Бросьте <code>🎲</code> в ОТВЕТ на ЭТО сообщение, что бы начать игру</blockquote>
'''

    return text


def update_dice_game_text(original_text, is_win, win_amount):
    """
    Обновляет текст сообщения в зависимости от результата игры.

    :param original_text: Исходный текст сообщения.
    :param is_win: Булево значение (True, если выигрыш, False, если проигрыш).
    :param win_amount: Сумма выигрыша или проигрыша.
    :return: Обновленный текст сообщения.
    """
    # Удаляем строку с предложением бросить кубик
    updated_text = original_text.split('\n')
    updated_text = [line for line in updated_text if "Бросьте" not in line]

    # Добавляем сообщение о результате
    result_text = f"\n🎉 Вы выиграли <b>{win_amount}₽</b>! 🎉" if is_win else f"\n😞 Вы проиграли <b>{win_amount}₽</b>. 😞"

    updated_text.append(result_text)

    return '\n'.join(updated_text)


def get_mines_text(gamer, price, count_mins, next_hod_x, status=None, prize=None):
    if status == "LOSE":
        text = f'''
💥 <b>Вы проиграли!</b>
💣 <b>Игра: Mines</b>
👤 <b>Игрок:</b> @{gamer}
💵 <b>Ставка:</b> <code>{price}₽</code>
❌ <b>Вы наткнулись на мину!</b>

😢 Попробуйте снова и удача может быть на вашей стороне!
    '''
    elif status == "WON":
        text = f'''
🎉 <b>Поздравляем, вы выиграли!</b>
💣 <b>Игра: Mines</b>
👤 <b>Игрок:</b> @{gamer}
💵 <b>Ставка:</b> <code>{price}₽</code>
💰 <b>Ваш выигрыш:</b> <code>{prize}₽</code>

🔥 Отличная игра! Хотите сыграть ещё раз?
    '''
    else:
        text = f'''
💣 <b>Игра: Mines</b>
👤 <b>Игрок:</b> @{gamer}
💵 <b>Ставка:</b> <code>{price}₽</code>
🔽 <b>Количество мин:</b> <code>{count_mins}</code>
💲 <b>Следующий ход:</b> <code>{int(price * next_hod_x)}₽</code>

❗ <b>При возникновении проблем с игрой:</b> используйте команду <code>/mines</code>.
        '''
    return text

