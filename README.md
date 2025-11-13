# Google Reviews Scraper

A Python-based web scraper for extracting reviews from Google Business pages (Google Maps). This tool uses Selenium and BeautifulSoup to scrape review data including reviewer names, ratings, review text, dates, and more.

## Features

- 🔍 Scrape reviews from any Google Business page
- 📊 Export data to JSON and CSV formats
- 🎯 Customizable scroll depth to load more reviews
- 🌐 Support for different languages
- 👻 Headless and non-headless browser modes
- 🔄 Automatic scrolling to load more reviews
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

# Scrape reviews from a Google Business URL
url = "https://www.google.com/maps/place/YourBusinessName/"
reviews = scraper.scrape(url, max_scrolls=5)

# Save results
scraper.save_to_json('reviews.json')
scraper.save_to_csv('reviews.csv')

# Access reviews data
for review in reviews:
    print(f"{review['reviewer_name']}: {review['rating']} stars")
    print(f"{review['review_text']}\n")
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

Each review contains the following fields:

```python
{
    "reviewer_name": "John Doe",
    "rating": "5",
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

### Example 4: Filter and Analyze Reviews

```python
scraper = GoogleReviewsScraper(headless=True)
reviews = scraper.scrape(url, max_scrolls=10)

# Filter 5-star reviews
five_star = [r for r in reviews if r['rating'] == '5']
print(f"5-star reviews: {len(five_star)}")

# Filter by keyword
keyword_reviews = [r for r in reviews if 'excellent' in r['review_text'].lower()]
print(f"Reviews mentioning 'excellent': {len(keyword_reviews)}")
```

## Output Formats

### JSON Format
```json
[
  {
    "reviewer_name": "John Doe",
    "rating": "5",
    "review_text": "Amazing service and great atmosphere!",
    "review_date": "3 weeks ago",
    "reviewer_stats": "25 reviews"
  }
]
```

### CSV Format
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
