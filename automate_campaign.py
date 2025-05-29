# import subprocess
# import os
# import time
# from datetime import datetime
# import sys
# import psutil
# from dotenv import load_dotenv

# # Create a log file for the automation process
# timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
# log_file = f"campaign_automation_log_{timestamp}.txt"

# # Function to append to the log file
# def log_message(message, mode='a'):
#     with open(log_file, mode, encoding='utf-8') as f:
#         f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
#     print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

# # Check for required files and dependencies
# def check_requirements():
#     log_message("Checking project requirements...", mode='w')
    
#     # Check for required files
#     required_files = ['map_lead.py', 'email_template.html', 'generate_emails.py', 'tracking_server.py', 'send_emails.py', '.env']
#     for file in required_files:
#         if not os.path.exists(file):
#             log_message(f"Error: Required file '{file}' not found in the project directory.")
#             sys.exit(1)
#     log_message("All required files are present.")
    
#     # Check for .env variables
#     load_dotenv()
#     sender_email = os.getenv("SENDER_EMAIL")
#     sender_password = os.getenv("SENDER_PASSWORD")
#     if not sender_email or not sender_password:
#         log_message("Error: SENDER_EMAIL or SENDER_PASSWORD not found in .env file.")
#         sys.exit(1)
#     log_message("Environment variables loaded successfully.")

# # Step 1: Run the lead scraping process (map_lead.py)
# def run_lead_scraping():
#     log_message("Starting lead scraping process (map_lead.py)...")
#     try:
#         process = subprocess.run(['python', 'map_lead.py'], capture_output=True, text=True, check=True)
#         log_message("Lead scraping completed successfully.")
#         log_message(f"Output:\n{process.stdout}")
#         if process.stderr:
#             log_message(f"Errors/Warnings:\n{process.stderr}")
        
#         # Check if the output file was created
#         if not os.path.exists("scraped_it_companies_ahmedabad_with_emails.xlsx"):
#             log_message("Error: Lead scraping did not produce 'scraped_it_companies_ahmedabad_with_emails.xlsx'.")
#             sys.exit(1)
#     except subprocess.CalledProcessError as e:
#         log_message(f"Error: Lead scraping failed with exit code {e.returncode}.")
#         log_message(f"Output:\n{e.output}")
#         log_message(f"Errors:\n{e.stderr}")
#         sys.exit(1)
#     except Exception as e:
#         log_message(f"Error: Unexpected error during lead scraping: {e}")
#         sys.exit(1)

# # Step 2: Generate and preview emails (generate_emails.py)
# def generate_emails():
#     log_message("Generating and previewing emails (generate_emails.py)...")
#     try:
#         process = subprocess.run(['python', 'generate_emails.py'], capture_output=True, text=True, check=True)
#         log_message("Email generation and preview completed successfully.")
#         log_message(f"Output:\n{process.stdout}")
#         if process.stderr:
#             log_message(f"Errors/Warnings:\n{process.stderr}")
#     except subprocess.CalledProcessError as e:
#         log_message(f"Error: Email generation failed with exit code {e.returncode}.")
#         log_message(f"Output:\n{e.output}")
#         log_message(f"Errors:\n{e.stderr}")
#         sys.exit(1)
#     except Exception as e:
#         log_message(f"Error: Unexpected error during email generation: {e}")
#         sys.exit(1)

# # Step 3: Start the tracking server (tracking_server.py)
# def start_tracking_server():
#     log_message("Starting tracking server (tracking_server.py)...")
#     try:
#         # Start the Flask server in a subprocess
#         server_process = subprocess.Popen(
#             ['python', 'tracking_server.py'],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True
#         )
        
#         # Wait a bit to ensure the server starts
#         time.sleep(5)
        
#         # Check if the server process is still running
#         if server_process.poll() is not None:
#             # Process terminated, there was an error
#             stdout, stderr = server_process.communicate()
#             log_message(f"Error: Tracking server failed to start.")
#             log_message(f"Output:\n{stdout}")
#             log_message(f"Errors:\n{stderr}")
#             sys.exit(1)
        
