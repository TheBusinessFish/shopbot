"""
Telegram Shop Bot (Minimal Version)
Description: Basic e-commerce bot with payment support
Author: YourName
"""

import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Configuration
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 123456789  # Replace with your ID

# Initialize bot
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    """Send welcome message"""
    await message.answer("🛍️ Welcome to ShopBot!\nUse /menu to browse products.")

@dp.message(Command("menu"))
async def show_menu(message: types.Message):
    """Show product menu"""
    await message.answer("📦 Available products:\n\n1. Product 1 - $10\n2. Product 2 - $15")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dp.run_polling(bot)
