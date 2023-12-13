import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os


def send_email(email_data, recepient):
    # Your email configuration
    sender_email = os.environ.get("SENDER_EMAIL")
    receiver_email = recepient
    password = os.environ.get("EMAIL_PASSWORD")
    print(sender_email, receiver_email, password)

    # HTML body with CSS styling
    html_body = f"""
    <html>
    <head>
    <style>
    body {{
        font-family: Arial, sans-serif;
        background-color: #f4f4f4;
        color: #333;
    }}
    .container {{
        max-width: 600px;
        margin: 20px auto;
        padding: 20px;
        background-color: #fff;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    }}
    h1 {{
        color: #3498db;
    }}
    .error {{
        color: #e74c3c;
    }}
    </style>
    </head>
    <body>
    <div class="container">
    <h1>Bulk Upload Report</h1>
    <p>Total: {email_data['total']}</p>
    <p>Success: {email_data['success']}</p>
    <p>Failed: {email_data['failed']}</p>

    <h2>Error Details:</h2>
    <p>{str(email_data['errors'])}</p>
    </div>
    </body>
    </html>
    """

    # Create the MIME object
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Employee Bulk Upload Report"

    # Attach the HTML body
    html_part = MIMEText(html_body, "html")
    message.attach(html_part)

    # Establish a connection with the SMTP server
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
    print("Email Sent..")
