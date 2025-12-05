import pdfplumber
import re

with pdfplumber.open("sample pdfs\sample_pdf_3.pdf") as pdf:
    first_page = pdf.pages[0]
    text = first_page.extract_text()

    print(text)

def extract_invoice(pdf_path: str) -> dict: