import logging
import asyncio
import os
import sys

# اضافه کردن پوشه فعلی به مسیر
sys.path.append('/home/runner/workspace')

# تنظیمات لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# دریافت توکن از environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not found in environment variables!")
    exit(1)

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from bot.handlers import register_handlers

# ایجاد بوت و دیسپچر
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ثبت هندلرها
register_handlers(dp)

async def main():
    logger.info("🚀 Starting Telegram Bot...")
    
    try:
        # حذف webhook قدیمی (اگر وجود دارد)
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Webhook deleted successfully")
        
        # شروع پولینگ
        logger.info("✅ Bot started successfully!")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
