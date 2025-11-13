"""
Debug script to inspect Google Maps page structure
This helps identify the correct CSS selectors
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


def debug_google_maps(url: str):
    """Debug script to see what elements are on the page"""

    # Setup Chrome
    chrome_options = Options()
    # Run in non-headless to see what's happening
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        print(f"Loading URL: {url}")
        driver.get(url)
        time.sleep(5)  # Wait for page to load

        # Save page source
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("Page source saved to page_source.html")

        # Try to find rating
        print("\n=== Looking for Rating ===")
        possible_rating_selectors = [
            'div.F7nice span[aria-hidden="true"]',
            'div[jsaction*="rating"] span',
            'span[aria-label*="stars"]',
            'div[role="img"][aria-label*="stars"]',
        ]
        for selector in possible_rating_selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✓ Found with selector: {selector}")
                print(f"  Text: {elem.text}")
                print(f"  Aria-label: {elem.get_attribute('aria-label')}")
            except:
                print(f"✗ Not found: {selector}")

        # Try to find address/location
        print("\n=== Looking for Address ===")
        possible_address_selectors = [
            'button[data-item-id="address"]',
            'button[aria-label*="Address"]',
            'div[data-section-id="ad"] button',
            'button[data-tooltip*="Copy address"]',
        ]
        for selector in possible_address_selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✓ Found with selector: {selector}")
                print(f"  Text: {elem.text}")
                print(f"  Aria-label: {elem.get_attribute('aria-label')}")
            except:
                print(f"✗ Not found: {selector}")

        # Try to find phone
        print("\n=== Looking for Phone ===")
        possible_phone_selectors = [
            'button[data-item-id*="phone"]',
            'button[aria-label*="Phone"]',
            'button[data-tooltip*="Copy phone"]',
        ]
        for selector in possible_phone_selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✓ Found with selector: {selector}")
                print(f"  Text: {elem.text}")
                print(f"  Aria-label: {elem.get_attribute('aria-label')}")
            except:
                print(f"✗ Not found: {selector}")

        # Try to find reviews button
        print("\n=== Looking for Reviews Button ===")
        possible_review_button_selectors = [
            'button[aria-label*="Reviews"]',
            'button[aria-label*="reviews"]',
            'div[role="tablist"] button',
        ]
        for selector in possible_review_button_selectors:
            try:
                elems = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"✓ Found {len(elems)} elements with selector: {selector}")
                for i, elem in enumerate(elems[:3]):
                    print(f"  [{i}] Text: {elem.text}, Aria-label: {elem.get_attribute('aria-label')}")
            except Exception as e:
                print(f"✗ Error with selector {selector}: {e}")

        # Try to find review elements
        print("\n=== Looking for Review Elements ===")
        soup = BeautifulSoup(driver.page_source, 'lxml')

        # Try different class patterns
        possible_review_classes = ['jftiEf', 'jJc9Ad', 'MyEned', 'fontBodyMedium']
        for class_name in possible_review_classes:
            elements = soup.find_all('div', class_=class_name)
            if elements:
                print(f"✓ Found {len(elements)} elements with class: {class_name}")
                print(f"  First element preview: {str(elements[0])[:200]}...")

        # Look for any div with review-like content
        print("\n=== Looking for divs with review patterns ===")
        review_divs = soup.find_all('div', class_=lambda x: x and ('review' in x.lower() or 'rating' in x.lower()))
        print(f"Found {len(review_divs)} divs with 'review' or 'rating' in class name")

        input("\nPress Enter to close browser...")

    finally:
        driver.quit()
        print("Browser closed")


if __name__ == "__main__":
    # Test with Googleplex
    url = "https://www.google.com/maps/place/Googleplex/@37.4220041,-122.0862515,17z/"
    debug_google_maps(url)
