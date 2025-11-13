"""
Example usage of Google Reviews Scraper
"""

from google_reviews_scraper import GoogleReviewsScraper


def main():
    """Example usage of the Google Reviews Scraper"""

    # Replace this with your target business URL
    business_url = "https://www.google.com/maps/place/Googleplex/@37.4220041,-122.0862515,17z/"

    print("=" * 70)
    print("Google Reviews Scraper - Business Analysis")
    print("=" * 70)

    # Create scraper instance (headless=True means no browser window)
    scraper = GoogleReviewsScraper(headless=True)

    # Scrape reviews and business information
    print(f"\nScraping reviews from: {business_url}\n")
    reviews = scraper.scrape(business_url, max_scrolls=10)

    # Generate and save business summary with all requested information
    print("\n" + "=" * 70)
    scraper.save_business_summary('business_summary.json')
    print("=" * 70)

    # Optionally save all reviews to JSON and CSV
    scraper.save_to_json('all_reviews.json')
    scraper.save_to_csv('all_reviews.csv')

    # Display detailed results
    print(f"\n{'=' * 70}")
    print(f"DETAILED ANALYSIS")
    print(f"{'=' * 70}")

    summary = scraper.generate_business_summary()

    print("\n📊 BUSINESS INFORMATION:")
    print(f"  • Overall Rating: {summary['business_info']['rating']}")
    print(f"  • Location: {summary['business_info']['location']}")
    print(f"  • Contact: {summary['business_info']['contact_information']}")
    print(f"  • Cost for One: {summary['business_info']['cost_for_one']}")

    print("\n📅 REVIEW TIMELINE:")
    print(f"  • First Review: {summary['reviews_summary']['first_review_date']}")
    print(f"  • Total Reviews Scraped: {summary['reviews_summary']['total_reviews_scraped']}")

    print("\n⚠️  NEGATIVE REVIEWS ANALYSIS:")
    print(f"  • Total Negative Reviews (1-3 stars): {summary['reviews_summary']['total_negative_reviews']}")

    if summary['reviews_summary']['last_negative_review']:
        last_neg = summary['reviews_summary']['last_negative_review']
        print(f"\n  Last Negative Review:")
        print(f"    - Rating: {last_neg['rating']} stars")
        print(f"    - Date: {last_neg['date']}")
        print(f"    - Content: {last_neg['content'][:200]}...")
    else:
        print("  • No negative reviews found in scraped data")

    # Show sample of recent reviews
    print(f"\n{'=' * 70}")
    print("SAMPLE RECENT REVIEWS:")
    print(f"{'=' * 70}")

    for i, review in enumerate(reviews[:3], 1):
        print(f"\nReview {i}:")
        print(f"  • Reviewer: {review.get('reviewer_name')}")
        print(f"  • Rating: {review.get('rating')} stars")
        print(f"  • Date: {review.get('review_date')}")
        print(f"  • Review: {review.get('review_text')[:150]}...")

    print(f"\n{'=' * 70}")
    print("✅ Scraping completed!")
    print(f"{'=' * 70}")
    print("\nOutput files:")
    print("  1. business_summary.json - Contains all requested business data")
    print("  2. all_reviews.json - Contains all scraped reviews")
    print("  3. all_reviews.csv - Contains all scraped reviews in CSV format")


if __name__ == "__main__":
    main()
