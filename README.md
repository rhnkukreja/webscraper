# Google Reviews Scraper

A Python-based web scraper for extracting reviews and business information from Google Business pages (Google Maps). This tool uses Selenium and BeautifulSoup to scrape comprehensive business data including reviews, ratings, location, contact info, and analytical insights.

## Features

- 🔍 Scrape reviews from any Google Business page
- 📊 Extract business metadata (rating, location, contact, cost)
- 📅 Find first review date (oldest review)
- ⚠️ Analyze negative reviews (1-3 stars)
- 🎯 Get the most recent negative review
- 💾 Export data to JSON and CSV formats
- 🔄 Customizable scroll depth to load more reviews
- 🌐 Support for different languages
- 👻 Headless and non-headless browser modes
- 📝 Expands truncated review text
- 🛡️ Anti-detection measures

## Installation

### Prerequisites

- Python 3.7 or higher
- Google Chrome browser installed

### Setup

1. Clone this repository:
```bash
git clone <repository-url>
cd webscraper
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

The scraper will automatically download and manage the Chrome WebDriver.

## Usage

### Basic Usage

```python
from google_reviews_scraper import GoogleReviewsScraper

# Initialize scraper
scraper = GoogleReviewsScraper(headless=True)

# Scrape reviews and business information
url = "https://www.google.com/maps/place/YourBusinessName/"
reviews = scraper.scrape(url, max_scrolls=10)

# Save business summary with all key information
scraper.save_business_summary('business_summary.json')

# Optionally save all reviews
scraper.save_to_json('all_reviews.json')
scraper.save_to_csv('all_reviews.csv')

# Access business summary programmatically
summary = scraper.generate_business_summary()
print(f"Rating: {summary['business_info']['rating']}")
print(f"Location: {summary['business_info']['location']}")
print(f"First Review: {summary['reviews_summary']['first_review_date']}")
print(f"Negative Reviews: {summary['reviews_summary']['total_negative_reviews']}")
```

### Running the Example

```bash
python example.py
```

### Finding the Business URL

1. Go to [Google Maps](https://www.google.com/maps)
2. Search for the business you want to scrape reviews from
3. Copy the URL from your browser's address bar
4. Use this URL with the scraper

Example URL format:
```
https://www.google.com/maps/place/Business+Name/@latitude,longitude,zoom/
```

## Configuration Options

### GoogleReviewsScraper Parameters

- `headless` (bool): Run browser in headless mode (default: True)
  - `True`: Browser runs in background (faster, no GUI)
  - `False`: Browser window is visible (useful for debugging)

- `language` (str): Browser language setting (default: 'en')
  - Examples: 'en', 'es', 'fr', 'de', 'ja', etc.

### Scrape Method Parameters

- `url` (str): Google Business page URL (required)
- `max_scrolls` (int): Number of times to scroll down to load more reviews (default: 5)
  - More scrolls = more reviews loaded (but slower)
  - Recommended: 3-10 scrolls depending on how many reviews you need

## Data Structure

### Business Summary Output

The `business_summary.json` file contains comprehensive business information:

```json
{
  "business_info": {
    "rating": "4.5",
    "location": "123 Main Street, City, State 12345",
    "contact_information": "+1 (555) 123-4567",
    "cost_for_one": "$$"
  },
  "reviews_summary": {
    "total_reviews_scraped": 150,
    "total_negative_reviews": 12,
    "first_review_date": "5 years ago",
    "last_negative_review": {
      "content": "Service was slow and food was cold...",
      "date": "2 weeks ago",
      "rating": 2
    }
  }
}
```

### Individual Review Structure

Each review in `all_reviews.json` contains:

```json
{
    "reviewer_name": "John Doe",
    "rating": 5,
    "review_text": "Great place! Highly recommended...",
    "review_date": "2 months ago",
    "reviewer_stats": "50 reviews"
}
```

## Advanced Examples

### Example 1: Visible Browser Mode

```python
scraper = GoogleReviewsScraper(headless=False)
reviews = scraper.scrape(url, max_scrolls=3)
```

### Example 2: Different Language

```python
scraper = GoogleReviewsScraper(headless=True, language='es')
reviews = scraper.scrape(url, max_scrolls=5)
```

### Example 3: Process Multiple Businesses

```python
urls = [
    "https://www.google.com/maps/place/Business1/",
    "https://www.google.com/maps/place/Business2/",
    "https://www.google.com/maps/place/Business3/"
]

