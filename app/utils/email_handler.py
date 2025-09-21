import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from dotenv import load_dotenv
import os
import requests

load_dotenv()
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

class EmailHandler:
    def __init__(self):
        self.email_server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        self.email_server.login(SMTP_USERNAME, SMTP_PASSWORD)
        self.email_template = open("app/data/email_template_firm.html", "r").read()

    def send_email(self, client_name, firm_name, location, contact, legal_matter_type, to_email, pdf_url, user_type):
        if user_type == "firms":
            for firmname, firm_email in zip(firm_name, to_email):   
                self.send(client_name, firmname, location, contact, legal_matter_type, firm_email, pdf_url)
        else:
            self.send(client_name, firm_name, location, contact, legal_matter_type, to_email, pdf_url)   
    
    def send(self, client_name, firmname, location, contact, legal_matter_type, firm_email, pdf_url):
        email_content = self.email_template.format(
                firm_name=firmname,
                client_name=client_name,
                location=location,
                contact=contact,
                matter_type=legal_matter_type
            )
        msg = MIMEMultipart()
        msg['From'] = "<support@briefbase.ai>"
        msg['To'] = f"<{firm_email}>"
        msg['Subject'] = "A Legal Enquiry Matching Your Expertise - Briefbase Introduction"
        msg.attach(MIMEText(email_content, 'html')) 
        # Download the PDF and attach it
        try:
            response = requests.get(pdf_url)
            response.raise_for_status()
            pdf_attachment = MIMEText(response.content, 'base64', 'utf-8')
            pdf_attachment.add_header('Content-Disposition', 'attachment', filename=f"{client_name} Brief.pdf")
            pdf_attachment.add_header('Content-Type', 'application/pdf')
            msg.attach(pdf_attachment)
            self.email_server.sendmail("support@briefbase.ai", firm_email, msg.as_string())
            print(f"Email sent to {firm_email}")
        except requests.RequestException as e:
            print(f"Failed to send email: {e}")
            return