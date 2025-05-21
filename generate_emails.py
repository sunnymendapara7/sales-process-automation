import pandas as pd

# Error handling for missing Excel file
try:
    df = pd.read_excel("scraped_it_companies_ahmedabad_with_emails.xlsx")
except FileNotFoundError:
    print("Error: 'scraped_it_companies_ahmedabad_with_emails.xlsx' not found. Please ensure the file exists in the current directory or provide the correct path.")
    exit(1)

# Read the email template
try:
    with open("email_template.html", "r", encoding="utf-8") as file:
        email_template = file.read()
except FileNotFoundError:
    print("Error: 'email_template.html' not found. Please ensure the file exists in the current directory.")
    exit(1)

# Bonkstreet details
your_company_name = "Bonkstreet"
your_name = "Ravi Patel"
your_position = "Business Development Manager"
your_email = "officialbonkstreet@gmail.com"
your_phone = "+91 99090 03633"

# Generate the subject line and email body for each company
for index, row in df.iterrows():
    # Extract data
    company_name = row["Company Name"]
    # Derive a recipient name (e.g., "CodeAroma Team")
    recipient_name = f"{company_name.split()[0]} Team"
    
    # Populate the subject line
    subject = f"Custom T-Shirts for {company_name} – No MOQ with Bonkstreet!"
    
    # Populate the email body
    email_body = email_template.replace("[Recipient Name]", recipient_name)
    email_body = email_body.replace("[Company Name]", company_name)
    email_body = email_body.replace("[Your Company Name]", your_company_name)
    email_body = email_body.replace("[Your Name]", your_name)
    email_body = email_body.replace("[Your Position]", your_position)
    email_body = email_body.replace("[Your Email]", your_email)
    email_body = email_body.replace("[Your Phone]", your_phone)
    
    # Print the email (for demonstration)
    print(f"\nEmail {index + 1}:")
    print(f"Subject: {subject}")
    print("Body:")
    print(email_body)
    print("-" * 50)