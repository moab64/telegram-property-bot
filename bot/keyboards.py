from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)

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

def get_city_keyboard():
    """کیبورد انتخاب شهر با تمام شهرهای جدید"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            # شهرهای مازندران - ردیف اول
            [
                InlineKeyboardButton(text="ساری", callback_data="city_sari"),
                InlineKeyboardButton(text="قائمشهر", callback_data="city_qaemshahr")
            ],
            # شهرهای مازندران - ردیف دوم
            [
                InlineKeyboardButton(text="بابل", callback_data="city_babol"),
                InlineKeyboardButton(text="بهشهر", callback_data="city_behshahr")
            ],
            # شهرهای مازندران - ردیف سوم
            [
                InlineKeyboardButton(text="نکا", callback_data="city_neka"),
                InlineKeyboardButton(text="جویبار", callback_data="city_joybar")
            ],
            # شهرهای بزرگ دیگر - ردیف چهارم
            [
                InlineKeyboardButton(text="تهران", callback_data="city_tehran"),
                InlineKeyboardButton(text="مشهد", callback_data="city_mashhad")
            ],
            # شهرهای بزرگ دیگر - ردیف پنجم
            [
                InlineKeyboardButton(text="اصفهان", callback_data="city_esfahan"),
                InlineKeyboardButton(text="شیراز", callback_data="city_shiraz")
            ],
            # شهرهای بزرگ دیگر - ردیف ششم
            [
                InlineKeyboardButton(text="تبریز", callback_data="city_tabriz")
            ]
        ]
    )
    return keyboard
