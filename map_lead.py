from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, WebDriverException, NoSuchElementException
import pandas as pd
import time
import re

def initialize_driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    return driver

def extract_email_from_page(driver):
    """Extract an email address from the current webpage."""
    try:
        page_source = driver.page_source
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, page_source)
        return emails[0] if emails else "Not Found"
    except:
        return "Not Found"

def find_contact_page(driver):
    """Look for a 'Contact Us' link and visit it."""
    try:
        contact_link = driver.find_element(By.XPATH, "//a[contains(translate(@href, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'contact') or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'contact')]")
        contact_url = contact_link.get_attribute('href')
        if contact_url:
            driver.get(contact_url)
            time.sleep(3)
            return True
        return False
    except:
        return False

# Initialize the driver and scrape company data
driver = initialize_driver()
search_query = "it company ahmedabad"
driver.get(f"https://www.google.com/maps/search/{search_query}/")
time.sleep(5)

data = []

# Scroll until at least 20 results are visible
while True:
    results = driver.find_elements(By.CSS_SELECTOR, ".hfpxzc")
    if len(results) >= 20:
        break
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
    time.sleep(2)

# Scrape 20 entries
for index in range(min(20, len(results))):
    try:
        # Re-fetch results to avoid stale elements
        results = driver.find_elements(By.CSS_SELECTOR, ".hfpxzc")
        if index >= len(results):
            print(f"Entry {index + 1}: Not enough results available after re-fetch, skipping.")
            continue

        result = results[index]
        driver.execute_script("arguments[0].scrollIntoView(true);", result)
        time.sleep(1)

        # Get the expected name from the list item using aria-label
        expected_name = result.get_attribute("aria-label")
        if not expected_name:
            print(f"Entry {index + 1}: Could not extract expected name from list item, skipping.")
            continue

        # Minimal tracking log
        print(f"Scraping entry {index + 1}: {expected_name}")

        # Click the result to open the sidebar
        driver.execute_script("arguments[0].click();", result)

        # Wait for panel content to load
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-item-id="address"]'))
            )
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='main']//div[contains(@class, 'kA9KIf') and not(contains(@class, 'ecceSd'))]//h1"))
            )
        except TimeoutException:
            print(f"Entry {index + 1}: Panel didn't load completely, skipping.")
            continue

        # Extract company name from the sidebar
        max_retries = 2
        retry_count = 0
        name = None

        while retry_count < max_retries:
            try:
                name = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, "//div[@role='main']//div[contains(@class, 'kA9KIf') and not(contains(@class, 'ecceSd'))]//h1"))
                ).text
                if name.strip() == expected_name.strip():
                    break
                else:
                    retry_count += 1
                    time.sleep(2)
                    try:
                        back_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Back']")
                        back_button.click()
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", result)
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-item-id="address"]'))
                        )
                    except:
                        pass
            except:
                retry_count += 1
                time.sleep(2)

        if not name or name.strip() != expected_name.strip():
            name = expected_name

        try:
            website = driver.find_element(By.CSS_SELECTOR, 'a.CsEnBe').get_attribute('href')
        except:
            website = "Not Found"

        try:
            location = driver.find_element(By.CSS_SELECTOR, '[data-item-id="address"]').text
            location = location.replace('', '').strip()
        except:
            location = "Not Found"

        try:
            phone = driver.find_element(By.CSS_SELECTOR, 'button[data-tooltip="Copy phone number"]').text
            phone = phone.replace('', '').strip()
        except:
            phone = "Not Found"

        data.append({
            "Company Name": name,
            "Phone": phone,
            "Website": website,
            "Address": location,
            "Email": None
        })

        # Reset the sidebar
        try:
            back_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Back']")
            back_button.click()
            time.sleep(1)
        except:
            try:
                search_results = driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
                search_results.click()
                time.sleep(1)
            except:
                pass

    except WebDriverException as e:
        print(f"Entry {index + 1} failed with WebDriverException: {e}")
        print("Restarting WebDriver session...")
        driver.quit()
        driver = initialize_driver()
        driver.get(f"https://www.google.com/maps/search/{search_query}/")
        time.sleep(5)
        while True:
            results = driver.find_elements(By.CSS_SELECTOR, ".hfpxzc")
            if len(results) >= 20:
                break
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(2)
        continue

# Scrape emails from the websites
print("\nScraping emails from websites...\n")
for idx, entry in enumerate(data):
    website = entry["Website"]
    if website == "Not Found" or not website:
        entry["Email"] = "Not Found"
        print(f"Scraping email for entry {idx + 1}: {entry['Company Name']} - No website")
        continue

    try:
        print(f"Scraping email for entry {idx + 1}: {entry['Company Name']}")
        driver.get(website)
        time.sleep(3)

        email = extract_email_from_page(driver)
        if email != "Not Found":
            entry["Email"] = email
            continue

        if find_contact_page(driver):
            email = extract_email_from_page(driver)
            entry["Email"] = email
        else:
            entry["Email"] = "Not Found"

    except Exception as e:
        entry["Email"] = "Not Found"
        print(f"Scraping email for entry {idx + 1}: {entry['Company Name']} - Failed")

    time.sleep(2)

# Filter data to include only entries with valid email addresses
filtered_data = [entry for entry in data if entry["Email"] != "Not Found"]

# Save to Excel
df = pd.DataFrame(filtered_data)
df.drop_duplicates(subset=["Website"], inplace=True)
df.to_excel("scraped_it_companies_ahmedabad_with_emails.xlsx", index=False)
# Updated print statement to avoid Unicode character
print(f"\nSuccess: Saved {len(filtered_data)} entries with emails to 'scraped_it_companies_ahmedabad_with_emails.xlsx'")

driver.quit()