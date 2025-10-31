import json
import re
from typing import List, Dict, Any
from .base_crawler import BaseCrawler

class SheypoorCrawler(BaseCrawler):
    async def crawl(self, city: str, property_type: str) -> List[Dict[str, Any]]:
        base_url = f"https://www.sheypoor.com/{city}"
        
        # Map property types to Sheypoor categories
        property_mapping = {
            "apartment": "اجاره-مسکونی-آپارتمان",
            "house": "اجاره-مسکونی-خانه-و-ویلا",
            "commercial": "اجاره-تجاری",
            "land": "اجاره-زمین",
            "garden": "باغ-و-باغچه"
        }
        
        category = property_mapping.get(property_type, "اجاره-مسکونی")
        url = f"{base_url}/{category}"
        
        logger.info(f"Crawling Sheypoor: {url}")
        html = await self._make_request(url)
        
        if not html:
            return []
            
        return self._extract_ads_from_html(html, city)
    
    def _extract_ads_from_html(self, html: str, city: str) -> List[Dict[str, Any]]:
        ads = []
        
        # Extract ad listings from HTML
        pattern = r'<article[^>]*data-id="(\d+)"[^>]*>.*?<a href="([^"]*)"[^>]*>.*?<h2[^>]*>(.*?)</h2>.*?<p[^>]*>(.*?)</p>'
        matches = re.findall(pattern, html, re.DOTALL)
        
        for match in matches:
            ad_id, relative_url, title, details = match
            ad_data = {
                'id': ad_id,
                'url': f"https://www.sheypoor.com{relative_url}",
                'title': self._clean_text(title),
                'details': self._clean_text(details)
            }
            parsed_ad = self._parse_ad(ad_data, city)
            if parsed_ad:
                ads.append(parsed_ad)
                
        return ads
    
    def _parse_ad(self, ad_data: Dict[str, Any], city: str) -> Dict[str, Any]:
        try:
            title = ad_data['title']
            details = ad_data['details']
            
            # Extract price
            price = self._extract_price(details)
            
            # Extract area and bedrooms
            area, bedrooms = self._extract_attributes(title + ' ' + details)
            
            # Determine property type
            property_type = self._determine_property_type(title)
            
            # Determine advertiser type
            advertiser_type = 'agent' if 'مشاور' in title else 'owner'
            
            return {
                'source': 'sheypoor',
                'external_id': ad_data['id'],
                'title': title,
                'description': details,
                'price': price,
                'area': area,
                'bedrooms': bedrooms,
                'property_type': property_type,
                'city': city,
                'district': self._extract_district(title),
                'advertiser_type': advertiser_type,
                'url': ad_data['url']
            }
        except Exception as e:
            logger.error(f"Error parsing Sheypoor ad: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        return re.sub(r'\s+', ' ', text).strip()
    
    def _extract_price(self, text: str) -> int:
        price_match = re.search(r'(\d[\d,]*)\s*تومان', text)
        if price_match:
            price_str = price_match.group(1).replace(',', '')
            return int(price_str)
        return None
    
    def _extract_attributes(self, text: str) -> tuple:
        area = None
        bedrooms = None
        
        # Extract area
        area_match = re.search(r'(\d+)\s*متر', text)
        if area_match:
            area = int(area_match.group(1))
        
        # Extract bedrooms
        room_match = re.search(r'(\d+)\s*خواب', text)
        if room_match:
            bedrooms = int(room_match.group(1))
            
        return area, bedrooms
    
    def _determine_property_type(self, title: str) -> str:
        title_lower = title.lower()
        
        if 'آپارتمان' in title_lower:
            return 'apartment'
        elif 'ویلا' in title_lower or 'خانه' in title_lower:
            return 'house'
        elif 'تجاری' in title_lower or 'مغازه' in title_lower:
            return 'commercial'
        elif 'زمین' in title_lower:
            return 'land'
        elif 'باغ' in title_lower:
            return 'garden'
        else:
            return 'apartment'
    
    def _extract_district(self, title: str) -> str:
        # Simple district extraction
        district_patterns = [
            r'خیابان\s+(\S+)',
            r'محله\s+(\S+)'
        ]
        
        for pattern in district_patterns:
            match = re.search(pattern, title)
            if match:
                return match.group(1)
                
        return ''