#         log_message(f"Tracking server started successfully with PID {server_process.pid}.")
#         return server_process
#     except Exception as e:
#         log_message(f"Error: Failed to start tracking server: {e}")
#         sys.exit(1)

# # Step 4: Run the email sending and tracking process (send_emails.py)
# def run_email_campaign():
#     log_message("Starting email sending and tracking process (send_emails.py)...")
#     try:
#         process = subprocess.run(['python', 'send_emails.py'], capture_output=True, text=True, check=True)
#         log_message("Email campaign completed successfully.")
#         log_message(f"Output:\n{process.stdout}")
#         if process.stderr:
#             log_message(f"Errors/Warnings:\n{process.stderr}")
#     except subprocess.CalledProcessError as e:
#         log_message(f"Error: Email campaign failed with exit code {e.returncode}.")
#         log_message(f"Output:\n{e.output}")
#         log_message(f"Errors:\n{e.stderr}")
#         sys.exit(1)
#     except Exception as e:
#         log_message(f"Error: Unexpected error during email campaign: {e}")
#         sys.exit(1)

# # Step 5: Stop the tracking server
# def stop_tracking_server(server_process):
#     log_message("Stopping tracking server...")
#     try:
#         # Terminate the server process and its children
#         parent = psutil.Process(server_process.pid)
#         for child in parent.children(recursive=True):
#             child.terminate()
#         parent.terminate()
        
#         # Wait for the process to terminate
#         server_process.wait(timeout=10)
#         log_message("Tracking server stopped successfully.")
#     except Exception as e:
#         log_message(f"Error: Failed to stop tracking server: {e}")
#         # Continue execution even if stopping fails, as the campaign is already complete

# # Main automation function
# def main():
#     # Check requirements before starting
#     check_requirements()
    
#     log_message("Starting email campaign automation process...")
    
#     # Step 1: Scrape leads
#     run_lead_scraping()
    
#     # Step 2: Generate and preview emails
#     generate_emails()
    
#     # Step 3: Start the tracking server
#     server_process = start_tracking_server()
    
#     # Step 4: Run the email campaign
#     run_email_campaign()
    
#     # Step 5: Stop the tracking server
#     stop_tracking_server(server_process)
    
#     log_message("Email campaign automation process completed successfully!")

# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         log_message("Process interrupted by user.")
#         sys.exit(1)
#     except Exception as e:
#         log_message(f"Unexpected error in automation process: {e}")
#         sys.exit(1)


import subprocess
import os
import time
from datetime import datetime
import sys
import psutil
from dotenv import load_dotenv

# Create a log file for the automation process
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = f"campaign_automation_log_{timestamp}.txt"

# Function to append to the log file
def log_message(message, mode='a'):
    with open(log_file, mode, encoding='utf-8') as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

# Check for required files and dependencies
def check_requirements():
    log_message("Checking project requirements...", mode='w')
    
    # Check for required files
    required_files = ['linkedin_scraper.py', 'email_template.html', 'generate_emails.py', 'tracking_server.py', 'send_emails.py', '.env', 'credentials.txt']
    for file in required_files:
        if not os.path.exists(file):
            log_message(f"Error: Required file '{file}' not found in the project directory.")
            sys.exit(1)
    log_message("All required files are present.")
    
    # Check for .env variables
    load_dotenv()
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    if not sender_email or not sender_password:
        log_message("Error: SENDER_EMAIL or SENDER_PASSWORD not found in .env file.")
        sys.exit(1)
    log_message("Environment variables loaded successfully.")

# Step 1: Run the lead scraping process (linkedin_scraper.py)
def run_lead_scraping():
    log_message("Starting lead scraping process (linkedin_scraper.py)...")
    try:
        # Run linkedin_scraper.py and capture its output
        process = subprocess.run(['python', 'linkedin_scraper.py'], capture_output=True, text=True, check=True)
        log_message("Lead scraping completed successfully.")
        # Avoid re-printing the output to prevent duplication
        # log_message(f"Output:\n{process.stdout}")
        if process.stderr:
            log_message(f"Errors/Warnings:\n{process.stderr}")
        
        # Check if the output file was created
        if not os.path.exists("company_data.xlsx"):
            log_message("Error: Lead scraping did not produce 'company_data.xlsx'.")
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        log_message(f"Error: Lead scraping failed with exit code {e.returncode}.")
        log_message(f"Output:\n{e.output}")
        log_message(f"Errors:\n{e.stderr}")
        sys.exit(1)
    except Exception as e:
        log_message(f"Error: Unexpected error during lead scraping: {e}")
        sys.exit(1)

