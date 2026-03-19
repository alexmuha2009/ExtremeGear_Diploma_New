import requests
import time
import json
import os

TELEGRAM_BOT_TOKEN = '8628245847:AAG3Mlxk2ycbuGVnXg1ouHhzo-j9lqjem6E'
ADMIN_CHAT_ID = '1654502612'
USERS_FILE = 'tg_users.json'

offset = 0

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def register_user(username, chat_id):
    users = load_users()
    users[username.lower()] = str(chat_id)
    save_users(users)

def get_chat_id_by_username(username):
    users = load_users()
    return users.get(username.lower().lstrip('@'))

def get_updates():
    global offset
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {"offset": offset, "timeout": 30}
    try:
        response = requests.get(url, params=params, timeout=35)
        return response.json().get("result", [])
    except:
        return []

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    requests.post(url, data=data)

def forward_to_admin(from_user, text, chat_id):
    username = from_user.get("username", "невідомо")
    first_name = from_user.get("first_name", "невідомо")
    message = (
        f"📬 <b>НОВЕ ПОВІДОМЛЕННЯ ВІД ПОКУПЦЯ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>{first_name}</b> (@{username})\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"💬 {text}"
    )
    send_message(ADMIN_CHAT_ID, message)

waiting_for_address = {}

print("🚀 Extreme Gear Bot запущено!")

while True:
    updates = get_updates()
    for update in updates:
        offset = update["update_id"] + 1
        message = update.get("message", {})
        text = message.get("text", "")
        from_user = message.get("from", {})
        chat_id = str(message.get("chat", {}).get("id", ""))
        username = from_user.get("username", "")
        first_name = from_user.get("first_name", "друже")

        if not text or not chat_id:
            continue

        if username:
            register_user(username, chat_id)

        if text == "/start":
            send_message(chat_id,
                f"🏔️ <b>Вітаємо в Extreme Gear!</b>\n\n"
                f"Привіт, <b>{first_name}</b>! 👋\n\n"
                f"Я офіційний бот магазину екстремального спорядження.\n\n"
                f"<b>Що я вмію:</b>\n"
                f"📦 Надсилати підтвердження замовлень\n"
                f"🚚 Уточнювати деталі доставки\n"
                f"💬 Передавати питання менеджеру\n\n"
                f"✅ <b>Ви успішно підключені!</b>\n"
                f"При замовленні на сайті вкажіть username "
                f"<code>@{username}</code> — і все прийде сюди.\n\n"
                f"📌 /help — довідка"
            )

        elif text == "/help":
            send_message(chat_id,
                f"❓ <b>Довідка Extreme Gear Bot</b>\n\n"
                f"<b>Як отримати сповіщення про замовлення:</b>\n"
                f"1️⃣ Напишіть /start цьому боту\n"
                f"2️⃣ На сайті extremegear.com у полі Telegram вкажіть <code>@{username}</code>\n"
                f"3️⃣ Після замовлення бот надішле підтвердження і запитає адресу доставки\n\n"
                f"<b>Контакти магазину:</b>\n"
                f"🌐 extremegear.com\n"
                f"📞 +380 68 672 69 60\n\n"
                f"💬 Будь-яке питання — просто напишіть сюди, менеджер відповість!"
            )

        elif chat_id in waiting_for_address:
            order_info = waiting_for_address.pop(chat_id)
            forward_to_admin(from_user,
                f"📍 <b>Адреса доставки:</b>\n{text}\n\n"
                f"🛒 <b>Замовлення:</b>\n{order_info}",
                chat_id
            )
            send_message(chat_id,
                f"✅ <b>Адресу отримано, {first_name}!</b>\n\n"
                f"📍 <b>Ваша адреса:</b>\n{text}\n\n"
                f"🚚 Менеджер підтвердить замовлення найближчим часом.\n"
                f"💬 Якщо є питання — пишіть прямо сюди!"
            )

        else:
            forward_to_admin(from_user, text, chat_id)
            send_message(chat_id,
                f"✅ <b>Повідомлення отримано!</b>\n\n"
                f"Менеджер відповість найближчим часом, {first_name} 👌"
            )

    time.sleep(1)