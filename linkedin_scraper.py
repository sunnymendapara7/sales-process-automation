import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup
import pandas as pd
import re
from time import sleep
from random import uniform
import csv
import sys

# Fix for UnicodeEncodeError: Set console encoding to UTF-8
os.environ["PYTHONIOENCODING"] = "utf-8"

# Custom print function to handle encoding errors and log to file
def safe_print(*args, sep=' ', end='\n', file=None):
    # Combine the arguments into a single string
    message = sep.join(str(arg) for arg in args) + end
    # Try to print to console, replacing unprintable characters
    try:
        print(message, end='', file=sys.stdout, flush=True)
    except UnicodeEncodeError:
        # Replace unprintable characters with '?'
        safe_message = message.encode('ascii', 'replace').decode('ascii')
        print(safe_message, end='', file=sys.stdout, flush=True)
    # Log to file in UTF-8 encoding
    with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
        log_file.write(message)

# Function to initialize WebDriver with explicit desktop settings
def initialize_driver():
    chrome_options = webdriver.ChromeOptions()
    # Use a specific desktop user-agent (Chrome on Windows 11)
    desktop_user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
    chrome_options.add_argument(f"user-agent={desktop_user_agent}")
    chrome_options.add_argument("--disable-webrtc")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    # Suppress ChromeDriver logs
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Set window size to a typical desktop resolution
    driver.set_window_size(1920, 1080)
    driver.maximize_window()
    
    # Use Chrome DevTools Protocol to force desktop device metrics
    driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
        'width': 1920,
        'height': 1080,
        'deviceScaleFactor': 1,
        'mobile': False,
        'screenWidth': 1920,
        'screenHeight': 1080,
    })
    
    # Disable touch events to further mimic a desktop environment
    driver.execute_cdp_cmd('Emulation.setTouchEmulationEnabled', {
        'enabled': False
    })
    
    return driver

# Function to log into LinkedIn
def login_to_linkedin(driver):
    safe_print('- Starting LinkedIn login process')
    driver.get('https://www.linkedin.com/login')
    sleep(2)
    safe_print('- Accessed LinkedIn login page')

    # Add a small delay to ensure the desktop view is applied
    sleep(2)

    with open('credentials.txt') as credential:
        lines = credential.readlines()
        username = lines[0].strip()
        password = lines[1].strip()
    safe_print('- Imported login credentials')
    sleep(2)

    email_field = driver.find_element(By.ID, 'username')
    email_field.send_keys(username)
    safe_print('- Entered email')
    sleep(3)

    password_field = driver.find_element(By.NAME, 'session_password')
    password_field.send_keys(password)
    safe_print('- Entered password')
    sleep(2)

    signin_field = driver.find_element(By.CSS_SELECTOR, '#organic-div form button')
    signin_field.click()
    sleep(3)
    safe_print('- Submitted login form')

    # Wait for the user to complete the verification challenge (e.g., CAPTCHA)
    safe_print('- Waiting for you to complete any verification challenge (e.g., CAPTCHA)...')
    try:
        WebDriverWait(driver, 300).until(  # Wait up to 5 minutes for manual verification
            EC.url_contains("feed")
        )
        current_url = driver.current_url
        safe_print(f'- Current URL after login: {current_url}')
        if 'login' in current_url or 'checkpoint' in current_url:
            raise Exception("Login failed or additional verification still required. Please ensure the verification is completed.")
        safe_print('- Successfully logged into LinkedIn')
    except Exception as e:
        safe_print(f'- Error during login: {e}')
        raise Exception("Login process failed. Please ensure you completed the verification and try again.")

# Function to search for profiles
def search_profiles(driver):
    # search_query = input('What profile do you want to scrape? ')
    search_query = 'hr manager'
    search_field = driver.find_element(By.XPATH, '//*[@id="global-nav-typeahead"]/input')
    search_field.send_keys(search_query)
    search_field.send_keys(Keys.RETURN)
    sleep(3)
    safe_print('- Starting Task 2: Search for profiles')
    safe_print('- Finish Task 2: Search for profiles')
    return search_query

