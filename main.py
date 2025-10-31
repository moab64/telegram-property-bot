import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# تنظیمات لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# دریافت توکن
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not found!")
    exit(1)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()

class TestStates(StatesGroup):
    city = State()

# کیبورد تستی با شهرهای جدید
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_test_city_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="ساری", callback_data="city_sari"),
            InlineKeyboardButton(text="قائمشهر", callback_data="city_qaemshahr")
        ],
        [
            InlineKeyboardButton(text="بابل", callback_data="city_babol"),
            InlineKeyboardButton(text="بهشهر", callback_data="city_behshahr")
        ],
        [
            InlineKeyboardButton(text="نکا", callback_data="city_neka"),
            InlineKeyboardButton(text="جویبار", callback_data="city_joybar")
        ]
    ])
    return keyboard

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "🎯 **ربات تست - شهرهای جدید**\n\n"
        "برای دیدن شهرهای جدید روی دکمه زیر کلیک کن:",
        reply_markup=get_test_city_keyboard()
    )

@router.callback_query(F.data.startswith("city_"))
async def handle_city(callback: CallbackQuery):
    city_code = callback.data.split("_")[1]
    city_names = {
        'sari': 'ساری',
        'qaemshahr': 'قائمشهر',
        'babol': 'بابل',
        'behshahr': 'بهشهر',
        'neka': 'نکا',
        'joybar': 'جویبار'
    }
    city_name = city_names.get(city_code, city_code)
    
    await callback.message.edit_text(f"✅ شما شهر {city_name} را انتخاب کردید!")

@router.message(Command("test"))
async def cmd_test(message: Message):
    await message.answer(
        "🏙️ شهرهای جدید:\n\n"
        "ساری، قائمشهر، بابل، بهشهر، نکا، جویبار\n\n"
        "برای تست کیبورد از /start استفاده کن",
        reply_markup=get_test_city_keyboard()
    )

dp.include_router(router)

async def main():
    logger.info("🚀 Starting Test Bot...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
