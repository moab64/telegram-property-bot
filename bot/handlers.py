import logging
from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.operations import UserOperations, AdOperations
from bot.keyboards import (
    get_main_keyboard,
    get_city_keyboard,
    get_property_type_keyboard,
    get_bedrooms_keyboard,
    get_advertiser_type_keyboard,
    get_filter_confirmation_keyboard,
    get_back_keyboard,
    get_cancel_keyboard
)
from utils.config import load_config

logger = logging.getLogger(__name__)
router = Router()
config = load_config()

class FilterStates(StatesGroup):
    city = State()
    property_type = State()
    min_price = State()
    max_price = State()
    min_area = State()
    max_area = State()
    bedrooms = State()
    advertiser_type = State()
    include_keywords = State()
    exclude_keywords = State()
    confirmation = State()

class AdminStates(StatesGroup):
    broadcast = State()
    stats = State()

# Basic Commands
@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command"""
    user = UserOperations.get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name
    )
    
    welcome_text = """
🏠 به ربات استخراج آگهی‌های ملک خوش آمدید!

این ربات هر ۱۵ دقیقه آگهی‌های جدید فروش ملک از دیوار و شیپور را بررسی کرده و بر اساس فیلترهای شخصی شما ارسال می‌کند.

📋 دستورات موجود:
/filter - تنظیم فیلترهای جستجو
/update_filter - به‌روزرسانی فیلترها
/reset_filter - حذف فیلترها
/status - مشاهده وضعیت فعلی
/help - راهنمای استفاده

برای شروع، فیلترهای جستجوی خود را با دستور /filter تنظیم کنید.
"""
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    help_text = """
📖 راهنمای استفاده از ربات:

🔍 **تنظیم فیلترها**:
- از دستور /filter برای تنظیم فیلترهای جستجو استفاده کنید
- می‌توانید شهر، نوع ملک، بازه قیمت، متراژ و سایر فیلترها را تنظیم کنید

🔄 **به‌روزرسانی فیلترها**:
- از دستور /update_filter برای تغییر فیلترهای موجود استفاده کنید

🗑️ **حذف فیلترها**:
- از دستور /reset_filter برای حذف تمام فیلترها استفاده کنید

📊 **مشاهده وضعیت**:
- از دستور /status برای مشاهده فیلترهای فعلی استفاده کنید

⏰ **زمان بررسی آگهی‌ها**:
- ربات هر ۱۵ دقیقه یکبار آگهی‌های جدید را بررسی می‌کند
- فقط آگهی‌های جدید برای شما ارسال می‌شوند

⚠️ **نکات مهم**:
- این ربات فقط آگهی‌های فروش را بررسی می‌کند
- اطلاعات از سایت‌های دیوار و شیپور استخراج می‌شوند
- ربات فقط لینک آگهی‌ها را ارسال می‌کند و عکس‌ها نمایش داده نمی‌شوند

📞 **پشتیبانی**:
در صورت بروز مشکل با ادمین ربات تماس بگیرید.
"""
    await message.answer(help_text)

@router.message(Command("status"))
async def cmd_status(message: Message):
    """Handle /status command"""
    user_filter = UserOperations.get_user_filter(message.from_user.id)
    
    if not user_filter:
        await message.answer(
            "📊 شما هنوز فیلتری تنظیم نکرده‌اید.\n\n"
            "برای تنظیم فیلتر از دستور /filter استفاده کنید.",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Format status message
    status_text = f"""
📊 وضعیت فیلترهای شما:

🏙️ شهر: {user_filter.city or 'ساری (پیش‌فرض)'}
🏠 نوع ملک: {user_filter.property_type or 'همه'}
💰 بازه قیمت: {user_filter.min_price or '۰'} - {user_filter.max_price or 'نامحدود'} تومان
📏 متراژ: {user_filter.min_area or '۰'} - {user_filter.max_area or 'نامحدود'} متر
🛏️ تعداد خواب: {user_filter.bedrooms or 'همه'}
👤 آگهی‌دهنده: {user_filter.advertiser_type or 'همه'}
🔍 کلمات شامل: {user_filter.include_keywords or 'ندارد'}
🚫 کلمات حذف: {user_filter.exclude_keywords or 'ندارد'}

