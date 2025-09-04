"""
Example usage of ScraperEtico class
"""

from src.scraper_etico import ScraperEtico
import logging

def main():
    """Demonstrate ScraperEtico usage"""
    
    # Initialize the scraper with custom settings
    scraper = ScraperEtico(
        user_agent="MyBot/1.0 (Contact: example@email.com)",
        default_delay=2.0,  # 2 seconds between requests
        timeout=20.0,
        log_level=logging.DEBUG  # Show detailed logs
    )
    
    # Example URLs to test
    test_urls = [
        "https://www.example.com/",
        "https://www.python.org/",
    ]
    
    for url in test_urls:
        print(f"\n{'='*50}")
        print(f"Testing URL: {url}")
        print('='*50)
        
        # Check if we can fetch the URL
        can_fetch = scraper.can_fetch(url)
        print(f"Can fetch according to robots.txt: {can_fetch}")
        
        # Get crawl delay if specified
        crawl_delay = scraper.get_crawl_delay(url)
        if crawl_delay:
            print(f"Recommended crawl delay: {crawl_delay}s")
        
        # Attempt to fetch the URL
        if can_fetch:
            response = scraper.get(url)
            if response:
                print(f"Success! Status code: {response.status_code}")
                print(f"Content length: {len(response.content)} bytes")
                print(f"Content type: {response.headers.get('content-type', 'unknown')}")
            else:
                print("Failed to fetch the URL")
        else:
            print("Skipping fetch - disallowed by robots.txt")
    
    # Clear cache when done
    scraper.clear_cache()
    print("\nCache cleared. Scraping session complete.")


if __name__ == "__main__":
    main()