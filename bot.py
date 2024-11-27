import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import filters
from aiogram.utils import executor

API_TOKEN = '7692626473:AAEgJxf5PS_RG0_geBIqP3V8UU1uKlzmwl8'
GROUP_CHAT_ID = '-1002247244049'
# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Подключение к базе данных SQLite
conn = sqlite3.connect('support_requests.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT
    )
''')
conn.commit()

# Команда /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Добро пожаловать! Нажмите кнопку для отправки запроса в техподдержку.", reply_markup=main_menu())

# Функция для создания клавиатуры
def main_menu():
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Запросить поддержку", callback_data="support_request")
    keyboard.add(button)
    return keyboard

# Обработка нажатия на кнопку
@dp.callback_query_handler(filters.Text(equals="support_request"))
async def handle_support_request(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Введите ваш вопрос:")

# Обработка текстового сообщения от пользователя
@dp.message_handler(lambda message: message.chat.type == 'private')
async def handle_message(message: types.Message):
    # Сохранение запроса в базе данных
    cursor.execute('INSERT INTO requests (user_id, message) VALUES (?, ?)', (message.from_user.id, message.text))
    conn.commit()

    # Отправка сообщения в группу
    await bot.send_message(GROUP_CHAT_ID, f"Новый запрос от {message.from_user.first_name} ({message.from_user.id}): {message.text}")

    await message.reply("Ваш запрос отправлен в техподдержку. Ожидайте ответа.")

# Обработка ответов администраторов в группе
@dp.message_handler(filters.ChatTypeFilter(types.ChatType.GROUP))
async def handle_group_message(message: types.Message):
    if message.chat.id == GROUP_CHAT_ID:
        # Здесь можно добавить логику для отправки ответа пользователю
        user_id = extract_user_id_from_message(message.text)
        if user_id:
            await bot.send_message(user_id, f"Ответ от администратора: {message.text}")

def extract_user_id_from_message(text):
    # Извлечение user_id из текста сообщения (например, если формат: "Ответ от админа для 123456: ...")
    parts = text.split(":")
    if len(parts) > 0:
        user_id_part = parts[0].split(" ")[-1]
        return int(user_id_part) if user_id_part.isdigit() else None
    return None

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
