import mysql.connector
from itemadapter import ItemAdapter


class MySQLPipeline:
    def __init__(self, mysql_host, mysql_port, mysql_user, mysql_password, mysql_db):
        self.mysql_host = mysql_host
        self.mysql_port = mysql_port
        self.mysql_user = mysql_user
        self.mysql_password = mysql_password
        self.mysql_db = mysql_db
        self.conn = None
        self.cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_host=crawler.settings.get('MYSQL_HOST'),
            mysql_port=crawler.settings.get('MYSQL_PORT'),
            mysql_user=crawler.settings.get('MYSQL_USER'),
            mysql_password=crawler.settings.get('MYSQL_PASSWORD'),
            mysql_db=crawler.settings.get('MYSQL_DB')
        )

    def open_spider(self, spider):
        self.conn = mysql.connector.connect(
            host=self.mysql_host,
            port=self.mysql_port,
            user=self.mysql_user,
            password=self.mysql_password,
            database=self.mysql_db
        )
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Process host data
        host_name = adapter.get('host_name')
        host_image = adapter.get('host_image')
        host_is_superhost = adapter.get('host_is_superhost', False)
        host_joined = adapter.get('host_joined')

        # Check if host exists
        self.cursor.execute(
            "SELECT id FROM listings_host WHERE name = %s",
            (host_name,)
        )
        host_result = self.cursor.fetchone()

        if host_result:
            host_id = host_result[0]
        else:
            # Insert new host
            self.cursor.execute(
                """
                INSERT INTO listings_host (name, image_url, is_superhost, joined_date)
                VALUES (%s, %s, %s, %s)
                """,
                (host_name, host_image, host_is_superhost, host_joined)
            )
            self.conn.commit()
            host_id = self.cursor.lastrowid

        # Process listing data
        title = adapter.get('title')
        location = adapter.get('location')
        address = adapter.get('address')
        price_per_night = adapter.get('price_per_night')
        currency = adapter.get('currency', 'USD')
        total_price = adapter.get('total_price')
        rating = adapter.get('rating')
        description = adapter.get('description')
        reviews_count = adapter.get('reviews_count', 0)
        property_type = adapter.get('property_type')

        # Check if listing exists
        self.cursor.execute(
            "SELECT id FROM listings_listing WHERE title = %s AND location = %s AND host_id = %s",
            (title, location, host_id)
        )
        listing_result = self.cursor.fetchone()

        if listing_result:
            listing_id = listing_result[0]
            # Update existing listing
            self.cursor.execute(
                """
                UPDATE listings_listing
                SET price_per_night = %s, currency = %s, total_price = %s, 
                    rating = %s, description = %s, reviews_count = %s, 
                    property_type = %s, updated_at = NOW()
                WHERE id = %s
                """,
                (price_per_night, currency, total_price, rating, description,
                 reviews_count, property_type, listing_id)
            )
        else:
            # Insert new listing
            self.cursor.execute(
                """
                INSERT INTO listings_listing 
                (title, location, address, price_per_night, currency, total_price, 
                 rating, description, reviews_count, property_type, host_id, 
                 created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """,
                (title, location, address, price_per_night, currency, total_price,
                 rating, description, reviews_count, property_type, host_id)
            )
            self.conn.commit()
            listing_id = self.cursor.lastrowid

        # Process images
        image_urls = adapter.get('image_urls', [])

        # Clear existing images
        self.cursor.execute(
            "DELETE FROM listings_listingimage WHERE listing_id = %s",
            (listing_id,)
        )

        # Insert new images
        for i, image_url in enumerate(image_urls):
            is_primary = (i == 0)
            self.cursor.execute(
                """
                INSERT INTO listings_listingimage (listing_id, image_url, is_primary)
                VALUES (%s, %s, %s)
                """,
                (listing_id, image_url, is_primary)
            )

        # Process amenities
        amenities = adapter.get('amenities', [])

        # Clear existing listing amenities
        self.cursor.execute(
            "DELETE FROM listings_listingamenity WHERE listing_id = %s",
            (listing_id,)
        )

        # Insert new amenities
        for amenity_name in amenities:
            # Check if amenity exists
            self.cursor.execute(
                "SELECT id FROM listings_amenity WHERE name = %s",
                (amenity_name,)
            )
            amenity_result = self.cursor.fetchone()

            if amenity_result:
                amenity_id = amenity_result[0]
            else:
                # Insert new amenity
                self.cursor.execute(
                    "INSERT INTO listings_amenity (name) VALUES (%s)",
                    (amenity_name,)
                )
                self.conn.commit()
                amenity_id = self.cursor.lastrowid

            # Link amenity to listing
            self.cursor.execute(
                """
                INSERT INTO listings_listingamenity (listing_id, amenity_id)
                VALUES (%s, %s)
                """,
                (listing_id, amenity_id)
            )

        self.conn.commit()
        return item
