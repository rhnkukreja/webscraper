"""
Example usage of Google Reviews Scraper
"""

from google_reviews_scraper import GoogleReviewsScraper


def main():
    """Example usage of the Google Reviews Scraper"""

    # Example 1: Basic usage with a Google Maps business URL
    print("=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)

    # Replace this with your target business URL
    business_url = "https://www.google.com/maps/place/Googleplex/@37.4220041,-122.0862515,17z/"

    # Create scraper instance (headless=True means no browser window)
    scraper = GoogleReviewsScraper(headless=True)

    # Scrape reviews (max_scrolls determines how many reviews to load)
    print(f"\nScraping reviews from: {business_url}\n")
    reviews = scraper.scrape(business_url, max_scrolls=5)

    # Save to both JSON and CSV
    scraper.save_to_json('reviews.json')
    scraper.save_to_csv('reviews.csv')

    # Display results
    print(f"\n{'=' * 60}")
    print(f"Total reviews scraped: {len(reviews)}")
    print(f"{'=' * 60}")

    if reviews:
        print("\n--- Sample Reviews ---\n")
        for i, review in enumerate(reviews[:3], 1):  # Show first 3 reviews
            print(f"Review {i}:")
            print(f"  Reviewer: {review.get('reviewer_name')}")
            print(f"  Rating: {review.get('rating')} stars")
            print(f"  Date: {review.get('review_date')}")
            print(f"  Text: {review.get('review_text')[:150]}...")
            print()

    # Example 2: Non-headless mode (opens browser window)
    print("\n" + "=" * 60)
    print("Example 2: Non-Headless Mode (Visible Browser)")
    print("=" * 60)
    print("Uncomment the code below to see the browser in action")
    print()

    # Uncomment to run in non-headless mode
    # scraper2 = GoogleReviewsScraper(headless=False)
    # reviews2 = scraper2.scrape(business_url, max_scrolls=3)
    # print(f"Scraped {len(reviews2)} reviews with visible browser")

    # Example 3: Different language setting
    print("\n" + "=" * 60)
    print("Example 3: Custom Language Setting")
    print("=" * 60)
    print("You can set language parameter for international reviews")
    print()

    # Uncomment to use different language (e.g., Spanish)
    # scraper3 = GoogleReviewsScraper(headless=True, language='es')
    # reviews3 = scraper3.scrape(business_url, max_scrolls=3)

    print("\n✅ Examples completed!")
    print("Check 'reviews.json' and 'reviews.csv' for the scraped data")


if __name__ == "__main__":
    main()
