import asyncio
import logging
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import directly from folders (استفاده از ایمپورت مستقیم)
from bot.handlers import register_handlers
from database.operations import init_db
from utils.config import load_config
from utils.logger import setup_logging
from scheduler.tasks import start_crawler_tasks
from admin.panel import register_admin_handlers

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def main():
    """Main application entry point"""
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config()
        
        # Check if bot token is provided
        if not config.bot.token or config.bot.token == "your_bot_token_here":
            logger.error("Bot token not configured. Please set BOT_TOKEN in .env file")
            return
        
        # Initialize database
        logger.info("Initializing database...")
        await init_db()
        
        # Initialize bot and dispatcher
        logger.info("Initializing bot...")
        bot = Bot(token=config.bot.token)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Register handlers
        logger.info("Registering handlers...")
        register_handlers(dp)
        register_admin_handlers(dp)
        
        # Initialize scheduler
        logger.info("Initializing scheduler...")
        scheduler = AsyncIOScheduler()
        
        # Start crawler tasks
        logger.info("Starting crawler tasks...")
        await start_crawler_tasks(scheduler, bot)
        
        # Start the bot
        logger.info("Starting bot polling...")
        
        # Set bot commands (optional)
        await set_bot_commands(bot)
        
        # Start polling
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
    
    finally:
        # Cleanup
        if 'bot' in locals():
            await bot.session.close()

async def set_bot_commands(bot: Bot):
    """Set bot commands for better user experience"""
    from aiogram.types import BotCommand, BotCommandScopeDefault
    
    commands = [
        BotCommand(command="start", description="شروع کار با ربات"),
        BotCommand(command="filter", description="تنظیم فیلترهای جستجو"),
        BotCommand(command="update_filter", description="به‌روزرسانی فیلترها"),
        BotCommand(command="reset_filter", description="حذف فیلترها"),
        BotCommand(command="status", description="مشاهده وضعیت فعلی"),
        BotCommand(command="help", description="راهنمای استفاده"),
        BotCommand(command="admin", description="پنل مدیریت (فقط ادمین)"),
    ]
    
    try:
        await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
        logging.info("Bot commands set successfully")
    except Exception as e:
        logging.error(f"Failed to set bot commands: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")