"""
Telegram Property Bot Package

A multi-user Telegram bot for extracting and filtering property advertisements
from Divar and Sheypoor websites.
"""

__version__ = '1.0.0'
__author__ = 'Property Bot Team'
__description__ = 'Telegram bot for property advertisements filtering'

# Import main components for easy access
from bot import register_handlers
from database import init_db, UserOperations, AdOperations
from utils import load_config, setup_logging
from scheduler import start_crawler_tasks
from admin import register_admin_handlers

__all__ = [
    'register_handlers',
    'init_db', 
    'UserOperations',
    'AdOperations',
    'load_config',
    'setup_logging',
    'start_crawler_tasks',
    'register_admin_handlers'
]