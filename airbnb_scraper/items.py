import scrapy


class AirbnbListingItem(scrapy.Item):
    # Listing details
    title = scrapy.Field()
    location = scrapy.Field()
    address = scrapy.Field()
    price_per_night = scrapy.Field()
    currency = scrapy.Field()
    total_price = scrapy.Field()
    image_urls = scrapy.Field()
    rating = scrapy.Field()
    description = scrapy.Field()
    reviews_count = scrapy.Field()
    amenities = scrapy.Field()
    property_type = scrapy.Field()

    # Host details
    host_name = scrapy.Field()
    host_image = scrapy.Field()
    host_is_superhost = scrapy.Field()
    host_joined = scrapy.Field()
