import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from utils.helpers import retry_on_failure, generate_user_agent, safe_async_execution
import aiohttp
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class BaseCrawler(ABC):
    def __init__(self, config):
        self.config = config
        self.session = None
        self.ua = UserAgent()
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={'User-Agent': self.ua.random},
            timeout=aiohttp.ClientTimeout(total=self.config.crawler.timeout)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def crawl(self, city: str, property_type: str) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def _parse_ad(self, ad_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    async def _make_request(self, url: str, max_retries: int = None) -> str:
        if max_retries is None:
            max_retries = self.config.crawler.max_retries
            
        for attempt in range(max_retries):
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    elif response.status == 429:
                        logger.warning(f"Rate limited. Waiting before retry...")
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        logger.error(f"HTTP {response.status} for URL: {url}")
                        return None
            except Exception as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    
        return None
    
    async def _delay(self):
        await asyncio.sleep(self.config.crawler.request_delay)