import logging
import re
from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.operations import UserOperations, AdOperations
from bot.keyboards import (
    get_main_keyboard,
    get_city_keyboard,
    get_cancel_keyboard
)

logger = logging.getLogger(__name__)
router = Router()

class FilterStates(StatesGroup):
    city = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    """مدیریت دستور /start"""
    user = UserOperations.get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name
    )
    
    welcome_text = """
🏠 به ربات استخراج آگهی‌های ملک خوش آمدید!

🤖 این ربات آگهی‌های فروش ملک از شهر مورد نظر شما را نمایش می‌دهد.

📋 دستورات موجود:
/filter - انتخاب شهر برای مشاهده آگهی‌ها
/status - مشاهده وضعیت فعلی
/help - راهنمای استفاده

برای شروع، شهر مورد نظر خود را با دستور /filter انتخاب کنید.
"""
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@router.message(Command("help"))
async def cmd_help(message: Message):
    """مدیریت دستور /help"""
    help_text = """
📖 راهنمای استفاده از ربات:

🏙️ **انتخاب شهر**:
- از دستور /filter برای انتخاب شهر استفاده کنید
- تمام آگهی‌های فروش ملک از شهر انتخاب شده نمایش داده می‌شود

📊 **مشاهده وضعیت**:
- از دستور /status برای مشاهده شهر انتخاب شده استفاده کنید

🔄 **تغییر شهر**:
- برای تغییر شهر مجدداً از دستور /filter استفاده کنید

⚠️ **نکات مهم**:
- تمام آگهی‌های فروش ملک نمایش داده می‌شود
- نیازی به تنظیم فیلترهای دیگر نیست
- آگهی‌ها به صورت خودکار به روز می‌شوند

🏙️ **شهرهای موجود**:
ساری، قائمشهر، بابل، بهشهر، نکا، جویبار، تهران، مشهد، اصفهان، شیراز، تبریز
"""
    await message.answer(help_text)

@router.message(Command("status"))
async def cmd_status(message: Message):
    """مدیریت دستور /status"""
    user_filter = UserOperations.get_user_filter(message.from_user.id)
    
    if not user_filter or not user_filter.city:
        await message.answer(
            "📊 شما هنوز شهری انتخاب نکرده‌اید.\n\n"
            "برای انتخاب شهر از دستور /filter استفاده کنید.",
            reply_markup=get_main_keyboard()
        )
        return
    
    city_name = _get_city_name(user_filter.city)
    status_text = f"""
📊 وضعیت فعلی:

🏙️ شهر انتخاب شده: {city_name}

🤖 ربات تمام آگهی‌های فروش ملک در {city_name} را نمایش می‌دهد.
"""
    await message.answer(status_text)

@router.message(Command("filter"))
async def cmd_filter(message: Message, state: FSMContext):
    """مدیریت دستور /filter"""
    await state.set_state(FilterStates.city)
    await message.answer(
        "🏙️ لطفا شهر مورد نظر خود را انتخاب کنید:\n\n"
        "تمام آگهی‌های فروش ملک از شهر انتخاب شده نمایش داده خواهد شد.\n\n"
        "🏙️ شهرهای موجود:\n"
        "ساری، قائمشهر، بابل، بهشهر، نکا، جویبار، تهران، مشهد، اصفهان، شیراز، تبریز",
        reply_markup=get_city_keyboard()
    )

@router.callback_query(FilterStates.city, F.data.startswith("city_"))
async def process_city(callback: CallbackQuery, state: FSMContext):
    """پردازش انتخاب شهر"""
    city_code = callback.data.split("_")[1]
    city_name = _get_city_name(city_code)
    
    # ذخیره فقط شهر در دیتابیس (بقیه فیلترها None می‌شوند)
    filter_data = {
        'city': city_code,
        'property_type': None,  # همه انواع ملک
        'min_price': None,      # بدون محدودیت قیمت
        'max_price': None,      # بدون محدودیت قیمت
        'min_area': None,       # بدون محدودیت متراژ
        'max_area': None,       # بدون محدودیت متراژ
        'bedrooms': None,       # همه تعداد خواب
        'advertiser_type': None, # همه آگهی‌دهندگان
        'include_keywords': None, # بدون کلمات شامل
        'exclude_keywords': None  # بدون کلمات حذف
    }
    
    # ذخیره فیلتر در دیتابیس
    user_filter = UserOperations.update_user_filter(callback.from_user.id, filter_data)
    
    if user_filter:
        await callback.message.edit_text(
            f"✅ شهر {city_name} انتخاب شد!\n\n"
            f"🤖 از این پس تمام آگهی‌های فروش ملک در {city_name} برای شما نمایش داده می‌شود.\n\n"
            f"آگهی‌های جدید به صورت خودکار بررسی و ارسال خواهند شد.\n\n"
            f"برای تغییر شهر از دستور /filter استفاده کنید."
        )
    else:
        await callback.message.edit_text(
            "❌ خطا در ذخیره‌سازی شهر. لطفا دوباره تلاش کنید."
        )
    
    await state.clear()
    await callback.answer()

# هندلرهای دکمه‌های متنی
@router.message(F.text == "🏙️ انتخاب شهر")
async def handle_set_filter(message: Message, state: FSMContext):
    await cmd_filter(message, state)

@router.message(F.text == "📊 وضعیت فعلی")
async def handle_status(message: Message):
    await cmd_status(message)

@router.message(F.text == "ℹ️ راهنما")
async def handle_help(message: Message):
    await cmd_help(message)

@router.message(F.text == "🔙 بازگشت")
async def handle_back(message: Message):
    await message.answer("منوی اصلی:", reply_markup=get_main_keyboard())

@router.message(F.text == "❌ لغو عملیات")
async def handle_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("عملیات لغو شد.", reply_markup=get_main_keyboard())

# توابع کمکی
def _get_city_name(city_code):
    """تبدیل کد شهر به نام فارسی"""
    city_map = {
        'sari': 'ساری',
        'qaemshahr': 'قائمشهر',
        'babol': 'بابل',
        'behshahr': 'بهشهر',
        'neka': 'نکا',
        'joybar': 'جویبار',
        'tehran': 'تهران',
        'mashhad': 'مشهد',
        'esfahan': 'اصفهان',
        'shiraz': 'شیراز',
        'tabriz': 'تبریز'
    }
    return city_map.get(city_code, city_code)

def register_handlers(dp):
    dp.include_router(router)
