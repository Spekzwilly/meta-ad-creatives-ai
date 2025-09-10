"""
Product metadata extraction utilities.
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class ProductMetadataExtractor:
    """Extracts product metadata from e-commerce URLs."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def extract_metadata(self, url: str) -> Dict:
        """Extract metadata from product page URL."""
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract description
            description = self._extract_description(soup)
            
            # Extract image
            image_url = self._extract_image(soup)
            
            # Extract price
            price = self._extract_price(soup)
            
            # Extract USPs (Unique Selling Points)
            usps = self._extract_usps(soup)
            
            return {
                "title": title,
                "description": description,
                "image": image_url,
                "price": price,
                "usps": usps,
                "url": url
            }
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {url}: {str(e)}")
            return {
                "title": "",
                "description": "",
                "image": "",
                "price": "",
                "usps": [],
                "url": url,
                "error": str(e)
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract product title."""
        # Try Open Graph title first
        title = soup.find('meta', property='og:title')
        if title:
            return title.get('content', '').strip()
        
        # Try page title
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.string.strip() if title_tag.string else ''
        
        return ""
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract product description."""
        # Try meta description
        desc = soup.find('meta', attrs={'name': 'description'})
        if desc:
            return desc.get('content', '').strip()
        
        # Try Open Graph description
        desc = soup.find('meta', property='og:description')
        if desc:
            return desc.get('content', '').strip()
        
        return ""
    
    def _extract_image(self, soup: BeautifulSoup) -> str:
        """Extract main product image."""
        # Try Open Graph image
        img = soup.find('meta', property='og:image')
        if img:
            return img.get('content', '').strip()
        
        # Try first image tag
        img_tag = soup.find('img')
        if img_tag and img_tag.has_attr('src'):
            return img_tag['src']
        
        return ""
    
    def _extract_price(self, soup: BeautifulSoup) -> str:
        """Extract product price."""
        # Common price selectors
        price_selectors = [
            '.price', '.product-price', '.price-current',
            '[class*="price"]', '[data-price]'
        ]
        
        for selector in price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                return price_element.get_text().strip()
        
        return ""
    
    def _extract_usps(self, soup: BeautifulSoup) -> List[str]:
        """Extract unique selling points from bullet points."""
        usps = []
        
        # Try to find list items
        for li in soup.find_all('li'):
            text = li.get_text().strip()
            if text and len(text) > 10:  # Filter out short/empty items
                usps.append(text)
        
        return usps[:10]  # Limit to top 10 USPs
