import re
import asyncio
import aiohttp
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter for API requests"""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def acquire(self):
        """Acquire permission to make a request"""
        now = datetime.now()
        
        # Remove old requests
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < timedelta(seconds=self.time_window)]
        
        # Check if we've exceeded the rate limit
        if len(self.requests) >= self.max_requests:
            oldest_request = self.requests[0]
            wait_time = self.time_window - (now - oldest_request).total_seconds()
            if wait_time > 0:
                logger.debug(f"Rate limit exceeded, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
                self.requests = []  # Reset after waiting
        
        # Add current request
        self.requests.append(now)

class ProxyManager:
    """Manage proxy servers for requests"""
    
    def __init__(self, proxy_list: List[str] = None):
        self.proxies = proxy_list or []
        self.current_proxy = None
        self.proxy_index = 0
    
    def get_proxy(self) -> Optional[str]:
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        self.current_proxy = proxy
        return proxy
    
    def mark_bad_proxy(self, proxy: str):
        """Mark a proxy as bad (remove from list)"""
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            logger.warning(f"Removed bad proxy: {proxy}")
            
            # Reset index if necessary
            if self.proxy_index >= len(self.proxies):
                self.proxy_index = 0

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator for retrying functions on failure
    
    Args:
        max_retries: Maximum number of retries
        delay: Initial delay between retries
        backoff: Backoff multiplier
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            
            while retries <= max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                        raise
                    
                    logger.warning(f"Function {func.__name__} failed (attempt {retries}/{max_retries}), retrying in {current_delay}s: {e}")
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                        raise
                    
                    logger.warning(f"Function {func.__name__} failed (attempt {retries}/{max_retries}), retrying in {current_delay}s: {e}")
                    import time
                    time.sleep(current_delay)
                    current_delay *= backoff
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Input text to clean
    
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Replace multiple whitespaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove extra spaces around punctuation
    text = re.sub(r'\s*([.,!?;:])\s*', r'\1 ', text)
    
    # Trim and strip
    text = text.strip()
    
    return text

def extract_numbers(text: str) -> List[int]:
    """
    Extract all numbers from text
    
    Args:
        text: Input text
    
    Returns:
        List of numbers found
    """
    if not text:
        return []
    
    numbers = re.findall(r'\d+', text)
    return [int(num) for num in numbers]

def format_currency(amount: int, currency: str = "تومان") -> str:
    """
    Format currency amount
    
    Args:
        amount: Amount to format
        currency: Currency symbol
    
    Returns:
        Formatted currency string
    """
    if not amount:
        return "توافقی"
    
    if amount >= 1_000_000_000:
        return f"{amount / 1_000_000_000:.1f} میلیارد {currency}"
    elif amount >= 1_000_000:
        return f"{amount / 1_000_000:.0f} میلیون {currency}"
    else:
        return f"{amount:,} {currency}"

def format_area(area: int) -> str:
    """
    Format area with unit
    
    Args:
        area: Area in square meters
    
    Returns:
        Formatted area string
    """
    if not area:
        return "نامشخص"
    
    return f"{area:,} متر مربع"

def is_valid_url(url: str) -> bool:
    """
    Check if URL is valid
    
    Args:
        url: URL to validate
    
    Returns:
        True if URL is valid
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def normalize_url(url: str, base_url: str = None) -> str:
    """
    Normalize URL by joining with base URL if relative
    
    Args:
        url: URL to normalize
        base_url: Base URL for relative URLs
    
    Returns:
        Normalized URL
    """
    if not url:
        return ""
    
    if base_url and not url.startswith(('http://', 'https://')):
        return urljoin(base_url, url)
    
    return url

