# notifier.py
import smtplib
import logging
from email.message import EmailMessage
from config import BASE_URL

class Notifier:
    def __init__(self, smtp_server, smtp_port, sender_email, email_password, receiver_email):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.email_password = email_password
        self.receiver_email = receiver_email

    def send_notification(self, plate_number, tin_number, fine_amount, fine_details_html):
        """Formats and sends an email notification about a new traffic fine."""
        logging.info(f"Preparing to send email notification to {self.receiver_email}...")
        
        subject = f"URGENT: New Traffic Fine Issued for Plate {plate_number}"
        body = self._create_email_body(plate_number, tin_number, fine_amount, fine_details_html)
        
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = self.receiver_email
        msg.set_content("A new traffic fine has been issued. Please view this email in an HTML-compatible client to see details.")
        msg.add_alternative(body, subtype='html')

        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender_email, self.email_password)
                server.send_message(msg)
            logging.info("Email sent successfully!")
        except Exception as e:
            logging.error(f"Failed to send email: {e}")

    def _create_email_body(self, plate_number, tin_number, fine_amount, fine_details_html):
        """Creates the HTML content for the email."""
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: sans-serif; }}
                .container {{ border: 1px solid #ddd; padding: 20px; border-radius: 5px; max-width: 700px; }}
                .header {{ font-size: 24px; color: #d9534f; }}
                .total {{ font-size: 18px; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="header">Traffic Fine Alert</h1>
                <p>A new traffic fine has been detected for vehicle with:</p>
                <ul>
                    <li><strong>Plate Number:</strong> {plate_number}</li>
                    <li><strong>TIN Number:</strong> {tin_number}</li>
                </ul>
                <p class="total">Total Amount Due: {fine_amount} FRW</p>
                <hr>
                <h3>Fine Details:</h3>
                {fine_details_html}
                <p>Please visit the official website to verify and pay the fine: <a href="{BASE_URL}">{BASE_URL}</a></p>
            </div>
        </body>
        </html>
        """