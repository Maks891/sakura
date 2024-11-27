import logging
import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher import filters
from aiogram.utils import executor

API_TOKEN = '7692626473:AAEgJxf5PS_RG0_geBIqP3V8UU1uKlzmwl8'
GROUP_CHAT_ID = '-1002247244049'  # Замените на ID вашей группы

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Создание базы данных
async def create_db():
    async with aiosqlite.connect('support.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                message TEXT
            )
        ''')
        await db.commit()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Нажмите на кнопку, чтобы задать вопрос.")

@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.reply("Если у вас есть вопрос, просто напишите его.")

@dp.message_handler(lambda message: message.text, content_types=types.ContentTypes.TEXT)
async def handle_message(message: types.Message):
    # Сохранение сообщения в базу данных
    async with aiosqlite.connect('support.db') as db:
        await db.execute('INSERT INTO messages (user_id, message) VALUES (?, ?)', (message.from_user.id, message.text))
        await db.commit()

    # Отправка сообщения в группу
    await bot.send_message(GROUP_CHAT_ID, f"Новый вопрос от {message.from_user.full_name}:\n{message.text}")

@dp.message_handler(filters.ChatType.GROUP)
async def handle_group_message(message: types.Message):
    if message.reply_to_message and message.reply_to_message.from_user.id == bot.id:
        user_id = message.reply_to_message.text.split(':')[0].split(' ')[-1]
        await bot.send_message(user_id, f"Ответ от администратора: {message.text}")

if __name__ == '__main__':
    loop = create_db()
    loop.run_until_complete(create_db())
    executor.start_polling(dp, skip_updates=True)