# Function to extract profile URLs from one page
def get_profile_urls(driver, target_profiles=20):
    all_profile_URL = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    max_attempts_without_new_content = 3
    attempts_without_new_content = 0

    while len(all_profile_URL) < target_profiles:
        page_source = BeautifulSoup(driver.page_source, 'html.parser')
        profiles = page_source.select('a[href*="/in/"]')

        for profile in profiles:
            profile_ID = profile.get('href')
            if profile_ID and '/in/' in profile_ID:
                if profile_ID.startswith('https://www.linkedin.com'):
                    profile_URL = profile_ID.split('?')[0]
                else:
                    profile_URL = 'https://www.linkedin.com' + profile_ID.split('?')[0]
                if profile_URL not in all_profile_URL:
                    all_profile_URL.append(profile_URL)
                    if len(all_profile_URL) >= target_profiles:
                        safe_print(f'- Reached target of {target_profiles} profiles on this page')
                        break

        safe_print(f'- Collected {len(all_profile_URL)} profiles so far on this page')

        if len(all_profile_URL) >= target_profiles:
            break

        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        sleep(5)

        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/in/"]'))
            )
        except:
            safe_print('- No new profile elements detected after waiting')

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            attempts_without_new_content += 1
            safe_print(f'- No new content loaded (attempt {attempts_without_new_content}/{max_attempts_without_new_content})')
            if attempts_without_new_content >= max_attempts_without_new_content:
                safe_print('- No more new profiles loaded on this page')
                break
        else:
            attempts_without_new_content = 0
        last_height = new_height

    return all_profile_URL

# Function to scrape profile data
def scrape_profile_data(driver, profile_url):
    driver.get(profile_url)
    safe_print('- Accessing profile: ', profile_url)
    sleep(uniform(3, 5))

    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    sleep(2)

    try:
        show_more_button = driver.find_element(By.XPATH, '//section[contains(@class, "experience")]//button[contains(text(), "Show more")]')
        driver.execute_script("arguments[0].click();", show_more_button)
        sleep(2)
        safe_print('--- Debug: Clicked "Show more" button in Experience section')
    except NoSuchElementException:
        safe_print('--- Debug: No "Show more" button found in Experience section')

    # Extract Name
    try:
        name = driver.find_element(By.XPATH, '//h1[contains(@class, "text-heading-xlarge")]').text.strip()
    except NoSuchElementException:
        try:
            name = driver.find_element(By.XPATH, '//h1').text.strip()
        except NoSuchElementException:
            name = 'N/A'
    safe_print('--- Profile name is: ', name)

    # Extract Job Title
    try:
        title = driver.find_element(By.XPATH, '//main/section[1]//div[contains(@class, "text-body-medium")]').text.strip()
    except NoSuchElementException:
        try:
            title = driver.find_element(By.XPATH, '//h2').text.strip()
        except NoSuchElementException:
            title = 'N/A'
    safe_print('--- Profile title is: ', title)

    # Extract Location
    try:
        location = driver.find_element(By.XPATH, '//main/section[1]//span[contains(@class, "text-body-small") and contains(@class, "inline")]').text.strip()
    except NoSuchElementException:
        try:
            location = driver.find_element(By.XPATH, '//span[contains(@class, "location")]').text.strip()
        except NoSuchElementException:
            location = 'N/A'
    safe_print('--- Profile location is: ', location)

    # Extract Company URL
    company_url = 'N/A'
    try:
        safe_print('--- Debug: Waiting for Experience section to load...')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//section[contains(@class, "experience")]'))
        )
        safe_print('--- Debug: Experience section found, looking for company link...')
        company_link = driver.find_element(
            By.XPATH,
            '//section[contains(@class, "experience")]//a[contains(@href, "/company/")]'
        )
        company_url = company_link.get_attribute('href').split('?')[0]
        if not company_url.startswith('https://www.linkedin.com'):
            company_url = 'https://www.linkedin.com' + company_url
        safe_print('--- Debug: Company URL found in Experience section')
    except (NoSuchElementException, Exception):
        safe_print('--- Debug: No company link found in Experience section')
        try:
            safe_print('--- Debug: Looking for company links on the entire page...')
            company_link = driver.find_element(
                By.XPATH,
                '//a[contains(@href, "/company/") and not(contains(@href, "/jobs/")) and not(contains(@href, "/search/"))]'
            )
            company_url = company_link.get_attribute('href').split('?')[0]
            if not company_url.startswith('https://www.linkedin.com'):
                company_url = 'https://www.linkedin.com' + company_url
            safe_print('--- Debug: Company URL found on the entire page')
        except NoSuchElementException:
            safe_print('--- Debug: No company link found on the entire page')

    # Validate company URL
    if '/search/' in company_url or '/posts' in company_url:
        safe_print(f'--- Debug: Invalid company URL detected ({company_url}), setting to N/A')
        company_url = 'N/A'
    safe_print('--- Company URL is: ', company_url)

    return {
        'Name': name,
        'Job Title': title,
        'Location': location,
        'Company URL': company_url,
        'Profile URL': profile_url
    }

