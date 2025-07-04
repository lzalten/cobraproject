import requests
import time
from datetime import datetime

# Токен вашего бота
BOT_TOKEN = "6880816947:AAEqfh7zQ2dCybGmpnw_Yd3qixipT69Kzqs"

# URL для Telegram API
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_updates(offset=None):
    """
    Отправляет запрос на getUpdates для получения последних обновлений.
    """
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 10, "allowed_updates": ["callback_query"]}
    if offset:
        params["offset"] = offset

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def main():
    """
    Основной цикл: раз в секунду запрашивает обновления и выводит уникальные callback-запросы.
    """
    offset = None  # Смещение для обработки новых обновлений
    seen_callbacks = set()  # Множество для хранения обработанных callback-запросов

    while True:
        result = get_updates(offset)

        if result and result.get("ok") and result.get("result"):
            for update in result["result"]:
                # Обновляем offset, чтобы исключить старые обновления
                offset = update["update_id"] + 1

                # Проверяем, есть ли callback_query
                callback_query = update.get("callback_query")
                if callback_query:
                    user = callback_query["from"]
                    callback_data = callback_query.get("data", "Нет данных")
                    user_id = user["id"]
                    message_id = callback_query["message"]["message_id"]

                    # Уникальный ключ для callback-запроса
                    callback_key = (user_id, callback_data, message_id)

                    # Проверяем, не обрабатывали ли мы этот callback ранее
                    if callback_key not in seen_callbacks:
                        seen_callbacks.add(callback_key)
                        timestamp = datetime.fromtimestamp(callback_query["message"]["date"]).strftime("%Y-%m-%d %H:%M:%S")
                        print(
                            f"username={user.get('username', 'N/A')}, "
                            f"data={callback_data}, "
                            f"time={timestamp}"
                        )

        # Очистка старых callback-запросов (чтобы не накапливать память)
        if len(seen_callbacks) > 1000:
            seen_callbacks.clear()

        # Задержка 2 секунды
        time.sleep(5)

if __name__ == "__main__":
    try:
        print("Запуск скрипта для получения callback-запросов")
        main()
    except KeyboardInterrupt:
        print("Скрипт остановлен пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {e}")