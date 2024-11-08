from PyPDF2 import PdfReader
import re

def extract_text_from_pdf(pdf_file):
    """Extract text content from a PDF file."""
    text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_certificate(pdf_file):
    """Extract text content from a certificate PDF file."""
    text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def verify_company_name(company_name):
    """Verify if the given company name is recognized."""
    # Example: List of recognized companies (replace with actual list or API call)
    recognized_companies = ["TVS", "Google", "Amazon"]
    
    # Check if the company name is in the recognized list
    return company_name in recognized_companies

def verify_name_in_text(name, extracted_text):
    """Verify if the given name is present in the extracted text."""
    name_lower = name.lower()
    extracted_text_lower = extracted_text.lower()
    return name_lower in extracted_text_lower
