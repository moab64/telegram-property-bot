"""
Database module for Telegram Property Bot

This module contains database models, operations, and utilities
for storing and managing user data and property advertisements.
"""

from .models import Base, User, UserFilter, Advertisement, SentAd
from .operations import (
    # Database initialization
    init_db,
    get_db,
    
    # User operations
    UserOperations,
    
    # Advertisement operations
    AdOperations,
)

# Export all models
__all__ = [
    # Models
    'Base',
    'User',
    'UserFilter',
    'Advertisement',
    'SentAd',
    
    # Database management
    'init_db',
    'get_db',
    
    # Operations
    'UserOperations',
    'AdOperations',
]

# Database configuration
DEFAULT_DATABASE_URL = "sqlite:///property_bot.db"
SUPPORTED_DATABASES = ['sqlite', 'postgresql', 'mysql']

# Table names for reference
TABLE_NAMES = {
    'users': 'users',
    'user_filters': 'user_filters',
    'advertisements': 'advertisements',
    'sent_ads': 'sent_ads'
}

__version__ = '1.0.0'
__author__ = 'Property Bot Team'
__description__ = 'Database models and operations for property advertisement bot'