for idx, url in enumerate(urls):
    scraper = GoogleReviewsScraper(headless=True)
    reviews = scraper.scrape(url, max_scrolls=5)
    scraper.save_to_json(f'reviews_{idx}.json')
    scraper.save_to_csv(f'reviews_{idx}.csv')
```

### Example 4: Analyze Negative Reviews

```python
scraper = GoogleReviewsScraper(headless=True)
reviews = scraper.scrape(url, max_scrolls=10)

# Get all negative reviews (1-3 stars)
negative_reviews = scraper.get_negative_reviews()
print(f"Total negative reviews: {len(negative_reviews)}")

# Get the most recent negative review
last_negative = scraper.get_last_negative_review()
if last_negative:
    print(f"Last negative review: {last_negative['review_text']}")
    print(f"Rating: {last_negative['rating']} stars")
    print(f"Date: {last_negative['review_date']}")

# Filter by keyword
keyword_reviews = [r for r in reviews if 'excellent' in r['review_text'].lower()]
print(f"Reviews mentioning 'excellent': {len(keyword_reviews)}")
```

## Output Formats

The scraper generates three types of output files:

### 1. Business Summary (business_summary.json)
Contains comprehensive business analytics:
- Overall rating
- Business location
- Contact information
- Cost for one
- First review date
- Total negative reviews count
- Most recent negative review details

### 2. All Reviews (all_reviews.json)
Array of all scraped reviews in JSON format:
```json
[
  {
    "reviewer_name": "John Doe",
    "rating": 5,
    "review_text": "Amazing service and great atmosphere!",
    "review_date": "3 weeks ago",
    "reviewer_stats": "25 reviews"
  }
]
```

### 3. CSV Format (all_reviews.csv)
```
reviewer_name,rating,review_text,review_date,reviewer_stats
John Doe,5,Amazing service and great atmosphere!,3 weeks ago,25 reviews
```

## Troubleshooting

### Common Issues

1. **Chrome Driver Issues**
   - Solution: The scraper automatically downloads the correct ChromeDriver version
   - If issues persist, try updating Chrome browser

2. **Timeout Errors**
   - Increase wait times in the code
   - Check your internet connection
   - Try with `headless=False` to see what's happening

3. **No Reviews Found**
   - Verify the URL is correct and contains reviews
   - Try increasing `max_scrolls` parameter
   - Check if Google changed their page structure

4. **Rate Limiting**
   - Add delays between requests
   - Don't scrape too aggressively
   - Consider using rotating proxies for large-scale scraping

## Best Practices

- ✅ Respect robots.txt and terms of service
- ✅ Add delays between requests
- ✅ Use headless mode for efficiency
- ✅ Start with fewer scrolls and increase as needed
- ⚠️ Be mindful of scraping frequency to avoid rate limiting
- ⚠️ Use for personal/research purposes only

## Legal Disclaimer

This tool is for educational and research purposes only. Users are responsible for complying with Google's Terms of Service and applicable laws. Web scraping may be against the terms of service of some websites. Always check and respect the website's robots.txt file and terms of service.

## Dependencies

- `selenium>=4.15.0` - Browser automation
- `beautifulsoup4>=4.12.0` - HTML parsing
- `webdriver-manager>=4.0.0` - Automatic WebDriver management
- `pandas>=2.0.0` - Data processing (optional)
- `lxml>=4.9.0` - XML/HTML parser

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

**Note**: Google frequently updates their website structure. If the scraper stops working, it may need updates to match the new HTML structure.