# Function to scrape company page data
def scrape_company_page(driver, company_url):
    company_url = company_url.split('/posts')[0]
    about_url = company_url + '/about/' if not company_url.endswith('/about/') else company_url
    driver.get(about_url)
    safe_print(f'- Accessing company page: {about_url}')
    sleep(uniform(3, 5))

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(2)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//section[.//dl]'))
        )
    except:
        safe_print(f'--- Timeout waiting for About section to load: {about_url}')
        return {
            'Company Name': 'N/A',
            'Website': 'N/A',
            'Phone': 'N/A',
            'Industry': 'N/A',
            'Company URL': company_url,
            'Email': 'N/A'
        }

    try:
        company_name = driver.find_element(By.CSS_SELECTOR, 'h1.org-top-card-summary__title').text.strip()
    except NoSuchElementException:
        company_name = 'N/A'
    safe_print(f'--- Company Name: {company_name}')

    website = 'N/A'
    phone = 'N/A'
    industry = 'N/A'

    try:
        about_section = driver.find_element(By.XPATH, '//section[.//dl]')
        dt_elements = about_section.find_elements(By.XPATH, './/dl/dt')
        dd_elements = about_section.find_elements(By.XPATH, './/dl/dd')

        safe_print('--- Debug: dt elements:', [dt.text.strip() for dt in dt_elements])
        safe_print('--- Debug: dd elements:', [dd.text.strip() for dd in dd_elements])

        if len(dt_elements) != len(dd_elements):
            safe_print(f'--- Mismatch in dt/dd pairs: {len(dt_elements)} dt vs {len(dd_elements)} dd')

        for i in range(min(len(dt_elements), len(dd_elements))):
            label = dt_elements[i].text.strip().lower()
            value_element = dd_elements[i]
            try:
                value = value_element.find_element(By.TAG_NAME, 'span').text.strip()
            except NoSuchElementException:
                value = value_element.text.strip()

            if label in ['website', 'site', 'web']:
                website = value
                if not (website.startswith('http://') or website.startswith('https://')):
                    website = f'https://{website}'
            elif label in ['phone', 'contact number', 'tel']:
                phone = value
                if not any(char.isdigit() for char in phone):
                    phone = 'N/A'
            elif label == 'industry':
                industry = value

    except NoSuchElementException as e:
        safe_print(f'--- Failed to extract About Us details: {e}')
        with open(f'page_source_{company_url.split("/")[-2]}.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)

    safe_print(f'--- Website: {website}')
    safe_print(f'--- Phone: {phone}')
    safe_print(f'--- Industry: {industry}')

    return {
        'Company Name': company_name,
        'Website': website,
        'Phone': phone,
        'Industry': industry,
        'Company URL': company_url,
        'Email': 'N/A'
    }

# Function to scrape emails from a website
def scrape_emails(driver, website):
    if pd.isna(website) or website == 'N/A':
        return 'N/A'

    try:
        safe_print(f'- Accessing website: {website}')
        driver.get(website)
        sleep(uniform(3, 5))

        try:
            contact_link = driver.find_element(By.XPATH, '//a[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "contact") or contains(@href, "contact")]')
            contact_url = contact_link.get_attribute('href')
            driver.get(contact_url)
            safe_print(f'--- Navigated to Contact Us page: {contact_url}')
            sleep(uniform(2, 4))
        except NoSuchElementException:
            safe_print('--- No Contact Us link found, scraping main page')

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
        except:
            safe_print(f'--- Timeout waiting for page to load: {website}')

        page_source = driver.page_source
        email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', re.IGNORECASE)
        emails = email_pattern.findall(page_source)

        if emails:
            safe_print(f'--- Extracted Email: {emails[0]}')
            return emails[0]
        else:
            safe_print('--- No email found on this page')
            return 'N/A'

    except Exception as e:
        safe_print(f'--- Error processing website {website}: {e}')
        return 'N/A'

# Main script
# Clear the log file at the start
with open('scraper_log.txt', 'w', encoding='utf-8') as log_file:
    log_file.write('')

driver = initialize_driver()
try:
    # Task 1: Log into LinkedIn
    login_to_linkedin(driver)

    # Task 2: Search for profiles
    search_profiles(driver)

    # Task 3: Scrape profile URLs
    # number_of_page = int(input('How many pages you want to scrape: '))
    number_of_page = 1
    URLs_all_page = []
    for page in range(number_of_page):
        safe_print(f'- Scraping page {page + 1}')
        URLs_one_page = get_profile_urls(driver)
        URLs_all_page.extend(URLs_one_page)
        sleep(2)
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        sleep(2)
        try:
            next_button = driver.find_element(By.CLASS_NAME, 'artdeco-pagination__button--next')
            driver.execute_script("arguments[0].click();", next_button)
            sleep(3)
        except NoSuchElementException:
            safe_print(f'- No more pages to scrape after page {page + 1}')
            break
    safe_print('- Finish Task 3: Scrape the URLs')

    # Task 4: Scrape profile data and save to CSV
    with open('output.csv', 'w', newline='', encoding='utf-8') as file_output:
        headers = ['Name', 'Job Title', 'Location', 'Company URL', 'Profile URL']
        writer = csv.DictWriter(file_output, delimiter=',', lineterminator='\n', fieldnames=headers)
        writer.writeheader()

        for linkedin_URL in URLs_all_page:
            try:
                profile_data = scrape_profile_data(driver, linkedin_URL)
                writer.writerow(profile_data)
                safe_print('\n')
            except WebDriverException as e:
                safe_print(f'--- Error processing {linkedin_URL}: {e}')
                if 'invalid session id' in str(e).lower():
                    safe_print('--- Debug: Invalid session detected, reinitializing WebDriver...')
                    driver.quit()
                    driver = initialize_driver()
                    login_to_linkedin(driver)
                    profile_data = scrape_profile_data(driver, linkedin_URL)
                    writer.writerow(profile_data)
                else:
                    writer.writerow({
                        'Name': 'N/A',
                        'Job Title': 'N/A',
                        'Location': 'N/A',
                        'Company URL': 'N/A',
                        'Profile URL': linkedin_URL
                    })
    safe_print('- Finish Task 4: Scrape profile data and save to CSV')

    # Task 5: Scrape company pages
    safe_print('\nStarting Task 5: Scrape company pages\n')
    company_urls = []
    with open('output.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            company_url = row['Company URL']
            if company_url != 'N/A' and '/company/' in company_url and '/search/' not in company_url:
                company_urls.append(company_url)

    unique_company_urls = list(set(company_urls))
    safe_print(f'- Total unique company URLs to scrape: {len(unique_company_urls)}')
    safe_print(f'- Unique company URLs: {unique_company_urls}')

    company_data = []
    for company_url in unique_company_urls:
        try:
            company_info = scrape_company_page(driver, company_url)
            company_data.append(company_info)
        except WebDriverException as e:
            safe_print(f'--- Error processing company page {company_url}: {e}')
            if 'invalid session id' in str(e).lower():
                safe_print('--- Debug: Invalid session detected, reinitializing WebDriver...')
                driver.quit()
                driver = initialize_driver()
                login_to_linkedin(driver)
                company_info = scrape_company_page(driver, company_url)
                company_data.append(company_info)
            else:
                company_data.append({
                    'Company Name': 'N/A',
                    'Website': 'N/A',
                    'Phone': 'N/A',
                    'Industry': 'N/A',
                    'Company URL': company_url,
                    'Email': 'N/A'
                })

    if company_data:
        # Explicitly set dtypes for the DataFrame to avoid type mismatches
        df = pd.DataFrame(company_data, dtype=object)
        df.to_excel('company_data.xlsx', index=False)
        safe_print('- Successfully saved company data to company_data.xlsx')
    else:
        safe_print('- No company data to save, creating an empty company_data.xlsx with headers')
        empty_data = pd.DataFrame(columns=['Company Name', 'Website', 'Phone', 'Industry', 'Company URL', 'Email'])
        empty_data = empty_data.astype(object)  # Ensure all columns are object dtype
        empty_data.to_excel('company_data.xlsx', index=False)
        safe_print('- Created empty company_data.xlsx with headers')

    # Task 6: Scrape emails from websites
    safe_print('\nStarting Task 6: Scrape emails from websites\n')
    try:
        # Read the Excel file, ensuring Email column is treated as string
        df = pd.read_excel('company_data.xlsx', dtype={'Email': str})
        safe_print('- Loaded company_data.xlsx')
        safe_print(df)
    except FileNotFoundError:
        safe_print('- Error: company_data.xlsx not found, creating an empty file with headers')
        empty_data = pd.DataFrame(columns=['Company Name', 'Website', 'Phone', 'Industry', 'Company URL', 'Email'])
        empty_data = empty_data.astype(object)  # Ensure all columns are object dtype
        empty_data.to_excel('company_data.xlsx', index=False)
        df = pd.read_excel('company_data.xlsx', dtype={'Email': str})

    for index, row in df.iterrows():
        website = row['Website']
        email = scrape_emails(driver, website)
        df.at[index, 'Email'] = email

    df.to_excel('company_data.xlsx', index=False)
    safe_print('- Successfully updated company_data.xlsx with email IDs')

    safe_print('Mission Completed - All Tasks Including Email Scraping!')

except Exception as e:
    import traceback
    safe_print(f"An error occurred: {e}")
    safe_print(traceback.format_exc())
finally:
    driver.quit()