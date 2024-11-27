import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher import filters
from aiogram.utils import executor
import sqlite3

API_TOKEN = '7692626473:AAEgJxf5PS_RG0_geBIqP3V8UU1uKlzmwl8'
GROUP_CHAT_ID = '-1002247244049'

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Создание базы данных SQLite
def db_start():
    conn = sqlite3.connect('support_requests.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            question TEXT
        )
    ''')
    conn.commit()
    conn.close()

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Задать вопрос", callback_data="ask_question")
    keyboard.add(button)
    await message.answer("Привет! Нажми на кнопку, чтобы задать вопрос.", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'ask_question')
async def process_callback_query(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Введите ваш вопрос:")

@dp.message_handler(lambda message: message.text and message.chat.type == 'private')
async def handle_question(message: types.Message):
    user_id = message.from_user.id
    question = message.text

    # Сохранение вопроса в базе данных
    conn = sqlite3.connect('support_requests.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO requests (user_id, question) VALUES (?, ?)', (user_id, question))
    conn.commit()
    conn.close()

    # Отправка вопроса в группу
    await bot.send_message(GROUP_CHAT_ID, f"Новый вопрос от пользователя {user_id}: {question}")

    await message.answer("Ваш вопрос отправлен администратору. Ожидайте ответа.")

@dp.message_handler(filters.ChatType.GROUP)
async def handle_group_message(message: types.Message):
    if message.reply_to_message and message.reply_to_message.from_user.id == bot.id:
        # Если это ответ на вопрос от бота
        user_id = message.reply_to_message.text.split(":")[1].strip().split()[0]
        await bot.send_message(user_id, f"Ответ от администратора: {message.text}")

if __name__ == '__main__':
    db_start()
    executor.start_polling(dp, skip_updates=True)