async def make_http_request(
    url: str,
    method: str = "GET",
    session: aiohttp.ClientSession = None,
    headers: Dict[str, str] = None,
    proxy: str = None,
    timeout: int = 30
) -> Tuple[Optional[str], int]:
    """
    Make HTTP request with error handling
    
    Args:
        url: URL to request
        method: HTTP method
        session: aiohttp session
        headers: Request headers
        proxy: Proxy server
        timeout: Request timeout
    
    Returns:
        Tuple of (response_text, status_code)
    """
    close_session = False
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True
    
    try:
        async with session.request(
            method=method,
            url=url,
            headers=headers,
            proxy=proxy,
            timeout=aiohttp.ClientTimeout(total=timeout)
        ) as response:
            text = await response.text()
            return text, response.status
            
    except asyncio.TimeoutError:
        logger.error(f"Request timeout for URL: {url}")
        return None, 408
    except aiohttp.ClientError as e:
        logger.error(f"HTTP client error for URL {url}: {e}")
        return None, 0
    except Exception as e:
        logger.error(f"Unexpected error for URL {url}: {e}")
        return None, 0
    finally:
        if close_session and session:
            await session.close()

def generate_user_agent() -> str:
    """
    Generate random user agent string
    
    Returns:
        User agent string
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
    ]
    
    return random.choice(user_agents)

def parse_persian_number(text: str) -> Optional[int]:
    """
    Parse Persian numbers to integers
    
    Args:
        text: Text containing Persian numbers
    
    Returns:
        Parsed integer or None
    """
    if not text:
        return None
    
    # Persian to English digit mapping
    persian_digits = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    
    # Convert Persian digits to English
    for persian, english in persian_digits.items():
        text = text.replace(persian, english)
    
    # Extract numbers
    numbers = re.findall(r'\d+', text)
    if numbers:
        return int(''.join(numbers))
    
    return None

def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts (simple implementation)
    
    Args:
        text1: First text
        text2: Second text
    
    Returns:
        Similarity score between 0 and 1
    """
    if not text1 or not text2:
        return 0.0
    
    text1 = text1.lower()
    text2 = text2.lower()
    
    # Simple word-based similarity
    words1 = set(text1.split())
    words2 = set(text2.split())
    
    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks of specified size
    
    Args:
        lst: List to split
        chunk_size: Size of each chunk
    
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

async def safe_async_execution(coro, default_value=None):
    """
    Safely execute async coroutine and return default value on error
    
    Args:
        coro: Coroutine to execute
        default_value: Value to return on error
    
    Returns:
        Coroutine result or default_value
    """
    try:
        return await coro
    except Exception as e:
        logger.error(f"Error in safe_async_execution: {e}")
        return default_value

class Cache:
    """Simple in-memory cache with TTL"""
    
    def __init__(self, ttl: int = 300):  # 5 minutes default
        self.ttl = ttl
        self._cache = {}
    
    def set(self, key: str, value: Any):
        """Set cache value"""
        self._cache[key] = {
            'value': value,
            'expires': datetime.now() + timedelta(seconds=self.ttl)
        }
    
    def get(self, key: str) -> Any:
        """Get cache value"""
        if key not in self._cache:
            return None
        
        item = self._cache[key]
        if datetime.now() > item['expires']:
            del self._cache[key]
            return None
        
        return item['value']
    
    def delete(self, key: str):
        """Delete cache value"""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self):
        """Clear all cache"""
        self._cache.clear()

# Global cache instance
cache = Cache()

def get_emoji_for_property_type(property_type: str) -> str:
    """
    Get emoji for property type
    
    Args:
        property_type: Property type
    
    Returns:
        Emoji string
    """
    emoji_map = {
        'apartment': '🏠',
        'house': '🏡',
        'commercial': '🏢',
        'land': '📄',
        'garden': '🌳'
    }
    return emoji_map.get(property_type, '🏠')

def format_timestamp(timestamp: datetime) -> str:
    """
    Format timestamp for display
    
    Args:
        timestamp: Datetime object
    
    Returns:
        Formatted timestamp string
    """
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 7:
        return timestamp.strftime("%Y-%m-%d")
    elif diff.days > 0:
        return f"{diff.days} روز پیش"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} ساعت پیش"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} دقیقه پیش"
    else:
        return "همین الان"