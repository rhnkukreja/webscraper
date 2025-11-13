"""
Google Reviews Scraper
A tool to scrape reviews from Google Business pages
"""

import time
import json
import csv
from typing import List, Dict, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


class GoogleReviewsScraper:
    """Scraper for Google Business Reviews"""

    def __init__(self, headless: bool = True, language: str = 'en'):
        """
        Initialize the scraper

        Args:
            headless: Run browser in headless mode
            language: Language for the browser
        """
        self.headless = headless
        self.language = language
        self.driver = None
        self.reviews = []

    def _setup_driver(self):
        """Set up Chrome driver with options"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless')

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument(f'--lang={self.language}')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # Exclude automation flags
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def _scroll_reviews(self, scrolls: int = 5):
        """
        Scroll through reviews to load more

        Args:
            scrolls: Number of times to scroll
        """
        try:
            # Find the scrollable reviews container
            scrollable_div = self.driver.find_element(By.CSS_SELECTOR, 'div[role="main"]')

            for i in range(scrolls):
                # Scroll down
                self.driver.execute_script(
                    'arguments[0].scrollTo(0, arguments[0].scrollHeight);',
                    scrollable_div
                )
                time.sleep(2)  # Wait for content to load
                print(f"Scroll {i+1}/{scrolls} completed")

        except Exception as e:
            print(f"Scrolling error: {e}")

    def _expand_reviews(self):
        """Click 'More' buttons to expand truncated reviews"""
        try:
            more_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button[aria-label*="More"]')

            for button in more_buttons[:10]:  # Expand first 10 to avoid too many clicks
                try:
                    self.driver.execute_script("arguments[0].click();", button)
                    time.sleep(0.3)
                except:
                    continue

        except Exception as e:
            print(f"Error expanding reviews: {e}")

    def _parse_reviews(self) -> List[Dict]:
        """
        Parse reviews from the page

        Returns:
            List of review dictionaries
        """
        reviews = []

        try:
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'lxml')

            # Find all review elements
            review_elements = soup.find_all('div', class_='jftiEf')

            print(f"Found {len(review_elements)} review elements")

            for idx, review_elem in enumerate(review_elements):
                try:
                    review_data = {}

                    # Reviewer name
                    name_elem = review_elem.find('div', class_='d4r55')
                    review_data['reviewer_name'] = name_elem.text.strip() if name_elem else 'N/A'

                    # Rating (aria-label contains rating info)
                    rating_elem = review_elem.find('span', class_='kvMYJc')
                    if rating_elem and rating_elem.get('aria-label'):
                        rating_text = rating_elem.get('aria-label')
                        # Extract number from "X stars" or "X star"
                        rating = rating_text.split()[0] if rating_text else 'N/A'
                        review_data['rating'] = rating
                    else:
                        review_data['rating'] = 'N/A'

                    # Review text
                    text_elem = review_elem.find('span', class_='wiI7pd')
                    review_data['review_text'] = text_elem.text.strip() if text_elem else 'N/A'

                    # Date
                    date_elem = review_elem.find('span', class_='rsqaWe')
                    review_data['review_date'] = date_elem.text.strip() if date_elem else 'N/A'

                    # Number of reviews by this reviewer
                    reviewer_stats = review_elem.find('div', class_='RfnDt')
                    review_data['reviewer_stats'] = reviewer_stats.text.strip() if reviewer_stats else 'N/A'

                    reviews.append(review_data)

                except Exception as e:
                    print(f"Error parsing review {idx}: {e}")
                    continue

        except Exception as e:
            print(f"Error parsing reviews: {e}")

        return reviews

    def scrape(self, url: str, max_scrolls: int = 5) -> List[Dict]:
        """
        Scrape reviews from a Google Business page

        Args:
            url: URL of the Google Business page
            max_scrolls: Maximum number of scrolls to perform

        Returns:
            List of review dictionaries
        """
        try:
            print("Setting up Chrome driver...")
            self._setup_driver()

            print(f"Loading URL: {url}")
            self.driver.get(url)

            # Wait for page to load
            time.sleep(3)

            # Click on reviews tab if not already there
            try:
                reviews_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label*="Reviews"]'))
                )
                reviews_button.click()
                time.sleep(2)
                print("Clicked on Reviews tab")
            except:
                print("Reviews tab not found or already on reviews")

            # Sort by newest (optional, can be modified)
            try:
                sort_button = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label*="Sort"]')
                sort_button.click()
                time.sleep(1)

                # Click on "Newest" option
                newest_option = self.driver.find_element(By.XPATH, "//div[@role='menuitemradio' and contains(., 'Newest')]")
                newest_option.click()
                time.sleep(2)
                print("Sorted by newest")
            except:
                print("Could not sort reviews, continuing...")

            # Scroll to load more reviews
            print(f"Scrolling to load more reviews ({max_scrolls} scrolls)...")
            self._scroll_reviews(scrolls=max_scrolls)

            # Expand truncated reviews
            print("Expanding truncated reviews...")
            self._expand_reviews()

            # Parse reviews
            print("Parsing reviews...")
            self.reviews = self._parse_reviews()

            print(f"Successfully scraped {len(self.reviews)} reviews")

            return self.reviews

        except Exception as e:
            print(f"Error during scraping: {e}")
            return []

        finally:
            if self.driver:
                self.driver.quit()
                print("Browser closed")

    def save_to_json(self, filename: str = 'reviews.json'):
        """
        Save reviews to JSON file

        Args:
            filename: Output filename
        """
        if not self.reviews:
            print("No reviews to save")
            return

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.reviews, f, ensure_ascii=False, indent=2)

        print(f"Saved {len(self.reviews)} reviews to {filename}")

    def save_to_csv(self, filename: str = 'reviews.csv'):
        """
        Save reviews to CSV file

        Args:
            filename: Output filename
        """
        if not self.reviews:
            print("No reviews to save")
            return

        keys = self.reviews[0].keys()

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.reviews)

        print(f"Saved {len(self.reviews)} reviews to {filename}")

    def get_reviews(self) -> List[Dict]:
        """
        Get the scraped reviews

        Returns:
            List of review dictionaries
        """
        return self.reviews


if __name__ == "__main__":
    # Example usage
    url = "https://www.google.com/maps/place/Googleplex/@37.4220041,-122.0862515,17z/"

    scraper = GoogleReviewsScraper(headless=True)
    reviews = scraper.scrape(url, max_scrolls=3)

    # Save results
    scraper.save_to_json('google_reviews.json')
    scraper.save_to_csv('google_reviews.csv')

    # Print summary
    print(f"\n=== Summary ===")
    print(f"Total reviews scraped: {len(reviews)}")

    if reviews:
        print("\nFirst review:")
        print(f"Name: {reviews[0].get('reviewer_name')}")
        print(f"Rating: {reviews[0].get('rating')}")
        print(f"Date: {reviews[0].get('review_date')}")
        print(f"Text: {reviews[0].get('review_text')[:100]}...")
