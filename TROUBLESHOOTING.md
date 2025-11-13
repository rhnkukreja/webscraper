# Troubleshooting Guide

This guide helps you diagnose and fix common issues with the Google Reviews Scraper.

## Running the Debug Script

If the scraper isn't finding reviews or business information, run the debug script first:

```bash
python debug_scraper.py
```

This will:
- Test various selectors to find elements
- Save the page source to `page_source.html` for inspection
- Show which selectors are working and which aren't
- Keep the browser open so you can see what's happening

## Common Issues and Solutions

### 1. No Reviews Found (0 reviews scraped)

**Problem**: The scraper completes but finds 0 reviews.

**Possible Causes**:
- Google Maps HTML structure changed
- The business doesn't have reviews
- JavaScript hasn't loaded yet
- You're being rate-limited

**Solutions**:
1. **Run in non-headless mode** to see what's happening:
   ```python
   scraper = GoogleReviewsScraper(headless=False)
   ```

2. **Increase wait times** - Modify the scraper to wait longer:
   - Line 512: Change `time.sleep(5)` to `time.sleep(10)`
   - Add more delays between operations

3. **Check the business URL**:
   - Make sure the URL actually has reviews
   - Try visiting the URL in your browser first
   - URL should be the full Google Maps business page URL

4. **Run the debug script**:
   ```bash
   python debug_scraper.py
   ```
   This will help identify which selectors need updating.

### 2. Business Info Not Found (Rating, Location, Contact all N/A)

**Problem**: The scraper runs but can't extract business metadata.

**Solutions**:
1. **Check if the business has this information publicly available**:
   - Not all businesses have phone numbers, prices, etc. listed

2. **Run debug script to identify correct selectors**:
   ```bash
   python debug_scraper.py
   ```

3. **The page might need more time to load**:
   - Increase initial wait time on line 512
   - Add explicit waits before extracting business info

### 3. ChromeDriver Issues

**Problem**: "ChromeDriver not found" or version mismatch errors.

**Solutions**:
1. **Update Chrome browser** to the latest version

2. **Clear webdriver cache**:
   ```bash
   # On Windows
   rmdir /s %USERPROFILE%\.wdm

   # On Mac/Linux
   rm -rf ~/.wdm
   ```

3. **Manual install** if automatic fails:
   - Download ChromeDriver from https://chromedriver.chromium.org/
   - Place it in your PATH

### 4. Timeout Errors

**Problem**: "TimeoutException" or elements not found errors.

**Solutions**:
1. **Increase timeouts** in the code:
   - Look for `WebDriverWait` calls
   - Increase the timeout value (default is 10 seconds)

2. **Check your internet connection**:
   - Slow connection may cause timeouts
   - Try again with a better connection

3. **Google may be rate-limiting you**:
   - Wait a few minutes between runs
   - Use delays between requests
   - Consider using a VPN

### 5. Getting Old HTML Structure

**Problem**: The selectors in the code don't match current Google Maps.

**Solution**:
Google frequently updates their page structure. If selectors are outdated:

1. **Run the debug script** to see current structure:
   ```bash
   python debug_scraper.py
   ```

2. **Inspect page_source.html**:
   - Look for review elements and their classes
   - Update the selectors in `google_reviews_scraper.py`

3. **Check for updates**:
   - Pull the latest version of this code
   - Check if there are community fixes

### 6. "No such element" Errors

**Problem**: Specific elements can't be found despite being visible.

**Solutions**:
1. **Element might be in an iframe**:
   - Check if you need to switch to an iframe context
   - Add: `driver.switch_to.frame(frame_element)`

2. **Element might not be clickable**:
   - Use JavaScript click instead:
   ```python
   driver.execute_script("arguments[0].click();", element)
   ```

3. **Wait for element to be visible**:
   ```python
   from selenium.webdriver.support import expected_conditions as EC
   element = WebDriverWait(driver, 10).until(
       EC.presence_of_element_located((By.XPATH, "//your/xpath"))
   )
   ```

### 7. Headless Mode Issues

**Problem**: Works in normal mode but fails in headless mode.

**Solutions**:
1. **Update headless argument**:
   - Use `--headless=new` instead of `--headless`
   - Already implemented in current version

2. **Increase window size** for headless:
   ```python
   chrome_options.add_argument('--window-size=1920,1080')
   ```

3. **Add more realistic user agent**:
   - Already implemented in current version

## Debugging Tips

### Enable Verbose Logging

Add more print statements to see what's happening:

```python
print(f"Page title: {driver.title}")
print(f"Current URL: {driver.current_url}")
print(f"Page source length: {len(driver.page_source)}")
```

### Take Screenshots

Add screenshots at key points:

```python
driver.save_screenshot('step1_loaded.png')
# After some action
driver.save_screenshot('step2_clicked.png')
```

### Save Page Source

Save HTML for inspection:

```python
with open('debug_page.html', 'w', encoding='utf-8') as f:
    f.write(driver.page_source)
```

### Check Console Errors

Look for JavaScript errors:

```python
logs = driver.get_log('browser')
for log in logs:
    print(log)
```

## Getting Help

If none of these solutions work:

1. **Run the debug script** and share the output
2. **Save the page source** and inspect it manually
3. **Check if Google Maps structure changed** by comparing with working examples
4. **Try different business URLs** to see if it's specific to one business
5. **Report the issue** with:
   - Error messages
   - Debug script output
   - Chrome and ChromeDriver versions
   - Operating system

## Best Practices

1. **Don't scrape too aggressively**:
   - Add delays between requests
   - Limit the number of businesses scraped per hour
   - Respect robots.txt

2. **Handle errors gracefully**:
   - Use try-except blocks
   - Log errors for debugging
   - Have fallback strategies

3. **Keep selectors updated**:
   - Google changes their structure frequently
   - Use multiple fallback selectors
   - Test regularly

4. **Test with known-good URLs first**:
   - Start with popular businesses that definitely have reviews
   - Example: Googleplex, restaurants with many reviews

## Environment-Specific Issues

### Windows

- Make sure Chrome is properly installed
- Check that PATH includes Python and pip
- Use proper escaping for file paths

### Mac

- May need to allow ChromeDriver in Security settings
- Use `python3` instead of `python`

### Linux

- May need additional Chrome dependencies:
  ```bash
  sudo apt-get install -y libgconf-2-4 libatk1.0-0 libatk-bridge2.0-0 libgdk-pixbuf2.0-0 libgtk-3-0 libgbm-dev libnss3-dev libxss-dev
  ```

- Headless mode may require `xvfb`:
  ```bash
  sudo apt-get install xvfb
  xvfb-run python scraper.py
  ```
