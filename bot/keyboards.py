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
            [KeyboardButton(text="🏙️ انتخاب شهر"), KeyboardButton(text="📊 وضعیت فعلی")],
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

# کیبوردهای اینلاین (Inline Keyboard)
def get_city_keyboard():
    """کیبورد انتخاب شهر با شهرهای جدید"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            # شهرهای مازندران
            [
                InlineKeyboardButton(text="ساری", callback_data="city_sari"),
                InlineKeyboardButton(text="قائمشهر", callback_data="city_qaemshahr")
            ],
            [
                InlineKeyboardButton(text="بابل", callback_data="city_babol"),
                InlineKeyboardButton(text="جویبار", callback_data="city_joybar")
            ],
            [
                InlineKeyboardButton(text="بهشهر", callback_data="city_behshahr"),
                InlineKeyboardButton(text="نکا", callback_data="city_neka")
            ],
            # شهرهای بزرگ دیگر
            [
                InlineKeyboardButton(text="تهران", callback_data="city_tehran"),
                InlineKeyboardButton(text="مشهد", callback_data="city_mashhad")
            ],
            [
                InlineKeyboardButton(text="اصفهان", callback_data="city_esfahan"),
                InlineKeyboardButton(text="شیراز", callback_data="city_shiraz")
            ],
            [
                InlineKeyboardButton(text="تبریز", callback_data="city_tabriz")
            ]
        ]
    )
    return keyboard
