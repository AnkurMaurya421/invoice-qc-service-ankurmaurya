#Import necessary libraries
import pdfplumber
import re
import json

#Lists of fields for invoice and line items
invoice_fields=["invoice_number", "reference_number", "invoice_date", "seller_name", "buyer_name", 
                "customer_number", "end_customer_number", "net_total","tax_percentage",
                "gross_total", "tax_amount", "currency"]

line_item_fields=["description", "item_number", "quantity", "price_per_unit", "line_total"]


#Mapping of invoice fields to their regex patterns in the PDF text using raw string notation and using re library for pattern matching
INVOICE_FIELD_PATTERNS ={
    "invoice_number": r"Bestellung\s*([A-Za-z0-9-]+)\s*",
    "reference_number": r"Auftrag von\s*([A-Za-z0-9-]+)\n",
    "invoice_date": r"vom\s*(\d{2,4}[./-]\d{2}[./-]\d{2,4})",
    "seller_name": r"\n([\D]+)\s+Bestellung",
    "buyer_name": r"\d+\s*(\D*)\s*[\d/\s]*\n\s*Endkundennummer",
    "customer_number": r"Unsere Kundennummer\s*.*\n\s*(\d+)",
    "end_customer_number": r"Endkundennummer\s*(?:\n\s*|\s+)(\d+)",
    "net_total": r"Gesamtwert EUR\s*([\d\.]+,\d{2})",
    "tax_percentage": r"MwSt\.\s*(\d{1,2},\d{2})%\s*EUR\s*(\d{1,3}(?:\.\d{3})*,\d{2})",
    "tax_amount": r"MwSt\.\s*\d{1,2},\d{2}%\s*EUR\s*(\d{1,3}(?:\.\d{3})*,\d{2})",
    "currency": r"\n([A-Z]{3})\s*in.*\n",
    "gross_total": r"Gesamtwert inkl\. MwSt\. EUR\s*([\d\.]+,\d{2})"
}


#Mapping of line item fields to their regex patterns in the PDF text
LINE_ITEM_PATTERN = {
    "description": r"\n\d+\s*(.+)\s*\d+\s*VE\s*\d+\s*VE",
    "item_number": r"Lief.Art.Nr:\s* ([A-Za-z0-9-]+).*\n",
    "quantity": r"\n\d+\s*.+\s*(\d)+\s*VE\s*\d+\s*VE",
    "price_per_unit": r"\s([\d,\.]+)\s*pro",
    "line_total": r"Stück\s*([\d,\.]+)\s*\n",
}


# Function to extract invoice data from a single PDF file
def extract_invoice_data_from_pdf(file_path,invoice_id):
    invoice_data = {}
    line_items = []
    invoice_data["invoice_id"]=invoice_id
    with pdfplumber.open(file_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"

        # Extract invoice level fields
        for field, pattern in INVOICE_FIELD_PATTERNS.items():
            match = re.search(pattern, full_text)
            if match:
                invoice_data[field] = match.group(1).strip()
            else:
                invoice_data[field] = None

        # Extract line items
        line_item_matches = re.finditer(r"(\n\d+\s*.+?\s*\d+\s*VE\s*\d+\s*VE.*?)(?=\n\d+\s*.+?\s*\d+\s*VE\s*\d+\s*VE|\Z)", full_text, re.DOTALL)
        for item_match in line_item_matches:
            item_text = item_match.group(1)
            line_item = {}
            for field, pattern in LINE_ITEM_PATTERN.items():
                match = re.search(pattern, item_text)
                if match:
                    line_item[field] = match.group(1).strip()
                else:
                    line_item[field] = None
            line_items.append(line_item)
        if line_items==[]:
            invoice_data["line_items"]=None

    invoice_data["line_items"] = line_items
    return invoice_data

# Function to extract invoice data from all PDF files in a folder by calling the single PDF extraction function
def extract_invoice_data_from_folder(folder_path):
    import os
    invoice_data_list = []
    id = 1

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            invoice_data = extract_invoice_data_from_pdf(file_path, id)
            invoice_data_list.append(invoice_data)
            id += 1

    return invoice_data_list   # <-- FIXED: return list, not JSON string


