# Call the PdfGenerator class to create a PDF and save it to the Supabase bucket
from app.utils.pdf_generator import PDFGenerator
import dotenv
import vercel_blob
import datetime
from app.utils.helper_functions import return_response

dotenv.load_dotenv()

class PDFSaver:
    def __init__(self):
        self.pdf_generator = PDFGenerator()

    def save_pdf(self, text):
        pdf_path = self.pdf_generator.generate_pdf(text)
        return pdf_path
    
    def upload_to_blob(self, text, client_name):
        pdf_path = self.save_pdf(text)
        try:
            response = vercel_blob.put(f"{client_name}_{datetime.datetime.now()}_brief.pdf", open(pdf_path, "rb").read(), verbose=True)
            return return_response({"pdf_url": response["downloadUrl"]})
        except Exception as e:
            return return_response({"error": f"Error uploading PDF: {e}"}, error=True)
        