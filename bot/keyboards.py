from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def get_main_keyboard():
    """Main menu keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎯 تنظیم فیلتر"), KeyboardButton(text="📊 وضعیت فعلی")],
            [KeyboardButton(text="🆘 راهنما"), KeyboardButton(text="🔄 به‌روزرسانی فیلتر")],
            [KeyboardButton(text="🗑️ حذف فیلتر")]
        ],
        resize_keyboard=True,
        input_field_placeholder="یک گزینه انتخاب کنید..."
    )
    return keyboard

def get_city_keyboard():
    """City selection inline keyboard"""
    keyboard = InlineKeyboardBuilder()
    
    cities = [
        ("ساری", "city_sari"),
        ("تهران", "city_tehran"),
        ("مشهد", "city_mashhad"),
        ("اصفهان", "city_esfahan"),
        ("شیراز", "city_shiraz"),
        ("تبریز", "city_tabriz"),
    ]
    
    for city, callback_data in cities:
        keyboard.button(text=city, callback_data=callback_data)
    
    keyboard.adjust(2)  # 2 buttons per row
    return keyboard.as_markup()

def get_property_type_keyboard():
    """Property type selection inline keyboard"""
    keyboard = InlineKeyboardBuilder()
    
    property_types = [
        ("🏠 آپارتمان", "type_apartment"),
        ("🏡 خانه و ویلا", "type_house"),
        ("🏢 تجاری", "type_commercial"),
        ("📄 زمین", "type_land"),
        ("🌳 باغ", "type_garden"),
        ("همه انواع", "type_any"),
    ]
    
    for prop_type, callback_data in property_types:
        keyboard.button(text=prop_type, callback_data=callback_data)
    
    keyboard.adjust(2)
    return keyboard.as_markup()

def get_bedrooms_keyboard():
    """Bedrooms selection inline keyboard"""
    keyboard = InlineKeyboardBuilder()
    
    bedrooms = [
        ("۱ خواب", "bed_1"),
        ("۲ خواب", "bed_2"),
        ("۳ خواب", "bed_3"),
        ("۴ خواب", "bed_4"),
        ("+۴ خواب", "bed_5"),
        ("همه", "bed_any"),
    ]
    
    for bed, callback_data in bedrooms:
        keyboard.button(text=bed, callback_data=callback_data)
    
    keyboard.adjust(3)
    return keyboard.as_markup()

def get_advertiser_type_keyboard():
    """Advertiser type selection inline keyboard"""
    keyboard = InlineKeyboardBuilder()
    
    advertiser_types = [
        ("👤 مالک", "adv_owner"),
        ("🏢 مشاور", "adv_agent"),
        ("همه", "adv_any"),
    ]
    
    for adv_type, callback_data in advertiser_types:
        keyboard.button(text=adv_type, callback_data=callback_data)
    
    keyboard.adjust(2)
    return keyboard.as_markup()

def get_filter_confirmation_keyboard():
    """Filter confirmation inline keyboard"""
    keyboard = InlineKeyboardBuilder()
    
    keyboard.button(text="✅ ذخیره فیلترها", callback_data="confirm_filter")
    keyboard.button(text="❌ لغو", callback_data="cancel_filter")
    
    keyboard.adjust(2)
    return keyboard.as_markup()

def get_yes_no_keyboard():
    """Yes/No inline keyboard"""
    keyboard = InlineKeyboardBuilder()
    
    keyboard.button(text="✅ بله", callback_data="yes")
    keyboard.button(text="❌ خیر", callback_data="no")
    
    keyboard.adjust(2)
    return keyboard.as_markup()

def get_admin_keyboard():
    """Admin panel keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👥 آمار کاربران"), KeyboardButton(text="📊 آمار آگهی‌ها")],
            [KeyboardButton(text="🔍 مشاهده لاگ"), KeyboardButton(text="⚙️ وضعیت کراولر")],
            [KeyboardButton(text="🔄 راه‌اندازی مجدد"), KeyboardButton(text="🏠 منوی اصلی")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_back_keyboard():
    """Simple back button keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 بازگشت")]],
        resize_keyboard=True
    )
    return keyboard

def get_cancel_keyboard():
    """Cancel operation keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ لغو عملیات")]],
        resize_keyboard=True
    )
    return keyboard

def get_numeric_keyboard():
    """Numeric keyboard for price/area input"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="0"), KeyboardButton(text="1000000000"), KeyboardButton(text="2000000000")],
            [KeyboardButton(text="3000000000"), KeyboardButton(text="5000000000"), KeyboardButton(text="10000000000")],
            [KeyboardButton(text="❌ بدون محدودیت")]
        ],
        resize_keyboard=True,
        input_field_placeholder="قیمت را وارد کنید..."
    )
    return keyboard

def get_area_keyboard():
    """Area selection keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="50"), KeyboardButton(text="70"), KeyboardButton(text="100")],
            [KeyboardButton(text="120"), KeyboardButton(text="150"), KeyboardButton(text="200")],
            [KeyboardButton(text="❌ بدون محدودیت")]
        ],
        resize_keyboard=True,
        input_field_placeholder="متراژ را وارد کنید..."
    )
    return keyboard

def get_settings_keyboard():
    """Settings menu keyboard"""
    keyboard = InlineKeyboardBuilder()
    
    settings = [
        ("🔔 تنظیم نوتیفیکیشن", "settings_notifications"),
        ("⏰ تنظیم بازه زمانی", "settings_interval"),
        ("🌆 تغییر شهر پیش‌فرض", "settings_city"),
        ("📱 حالت نمایش", "settings_display"),
    ]
    
    for setting, callback_data in settings:
        keyboard.button(text=setting, callback_data=callback_data)
    
    keyboard.adjust(1)
    return keyboard.as_markup()

def get_notification_settings_keyboard():
    """Notification settings keyboard"""
    keyboard = InlineKeyboardBuilder()
    
    notifications = [
        ("🔔 فعال", "notif_on"),
        ("🔕 غیرفعال", "notif_off"),
        ("⏰ فقط صبح", "notif_morning"),
        ("🌙 فقط عصر", "notif_evening"),
    ]
    
    for notif, callback_data in notifications:
        keyboard.button(text=notif, callback_data=callback_data)
    
    keyboard.adjust(2)
    return keyboard.as_markup()