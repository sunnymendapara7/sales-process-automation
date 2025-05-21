# Sales Process Automation using Python 

## Project Overview
This project automates key aspects of the sales process using Python programming and AI/ML techniques. The goal is to streamline lead generation, email outreach, and campaign analytics with minimal manual intervention.

This project automates the sales outreach process for a T-shirt manufacturing business targeting IT companies in Ahmedabad. The system is designed to scrape leads, generate personalized emails, send them via SMTP, track engagement, and categorize leads using analytics—all with one command.

You will be able to:
- Scrape business leads from Google Maps based on your target Ideal Customer Profile (ICP).
- Extract relevant contact data including emails by visiting each company website.
- Generate personalized email templates for outreach.
- Automate the sending of emails in batches to avoid spam filters.
- Track email opens and clicks using a lightweight Flask server.
- Collect and analyze campaign performance metrics.

---

## Step-by-Step Process Explanation

### Step 1: Lead Scraping & Email Extraction
- Using `map_lead.py`, the project scrapes company details such as name, website, address, and phone from Google Maps focused on IT companies in Ahmedabad.
- Since email addresses are not directly available, the script visits each company’s website and extracts email addresses by scanning the web page content.
- The final structured data is saved into an Excel file `scraped_it_companies_ahmedabad_with_emails.xlsx` for further use.

### Step 2: Email Generation
- The `generate_emails.py` script reads the Excel file and creates personalized emails using a predefined HTML email template.
- Dynamic placeholders such as `[Company Name]` and `[Recipient Name]` are replaced with actual data from the Excel sheet.
- This step prepares customized outreach emails for each lead.

### Step 3: Tracking Setup
- A lightweight Flask app in `tracking_server.py` serves a tracking pixel embedded in every email.
- When a recipient opens the email, the tracking pixel loads and registers the event.
- This enables the system to collect open and click analytics for the email campaign.

### Step 4: Sending Emails
- The `send_emails.py` script sends personalized emails by reading the leads Excel file.
- It supports batching and delay between emails to avoid spam detection and throttling by email providers.
- Each email includes the tracking pixel to monitor recipient engagement.

### Step 5: Automation
- The `automate_campaign.py` script automates the entire pipeline.
- It checks dependencies, runs lead scraping, generates emails, starts the tracking server, sends the email campaign, and then stops the server.
- All steps and results are logged to a timestamped log file for monitoring.

---

## 🛠️ Libraries & Technologies Used

| Library               | Purpose                                                  |
|-----------------------|----------------------------------------------------------|
| `selenium`            | Web scraping and browser automation                      |
| `requests`            | Sending HTTP requests for scraping emails on websites    |
| `lxml`, `html5lib`    | HTML parsing backends                                    |
| `pandas`              | Data manipulation and Excel file handling                |
| `openpyxl`            | Reading and writing Excel files                          |
| `dotenv`              | Loading environment variables from `.env` file           |
| `flask`               | Lightweight web server for email open tracking           |
| `smtplib`             | Sending emails via SMTP                                  |
| `chromedriver-binary` | Selenium Chrome driver                                   |
| `webdriver-manager`   | Manages Selenium web drivers                             |
| `geckodriver`         | Selenium Firefox driver                                  |

---

## Project Setup and Running Instructions

### Prerequisites
- Python 3.7 or higher installed
- Google Chrome or Firefox browser installed (for Selenium)
- SMTP email credentials (e.g., Gmail) with “less secure app access” enabled or app password


### Installation Guide

---

## 1. Clone the Repository

```bash
git clone https://github.com/sunnymendapara7/sales-process-automation.git
cd sales-process-automation
```

---

## 2. Install Required Python Libraries

Ensure Python 3.8+ is installed. Then install dependencies:

```bash
pip install -r requirements.txt
```

---

## 3. Prepare the Environment File

Create a `.env` file in the root directory and add your credentials:

```env
EMAIL_USER=your-email@example.com
EMAIL_PASS=your-password
```

---

## 4. Automate the Full Campaign Pipeline

This script handles scraping, generating emails, starting tracking server, and sending emails:

```bash
python automate_campaign.py
```

---

## 5. Monitor Logs and Analytics

Track campaign performance:

- `logs/` → Campaign logs campaign_automation_log_<timestamp>.txt
- `analytics/` → Open and click tracking data

---

### 🙌 Thank You!

Thank you for checking out this **Sales Process Automation** project!  
Feel free to ⭐️ the repository, contribute, or raise issues.

📬 For questions or collaboration, reach out to me at:  
**sunnymendapara09@gmail.com**

