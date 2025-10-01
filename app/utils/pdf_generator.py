import fpdf
import os
from dotenv import load_dotenv
from app.utils.helper_functions import return_response

load_dotenv()

class PDFGenerator:
    def __init__(self):
        self.pdf_generator = fpdf.FPDF()
        self.pdf_generator.set_auto_page_break(auto=True, margin=15)

    def add_page(self):
        self.pdf_generator.add_page()

    def set_font(self, family='Arial', style='', size=12):
        self.pdf_generator.set_font(family, style, size)

    def add_cell(self, w, h, txt, border=0, ln=0, align='', fill=False):
        self.pdf_generator.cell(w, h, txt, border, ln, align, fill)

    def generate_pdf(self, text):
        self.add_page()
        # There are 3 types of line starters: # for headers, ** for bold, and normal text
        self.set_font(size=12)
        lines = text.split('\n\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                self.set_font(size=16, style='B')
                self.add_cell(0, 10, line[2:], ln=1, align='C')
                self.set_font(size=12)
            elif line.startswith('**') and line.endswith('**'):
                self.set_font(size=12, style='B')
                self.add_cell(0, 10, line[2:-2], ln=1, align='L')
                self.set_font(size=12)
            else:
                paras = []
                temp_para = ""
                for word in line.split():
                    if self.pdf_generator.get_string_width(temp_para) + len(word) < 180:
                        temp_para += word + " "
                    else:
                        paras.append(temp_para.strip())
                        temp_para = word + " "
                if temp_para:
                    paras.append(temp_para.strip())
                for para in paras:
                    self.add_cell(0, 10, para, ln=1, align='L')
        temp_file_path = os.getenv("PDF_SAVE_PATH")
        self.pdf_generator.output(temp_file_path)
        return temp_file_path
