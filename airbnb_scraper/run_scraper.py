import os
import sys
import django
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from datetime import datetime

# Set up Django environment
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airbnb_project.settings')
django.setup()


def run_spider(location=None, check_in=None, check_out=None, guests=None):
    """
    Run the Airbnb spider with the given parameters
    """
    # Format dates if provided
    if check_in and isinstance(check_in, datetime):
        check_in = check_in.strftime('%Y-%m-%d')

    if check_out and isinstance(check_out, datetime):
        check_out = check_out.strftime('%Y-%m-%d')

    # Get Scrapy settings
    settings = get_project_settings()

    # Create and configure the crawler process
    process = CrawlerProcess(settings)

    # Add the spider to the process with parameters
    process.crawl(
        'airbnb',
        location=location,
        check_in=check_in,
        check_out=check_out,
        guests=str(guests) if guests else None
    )

    # Start the crawling process
    process.start()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run Airbnb scraper')
    parser.add_argument('--location', type=str, help='Location to search for')
    parser.add_argument('--check-in', type=str,
                        help='Check-in date (YYYY-MM-DD)')
    parser.add_argument('--check-out', type=str,
                        help='Check-out date (YYYY-MM-DD)')
    parser.add_argument('--guests', type=int, help='Number of guests')

    args = parser.parse_args()

    run_spider(
        location=args.location,
        check_in=args.check_in,
        check_out=args.check_out,
        guests=args.guests
    )