# Step 2: Generate and preview emails (generate_emails.py)
def generate_emails():
    log_message("Generating and previewing emails (generate_emails.py)...")
    try:
        process = subprocess.run(['python', 'generate_emails.py'], capture_output=True, text=True, check=True)
        log_message("Email generation and preview completed successfully.")
        # Avoid re-printing the output to prevent duplication
        # log_message(f"Output:\n{process.stdout}")
        if process.stderr:
            log_message(f"Errors/Warnings:\n{process.stderr}")
    except subprocess.CalledProcessError as e:
        log_message(f"Error: Email generation failed with exit code {e.returncode}.")
        log_message(f"Output:\n{e.output}")
        log_message(f"Errors:\n{e.stderr}")
        sys.exit(1)
    except Exception as e:
        log_message(f"Error: Unexpected error during email generation: {e}")
        sys.exit(1)

# Step 3: Start the tracking server (tracking_server.py)
def start_tracking_server():
    log_message("Starting tracking server (tracking_server.py)...")
    try:
        # Start the Flask server in a subprocess
        server_process = subprocess.Popen(
            ['python', 'tracking_server.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit to ensure the server starts
        time.sleep(5)
        
        # Check if the server process is still running
        if server_process.poll() is not None:
            # Process terminated, there was an error
            stdout, stderr = server_process.communicate()
            log_message(f"Error: Tracking server failed to start.")
            log_message(f"Output:\n{stdout}")
            log_message(f"Errors:\n{stderr}")
            sys.exit(1)
        
        log_message(f"Tracking server started successfully with PID {server_process.pid}.")
        return server_process
    except Exception as e:
        log_message(f"Error: Failed to start tracking server: {e}")
        sys.exit(1)

# Step 4: Run the email sending and tracking process (send_emails.py)
def run_email_campaign():
    log_message("Starting email sending and tracking process (send_emails.py)...")
    try:
        process = subprocess.run(['python', 'send_emails.py'], capture_output=True, text=True, check=True)
        log_message("Email campaign completed successfully.")
        # Avoid re-printing the output to prevent duplication
        # log_message(f"Output:\n{process.stdout}")
        if process.stderr:
            log_message(f"Errors/Warnings:\n{process.stderr}")
    except subprocess.CalledProcessError as e:
        log_message(f"Error: Email campaign failed with exit code {e.returncode}.")
        log_message(f"Output:\n{e.output}")
        log_message(f"Errors:\n{e.stderr}")
        sys.exit(1)
    except Exception as e:
        log_message(f"Error: Unexpected error during email campaign: {e}")
        sys.exit(1)

# Step 5: Stop the tracking server
def stop_tracking_server(server_process):
    log_message("Stopping tracking server...")
    try:
        # Terminate the server process and its children
        parent = psutil.Process(server_process.pid)
        for child in parent.children(recursive=True):
            child.terminate()
        parent.terminate()
        
        # Wait for the process to terminate
        server_process.wait(timeout=10)
        log_message("Tracking server stopped successfully.")
    except Exception as e:
        log_message(f"Error: Failed to stop tracking server: {e}")
        # Continue execution even if stopping fails, as the campaign is already complete

# Main automation function
def main():
    # Check requirements before starting
    check_requirements()
    
    log_message("Starting email campaign automation process...")
    
    # Step 1: Scrape leads
    run_lead_scraping()
    
    # Step 2: Generate and preview emails
    generate_emails()
    
    # Step 3: Start the tracking server
    server_process = start_tracking_server()
    
    # Step 4: Run the email campaign
    run_email_campaign()
    
    # Step 5: Stop the tracking server
    stop_tracking_server(server_process)
    
    log_message("Email campaign automation process completed successfully!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_message("Process interrupted by user.")
        sys.exit(1)
    except Exception as e:
        log_message(f"Unexpected error in automation process: {e}")
        sys.exit(1)