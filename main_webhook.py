import asyncio
import os
import logging
import sys
from aiohttp import web

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.handlers import register_handlers
from database.operations import init_db
from utils.config import load_config
from utils.logger import setup_logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

async def on_startup(bot: Bot, base_url: str):
    """تنظیم webhook هنگام شروع"""
    await bot.set_webhook(f"{base_url}/webhook")
    logging.info(f"Webhook set to: {base_url}/webhook")

async def on_shutdown(bot: Bot):
    """پاک کردن webhook هنگام توقف"""
    await bot.delete_webhook()
    logging.info("Webhook deleted")

async def main():
    """ورژن Webhook برای Render"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🚀 Starting Webhook Bot on Render...")
        config = load_config()
        
        # مقداردهی
        await init_db()
        
        # ایجاد bot و dispatcher
        bot = Bot(token=config.bot.token)
        dp = Dispatcher(storage=MemoryStorage())
        
        # ثبت handlerها
        register_handlers(dp)
        
        # ایجاد برنامه aiohttp
        app = web.Application()
        
        # دریافت آدرس Render
        render_url = os.getenv('RENDER_EXTERNAL_URL', 'https://your-app-name.onrender.com')
        
        # تنظیم startup/shutdown
        app.on_startup.append(lambda app: on_startup(bot, render_url))
        app.on_shutdown.append(lambda app: on_shutdown(bot))
        
        # ایجاد webhook handler
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        
        # ثبت مسیر webhook
        webhook_requests_handler.register(app, path="/webhook")
        
        # تنظیم application
        setup_application(app, dp, bot=bot)
        
        # route اصلی برای سلامت سرویس
        async def health_check(request):
            return web.Response(text="✅ Bot is running!")
        
        app.router.add_get("/", health_check)
        app.router.add_get("/health", health_check)
        
        logger.info(f"🌐 Webhook URL: {render_url}/webhook")
        logger.info("🟢 Bot is ready to receive updates via Webhook!")
        
        # اجرای سرور
        port = int(os.getenv("PORT", 10000))
        return app
        
    except Exception as e:
        logger.error(f"❌ Failed to start: {e}")
        raise

if __name__ == "__main__":
    app = asyncio.run(main())
    
    # اجرای سرور
    port = int(os.getenv("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)