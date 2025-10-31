"""
Bot module for Telegram Property Bot

This module contains all bot-related functionality including:
- Message handlers
- Keyboard layouts
- Filter management
- State machines
"""

from .handlers import register_handlers
from .filters import (
    apply_keyword_filters,
    validate_price,
    validate_area,
    extract_bedrooms,
    determine_advertiser_type,
    determine_property_type,
    extract_district,
    format_price,
    should_send_ad
)
from .keyboards import (
    get_main_keyboard,
    get_city_keyboard,
    get_property_type_keyboard,
    get_bedrooms_keyboard,
    get_advertiser_type_keyboard,
    get_filter_confirmation_keyboard,
    get_yes_no_keyboard,
    get_admin_keyboard,
    get_back_keyboard,
    get_cancel_keyboard,
    get_numeric_keyboard,
    get_area_keyboard,
    get_settings_keyboard,
    get_notification_settings_keyboard
)

__all__ = [
    # Handlers
    'register_handlers',
    
    # Filters
    'apply_keyword_filters',
    'validate_price',
    'validate_area',
    'extract_bedrooms',
    'determine_advertiser_type',
    'determine_property_type',
    'extract_district',
    'format_price',
    'should_send_ad',
    
    # Keyboards
    'get_main_keyboard',
    'get_city_keyboard',
    'get_property_type_keyboard',
    'get_bedrooms_keyboard',
    'get_advertiser_type_keyboard',
    'get_filter_confirmation_keyboard',
    'get_yes_no_keyboard',
    'get_admin_keyboard',
    'get_back_keyboard',
    'get_cancel_keyboard',
    'get_numeric_keyboard',
    'get_area_keyboard',
    'get_settings_keyboard',
    'get_notification_settings_keyboard'
]

__version__ = '1.0.0'
__author__ = 'Property Bot Team'
__description__ = 'Telegram bot handlers and utilities for property advertisement filtering'