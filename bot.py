import logging
import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher import filters
from aiogram.utils import executor

API_TOKEN = '7692626473:AAEgJxf5PS_RG0_geBIqP3V8UU1uKlzmwl8'
GROUP_CHAT_ID = '-1002247244049' # Замените на ID вашей группы

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Создание базы данных
async def create_db():
    try:
        async with aiosqlite.connect('support.db') as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    message TEXT
                )
            ''')
            await db.commit()
        logging.info("База данных создана/проверена.")
    except Exception as e:
        logging.error(f"Ошибка при создании базы данных: {e}")


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Напишите свой вопрос.")

@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.reply("Просто напишите свой вопрос.")

@dp.message_handler(lambda message: message.text, content_types=types.ContentTypes.TEXT)
async def handle_message(message: types.Message):
    try:
        async with aiosqlite.connect('support.db') as db:
            await db.execute('INSERT INTO messages (user_id, message) VALUES (?, ?)', (message.from_user.id, message.text))
            await db.commit()
        await bot.send_message(GROUP_CHAT_ID, f"Новый вопрос от {message.from_user.full_name}:\n{message.text}")
    except Exception as e:
        logging.error(f"Ошибка при сохранении сообщения в БД: {e}")


@dp.message_handler(lambda message: message.chat.type == types.ChatType.GROUP and message.reply_to_message and message.text)
async def handle_group_message(message: types.Message):
    # ... (ваш код обработки группового сообщения) ...
    try:
        if message.reply_to_message and message.reply_to_message.from_user.id == bot.id:
            reply_text = message.reply_to_message.text
            try:
                user_id_str = reply_text.split(':')[0].split(' ')[-1]
                user_id = int(user_id_str)
                await bot.send_message(user_id, f"Ответ от администратора: {message.text}")
            except (IndexError, ValueError):
                logging.error(f"Не удалось извлечь user_id из сообщения: {reply_text}")
    except Exception as e:
        logging.error(f"Ошибка при обработке группового сообщения: {e}")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_db())
    executor.start_polling(dp, skip_updates=True)

import asyncio
    
