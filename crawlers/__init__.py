"""
Crawlers module for Telegram Property Bot

This module contains web crawlers for extracting property advertisements
from various real estate websites.
"""

from .base_crawler import BaseCrawler
from .divar_crawler import DivarCrawler
from .sheypoor_crawler import SheypoorCrawler

# List of available crawlers
AVAILABLE_CRAWLERS = {
    'divar': DivarCrawler,
    'sheypoor': SheypoorCrawler
}

def get_crawler(source: str, config):
    """
    Get crawler instance for specified source
    
    Args:
        source: Crawler source ('divar', 'sheypoor')
        config: Application configuration
    
    Returns:
        BaseCrawler instance
    
    Raises:
        ValueError: If source is not supported
    """
    crawler_class = AVAILABLE_CRAWLERS.get(source.lower())
    if not crawler_class:
        raise ValueError(f"Unsupported crawler source: {source}")
    
    return crawler_class(config)

def get_available_sources() -> list:
    """
    Get list of available crawler sources
    
    Returns:
        List of source names
    """
    return list(AVAILABLE_CRAWLERS.keys())

def is_source_supported(source: str) -> bool:
    """
    Check if source is supported by available crawlers
    
    Args:
        source: Source name to check
    
    Returns:
        True if source is supported
    """
    return source.lower() in AVAILABLE_CRAWLERS

__all__ = [
    'BaseCrawler',
    'DivarCrawler',
    'SheypoorCrawler',
    'get_crawler',
    'get_available_sources',
    'is_source_supported',
    'AVAILABLE_CRAWLERS'
]

__version__ = '1.0.0'
__author__ = 'Property Bot Team'
__description__ = 'Web crawlers for extracting property advertisements from real estate websites'