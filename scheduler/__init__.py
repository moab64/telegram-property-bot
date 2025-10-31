"""
Scheduler module for Telegram Property Bot

This module contains task scheduling functionality for periodic
crawling and advertisement distribution.
"""

from .tasks import (
    crawl_property_ads,
    send_ads_to_users,
    scheduled_crawl_and_send,
    start_crawler_tasks,
    format_ad_message
)

# Scheduler configuration
DEFAULT_INTERVAL_MINUTES = 15
MAX_CONCURRENT_JOBS = 3
JOB_IDS = {
    'property_crawler': 'property_crawler',
    'cleanup_job': 'cleanup_job',
    'stats_job': 'stats_job'
}

# Task names
TASK_NAMES = {
    'crawl': 'crawl_property_ads',
    'send_ads': 'send_ads_to_users',
    'scheduled': 'scheduled_crawl_and_send'
}

__all__ = [
    'crawl_property_ads',
    'send_ads_to_users',
    'scheduled_crawl_and_send',
    'start_crawler_tasks',
    'format_ad_message',
    
    # Constants
    'DEFAULT_INTERVAL_MINUTES',
    'MAX_CONCURRENT_JOBS',
    'JOB_IDS',
    'TASK_NAMES'
]

__version__ = '1.0.0'
__author__ = 'Property Bot Team'
__description__ = 'Task scheduling and background job management for property advertisement bot'