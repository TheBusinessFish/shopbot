"""
EasyShop Assistant Bot
Core Application Module
"""

import os
import logging
import asyncio
from typing import Final

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
class Config:
    BOT_TOKEN: Final = os.getenv("BOT_TOKEN")
    ADMIN_IDS: Final = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
    YOOKASSA_SHOP_ID: Final = os.getenv("YOOKASSA_SHOP_ID")
    YOOKASSA_SECRET_KEY: Final = os.getenv("YOOKASSA_SECRET_KEY")
    REDIS_URL: Final = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize internationalization
i18n = I18n(path="locales", default_locale="en", domain="messages")

async def setup_handlers(dp: Dispatcher) -> None:
    """Register all application handlers"""
    from handlers import (
        user_commands,
        product_handlers,
        cart_handlers,
        payment_handlers,
        admin_handlers,
        error_handlers
    )
    
    # Include routers
    routers = (
        user_commands.router,
        product_handlers.router,
        cart_handlers.router,
        payment_handlers.router,
        admin_handlers.router
    )
    
    for router in routers:
        dp.include_router(router)
    
    # Register error handler last
    dp.errors.register(error_handlers.error_handler)

async def setup_middlewares(dp: Dispatcher) -> None:
    """Register application middlewares"""
    from middlewares import (
        UserMiddleware,
        ThrottlingMiddleware,
        DatabaseMiddleware
    )
    
    # Execution order matters - first registered runs last
    dp.update.middleware(DatabaseMiddleware())
    dp.update.middleware(UserMiddleware())
    dp.message.middleware(ThrottlingMiddleware())

async def main() -> None:
    """Application entry point"""
    # Initialize bot and dispatcher
    bot = Bot(token=Config.BOT_TOKEN, parse_mode=ParseMode.HTML)
    storage = RedisStorage.from_url(Config.REDIS_URL)
    dp = Dispatcher(storage=storage)
    
    # Configure application
    await setup_handlers(dp)
    await setup_middlewares(dp)
    
    # Register startup/shutdown events
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Start polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

async def on_startup(bot: Bot) -> None:
    """Actions on application startup"""
    logging.info("Starting bot...")
    await bot.send_message(
        chat_id=Config.ADMIN_IDS[0],
        text="🟢 Bot started successfully"
    )

async def on_shutdown(bot: Bot) -> None:
    """Actions on application shutdown"""
    logging.info("Stopping bot...")
    await bot.send_message(
        chat_id=Config.ADMIN_IDS[0],
        text="🔴 Bot stopped"
    )
    await bot.session.close()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped manually")
