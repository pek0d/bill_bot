import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, List

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Constants
MONTHS_RU = {
    1: "январь", 2: "февраль", 3: "март", 4: "апрель",
    5: "май", 6: "июнь", 7: "июль", 8: "август",
    9: "сентябрь", 10: "октябрь", 11: "ноябрь", 12: "декабрь"
}

SERVICES = [
    "коммунальные услуги 🏠🛁🚽",
    "доступ в интернет 🛜",
    "вывоз ТБО 🚛",
    "электроэнергия 🔌 ⚡"
]

# Initialize bot and dispatcher
bot = Bot(token=os.getenv("BOT_TOKEN", "").strip())
dp = Dispatcher()

# User data storage
class UserData:
    def __init__(self, month: str):
        self.step = 0
        self.values: List[float] = []
        self.month = month

# Global user data storage
user_data: Dict[int, UserData] = {}

# Helper functions
def get_previous_month() -> str:
    """Get previous month name in Russian."""
    current_month = datetime.now().month
    previous_month = current_month - 1 if current_month > 1 else 12
    return MONTHS_RU[previous_month]

# Keyboards
calculate_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="СОСЧИТАТЬ НОВЫЙ СЧЕТ")]],
    resize_keyboard=True
)

# Handlers
@dp.message(Command("start"))
async def start(message: Message):
    """Handle /start command."""
    chat_id = message.chat.id
    user_data[chat_id] = UserData(month=get_previous_month())
    
    await message.answer(
        f"Привет!👋\nЯ помогу посчитать твои коммунальные платежи 💸 за **{user_data[chat_id].month}**.\n"
        "Нажмите кнопку, чтобы начать.",
        reply_markup=calculate_keyboard,
        parse_mode="Markdown"
    )

@dp.message(lambda message: message.text == "СОСЧИТАТЬ НОВЫЙ СЧЕТ")
async def handle_calculate_button(message: Message):
    """Handle calculate button press."""
    chat_id = message.chat.id
    if chat_id not in user_data:
        user_data[chat_id] = UserData(month=get_previous_month())
    await ask_next_service(message)

async def ask_next_service(message: Message):
    """Ask for the next service."""
    chat_id = message.chat.id
    if chat_id not in user_data:
        return
    
    user = user_data[chat_id]
    if user.step < len(SERVICES):
        await message.answer(
            f"Введите **{SERVICES[user.step]}** за **{user.month}**:",
            parse_mode="Markdown"
        )
        user.step += 1
    else:
        await show_services(message)

@dp.message()
async def process_input(message: Message):
    """Process user input."""
    chat_id = message.chat.id
    if chat_id not in user_data:
        return
    
    user_data[chat_id].values.append(message.text)
    await ask_next_service(message)

async def show_services(message: Message):
    """Show all entered services and calculate total."""
    chat_id = message.chat.id
    if chat_id not in user_data:
        return
    
    user = user_data[chat_id]
    response = f"Ваши данные за **{user.month}**:\n\n"
    for service, value in zip(SERVICES, user.values):
        response += f"- {service}: {value}\n"
    
    # Calculate total
    try:
        total = sum(float(v.replace(',', '.')) for v in user.values)
        total_response = f"\nИтоговая сумма 🧮: *{total:.2f} рублей*"
        await message.answer(total_response, parse_mode="Markdown")
    except ValueError:
        total_response = "\nНе удалось посчитать итоговую сумму (некоторые значения не являются числами)"
        await message.answer(total_response)
    
    await message.answer(response, parse_mode="Markdown")
    
    # Reset user data
    del user_data[chat_id]

# Main function
async def main():
    """Start the bot."""
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot error: {e}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
