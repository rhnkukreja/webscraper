"""
Google Reviews Scraper
A tool to scrape reviews from Google Business pages
"""

import time
import json
import csv
import re
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
        self.business_info = {}

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

    def _extract_business_info(self):
        """Extract business information from the page"""
        try:
            soup = BeautifulSoup(self.driver.page_source, 'lxml')

            # Overall Rating
            try:
                rating_elem = self.driver.find_element(By.CSS_SELECTOR, 'div.F7nice span[aria-hidden="true"]')
                self.business_info['rating'] = rating_elem.text.strip()
                print(f"Found rating: {self.business_info['rating']}")
            except:
                self.business_info['rating'] = 'N/A'
                print("Rating not found")

            # Location/Address
            try:
                address_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-item-id="address"]')
                address_text = address_button.get_attribute('aria-label')
                if address_text:
                    # Extract address from "Address: ..." format
                    self.business_info['location'] = address_text.replace('Address: ', '').strip()
                else:
                    self.business_info['location'] = 'N/A'
                print(f"Found location: {self.business_info['location']}")
            except:
                self.business_info['location'] = 'N/A'
                print("Location not found")

            # Contact Information (Phone)
            try:
                phone_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-item-id*="phone"]')
                phone_text = phone_button.get_attribute('aria-label')
                if phone_text:
                    # Extract phone from "Phone: ..." format
                    self.business_info['contact'] = phone_text.replace('Phone: ', '').strip()
                else:
                    self.business_info['contact'] = 'N/A'
                print(f"Found contact: {self.business_info['contact']}")
            except:
                self.business_info['contact'] = 'N/A'
                print("Contact not found")

            # Cost for One (Price range)
            try:
                # Look for price range indicators like "$", "$$", "$$$"
                price_elem = soup.find('span', {'aria-label': re.compile(r'Price:.*', re.IGNORECASE)})
                if price_elem:
                    self.business_info['cost_for_one'] = price_elem.text.strip()
                else:
                    # Alternative: look in the attributes section
                    price_button = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label*="Price"]')
                    price_text = price_button.get_attribute('aria-label')
                    if price_text:
                        self.business_info['cost_for_one'] = price_text.replace('Price: ', '').strip()
                    else:
                        self.business_info['cost_for_one'] = 'N/A'
                print(f"Found cost for one: {self.business_info['cost_for_one']}")
            except:
                self.business_info['cost_for_one'] = 'N/A'
                print("Cost for one not found")

        except Exception as e:
            print(f"Error extracting business info: {e}")

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

            for button in more_buttons[:20]:  # Expand more reviews
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
                        review_data['rating'] = int(rating) if rating.isdigit() else rating
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

    def _get_oldest_review_date(self) -> str:
        """
        Get the oldest review by sorting by 'Oldest' and fetching the first review

        Returns:
            Date string of the oldest review
        """
        try:
            print("\nFetching oldest review...")

            # Click sort button
            sort_button = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label*="Sort"]')
            sort_button.click()
            time.sleep(1)

            # Click on "Oldest" option
            oldest_option = self.driver.find_element(By.XPATH, "//div[@role='menuitemradio' and contains(., 'Oldest')]")
            oldest_option.click()
            time.sleep(3)
            print("Sorted by oldest")

            # Parse just the first review
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            review_elements = soup.find_all('div', class_='jftiEf')

            if review_elements:
                first_review = review_elements[0]
                date_elem = first_review.find('span', class_='rsqaWe')
                oldest_date = date_elem.text.strip() if date_elem else 'N/A'
                print(f"Oldest review date: {oldest_date}")
                return oldest_date

            return 'N/A'

        except Exception as e:
            print(f"Error getting oldest review: {e}")
            return 'N/A'

    def scrape(self, url: str, max_scrolls: int = 10) -> List[Dict]:
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
            time.sleep(4)

            # Extract business information first
            print("Extracting business information...")
            self._extract_business_info()

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

            # Get oldest review date first
            oldest_date = self._get_oldest_review_date()
            self.business_info['first_review_date'] = oldest_date

            # Now sort by newest to get recent reviews
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

    def get_negative_reviews(self) -> List[Dict]:
        """
        Get all negative reviews (1-3 stars)

        Returns:
            List of negative review dictionaries
        """
        negative_reviews = []
        for review in self.reviews:
            rating = review.get('rating')
            if isinstance(rating, int) and rating <= 3:
                negative_reviews.append(review)
        return negative_reviews

    def get_last_negative_review(self) -> Optional[Dict]:
        """
        Get the most recent negative review

        Returns:
            Dictionary with negative review info or None
        """
        negative_reviews = self.get_negative_reviews()
        if negative_reviews:
            # Since reviews are sorted by newest, first negative is the most recent
            return negative_reviews[0]
        return None

    def generate_business_summary(self) -> Dict:
        """
        Generate a summary with all requested business information

        Returns:
            Dictionary with business summary
        """
        negative_reviews = self.get_negative_reviews()
        last_negative = self.get_last_negative_review()

        summary = {
            "business_info": {
                "rating": self.business_info.get('rating', 'N/A'),
                "location": self.business_info.get('location', 'N/A'),
                "contact_information": self.business_info.get('contact', 'N/A'),
                "cost_for_one": self.business_info.get('cost_for_one', 'N/A')
            },
            "reviews_summary": {
                "total_reviews_scraped": len(self.reviews),
                "total_negative_reviews": len(negative_reviews),
                "first_review_date": self.business_info.get('first_review_date', 'N/A'),
                "last_negative_review": {
                    "content": last_negative.get('review_text', 'N/A') if last_negative else 'N/A',
                    "date": last_negative.get('review_date', 'N/A') if last_negative else 'N/A',
                    "rating": last_negative.get('rating', 'N/A') if last_negative else 'N/A'
                } if last_negative else None
            }
        }

        return summary

    def save_business_summary(self, filename: str = 'business_summary.json'):
        """
        Save business summary to JSON file

        Args:
            filename: Output filename
        """
        summary = self.generate_business_summary()

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"\nBusiness summary saved to {filename}")
        print(f"\n=== Business Summary ===")
        print(f"Rating: {summary['business_info']['rating']}")
        print(f"Location: {summary['business_info']['location']}")
        print(f"Contact: {summary['business_info']['contact_information']}")
        print(f"Cost for One: {summary['business_info']['cost_for_one']}")
        print(f"First Review Date: {summary['reviews_summary']['first_review_date']}")
        print(f"Total Negative Reviews: {summary['reviews_summary']['total_negative_reviews']}")
        if summary['reviews_summary']['last_negative_review']:
            print(f"Last Negative Review Date: {summary['reviews_summary']['last_negative_review']['date']}")

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
    reviews = scraper.scrape(url, max_scrolls=5)

    # Save business summary with all requested information
    scraper.save_business_summary('business_summary.json')

    # Save all reviews
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
