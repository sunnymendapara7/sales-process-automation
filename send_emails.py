import pandas as pd
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime

# Create structured text files for campaign details and analytics report
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
campaign_details_file = f"campaign_details_{timestamp}.txt"
analytics_report_file = f"analytics_report_{timestamp}.txt"

# Function to append to the campaign details file
def write_to_campaign_file(content, mode='a'):
    try:
        with open(campaign_details_file, mode, encoding='utf-8') as f:
            f.write(content + "\n")
        print(f"Debug: Wrote to campaign file: {content}")
    except Exception as e:
        print(f"Error writing to campaign file: {e}")

# Function to append to the analytics report file
def write_to_analytics_file(content, mode='a'):
    try:
        with open(analytics_report_file, mode, encoding='utf-8') as f:
            f.write(content + "\n")
        print(f"Debug: Wrote to analytics file: {content}")
    except Exception as e:
        print(f"Error writing to analytics file: {e}")

# Load environment variables from .env file
load_dotenv()

# Access email credentials from environment variables
sender_email = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("SENDER_PASSWORD")

# Check if credentials are loaded
if not sender_email or not sender_password:
    print("Error: SENDER_EMAIL or SENDER_PASSWORD not found in .env file.")
    exit(1)
print("Debug: Environment variables loaded successfully.")

# Error handling for missing Excel file
try:
    df = pd.read_excel("company_data.xlsx")
    print(f"Debug: Excel file loaded successfully with {len(df)} rows.")
except FileNotFoundError:
    print("Error: 'company_data.xlsx' not found. Please ensure the file exists in the current directory or provide the correct path.")
    exit(1)
except Exception as e:
    print(f"Error reading Excel file: {e}")
    exit(1)

# Read the email template
try:
    with open("email_template.html", "r", encoding="utf-8") as file:
        email_template = file.read()
    print("Debug: Email template loaded successfully.")
except FileNotFoundError:
    print("Error: 'email_template.html' not found. Please ensure the file exists in the current directory.")
    exit(1)
except Exception as e:
    print(f"Error reading email template: {e}")
    exit(1)

# Bonkstreet details
your_company_name = "Bonkstreet"
your_name = "Ravi Patel"
your_position = "Business Development Manager"
your_email = sender_email  # Use the email from .env
your_phone = "+91 99090 03633"

# Email sending configuration (using Gmail SMTP)
smtp_server = "smtp.gmail.com"
smtp_port = 587

# Tracking server URL (use localhost for local testing)
TRACKING_SERVER_URL = "http://localhost:5000"

# File to store tracking data
TRACKING_FILE = "email_tracking_data.csv"

# Generate a campaign ID
campaign_id = str(uuid.uuid4())

