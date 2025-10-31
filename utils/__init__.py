"""
Utilities module for Telegram Property Bot

This module contains common utilities, helpers, and configuration
management for the application.
"""

from .config import (
    load_config,
    get_city_slug,
    get_property_type_name,
    is_admin,
    get_crawler_headers,
    AppConfig,
    BotConfig,
    DatabaseConfig,
    CrawlerConfig,
    CityConfig,
    ConfigLoader
)

from .logger import (
    setup_logging,
    get_logger,
    log_execution_time,
    BotLogger,
    setup_bot_logging,
    CustomFormatter,
    FileFormatter
)

from .helpers import (
    # Rate limiting and proxies
    RateLimiter,
    ProxyManager,
    
    # Retry decorators
    retry_on_failure,
    
    # Text processing
    clean_text,
    extract_numbers,
    parse_persian_number,
    calculate_similarity,
    
    # Formatting
    format_currency,
    format_area,
    format_timestamp,
    get_emoji_for_property_type,
    
    # URL handling
    is_valid_url,
    normalize_url,
    
    # HTTP utilities
    make_http_request,
    generate_user_agent,
    
    # List utilities
    chunk_list,
    
    # Async utilities
    safe_async_execution,
    
    # Caching
    Cache,
    cache,
)

# Module version and metadata
__version__ = '1.0.0'
__author__ = 'Property Bot Team'
__description__ = 'Common utilities and helpers for property advertisement bot'

# Export all utilities
__all__ = [
    # Configuration
    'load_config',
    'get_city_slug',
    'get_property_type_name',
    'is_admin',
    'get_crawler_headers',
    'AppConfig',
    'BotConfig',
    'DatabaseConfig',
    'CrawlerConfig',
    'CityConfig',
    'ConfigLoader',
    
    # Logging
    'setup_logging',
    'get_logger',
    'log_execution_time',
    'BotLogger',
    'setup_bot_logging',
    'CustomFormatter',
    'FileFormatter',
    
    # Helpers
    'RateLimiter',
    'ProxyManager',
    'retry_on_failure',
    'clean_text',
    'extract_numbers',
    'parse_persian_number',
    'calculate_similarity',
    'format_currency',
    'format_area',
    'format_timestamp',
    'get_emoji_for_property_type',
    'is_valid_url',
    'normalize_url',
    'make_http_request',
    'generate_user_agent',
    'chunk_list',
    'safe_async_execution',
    'Cache',
    'cache',
]

# Common constants
DEFAULT_REQUEST_TIMEOUT = 30
MAX_RETRY_ATTEMPTS = 3
DEFAULT_DELAY_SECONDS = 2

# Supported cities
SUPPORTED_CITIES = ['sari', 'tehran', 'mashhad', 'esfahan', 'shiraz', 'tabriz']

# Property types
PROPERTY_TYPES = ['apartment', 'house', 'commercial', 'land', 'garden']

# Advertiser types
ADVERTISER_TYPES = ['owner', 'agent']