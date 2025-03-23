import asyncio
import logging
import os
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup
from dotenv import load_dotenv

# Устанавливаем русскую локаль для корректного отображения месяцев
months_ru = {
    1: "январь", 2: "февраль", 3: "март", 4: "апрель",
    5: "май", 6: "июнь", 7: "июль", 8: "август",
    9: "сентябрь", 10: "октябрь", 11: "ноябрь", 12: "декабрь"
}

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Проверяем, найден ли токен
if not TOKEN:
    raise ValueError("Токен бота не найден. Проверьте .env файл.")

# Создание бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Список услуг
services = [
    "коммунальные услуги 🏠🛁🚽",
    "доступ в интернет 🛜",
    "вывоз ТБО 🚛",
    "электроэнергия 🔌 ⚡"
]

# Словарь для хранения данных пользователя
user_data = {}

# Функция для получения предыдущего месяца на русском языке
def get_previous_month():
    current_month = datetime.now().month
    previous_month = current_month - 1 if current_month > 1 else 12
    return months_ru[previous_month]

# Кнопки "Запуск" и "Стоп"
start_stop_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Запуск"), KeyboardButton(text="Стоп")]
    ],
    resize_keyboard=True
)


# Команда /start
@dp.message(Command("start"))
async def start(message: Message):
    chat_id = message.chat.id
    user_data[chat_id] = {"step": 0, "values": [], "month": get_previous_month()}

    await message.answer(
        f"Привет!👋\nЯ помогу посчитать твои коммунальные платежи 💸 за **{user_data[chat_id]['month']}**.\n"
        "Нажми кнопку _'СТАРТ'_ для начала ▶️",
        reply_markup=start_stop_keyboard,
        parse_mode="Markdown"
    )


# Обработчик кнопки "Запуск"
@dp.message(lambda message: message.text == "Запуск")
async def handle_start_button(message: Message):
    chat_id = message.chat.id

    if chat_id not in user_data:
        user_data[chat_id] = {"step": 0, "values": [], "month": get_previous_month()}

    await ask_next_service(message)


# Обработчик кнопки "Стоп"
@dp.message(lambda message: message.text == "Стоп")
async def handle_stop_button(message: Message):
    chat_id = message.chat.id

    if chat_id in user_data:
        del user_data[chat_id]  # Очищаем данные пользователя

    await message.answer("Бот остановлен. Напишите /start, чтобы начать заново.", reply_markup=start_stop_keyboard)


# Функция для запроса стоимости следующей услуги
async def ask_next_service(message: Message):
    chat_id = message.chat.id
    step = user_data[chat_id]["step"]

    if step < len(services):
        await message.answer(
            f"Введите стоимость **{services[step]}** за **{user_data[chat_id]['month']}**:",
            parse_mode="Markdown"
        )
    else:
        total = sum(user_data[chat_id]["values"])
        await message.answer(
            f"К оплате 💰(всего 🏠🛁🚽🚛🛜🔌) за **{user_data[chat_id]['month']}**: *{total} ₽*",
            parse_mode="Markdown"
        )
        del user_data[chat_id]  # Очищаем данные пользователя


# Обработка ответов пользователя
@dp.message()
async def process_input(message: Message):
    chat_id = message.chat.id

    if chat_id not in user_data:
        await message.answer("Напишите /start, чтобы начать заново.")
        return

    try:
        value = float(message.text)
        user_data[chat_id]["values"].append(value)
        user_data[chat_id]["step"] += 1
        await ask_next_service(message)
    except ValueError:
        await message.answer("Пожалуйста, введи корректную сумму (число).")


# Запуск бота
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
