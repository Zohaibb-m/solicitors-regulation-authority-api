import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
import requests
from app.utils.helper_functions import return_response

load_dotenv()
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

class EmailHandler:
    def __init__(self):
        self.email_template_firm = open("app/data/email_template_firm.html", "r").read()
        self.email_template_client = open("app/data/email_template_client.html", "r").read()
        self.login()

    def login(self):
        self.email_server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        self.email_server.login(SMTP_USERNAME, SMTP_PASSWORD)

    def send_email(self, client_name, firm_name, location, contact, legal_matter_type, to_email, pdf_url, user_type):
        if user_type == "firms":
            for firmname, firm_email in zip(firm_name, to_email):   
                return self.send_to_firm(client_name, firmname, location, contact, legal_matter_type, "lena@shakurova.io", pdf_url)
        else:
            return self.send_to_client(client_name, to_email, pdf_url)   
    
    def send_to_firm(self, client_name, firmname, location, contact, legal_matter_type, firm_email, pdf_url):
        email_content = self.email_template_firm.format(
                firm_name=firmname,
                client_name=client_name,
                location=location,
                contact=contact,
                matter_type=legal_matter_type
            )
        return self.attach_pdf_and_send(firm_email, email_content, "A Legal Enquiry Matching Your Expertise - Briefbase Introduction", pdf_url, client_name)
    
    def send_to_client(self, client_name, firm_email, pdf_url):
        email_content = self.email_template_client.format(
                client_name=client_name,
            )
        return self.attach_pdf_and_send(firm_email, email_content, "Your Brief is ready - Briefbase", pdf_url, client_name)
    
    def attach_pdf_and_send(self, firm_email, email_content, subject, pdf_url, client_name):
        msg = MIMEMultipart()
        msg['From'] = "<support@briefbase.ai>"
        msg['To'] = f"<{firm_email}>"
        msg['Subject'] = subject
        msg.attach(MIMEText(email_content, 'html')) 
        # Attach logo image
        with open("app/data/briefbase_logo.png", "rb") as img:
            logo = MIMEText(img.read(), 'base64', 'utf-8')
            logo.add_header('Content-Disposition', 'inline', filename="briefbase_logo.png")
            logo.add_header('Content-ID', '<logo_image>')
            msg.attach(logo)
        # Download the PDF and attach it
        try:
            response = requests.get(pdf_url)
            response.raise_for_status()
            pdf_attachment = MIMEText(response.content, 'base64', 'utf-8')
            pdf_attachment.add_header('Content-Disposition', 'attachment', filename=f"{client_name} Brief.pdf")
            pdf_attachment.add_header('Content-Type', 'application/pdf')
            msg.attach(pdf_attachment)
        except requests.RequestException as e:
            return return_response({"error": "Could not download the pdf."}, error=True)
        try:
            self.email_server.sendmail("support@briefbase.ai", firm_email, msg.as_string())
            return {"response": f"Email sent to {firm_email}"}
        except smtplib.SMTPServerDisconnected as e:
            try:
                self.login()
                self.email_server.sendmail("support@briefbase.ai", firm_email, msg.as_string())
                return return_response({"response": f"Email sent to {firm_email}"})
            except Exception as e:
                return return_response({"error": f"An error occured: {e}"},error=True)
