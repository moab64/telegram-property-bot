import json
import re
from typing import List, Dict, Any
from .base_crawler import BaseCrawler

class DivarCrawler(BaseCrawler):
    async def crawl(self, city: str, property_type: str) -> List[Dict[str, Any]]:
        base_url = f"https://divar.ir/s/{city}/real-estate"
        
        # Map property types to Divar categories
        property_mapping = {
            "apartment": "apartment",
            "house": "house-villa",
            "commercial": "commercial",
            "land": "land",
            "garden": "garden"
        }
        
        if property_type in property_mapping:
            url = f"{base_url}/{property_mapping[property_type]}"
        else:
            url = base_url
            
        logger.info(f"Crawling Divar: {url}")
        html = await self._make_request(url)
        
        if not html:
            return []
            
        return self._extract_ads_from_html(html, city)
    
    def _extract_ads_from_html(self, html: str, city: str) -> List[Dict[str, Any]]:
        ads = []
        
        # Extract JSON data from script tag
        pattern = r'window\.__PRELOADED_STATE__\s*=\s*({.*?})</script>'
        match = re.search(pattern, html, re.DOTALL)
        
        if not match:
            return ads
            
        try:
            data = json.loads(match.group(1))
            widgets = data.get('feed', {}).get('widget_list', [])
            
            for widget in widgets:
                if widget.get('widget_type') == 'POST_ROW':
                    ad_data = widget.get('data', {})
                    parsed_ad = self._parse_ad(ad_data, city)
                    if parsed_ad:
                        ads.append(parsed_ad)
                        
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Divar JSON: {e}")
            
        return ads
    
    def _parse_ad(self, ad_data: Dict[str, Any], city: str) -> Dict[str, Any]:
        try:
            token = ad_data.get('token', '')
            title = ad_data.get('title', '')
            description = ad_data.get('description', '')
            
            # Extract price
            price = None
            price_text = ad_data.get('price', '')
            if price_text and price_text != 'رایگان':
                price = self._parse_price(price_text)
            
            # Extract area and rooms
            area, bedrooms = self._parse_attributes(ad_data.get('bottom_description', ''))
            
            # Determine property type
            property_type = self._determine_property_type(title, description)
            
            # Determine advertiser type
            advertiser_type = 'agent' if 'مشاور' in title or 'مشاور' in description else 'owner'
            
            return {
                'source': 'divar',
                'external_id': token,
                'title': title,
                'description': description,
                'price': price,
                'area': area,
                'bedrooms': bedrooms,
                'property_type': property_type,
                'city': city,
                'district': self._extract_district(title, description),
                'advertiser_type': advertiser_type,
                'url': f"https://divar.ir/v/{token}"
            }
        except Exception as e:
            logger.error(f"Error parsing Divar ad: {e}")
            return None
    
    def _parse_price(self, price_text: str) -> int:
        # Remove commas and convert to integer
        numbers = re.findall(r'\d+', price_text.replace(',', ''))
        if numbers:
            return int(numbers[0])
        return None
    
    def _parse_attributes(self, text: str) -> tuple:
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
    
    def _determine_property_type(self, title: str, description: str) -> str:
        text = (title + ' ' + description).lower()
        
        if 'آپارتمان' in text or 'آپارتمان' in text:
            return 'apartment'
        elif 'ویلا' in text or 'خانه' in text:
            return 'house'
        elif 'تجاری' in text or 'مغازه' in text:
            return 'commercial'
        elif 'زمین' in text:
            return 'land'
        elif 'باغ' in text:
            return 'garden'
        else:
            return 'apartment'  # Default
    
    def _extract_district(self, title: str, description: str) -> str:
        # Simple district extraction - can be enhanced
        text = title + ' ' + description
        district_patterns = [
            r'خیابان\s+(\S+)',
            r'محله\s+(\S+)',
            r'کوی\s+(\S+)'
        ]
        
        for pattern in district_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
                
        return ''