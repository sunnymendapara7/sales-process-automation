from flask import Flask, redirect, request
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

# File to store tracking data
TRACKING_FILE = "email_tracking_data.csv"

# Create a log file for tracking events
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
tracking_events_file = f"tracking_events_{timestamp}.txt"

# Function to append to the tracking events file
def write_to_tracking_events(content, mode='a'):
    try:
        with open(tracking_events_file, mode, encoding='utf-8') as f:
            f.write(content + "\n")
    except Exception as e:
        print(f"Error writing to tracking events file: {e}")

# Initialize the tracking events file
write_to_tracking_events("--- Open Events ---", mode='w')
write_to_tracking_events("--- Click Events ---")

# Ensure the tracking file exists
if not os.path.exists(TRACKING_FILE):
    tracking_df = pd.DataFrame(columns=["campaign_id", "email_id", "recipient_email", "opened", "clicked", "open_time", "click_time"])
    tracking_df.to_csv(TRACKING_FILE, index=False)

@app.route('/track_open/<email_id>')
def track_open(email_id):
    print(f"Received open request for email_id: {email_id}")
    try:
        # Load the tracking data
        tracking_df = pd.read_csv(TRACKING_FILE)
        print(f"Tracking file columns: {list(tracking_df.columns)}")
        print(f"Tracking file rows: {len(tracking_df)}")

        # Find the email entry
        if email_id in tracking_df['email_id'].values:
            print(f"Found email_id {email_id} in tracking data")
            # Update the tracking data
            tracking_df.loc[tracking_df['email_id'] == email_id, 'opened'] = True
            open_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            tracking_df.loc[tracking_df['email_id'] == email_id, 'open_time'] = open_time
            
            # Save the updated tracking data
            tracking_df.to_csv(TRACKING_FILE, index=False)
            print(f"Updated tracking data: opened=True, open_time={open_time}")
            
            # Log the open event
            recipient = tracking_df.loc[tracking_df['email_id'] == email_id, 'recipient_email'].iloc[0]
            write_to_tracking_events(f"Email ID: {email_id}, Recipient: {recipient}, Opened at: {open_time}")
            print(f"Logged open event for {recipient}")
        else:
            print(f"Email ID {email_id} not found in tracking data")

        # Return a 1x1 pixel image
        with open("pixel.png", "rb") as f:
            return f.read(), 200, {'Content-Type': 'image/png'}
    except Exception as e:
        print(f"Error in track_open: {e}")
        # Return a 1x1 pixel image even if there's an error
        with open("pixel.png", "rb") as f:
            return f.read(), 200, {'Content-Type': 'image/png'}

@app.route('/track_click/<email_id>')
def track_click(email_id):
    print(f"Received click request for email_id: {email_id}")
    try:
        # Load the tracking data
        tracking_df = pd.read_csv(TRACKING_FILE)
        print(f"Tracking file columns: {list(tracking_df.columns)}")
        print(f"Tracking file rows: {len(tracking_df)}")

        # Find the email entry
        if email_id in tracking_df['email_id'].values:
            print(f"Found email_id {email_id} in tracking data")
            # Update the tracking data
            tracking_df.loc[tracking_df['email_id'] == email_id, 'clicked'] = True
            click_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            tracking_df.loc[tracking_df['email_id'] == email_id, 'click_time'] = click_time
            
            # Save the updated tracking data
            tracking_df.to_csv(TRACKING_FILE, index=False)
            print(f"Updated tracking data: clicked=True, click_time={click_time}")
            
            # Log the click event
            recipient = tracking_df.loc[tracking_df['email_id'] == email_id, 'recipient_email'].iloc[0]
            write_to_tracking_events(f"Email ID: {email_id}, Recipient: {recipient}, Clicked at: {click_time}")
            print(f"Logged click event for {recipient}")
        else:
            print(f"Email ID {email_id} not found in tracking data")

        # Redirect to a confirmation page or a relevant URL
        return redirect("https://www.bonkstreet.in")
    except Exception as e:
        print(f"Error in track_click: {e}")
        return redirect("https://www.bonkstreet.in")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)