import asyncio
import firebase_admin
from firebase_admin import credentials, firestore
from pyrogram import Client, filters
from pyrogram.types import Message
import time
import logging

# === Настройки ===
TELEGRAM_BOT_TOKEN = "8531993653:AAFJHWYMpumihCIVdrdhiTJcd95NpQTNccE"
ADMIN_USER_ID = 7700429042  # Твой Telegram ID
CHECK_INTERVAL = 5  # секунд между проверками новых регистраций

# Инициализация Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Инициализация Telegram-бота
app = Client("rid3_yt_bot", bot_token=TELEGRAM_BOT_TOKEN, api_id=2040, api_hash="b1844181088fe440ac8c420662eed376")

# Словарь для отслеживания уже обработанных пользователей
notified_users = set()

async def check_new_registrations():
    """Проверяет Firestore на новые регистрации и отправляет уведомления"""
    global notified_users
    while True:
        try:
            # Получаем всех пользователей из коллекции profiles
            users_ref = db.collection("profiles")
            docs = users_ref.stream()

            for doc in docs:
                user_id = doc.id
                if user_id in notified_users:
                    continue

                data = doc.to_dict()
                email = data.get("email", "—")
                name = data.get("displayName", "—")
                created = data.get("createdAt")

                # Преобразуем timestamp в читаемую дату (если нужно)
                if created:
                    try:
                        reg_time = created.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        reg_time = str(created)
                else:
                    reg_time = "—"

                # Отправляем сообщение админу
                msg = (
                    f"🆕 Новая регистрация!\n\n"
                    f"ID: `{user_id}`\n"
                    f"Имя: {name}\n"
                    f"Email: {email}\n"
                    f"Время: {reg_time}"
                )
                await app.send_message(ADMIN_USER_ID, msg, parse_mode="markdown")
                notified_users.add(user_id)
                print(f"[+] Уведомление отправлено для {user_id}")

        except Exception as e:
            print(f"[!] Ошибка при проверке регистраций: {e}")

        await asyncio.sleep(CHECK_INTERVAL)

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply("Привет! Я бот @Rid3_yt. Я слежу за новыми регистрациями на сайте.")

@app.on_message(filters.private & ~filters.command("start"))
async def handle_private(client: Client, message: Message):
    await message.reply("Я только слежу за новыми пользователями. Команды не поддерживаю.")

async def main():
    await app.start()
    print("[+] Бот запущен. Проверка регистраций...")
    await check_new_registrations()

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    asyncio.run(main())
