import json
import scrapy
import re
from datetime import datetime
from urllib.parse import urlencode
from ..items import AirbnbListingItem


class AirbnbSpider(scrapy.Spider):
    name = 'airbnb'
    allowed_domains = ['airbnb.com']

    def __init__(self, location=None, check_in=None, check_out=None, guests=None, *args, **kwargs):
        super(AirbnbSpider, self).__init__(*args, **kwargs)
        self.location = location or 'New York'
        self.check_in = check_in or datetime.now().strftime('%Y-%m-%d')
        self.check_out = check_out or (datetime.now().replace(
            day=datetime.now().day + 5)).strftime('%Y-%m-%d')
        self.guests = guests or '2'

    def start_requests(self):
        # Construct search URL with parameters
        params = {
            'query': self.location,
            'checkin': self.check_in,
            'checkout': self.check_out,
            'adults': self.guests,
            'source': 'search_blocks'
        }

        search_url = f"https://www.airbnb.com/s/{self.location.replace(' ', '-')}/homes?{urlencode(params)}"
        yield scrapy.Request(url=search_url, callback=self.parse_search_results)

    def parse_search_results(self, response):
        # Extract listing URLs from search results
        listing_links = response.css(
            'a[data-testid="card-link"]::attr(href)').getall()

        for link in listing_links:
            if not link.startswith('http'):
                link = f"https://www.airbnb.com{link}"

            yield scrapy.Request(url=link, callback=self.parse_listing)

        # Follow pagination if available
        next_page = response.css('a[aria-label="Next"]::attr(href)').get()
        if next_page:
            if not next_page.startswith('http'):
                next_page = f"https://www.airbnb.com{next_page}"

            yield scrapy.Request(url=next_page, callback=self.parse_search_results)

    def parse_listing(self, response):
        # Extract data from the listing page
        item = AirbnbListingItem()

        # Try to extract JSON data from script tags
        json_data = None
        for script in response.css('script[type="application/json"]::text').getall():
            try:
                data = json.loads(script)
                if 'data' in data and 'presentation' in data.get('data', {}):
                    json_data = data
                    break
            except:
                continue

        if json_data:
            # Extract data from JSON
            try:
                listing_data = json_data['data']['presentation']
                pdp_sections = listing_data.get('pdpSections', {})

                # Basic listing info
                item['title'] = self.extract_text(
                    response.css('h1::text').get())
                item['location'] = self.extract_text(response.css(
                    'span[data-testid="listing-location"]::text').get())
                item['address'] = self.extract_text(response.css(
                    'div[data-testid="listing-address"]::text').get())

                # Price info
                price_text = response.css(
                    'span[data-testid="listing-price"] span::text').get()
                if price_text:
                    price_match = re.search(r'(\$|€|£)(\d+)', price_text)
                    if price_match:
                        item['currency'] = price_match.group(1)
                        item['price_per_night'] = float(price_match.group(2))
                    else:
                        item['currency'] = '$'
                        item['price_per_night'] = self.extract_price(
                            price_text)

                # Total price
                total_price_text = response.css(
                    'span[data-testid="listing-total-price"]::text').get()
                item['total_price'] = self.extract_price(
                    total_price_text) if total_price_text else None

                # Rating and reviews
                rating_text = response.css(
                    'span[data-testid="listing-rating"]::text').get()
                item['rating'] = float(rating_text) if rating_text else None

                reviews_text = response.css(
                    'span[data-testid="listing-reviews-count"]::text').get()
                if reviews_text:
                    reviews_match = re.search(r'(\d+)', reviews_text)
                    item['reviews_count'] = int(
                        reviews_match.group(1)) if reviews_match else 0

                # Description
                item['description'] = self.extract_text(response.css(
                    'div[data-testid="listing-description"]::text').get())

                # Property type
                item['property_type'] = self.extract_text(response.css(
                    'div[data-testid="listing-property-type"]::text').get())

                # Images
                item['image_urls'] = response.css(
                    'img[data-testid="listing-image"]::attr(src)').getall()

                # Amenities
                amenities = response.css(
                    'div[data-testid="listing-amenities"] div::text').getall()
                item['amenities'] = [self.extract_text(
                    amenity) for amenity in amenities if self.extract_text(amenity)]

                # Host information
                host_section = response.css('div[data-testid="host-profile"]')
                item['host_name'] = self.extract_text(
                    host_section.css('h2::text').get())
                item['host_image'] = host_section.css('img::attr(src)').get()

                superhost_badge = host_section.css(
                    'div[data-testid="superhost-badge"]')
                item['host_is_superhost'] = bool(superhost_badge)

                host_joined_text = host_section.css(
                    'div[data-testid="host-joined-date"]::text').get()
                if host_joined_text:
                    joined_match = re.search(
                        r'Joined in (\w+ \d{4})', host_joined_text)
                    if joined_match:
                        try:
                            item['host_joined'] = datetime.strptime(
                                joined_match.group(1), '%B %Y').strftime('%Y-%m-%d')
                        except:
                            item['host_joined'] = None
            except Exception as e:
                self.logger.error(f"Error parsing JSON data: {e}")

        # Fallback to CSS selectors if JSON parsing fails
        if not item.get('title'):
            item['title'] = self.extract_text(response.css('h1::text').get())

        if not item.get('location'):
            item['location'] = self.extract_text(
                response.css('._9xiloll').get())

        if not item.get('price_per_night'):
            price_text = response.css('._tyxjp1').get()
            item['price_per_night'] = self.extract_price(
                price_text) if price_text else None
            item['currency'] = '$'  # Default currency

        if not item.get('image_urls'):
            item['image_urls'] = response.css(
                '._6tbg2q img::attr(src)').getall()

        yield item

    def extract_text(self, text):
        if not text:
            return None
        return text.strip()

    def extract_price(self, text):
        if not text:
            return None
        price_match = re.search(r'(\d+)', text.replace(',', ''))
        return float(price_match.group(1)) if price_match else None
