import fpdf

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
        self.set_font(size=12)
        for line in text.split('\n'):
            self.add_cell(0, 10, line, ln=1)
        temp_file_path = "app/data/generated_brief.pdf"
        self.pdf_generator.output(temp_file_path)
        return temp_file_path