🕒 آخرین به‌روزرسانی: {user_filter.updated_at.strftime('%Y-%m-%d %H:%M')}
"""
    await message.answer(status_text)

# Filter Management Commands
@router.message(Command("filter"))
async def cmd_filter(message: Message, state: FSMContext):
    """Handle /filter command"""
    await state.set_state(FilterStates.city)
    await message.answer(
        "🌆 لطفا شهر مورد نظر خود را انتخاب کنید:",
        reply_markup=get_city_keyboard()
    )

@router.message(Command("update_filter"))
async def cmd_update_filter(message: Message, state: FSMContext):
    """Handle /update_filter command"""
    user_filter = UserOperations.get_user_filter(message.from_user.id)
    if not user_filter:
        await message.answer(
            "❌ شما هنوز فیلتری تنظیم نکرده‌اید.\n\n"
            "برای تنظیم فیلتر از دستور /filter استفاده کنید.",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Load existing filter data into state
    await state.set_state(FilterStates.city)
    await state.update_data(**{
        'city': user_filter.city,
        'property_type': user_filter.property_type,
        'min_price': user_filter.min_price,
        'max_price': user_filter.max_price,
        'min_area': user_filter.min_area,
        'max_area': user_filter.max_area,
        'bedrooms': user_filter.bedrooms,
        'advertiser_type': user_filter.advertiser_type,
        'include_keywords': user_filter.include_keywords,
        'exclude_keywords': user_filter.exclude_keywords
    })
    
    await message.answer(
        "🔧 در حال به‌روزرسانی فیلترها. لطفا شهر مورد نظر را انتخاب کنید:",
        reply_markup=get_city_keyboard()
    )

@router.message(Command("reset_filter"))
async def cmd_reset_filter(message: Message):
    """Handle /reset_filter command"""
    if UserOperations.reset_user_filter(message.from_user.id):
        await message.answer(
            "✅ فیلترهای شما با موفقیت حذف شدند.\n\n"
            "برای تنظیم فیلتر جدید از دستور /filter استفاده کنید.",
            reply_markup=get_main_keyboard()
        )
    else:
        await message.answer(
            "❌ شما فیلتری برای حذف ندارید.\n\n"
            "برای تنظیم فیلتر از دستور /filter استفاده کنید.",
            reply_markup=get_main_keyboard()
        )

# Filter Setup States
@router.callback_query(FilterStates.city, F.data.startswith("city_"))
async def process_city(callback: CallbackQuery, state: FSMContext):
    """Process city selection"""
    city = callback.data.split("_")[1]
    await state.update_data(city=city)
    await state.set_state(FilterStates.property_type)
    
    await callback.message.edit_text(
        "🏠 لطفا نوع ملک مورد نظر را انتخاب کنید:",
        reply_markup=get_property_type_keyboard()
    )
    await callback.answer()

@router.callback_query(FilterStates.property_type, F.data.startswith("type_"))
async def process_property_type(callback: CallbackQuery, state: FSMContext):
    """Process property type selection"""
    property_type = callback.data.split("_")[1]
    if property_type == 'any':
        property_type = None
    
    await state.update_data(property_type=property_type)
    await state.set_state(FilterStates.min_price)
    
    await callback.message.edit_text(
        "💰 لطفا حداقل قیمت مورد نظر را به تومان وارد کنید:\n\n"
        "مثال: 2000000000\n"
        "یا '0' برای عدم محدودیت",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()

@router.message(FilterStates.min_price)
async def process_min_price(message: Message, state: FSMContext):
    """Process minimum price input"""
    try:
        if message.text == '0' or message.text.lower() == 'ندارد':
            min_price = None
        else:
            min_price = int(message.text.replace(',', '').replace(' ', ''))
        
        await state.update_data(min_price=min_price)
        await state.set_state(FilterStates.max_price)
        
        await message.answer(
            "💰 لطفا حداکثر قیمت مورد نظر را به تومان وارد کنید:\n\n"
            "مثال: 5000000000\n"
            "یا '0' برای عدم محدودیت",
            reply_markup=get_cancel_keyboard()
        )
    except ValueError:
        await message.answer(
            "❌ لطفا یک عدد معتبر وارد کنید:\n\n"
            "مثال: 2000000000\n"
            "یا '0' برای عدم محدودیت"
        )

@router.message(FilterStates.max_price)
async def process_max_price(message: Message, state: FSMContext):
    """Process maximum price input"""
    try:
        if message.text == '0' or message.text.lower() == 'ندارد':
            max_price = None
        else:
            max_price = int(message.text.replace(',', '').replace(' ', ''))
        
        await state.update_data(max_price=max_price)
        await state.set_state(FilterStates.min_area)
        
        await message.answer(
            "📏 لطفا حداقل متراژ مورد نظر را وارد کنید:\n\n"
            "مثال: 70\n"
            "یا '0' برای عدم محدودیت",
            reply_markup=get_cancel_keyboard()
        )
    except ValueError:
        await message.answer(
            "❌ لطفا یک عدد معتبر وارد کنید:\n\n"
            "مثال: 5000000000\n"
            "یا '0' برای عدم محدودیت"
        )

@router.message(FilterStates.min_area)
async def process_min_area(message: Message, state: FSMContext):
    """Process minimum area input"""
    try:
        if message.text == '0' or message.text.lower() == 'ندارد':
            min_area = None
        else:
            min_area = int(message.text)
        
        await state.update_data(min_area=min_area)
        await state.set_state(FilterStates.max_area)
        
        await message.answer(
            "📏 لطفا حداکثر متراژ مورد نظر را وارد کنید:\n\n"
            "مثال: 150\n"
            "یا '0' برای عدم محدودیت",
            reply_markup=get_cancel_keyboard()
        )
    except ValueError:
        await message.answer(
            "❌ لطفا یک عدد معتبر وارد کنید:\n\n"
            "مثال: 70\n"
            "یا '0' برای عدم محدودیت"
        )

@router.message(FilterStates.max_area)
async def process_max_area(message: Message, state: FSMContext):
    """Process maximum area input"""
    try:
        if message.text == '0' or message.text.lower() == 'ندارد':
            max_area = None
        else:
            max_area = int(message.text)
        
        await state.update_data(max_area=max_area)
        await state.set_state(FilterStates.bedrooms)
        
        await message.answer(
            "🛏️ لطفا تعداد خواب مورد نظر را انتخاب کنید:",
            reply_markup=get_bedrooms_keyboard()
        )
    except ValueError:
        await message.answer(
            "❌ لطفا یک عدد معتبر وارد کنید:\n\n"
            "مثال: 150\n"
            "یا '0' برای عدم محدودیت"
        )

@router.callback_query(FilterStates.bedrooms, F.data.startswith("bed_"))
async def process_bedrooms(callback: CallbackQuery, state: FSMContext):
    """Process bedrooms selection"""
    bedrooms_data = callback.data.split("_")[1]
    bedrooms = int(bedrooms_data) if bedrooms_data != 'any' else None
    await state.update_data(bedrooms=bedrooms)
    await state.set_state(FilterStates.advertiser_type)
    
    await callback.message.edit_text(
        "👤 لطفا نوع آگهی‌دهنده را انتخاب کنید:",
        reply_markup=get_advertiser_type_keyboard()
    )
    await callback.answer()

@router.callback_query(FilterStates.advertiser_type, F.data.startswith("adv_"))
async def process_advertiser_type(callback: CallbackQuery, state: FSMContext):
    """Process advertiser type selection"""
    advertiser_type = callback.data.split("_")[1]
    if advertiser_type == 'any':
        advertiser_type = None
    
    await state.update_data(advertiser_type=advertiser_type)
    await state.set_state(FilterStates.include_keywords)
    
    await callback.message.edit_text(
        "🔍 لطفا کلمات کلیدی که باید در آگهی وجود داشته باشند را وارد کنید:\n\n"
        "مثال: سنددار, نوساز, آسانسور\n"
        "یا 'ندارد' برای عدم محدودیت",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()

@router.message(FilterStates.include_keywords)
async def process_include_keywords(message: Message, state: FSMContext):
    """Process include keywords"""
    include_keywords = None if message.text == 'ندارد' else message.text
    await state.update_data(include_keywords=include_keywords)
    await state.set_state(FilterStates.exclude_keywords)
    
    await message.answer(
        "🚫 لطفا کلمات کلیدی که نباید در آگهی وجود داشته باشند را وارد کنید:\n\n"
        "مثال: رهن, اجاره, تخریب\n"
        "یا 'ندارد' برای عدم محدودیت",
        reply_markup=get_cancel_keyboard()
    )

@router.message(FilterStates.exclude_keywords)
async def process_exclude_keywords(message: Message, state: FSMContext):
    """Process exclude keywords"""
    exclude_keywords = None if message.text == 'ندارد' else message.text
    
    # Get all filter data
    filter_data = await state.get_data()
    filter_data['exclude_keywords'] = exclude_keywords
    
    # Show confirmation
    confirmation_text = await _format_filter_confirmation(filter_data)
    
    await state.set_state(FilterStates.confirmation)
    await message.answer(
        confirmation_text,
        reply_markup=get_filter_confirmation_keyboard()
    )

@router.callback_query(FilterStates.confirmation, F.data == "confirm_filter")
async def confirm_filter(callback: CallbackQuery, state: FSMContext):
    """Confirm and save filter"""
    filter_data = await state.get_data()
    
    # Save filter to database
    user_filter = UserOperations.update_user_filter(callback.from_user.id, filter_data)
    
    if user_filter:
        await callback.message.edit_text(
            "✅ فیلترهای شما با موفقیت ذخیره شدند!\n\n"
            "ربات هر ۱۵ دقیقه یکبار آگهی‌های جدید را بررسی کرده و در صورت وجود آگهی‌های مطابق با فیلترهای شما، "
            "آن‌ها را برای شما ارسال خواهد کرد.\n\n"
            "از دستور /status برای مشاهده وضعیت فعلی استفاده کنید."
        )
    else:
        await callback.message.edit_text(
            "❌ خطا در ذخیره‌سازی فیلترها. لطفا دوباره تلاش کنید."
        )
    
    await state.clear()
    await callback.answer()

@router.callback_query(FilterStates.confirmation, F.data == "cancel_filter")
async def cancel_filter(callback: CallbackQuery, state: FSMContext):
    """Cancel filter setup"""
    await callback.message.edit_text(
        "❌ تنظیم فیلترها لغو شد.\n\n"
        "برای تنظیم فیلتر جدید از دستور /filter استفاده کنید."
    )
    await state.clear()
    await callback.answer()

# Text Message Handlers
@router.message(F.text == "🎯 تنظیم فیلتر")
async def handle_set_filter(message: Message, state: FSMContext):
    """Handle set filter button"""
    await cmd_filter(message, state)

@router.message(F.text == "📊 وضعیت فعلی")
async def handle_status(message: Message):
    """Handle status button"""
    await cmd_status(message)

@router.message(F.text == "🆘 راهنما")
async def handle_help(message: Message):
    """Handle help button"""
    await cmd_help(message)

@router.message(F.text == "🔄 به‌روزرسانی فیلتر")
async def handle_update_filter(message: Message, state: FSMContext):
    """Handle update filter button"""
    await cmd_update_filter(message, state)

@router.message(F.text == "🗑️ حذف فیلتر")
async def handle_reset_filter(message: Message):
    """Handle reset filter button"""
    await cmd_reset_filter(message)

@router.message(F.text == "🔙 بازگشت")
async def handle_back(message: Message):
    """Handle back button"""
    await message.answer(
        "منوی اصلی:",
        reply_markup=get_main_keyboard()
    )

@router.message(F.text == "❌ لغو عملیات")
async def handle_cancel(message: Message, state: FSMContext):
    """Handle cancel button"""
    await state.clear()
    await message.answer(
        "عملیات لغو شد.",
        reply_markup=get_main_keyboard()
    )

# Helper Functions
async def _format_filter_confirmation(filter_data):
    """Format filter data for confirmation message"""
    
    def format_value(value):
        if value is None:
            return "ندارد"
        return str(value)
    
    city_map = {
        'sari': 'ساری',
        'tehran': 'تهران',
        'mashhad': 'مشهد',
        'esfahan': 'اصفهان',
        'shiraz': 'شیراز',
        'tabriz': 'تبریز'
    }
    
    type_map = {
        'apartment': 'آپارتمان',
        'house': 'خانه و ویلا',
        'commercial': 'تجاری',
        'land': 'زمین',
        'garden': 'باغ',
        None: 'همه'
    }
    
    advertiser_map = {
        'owner': 'مالک',
        'agent': 'مشاور',
        None: 'همه'
    }
    
    city_name = city_map.get(filter_data.get('city', 'sari'), filter_data.get('city', 'ساری'))
    property_type_name = type_map.get(filter_data.get('property_type'), 'همه')
    advertiser_name = advertiser_map.get(filter_data.get('advertiser_type'), 'همه')
    
    confirmation_text = f"""
✅ فیلترهای شما تنظیم شدند:

🏙️ شهر: {city_name}
🏠 نوع ملک: {property_type_name}
💰 بازه قیمت: {format_value(filter_data.get('min_price'))} - {format_value(filter_data.get('max_price'))} تومان
📏 متراژ: {format_value(filter_data.get('min_area'))} - {format_value(filter_data.get('max_area'))} متر
🛏️ تعداد خواب: {format_value(filter_data.get('bedrooms'))}
👤 آگهی‌دهنده: {advertiser_name}
🔍 کلمات شامل: {format_value(filter_data.get('include_keywords'))}
🚫 کلمات حذف: {format_value(filter_data.get('exclude_keywords'))}

آیا می‌خواهید این فیلترها را ذخیره کنید؟
"""
    return confirmation_text

def register_handlers(dp):
    """Register all handlers with dispatcher"""
    dp.include_router(router)