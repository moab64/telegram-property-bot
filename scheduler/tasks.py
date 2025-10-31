import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from database.operations import UserOperations, AdOperations
from crawlers.divar_crawler import DivarCrawler
from crawlers.sheypoor_crawler import SheypoorCrawler
from utils.config import load_config
from bot.filters import apply_keyword_filters

logger = logging.getLogger(__name__)
config = load_config()

async def crawl_property_ads():
    """Crawl property ads from all sources"""
    logger.info("Starting property ads crawl...")
    
    cities = list(config.cities.keys())
    property_types = list(config.property_types.keys())
    
    all_ads = []
    
    # Crawl from Divar
    async with DivarCrawler(config) as divar_crawler:
        for city in cities:
            for property_type in property_types:
                try:
                    ads = await divar_crawler.crawl(city, property_type)
                    all_ads.extend(ads)
                    await asyncio.sleep(config.crawler.request_delay)
                except Exception as e:
                    logger.error(f"Error crawling Divar {city} {property_type}: {e}")
    
    # Crawl from Sheypoor
    async with SheypoorCrawler(config) as sheypoor_crawler:
        for city in cities:
            for property_type in property_types:
                try:
                    ads = await sheypoor_crawler.crawl(city, property_type)
                    all_ads.extend(ads)
                    await asyncio.sleep(config.crawler.request_delay)
                except Exception as e:
                    logger.error(f"Error crawling Sheypoor {city} {property_type}: {e}")
    
    # Save new ads to database
    new_ads_count = 0
    for ad in all_ads:
        if not AdOperations.ad_exists(ad['source'], ad['external_id']):
            saved_ad = AdOperations.create_ad(ad)
            if saved_ad:
                new_ads_count += 1
                logger.info(f"New ad saved: {ad['title']}")
    
    logger.info(f"Crawl completed. {new_ads_count} new ads found.")
    return new_ads_count

async def send_ads_to_users(bot):
    """Send new ads to users based on their filters"""
    logger.info("Sending ads to users...")
    
    # Get all active users with filters
    sent_count = 0
    
    # This would typically involve querying all users with active filters
    # For simplicity, we'll get all users from database
    from database.operations import get_db
    db = get_db()
    
    try:
        users_with_filters = db.query(UserOperations.UserFilter).all()
        
        for user_filter in users_with_filters:
            unsent_ads = AdOperations.get_unsent_ads_for_user(user_filter.user_id, user_filter)
            
            for ad in unsent_ads:
                # Apply keyword filters
                if apply_keyword_filters(ad, user_filter):
                    try:
                        # Format ad message
                        message_text = format_ad_message(ad)
                        
                        # Send message to user
                        await bot.send_message(
                            chat_id=user_filter.user_id,
                            text=message_text,
                            disable_web_page_preview=True
                        )
                        
                        # Mark as sent
                        AdOperations.mark_ad_sent(user_filter.user_id, ad.id)
                        sent_count += 1
                        
                        # Small delay to avoid rate limiting
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        logger.error(f"Error sending ad to user {user_filter.user_id}: {e}")
    
    finally:
        db.close()
    
    logger.info(f"Sent {sent_count} ads to users.")

def format_ad_message(ad):
    """Format ad data into a readable message"""
    # Emoji mapping
    emojis = {
        'apartment': '🏠',
        'house': '🏡',
        'commercial': '🏢',
        'land': '📄',
        'garden': '🌳'
    }
    
    property_emoji = emojis.get(ad.property_type, '🏠')
    
    message = f"{property_emoji} **آگهی جدید فروش {ad.property_type}**\n\n"
    
    if ad.district:
        message += f"📍 موقعیت: {ad.city} ({ad.district})\n"
    else:
        message += f"📍 شهر: {ad.city}\n"
    
    if ad.price:
        message += f"💰 قیمت: {ad.price:,} تومان\n"
    else:
        message += f"💰 قیمت: توافقی\n"
    
    if ad.area:
        message += f"📏 متراژ: {ad.area} متر"
        if ad.bedrooms:
            message += f" | {ad.bedrooms} خواب\n"
        else:
            message += "\n"
    else:
        message += "\n"
    
    if ad.advertiser_type:
        advertiser_text = "مشاور" if ad.advertiser_type == 'agent' else "مالک"
        message += f"👤 آگهی‌دهنده: {advertiser_text}\n"
    
    if ad.description:
        # Truncate long descriptions
        description = ad.description[:200] + "..." if len(ad.description) > 200 else ad.description
        message += f"📝 توضیحات: {description}\n"
    
    message += f"\n🔗 لینک آگهی: {ad.url}"
    
    return message

async def scheduled_crawl_and_send(bot):
    """Scheduled task to crawl and send ads"""
    try:
        # Crawl new ads
        new_ads_count = await crawl_property_ads()
        
        if new_ads_count > 0:
            # Send ads to users
            await send_ads_to_users(bot)
        else:
            logger.info("No new ads to send.")
            
    except Exception as e:
        logger.error(f"Error in scheduled task: {e}")

async def start_crawler_tasks(scheduler: AsyncIOScheduler, bot):
    """Start the periodic crawler tasks"""
    # Schedule crawler to run every 15 minutes
    scheduler.add_job(
        scheduled_crawl_and_send,
        trigger=IntervalTrigger(minutes=15),
        args=[bot],
        id='property_crawler',
        replace_existing=True
    )
    
    logger.info("Crawler tasks scheduled to run every 15 minutes")