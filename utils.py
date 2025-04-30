
import pdfkit
from datetime import datetime

def generuj_numer_rachunku(id):
    rok = datetime.now().year
    return f"AGD-{rok}-{id:04d}"

def generuj_pdf(html_path, pdf_path):
    try:
        pdfkit.from_file(html_path, pdf_path)
        return True
    except Exception as e:
        print(f"Błąd PDF: {e}")
        return False
