import asyncio
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.handlers import register_handlers
from database.operations import init_db
from utils.config import load_config
from utils.logger import setup_logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import TCPConnector

async def main():
    """Version with better connection handling"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🚀 Starting Property Bot...")
        config = load_config()
        
        logger.info("📦 Initializing database...")
        await init_db()
        
        logger.info("🤖 Initializing bot with custom session...")
        
        # ایجاد session با تنظیمات بهتر
        bot = Bot(
            token=config.bot.token,
            timeout=60,
            session_timeout=60
        )
        
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        logger.info("📝 Registering handlers...")
        register_handlers(dp)
        
        logger.info("🎯 Starting bot polling...")
        logger.info("⏳ This may take a few minutes due to network restrictions...")
        
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        logger.info("💡 Solutions:")
        logger.info("1. Use VPN")
        logger.info("2. Try again later")
        logger.info("3. Run on a VPS outside Iran")
    
    finally:
        if 'bot' in locals():
            await bot.session.close()

if __name__ == "__main__":
    print("=" * 50)
    print("🔧 Telegram Property Bot")
    print("📱 Bot Token: 8478444625:...")
    print("🌐 Make sure you have stable internet connection")
    print("=" * 50)
    asyncio.run(main())