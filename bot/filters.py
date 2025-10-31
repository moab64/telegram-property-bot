import re
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

def apply_keyword_filters(ad, user_filter) -> bool:
    """
    Apply keyword filters to an advertisement
    Returns True if ad passes all filters, False otherwise
    """
    try:
        # Combine title and description for keyword search
        text = (ad.title + ' ' + (ad.description or '')).lower()
        
        # Check include keywords
        if user_filter.include_keywords:
            include_words = [word.strip().lower() for word in user_filter.include_keywords.split(',')]
            for word in include_words:
                if word and word not in text:
                    return False
        
        # Check exclude keywords
        if user_filter.exclude_keywords:
            exclude_words = [word.strip().lower() for word in user_filter.exclude_keywords.split(',')]
            for word in exclude_words:
                if word and word in text:
                    return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error applying keyword filters: {e}")
        return True  # If there's an error, don't filter out the ad

def validate_price(price_text: str) -> Optional[int]:
    """
    Validate and parse price text to integer
    """
    try:
        if not price_text or price_text == 'رایگان':
            return None
        
        # Remove commas and non-digit characters
        cleaned = re.sub(r'[^\d]', '', price_text)
        if cleaned:
            return int(cleaned)
        return None
    except (ValueError, TypeError):
        return None

def validate_area(area_text: str) -> Optional[int]:
    """
    Validate and parse area text to integer
    """
    try:
        if not area_text:
            return None
        
        # Extract numbers from area text
        match = re.search(r'(\d+)', area_text)
        if match:
            return int(match.group(1))
        return None
    except (ValueError, TypeError):
        return None

def extract_bedrooms(text: str) -> Optional[int]:
    """
    Extract number of bedrooms from text
    """
    try:
        if not text:
            return None
        
        patterns = [
            r'(\d+)\s*خواب',
            r'(\d+)\s*bedroom',
            r'(\d+)\s*room'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        return None
    except (ValueError, TypeError):
        return None

def determine_advertiser_type(title: str, description: str) -> str:
    """
    Determine if advertiser is owner or agent
    """
    text = (title + ' ' + (description or '')).lower()
    
    agent_keywords = ['مشاور', 'املاک', 'آژانس', 'دفتر', 'agency', 'agent']
    owner_keywords = ['مالک', 'واحد', 'شخصی', 'owner', 'personal']
    
    for keyword in agent_keywords:
        if keyword in text:
            return 'agent'
    
    for keyword in owner_keywords:
        if keyword in text:
            return 'owner'
    
    return 'owner'  # Default to owner

def determine_property_type(title: str, description: str) -> str:
    """
    Determine property type from title and description
    """
    text = (title + ' ' + (description or '')).lower()
    
    type_mapping = {
        'apartment': ['آپارتمان', 'آپارتما', 'apartment'],
        'house': ['خانه', 'ویلا', 'ویلا', 'خانه', 'villa', 'house'],
        'commercial': ['تجاری', 'مغازه', 'دفتر', 'commercial', 'shop', 'office'],
        'land': ['زمین', 'پلاک', 'land', 'plot'],
        'garden': ['باغ', 'باغچه', 'garden', 'farm']
    }
    
    for prop_type, keywords in type_mapping.items():
        for keyword in keywords:
            if keyword in text:
                return prop_type
    
    return 'apartment'  # Default to apartment

def extract_district(text: str) -> str:
    """
    Extract district/neighborhood from text
    """
    if not text:
        return ''
    
    patterns = [
        r'خیابان\s+([^\s،]+)',
        r'محله\s+([^\s،]+)',
        r'کوی\s+([^\s،]+)',
        r'میدان\s+([^\s،]+)',
        r'بلوار\s+([^\s،]+)',
        r'ناحیه\s+([^\s،]+)',
        r'منطقه\s+([^\s،]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    return ''

def format_price(price: Optional[int]) -> str:
    """
    Format price for display
    """
    if not price:
        return "توافقی"
    
    if price >= 1_000_000_000:
        return f"{price / 1_000_000_000:.1f} میلیارد"
    elif price >= 1_000_000:
        return f"{price / 1_000_000:.0f} میلیون"
    else:
        return f"{price:,}"

def should_send_ad(ad, user_filter) -> bool:
    """
    Comprehensive check to determine if ad should be sent to user
    """
    try:
        # Check basic filters
        if user_filter.city and ad.city != user_filter.city:
            return False
        
        if user_filter.property_type and ad.property_type != user_filter.property_type:
            return False
        
        if user_filter.advertiser_type and ad.advertiser_type != user_filter.advertiser_type:
            return False
        
        # Check price range
        if ad.price:
            if user_filter.min_price and ad.price < user_filter.min_price:
                return False
            if user_filter.max_price and ad.price > user_filter.max_price:
                return False
        
        # Check area range
        if ad.area:
            if user_filter.min_area and ad.area < user_filter.min_area:
                return False
            if user_filter.max_area and ad.area > user_filter.max_area:
                return False
        
        # Check bedrooms
        if user_filter.bedrooms and ad.bedrooms != user_filter.bedrooms:
            return False
        
        # Check keywords
        if not apply_keyword_filters(ad, user_filter):
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error in should_send_ad: {e}")
        return False