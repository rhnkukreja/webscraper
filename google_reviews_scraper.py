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
from selenium.webdriver.common.keys import Keys
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
            chrome_options.add_argument('--headless=new')

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

    def _find_element_with_fallback(self, selectors: List[tuple], description: str = "element"):
        """
        Try multiple selectors until one works

        Args:
            selectors: List of tuples (By.METHOD, "selector")
            description: Description for logging

        Returns:
            Element if found, None otherwise
        """
        for by_method, selector in selectors:
            try:
                element = self.driver.find_element(by_method, selector)
                if element:
                    return element
            except:
                continue
        print(f"{description} not found with any selector")
        return None

    def _extract_business_info(self):
        """Extract business information from the page"""
        try:
            # Overall Rating - try multiple selectors
            rating_selectors = [
                (By.XPATH, "//div[contains(@class, 'F7nice')]//span[@aria-hidden='true']"),
                (By.XPATH, "//div[@role='img' and contains(@aria-label, 'stars')]"),
                (By.XPATH, "//span[contains(@aria-label, 'stars')]"),
            ]

            rating_elem = self._find_element_with_fallback(rating_selectors, "Rating")
            if rating_elem:
                # Try to get from text first
                rating_text = rating_elem.text.strip()
                if rating_text and rating_text[0].isdigit():
                    self.business_info['rating'] = rating_text
                    print(f"Found rating: {rating_text}")
                else:
                    # Try aria-label
                    aria_label = rating_elem.get_attribute('aria-label')
                    if aria_label and 'star' in aria_label.lower():
                        # Extract rating from "4.5 stars" format
                        match = re.search(r'(\d+\.?\d*)', aria_label)
                        if match:
                            self.business_info['rating'] = match.group(1)
                            print(f"Found rating from aria-label: {match.group(1)}")
            else:
                self.business_info['rating'] = 'N/A'

            # Location/Address - try multiple approaches
            address_selectors = [
                (By.XPATH, "//button[@data-item-id='address']"),
                (By.XPATH, "//button[contains(@aria-label, 'Address')]"),
                (By.XPATH, "//button[@data-tooltip='Copy address']"),
                (By.XPATH, "//div[@class='rogA2c']//div[contains(text(), ',')]"),  # Often shows address
            ]

            address_elem = self._find_element_with_fallback(address_selectors, "Address")
            if address_elem:
                # Try aria-label first
                aria_label = address_elem.get_attribute('aria-label')
                if aria_label:
                    address = aria_label.replace('Address:', '').replace('Address', '').strip()
                    self.business_info['location'] = address
                    print(f"Found location: {address}")
                else:
                    # Try text content
                    text = address_elem.text.strip()
                    if text:
                        self.business_info['location'] = text
                        print(f"Found location from text: {text}")
            else:
                self.business_info['location'] = 'N/A'

            # Contact Information (Phone)
            phone_selectors = [
                (By.XPATH, "//button[contains(@data-item-id, 'phone')]"),
                (By.XPATH, "//button[contains(@aria-label, 'Phone')]"),
                (By.XPATH, "//button[@data-tooltip='Copy phone number']"),
                (By.XPATH, "//a[starts-with(@href, 'tel:')]"),
            ]

            phone_elem = self._find_element_with_fallback(phone_selectors, "Phone")
            if phone_elem:
                # Try aria-label
                aria_label = phone_elem.get_attribute('aria-label')
                if aria_label:
                    phone = aria_label.replace('Phone:', '').replace('Phone', '').strip()
                    self.business_info['contact'] = phone
                    print(f"Found contact: {phone}")
                elif phone_elem.tag_name == 'a':
                    # Extract from tel: link
                    href = phone_elem.get_attribute('href')
                    phone = href.replace('tel:', '').strip()
                    self.business_info['contact'] = phone
                    print(f"Found contact from link: {phone}")
            else:
                self.business_info['contact'] = 'N/A'

            # Cost for One (Price range)
            price_selectors = [
                (By.XPATH, "//span[@aria-label[contains(., 'Price')]]"),
                (By.XPATH, "//button[contains(@aria-label, 'Price')]"),
                (By.XPATH, "//span[contains(text(), '$')]"),
            ]

            price_elem = self._find_element_with_fallback(price_selectors, "Price")
            if price_elem:
                # Try aria-label
                aria_label = price_elem.get_attribute('aria-label')
                if aria_label:
                    price = aria_label.replace('Price:', '').replace('Price', '').strip()
                    self.business_info['cost_for_one'] = price
                    print(f"Found cost for one: {price}")
                else:
                    # Try text
                    text = price_elem.text.strip()
                    if '$' in text:
                        self.business_info['cost_for_one'] = text
                        print(f"Found cost for one from text: {text}")
            else:
                self.business_info['cost_for_one'] = 'N/A'

        except Exception as e:
            print(f"Error extracting business info: {e}")

    def _click_reviews_tab(self):
        """Click on the reviews tab to show reviews"""
        try:
            print("Looking for Reviews tab...")

            # Wait a bit for page to load
            time.sleep(2)

            # Multiple strategies to find and click reviews tab
            review_tab_selectors = [
                (By.XPATH, "//button[contains(@aria-label, 'Reviews')]"),
                (By.XPATH, "//button[contains(., 'Reviews')]"),
                (By.XPATH, "//div[@role='tab' and contains(., 'Reviews')]"),
                (By.XPATH, "//button[contains(@jsaction, 'review')]"),
            ]

            reviews_button = self._find_element_with_fallback(review_tab_selectors, "Reviews tab")

            if reviews_button:
                self.driver.execute_script("arguments[0].click();", reviews_button)
                time.sleep(3)
                print("✓ Clicked on Reviews tab")
                return True
            else:
                print("Reviews tab not found, continuing anyway...")
                return False

        except Exception as e:
            print(f"Error clicking reviews tab: {e}")
            return False

    def _sort_reviews(self, sort_type: str = "newest"):
        """
        Sort reviews by newest or oldest

        Args:
            sort_type: "newest" or "oldest"
        """
        try:
            print(f"\nSorting by {sort_type}...")

            # Find sort button - try multiple selectors
            sort_button_selectors = [
                (By.XPATH, "//button[contains(@aria-label, 'Sort')]"),
                (By.XPATH, "//button[@data-value='Sort']"),
                (By.XPATH, "//button[contains(., 'Sort')]"),
            ]

            sort_button = self._find_element_with_fallback(sort_button_selectors, "Sort button")

            if not sort_button:
                print("Could not find sort button")
                return False

            # Click sort button
            self.driver.execute_script("arguments[0].click();", sort_button)
            time.sleep(1)

            # Click on sort option
            if sort_type == "newest":
                option_selectors = [
                    (By.XPATH, "//div[@role='menuitemradio' and contains(., 'Newest')]"),
                    (By.XPATH, "//div[@role='menuitemradio' and contains(., 'Most recent')]"),
                    (By.XPATH, "//li[contains(., 'Newest')]"),
                ]
            else:  # oldest
                option_selectors = [
                    (By.XPATH, "//div[@role='menuitemradio' and contains(., 'Oldest')]"),
                    (By.XPATH, "//li[contains(., 'Oldest')]"),
                ]

            option = self._find_element_with_fallback(option_selectors, f"{sort_type} option")

            if option:
                self.driver.execute_script("arguments[0].click();", option)
                time.sleep(3)
                print(f"✓ Sorted by {sort_type}")
                return True
            else:
                print(f"Could not find {sort_type} sort option")
                return False

        except Exception as e:
            print(f"Error sorting reviews: {e}")
            return False

    def _scroll_reviews(self, scrolls: int = 5):
        """
        Scroll through reviews to load more

        Args:
            scrolls: Number of times to scroll
        """
        try:
            # Try to find scrollable container - multiple strategies
            scrollable_selectors = [
                (By.CSS_SELECTOR, 'div[role="main"]'),
                (By.XPATH, "//div[contains(@class, 'review')]//parent::div[@role='main']"),
                (By.XPATH, "//div[@tabindex='-1' and contains(@style, 'overflow')]"),
            ]

            scrollable_div = self._find_element_with_fallback(scrollable_selectors, "Scrollable container")

            if not scrollable_div:
                print("Could not find scrollable container, trying to scroll page body")
                # Fallback: scroll the whole page
                for i in range(scrolls):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    print(f"Scroll {i+1}/{scrolls} completed (page body)")
                return

            # Scroll the reviews container
            for i in range(scrolls):
                self.driver.execute_script(
                    'arguments[0].scrollTo(0, arguments[0].scrollHeight);',
                    scrollable_div
                )
                time.sleep(2)
                print(f"Scroll {i+1}/{scrolls} completed")

        except Exception as e:
            print(f"Scrolling error: {e}")

    def _expand_reviews(self):
        """Click 'More' buttons to expand truncated reviews"""
        try:
            # Find "More" buttons with various selectors
            more_button_selectors = [
                (By.XPATH, "//button[contains(@aria-label, 'More')]"),
                (By.XPATH, "//button[contains(., 'More')]"),
                (By.CSS_SELECTOR, "button[aria-label*='More']"),
            ]

            for selector in more_button_selectors:
                try:
                    more_buttons = self.driver.find_elements(selector[0], selector[1])
                    if more_buttons:
                        print(f"Found {len(more_buttons)} 'More' buttons")
                        for button in more_buttons[:20]:
                            try:
                                self.driver.execute_script("arguments[0].click();", button)
                                time.sleep(0.2)
                            except:
                                continue
                        break
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

            # Try multiple class patterns for review elements
            review_class_patterns = [
                'jftiEf',  # Old pattern
                'jJc9Ad',  # Alternative pattern
                'MyEned',  # Another pattern
                'fontBodyMedium',  # Newer pattern
            ]

            review_elements = []
            for pattern in review_class_patterns:
                review_elements = soup.find_all('div', class_=lambda x: x and pattern in str(x))
                if review_elements:
                    print(f"Found {len(review_elements)} review elements with pattern: {pattern}")
                    break

            # If still no reviews, try a more generic approach
            if not review_elements:
                print("Trying generic review finder...")
                # Look for elements that have typical review structure
                review_elements = soup.find_all('div', attrs={'data-review-id': True})

            if not review_elements:
                # Last resort: find divs that contain rating spans
                review_elements = soup.find_all('div', class_=lambda x: x and 'review' in str(x).lower())

            print(f"Found {len(review_elements)} review elements")

            for idx, review_elem in enumerate(review_elements):
                try:
                    review_data = {}

                    # Reviewer name - try multiple selectors
                    name_patterns = ['d4r55', 'WNxzHc', 'TSUbDb']
                    name_elem = None
                    for pattern in name_patterns:
                        name_elem = review_elem.find('div', class_=lambda x: x and pattern in str(x))
                        if name_elem:
                            break

                    if not name_elem:
                        # Try finding by button or link
                        name_elem = review_elem.find('button') or review_elem.find('a')

                    review_data['reviewer_name'] = name_elem.text.strip() if name_elem else 'N/A'

                    # Rating - look for aria-label with stars
                    rating_elem = review_elem.find('span', attrs={'role': 'img', 'aria-label': True})
                    if not rating_elem:
                        rating_elem = review_elem.find('span', class_=lambda x: x and 'kvMYJc' in str(x))

                    if rating_elem and rating_elem.get('aria-label'):
                        rating_text = rating_elem.get('aria-label')
                        # Extract number from "X stars" or "X star"
                        match = re.search(r'(\d+)', rating_text)
                        if match:
                            review_data['rating'] = int(match.group(1))
                    else:
                        review_data['rating'] = 'N/A'

                    # Review text - try multiple patterns
                    text_patterns = ['wiI7pd', 'MyEned', 'review-full-text']
                    text_elem = None
                    for pattern in text_patterns:
                        text_elem = review_elem.find('span', class_=lambda x: x and pattern in str(x))
                        if text_elem:
                            break

                    review_data['review_text'] = text_elem.text.strip() if text_elem else 'N/A'

                    # Date - try multiple patterns
                    date_patterns = ['rsqaWe', 'DZSIDd']
                    date_elem = None
                    for pattern in date_patterns:
                        date_elem = review_elem.find('span', class_=lambda x: x and pattern in str(x))
                        if date_elem:
                            break

                    review_data['review_date'] = date_elem.text.strip() if date_elem else 'N/A'

                    # Reviewer stats
                    stats_patterns = ['RfnDt', 'RHo1pe']
                    stats_elem = None
                    for pattern in stats_patterns:
                        stats_elem = review_elem.find('div', class_=lambda x: x and pattern in str(x))
                        if stats_elem:
                            break

                    review_data['reviewer_stats'] = stats_elem.text.strip() if stats_elem else 'N/A'

                    # Only add if we have at least a reviewer name or text
                    if review_data['reviewer_name'] != 'N/A' or review_data['review_text'] != 'N/A':
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
            # Sort by oldest
            if not self._sort_reviews("oldest"):
                return 'N/A'

            # Wait for reviews to reload
            time.sleep(2)

            # Parse just the first review
            soup = BeautifulSoup(self.driver.page_source, 'lxml')

            # Try to find date element
            date_patterns = ['rsqaWe', 'DZSIDd']
            date_elem = None

            for pattern in date_patterns:
                date_elem = soup.find('span', class_=lambda x: x and pattern in str(x))
                if date_elem:
                    oldest_date = date_elem.text.strip()
                    print(f"✓ Oldest review date: {oldest_date}")
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
            time.sleep(5)

            # Extract business information first
            print("\nExtracting business information...")
            self._extract_business_info()

            # Click on reviews tab
            self._click_reviews_tab()

            # Get oldest review date first
            oldest_date = self._get_oldest_review_date()
            self.business_info['first_review_date'] = oldest_date

            # Now sort by newest to get recent reviews
            self._sort_reviews("newest")

            # Scroll to load more reviews
            print(f"\nScrolling to load more reviews ({max_scrolls} scrolls)...")
            self._scroll_reviews(scrolls=max_scrolls)

            # Expand truncated reviews
            print("\nExpanding truncated reviews...")
            self._expand_reviews()

            # Parse reviews
            print("\nParsing reviews...")
            self.reviews = self._parse_reviews()

            print(f"\n✓ Successfully scraped {len(self.reviews)} reviews")

            return self.reviews

        except Exception as e:
            print(f"Error during scraping: {e}")
            import traceback
            traceback.print_exc()
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

        print(f"\n{'='*70}")
        print("BUSINESS SUMMARY")
        print(f"{'='*70}")
        print(f"Rating: {summary['business_info']['rating']}")
        print(f"Location: {summary['business_info']['location']}")
        print(f"Contact: {summary['business_info']['contact_information']}")
        print(f"Cost for One: {summary['business_info']['cost_for_one']}")
        print(f"First Review Date: {summary['reviews_summary']['first_review_date']}")
        print(f"Total Negative Reviews: {summary['reviews_summary']['total_negative_reviews']}")
        if summary['reviews_summary']['last_negative_review']:
            print(f"Last Negative Review Date: {summary['reviews_summary']['last_negative_review']['date']}")
        print(f"\n✓ Business summary saved to {filename}")

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

    scraper = GoogleReviewsScraper(headless=False)  # Set to False to see browser
    reviews = scraper.scrape(url, max_scrolls=5)

    # Save business summary with all requested information
    scraper.save_business_summary('business_summary.json')

    # Save all reviews
    if reviews:
        scraper.save_to_json('google_reviews.json')
        scraper.save_to_csv('google_reviews.csv')

    # Print summary
    print(f"\n{'='*70}")
    print(f"SCRAPING COMPLETED")
    print(f"{'='*70}")
    print(f"Total reviews scraped: {len(reviews)}")

    if reviews:
        print("\nSample review:")
        print(f"Name: {reviews[0].get('reviewer_name')}")
        print(f"Rating: {reviews[0].get('rating')}")
        print(f"Date: {reviews[0].get('review_date')}")
        print(f"Text: {reviews[0].get('review_text')[:100]}...")
