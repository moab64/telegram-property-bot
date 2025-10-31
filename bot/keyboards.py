from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)

# کیبوردهای اصلی (Reply Keyboard)
def get_main_keyboard():
    """کیبورد اصلی منو"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎯 تنظیم فیلتر"), KeyboardButton(text="📊 وضعیت فعال")],
            [KeyboardButton(text="🔄 به‌روزرسانی فیلتر"), KeyboardButton(text="🗑️ حذف فیلتر")],
            [KeyboardButton(text="ℹ️ راهنما")]
        ],
        resize_keyboard=True,
        input_field_placeholder="یک گزینه انتخاب کنید..."
    )
    return keyboard

def get_cancel_keyboard():
    """کیبورد لغو عملیات"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ لغو عملیات")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

def get_back_keyboard():
    """کیبورد بازگشت"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

# کیبوردهای اینلاین (Inline Keyboard)
def get_city_keyboard():
    """کیبورد انتخاب شهر"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="ساری", callback_data="city_sari")],
            [InlineKeyboardButton(text="تهران", callback_data="city_tehran")],
            [InlineKeyboardButton(text="مشهد", callback_data="city_mashhad")],
            [InlineKeyboardButton(text="اصفهان", callback_data="city_esfahan")],
            [InlineKeyboardButton(text="شیراز", callback_data="city_shiraz")],
            [InlineKeyboardButton(text="تبریز", callback_data="city_tabriz")]
        ]
    )
    return keyboard

def get_property_type_keyboard():
    """کیبورد انتخاب نوع ملک"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="آپارتمان", callback_data="type_apartment")],
            [InlineKeyboardButton(text="خانه و ویلا", callback_data="type_house")],
            [InlineKeyboardButton(text="تجاری", callback_data="type_commercial")],
            [InlineKeyboardButton(text="زمین", callback_data="type_land")],
            [InlineKeyboardButton(text="باغ", callback_data="type_garden")],
            [InlineKeyboardButton(text="همه انواع", callback_data="type_any")]
        ]
    )
    return keyboard

def get_bedrooms_keyboard():
    """کیبورد انتخاب تعداد خواب"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="۱ خواب", callback_data="bed_1")],
            [InlineKeyboardButton(text="۲ خواب", callback_data="bed_2")],
            [InlineKeyboardButton(text="۳ خواب", callback_data="bed_3")],
            [InlineKeyboardButton(text="۴ خواب", callback_data="bed_4")],
            [InlineKeyboardButton(text="۵ خواب+", callback_data="bed_5")],
            [InlineKeyboardButton(text="همه", callback_data="bed_any")]
        ]
    )
    return keyboard

def get_advertiser_type_keyboard():
    """کیبورد انتخاب نوع آگهی‌دهنده"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="مالک", callback_data="adv_owner")],
            [InlineKeyboardButton(text="مشاور", callback_data="adv_agent")],
            [InlineKeyboardButton(text="همه", callback_data="adv_any")]
        ]
    )
    return keyboard

def get_filter_confirmation_keyboard():
    """کیبورد تایید فیلتر"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ تایید و ذخیره", callback_data="confirm_filter")],
            [InlineKeyboardButton(text="❌ لغو", callback_data="cancel_filter")]
        ]
    )
    return keyboard

def get_inline_cancel_keyboard():
    """کیبورد اینلاین لغو"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ لغو", callback_data="cancel_operation")]
        ]
    )
    return keyboard

def get_inline_back_keyboard():
    """کیبورد اینلاین بازگشت"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back")]
        ]
    )
    return keyboard

# کیبوردهای پیشرفته
def get_price_range_keyboard():
    """کیبورد بازه قیمت پیش‌فرض"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="۱-۲ میلیارد", callback_data="price_1_2"),
                InlineKeyboardButton(text="۲-۳ میلیارد", callback_data="price_2_3")
            ],
            [
                InlineKeyboardButton(text="۳-۵ میلیارد", callback_data="price_3_5"),
                InlineKeyboardButton(text="۵+ میلیارد", callback_data="price_5plus")
            ],
            [InlineKeyboardButton(text="سفارشی", callback_data="price_custom")]
        ]
    )
    return keyboard

def get_area_range_keyboard():
    """کیبورد بازه متراژ پیش‌فرض"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="زیر ۷۰ متر", callback_data="area_under70"),
                InlineKeyboardButton(text="۷۰-۱۰۰ متر", callback_data="area_70_100")
            ],
            [
                InlineKeyboardButton(text="۱۰۰-۱۵۰ متر", callback_data="area_100_150"),
                InlineKeyboardButton(text="۱۵۰+ متر", callback_data="area_150plus")
            ],
            [InlineKeyboardButton(text="سفارشی", callback_data="area_custom")]
        ]
    )
    return keyboard

# کیبوردهای مدیریتی
def get_admin_keyboard():
    """کیبورد مدیریت"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 آمار کاربران"), KeyboardButton(text="📢 ارسال پیام همگانی")],
            [KeyboardButton(text="🔍 مشاهده لاگ‌ها"), KeyboardButton(text="⚙️ تنظیمات سیستم")],
            [KeyboardButton(text="🔙 بازگشت به منوی کاربر")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_broadcast_confirmation_keyboard():
    """کیبورد تایید ارسال همگانی"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ ارسال", callback_data="broadcast_confirm")],
            [InlineKeyboardButton(text="❌ لغو", callback_data="broadcast_cancel")]
        ]
    )
    return keyboard
