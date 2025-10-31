"""
Admin module for Telegram Property Bot

This module contains administrative functionality for
managing the bot, monitoring statistics, and system maintenance.
"""

from .panel import (
    AdminPanel,
    register_admin_handlers,
    AdminStates,
    
    # Command handlers
    cmd_admin,
    cmd_stats,
    cmd_users,
    cmd_broadcast,
    cmd_errors,
    cmd_status,
    cmd_restart,
)

# Admin permissions and access levels
ADMIN_PERMISSIONS = {
    'view_stats': 'view_statistics',
    'manage_users': 'manage_users',
    'send_broadcast': 'send_broadcast',
    'view_logs': 'view_logs',
    'manage_system': 'manage_system',
    'restart_services': 'restart_services'
}

# Admin command list
ADMIN_COMMANDS = {
    '/admin': 'پنل مدیریت اصلی',
    '/stats': 'مشاهده آمار سیستم',
    '/users': 'مدیریت کاربران',
    '/broadcast': 'ارسال پیام همگانی',
    '/errors': 'مشاهده خطاها',
    '/status': 'وضعیت سیستم',
    '/restart': 'راه‌اندازی مجدد سرویس‌ها'
}

__all__ = [
    'AdminPanel',
    'register_admin_handlers',
    'AdminStates',
    
    # Command handlers
    'cmd_admin',
    'cmd_stats',
    'cmd_users',
    'cmd_broadcast',
    'cmd_errors',
    'cmd_status',
    'cmd_restart',
    
    # Constants
    'ADMIN_PERMISSIONS',
    'ADMIN_COMMANDS'
]

__version__ = '1.0.0'
__author__ = 'Property Bot Team'
__description__ = 'Administrative panel and management tools for property advertisement bot'