# Write campaign metadata to the campaign details file
write_to_campaign_file(f"Campaign ID: {campaign_id}", mode='w')
write_to_campaign_file(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
write_to_campaign_file("")

# Initialize the tracking file if it doesn't exist
if not os.path.exists(TRACKING_FILE):
    tracking_df = pd.DataFrame(columns=["campaign_id", "email_id", "recipient_email", "opened", "clicked", "open_time", "click_time"])
    tracking_df.to_csv(TRACKING_FILE, index=False)
    print("Debug: Initialized new tracking file.")
else:
    print("Debug: Tracking file already exists.")

# Filter out rows with missing or invalid email addresses
df = df.dropna(subset=["Email"])  # Remove rows where Email is NaN
df = df[df["Email"].str.contains("@", na=False)]  # Keep only rows with valid email addresses (containing "@")
print(f"Debug: Filtered dataframe to {len(df)} valid email addresses.")

# Check if there are any valid emails to send
if df.empty:
    print("Error: No valid email addresses found in the Excel file.")
    exit(1)

# Batch sending configuration
batch_size = 5  # Number of emails per batch
delay_between_emails = 30  # Delay in seconds between emails
delay_between_batches = 300  # Delay in seconds between batches (5 minutes)

# Write section header for emails sent in the campaign details file
write_to_campaign_file("--- Emails Sent ---")

# Dictionary to store email_id to recipient mapping for simulation
email_id_to_recipient = {}

# Send emails in batches
for batch_start in range(0, len(df), batch_size):
    batch_end = min(batch_start + batch_size, len(df))
    print(f"Sending batch {batch_start // batch_size + 1}: Emails {batch_start + 1} to {batch_end}")
    
    for index in range(batch_start, batch_end):
        row = df.iloc[index]
        # Extract data
        company_name = row["Company Name"]
        recipient_name = f"{company_name.split()[0]} Team"
        recipient_email = row["Email"]
        
        # Generate a unique email_id for tracking
        email_id = str(uuid.uuid4())
        
        # Store the mapping for simulation
        email_id_to_recipient[email_id] = recipient_email
        
        # Log the email in the tracking file
        tracking_entry = pd.DataFrame({
            "campaign_id": [campaign_id],
            "email_id": [email_id],
            "recipient_email": [recipient_email],
            "opened": [False],
            "clicked": [False],
            "open_time": [None],
            "click_time": [None]
        })
        tracking_entry.to_csv(TRACKING_FILE, mode='a', header=False, index=False)
        print(f"Debug: Logged email {index + 1} to tracking file for {recipient_email}.")
        
        # Write email details to the campaign file
        write_to_campaign_file(f"Email {index + 1}: Sent to {recipient_email}")
        
        # Populate the subject line
        subject = f"Custom T-Shirts for {company_name} from Bonkstreet"
        
        # Populate the email body with the HTML template
        email_body_html = email_template.replace("[Recipient Name]", recipient_name)
        email_body_html = email_body_html.replace("[Company Name]", company_name)
        email_body_html = email_body_html.replace("[Your Company Name]", your_company_name)
        email_body_html = email_body_html.replace("[Your Name]", your_name)
        email_body_html = email_body_html.replace("[Your Position]", your_position)
        email_body_html = email_body_html.replace("[Your Email]", your_email)
        email_body_html = email_body_html.replace("[Your Phone]", your_phone)
        
        # Add tracking CTA link (replace a placeholder [CTA_LINK] in your email_template.html)
        cta_link = f"{TRACKING_SERVER_URL}/track_click/{email_id}"
        email_body_html = email_body_html.replace("[CTA_LINK]", cta_link)
        write_to_campaign_file(f"CTA Link: {cta_link}")
        print(f"CTA Link: {cta_link}")
        
        # Add tracking pixel
        tracking_pixel = f'<img src="{TRACKING_SERVER_URL}/track_open/{email_id}" width="1" height="1" alt="" />'
        email_body_html = email_body_html.replace("</body>", f"{tracking_pixel}</body>")
        write_to_campaign_file(f"Tracking Pixel: {TRACKING_SERVER_URL}/track_open/{email_id}")
        print(f"Tracking Pixel: {TRACKING_SERVER_URL}/track_open/{email_id}")
        
        # Debug: Print the final email body to verify replacements
        write_to_campaign_file("--- Debug: Final Email Body ---")
        write_to_campaign_file(email_body_html)
        write_to_campaign_file("-----------------------------")
        print("Debug: Final Email Body:")
        print(email_body_html)
        print("-----------------------------")
        
        # Create the email (multipart with a minimal plain text fallback)
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Minimal plain text fallback
        email_body_text = "Please view this email in an HTML-compatible email client."
        msg.attach(MIMEText(email_body_text, 'plain'))
        msg.attach(MIMEText(email_body_html, 'html'))

        # Send the email
        try:
            print(f"Debug: Connecting to SMTP server for email {index + 1}...")
            with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
                server.starttls()
                print(f"Debug: Logging in to SMTP server...")
                server.login(sender_email, sender_password)
                print(f"Debug: Sending email to {recipient_email}...")
                server.sendmail(sender_email, recipient_email, msg.as_string())
                print(f"Email {index + 1}: Sent at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            write_to_campaign_file(f"Error: Failed to send to {recipient_email} - {e}")
            print(f"Email {index + 1}: Failed to send to {recipient_email} - Error: {e}")
        
        # Delay between emails
        if index < batch_end - 1:  # No delay after the last email in the batch
            print(f"Debug: Waiting {delay_between_emails} seconds before sending next email...")
            time.sleep(delay_between_emails)
    
    # Delay between batches (except after the last batch)
    if batch_end < len(df):
        print(f"Debug: Waiting {delay_between_batches} seconds before next batch...")
        time.sleep(delay_between_batches)

# Debug: Confirm reaching the analytics section
print("Debug: Starting analytics section...")

# Wait for 30 seconds to collect tracking data (further reduced for faster testing)
try:
    print("Waiting for 30 seconds to collect tracking data...")
    write_to_campaign_file("")
    write_to_campaign_file("Waiting for 30 seconds to collect tracking data...")
    time.sleep(30)  # Reduced from 60 seconds to 30 seconds
except Exception as e:
    print(f"Error during wait period: {e}")
    write_to_campaign_file(f"Error during wait period: {e}")

# Debug: Confirm wait period completed
print("Debug: Wait period completed, analyzing tracking data...")

# Simulate a tracking event for testing (e.g., for officialbonkstreet@gmail.com)
print("Simulating tracking events for officialbonkstreet@gmail.com...")
try:
    tracking_df = pd.read_csv(TRACKING_FILE)
    print(f"Debug: Loaded tracking file with {len(tracking_df)} entries.")
    for email_id, recipient in email_id_to_recipient.items():
        if recipient == "officialbonkstreet@gmail.com":
            print(f"Simulating open and click for email_id: {email_id}")
            tracking_df.loc[tracking_df['email_id'] == email_id, 'opened'] = True
            tracking_df.loc[tracking_df['email_id'] == email_id, 'open_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            tracking_df.loc[tracking_df['email_id'] == email_id, 'clicked'] = True
            tracking_df.loc[tracking_df['email_id'] == email_id, 'click_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            tracking_df.to_csv(TRACKING_FILE, index=False)
            print(f"Simulated tracking events for {recipient}")
            break
except Exception as e:
    print(f"Error simulating tracking events: {e}")

# Analyze tracking data and generate report
try:
    tracking_df = pd.read_csv(TRACKING_FILE)
    print("Debug: Tracking file read successfully.")
except Exception as e:
    print(f"Error reading tracking file: {e}")
    write_to_campaign_file(f"Error reading tracking file: {e}")
    tracking_df = pd.DataFrame(columns=["campaign_id", "email_id", "recipient_email", "opened", "clicked", "open_time", "click_time"])

# Debug: Print the columns of tracking_df
print(f"Debug: Columns in tracking_df: {list(tracking_df.columns)}")

# Ensure required columns exist, fill with defaults if missing
required_columns = ["campaign_id", "email_id", "recipient_email", "opened", "clicked", "open_time", "click_time"]
for col in required_columns:
    if col not in tracking_df.columns:
        print(f"Debug: Missing column '{col}' in tracking_df, adding with default values.")
        tracking_df[col] = None if col in ["campaign_id", "email_id", "recipient_email", "open_time", "click_time"] else False

# Filter for the current campaign
tracking_df_filtered = pd.DataFrame(columns=required_columns)  # Default empty DataFrame
try:
    tracking_df_filtered = tracking_df[tracking_df['campaign_id'] == campaign_id]
    print("Debug: Filtered tracking data for campaign.")
except Exception as e:
    print(f"Error filtering tracking data: {e}")
    write_to_campaign_file(f"Error filtering tracking data: {e}")

# Use the filtered DataFrame (or empty if filtering failed)
tracking_df = tracking_df_filtered

# Calculate metrics
total_emails = len(tracking_df)
emails_opened = len(tracking_df[tracking_df['opened'] == True])
emails_clicked = len(tracking_df[tracking_df['clicked'] == True])
open_rate = (emails_opened / total_emails) * 100 if total_emails > 0 else 0
click_rate = (emails_clicked / total_emails) * 100 if total_emails > 0 else 0

# Categorize leads
hot_leads = tracking_df[tracking_df['clicked'] == True]  # Hot leads are those who clicked the CTA
cold_leads = tracking_df[tracking_df['clicked'] == False]  # Cold leads are those who didn't click
num_hot_leads = len(hot_leads)
num_cold_leads = len(cold_leads)

# Write the analytics report to a separate file (matching the exact desired format)
write_to_analytics_file("--- Email Campaign Analytics Report ---", mode='w')
write_to_analytics_file(f"Total Emails Sent: {total_emails}")
write_to_analytics_file(f"Emails Opened: {emails_opened}")
write_to_analytics_file(f"Open Rate: {open_rate:.2f}%")
write_to_analytics_file(f"Emails Clicked: {emails_clicked}")
write_to_analytics_file(f"Click-Through Rate: {click_rate:.2f}%")
write_to_analytics_file(f"Number of Hot Leads: {num_hot_leads}")
write_to_analytics_file(f"Hot Leads Emails: {', '.join(hot_leads['recipient_email'].tolist()) if num_hot_leads > 0 else 'None'}")
write_to_analytics_file(f"Number of Cold Leads: {num_cold_leads}")
write_to_analytics_file(f"Cold Leads Emails: {', '.join(cold_leads['recipient_email'].tolist()) if num_cold_leads > 0 else 'None'}")
write_to_analytics_file("--------------------------------------")

# Print the report to the terminal as well
print("\n--- Email Campaign Analytics Report ---")
print(f"Total Emails Sent: {total_emails}")
print(f"Emails Opened: {emails_opened}")
print(f"Open Rate: {open_rate:.2f}%")
print(f"Emails Clicked: {emails_clicked}")
print(f"Click-Through Rate: {click_rate:.2f}%")
print(f"Number of Hot Leads: {num_hot_leads}")
print(f"Hot Leads Emails: {', '.join(hot_leads['recipient_email'].tolist()) if num_hot_leads > 0 else 'None'}")
print(f"Number of Cold Leads: {num_cold_leads}")
print(f"Cold Leads Emails: {', '.join(cold_leads['recipient_email'].tolist()) if num_cold_leads > 0 else 'None'}")
print("--------------------------------------")

# Save campaign summary to a separate file
campaign_summary_file = "campaign_summaries.csv"
campaign_summary = pd.DataFrame({
    "campaign_id": [campaign_id],
    "timestamp": [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
    "total_emails": [total_emails],
    "emails_opened": [emails_opened],
    "open_rate": [open_rate],
    "emails_clicked": [emails_clicked],
    "click_through_rate": [click_rate],
    "hot_leads": [num_hot_leads],
    "cold_leads": [num_cold_leads]
})
try:
    if not os.path.exists(campaign_summary_file):
        campaign_summary.to_csv(campaign_summary_file, index=False)
    else:
        campaign_summary.to_csv(campaign_summary_file, mode='a', header=False, index=False)
    print("Debug: Campaign summary saved successfully.")
except Exception as e:
    print(f"Error saving campaign summary: {e}")
    write_to_campaign_file(f"Error saving campaign summary: {e}")

print("\nEmail campaign completed!")
write_to_campaign_file("")
write_to_campaign_file("Email campaign completed!")