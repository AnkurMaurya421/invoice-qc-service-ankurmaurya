# invoice-qc-service-ankurmaurya

A complete Invoice Quality Check (QC) system that can:

Extract structured data from PDFs

Validate invoices against business rules

Run via CLI

Expose a FastAPI backend

Provide a small internal Invoice QC Console UI

This project fulfills all required parts (A–D) and the bonus (Part E).


## 1. What I Built

A modular, production-like QC system:

PDF → JSON extraction module

Pydantic validation core

CLI tools (extract / validate / full-run)

FastAPI backend

Minimal frontend UI (HTML + CSS + JS)



## 🧩 2. Schema & Validation Design

### Invoice Fields

| Field               | Description                  |
| ------------------- | ---------------------------- |
| invoice_id          | Internal ID assigned per PDF |
| invoice_number      | Seller invoice number        |
| reference_number    | Buyer reference/order number |
| invoice_date        | Date in flexible formats     |
| seller_name         | Invoice issuer               |
| buyer_name          | Invoice recipient            |
| customer_number     | Seller customer number       |
| end_customer_number | Buyer customer number        |
| net_total           | Subtotal                     |
| tax_percentage      | VAT percentage               |
| tax_amount          | VAT amount                   |
| gross_total         | Final amount                 |
| currency            | Currency code (EUR, etc.)    |
| line_items          | List of LineItem entries     |

### Line Item Fields

| Field          | Description          |
| -------------- | -------------------- |
| description    | Product description  |
| item_number    | SKU / Article number |
| quantity       | Units                |
| price_per_unit | Unit price           |
| line_total     | quantity × price     |

## 3. Validation Rules (with rationale)
### ✔ Required Fields

Ensures critical fields are present (invoice number, seller, buyer, totals, etc.).

### ✔ Date Validation

Accepts multiple formats:

DD.MM.YYYY

YYYY-MM-DD

DD/MM/YYYY

etc.

Also checks year bounds (2000 → next year).

### ✔ Number Parsing

Handles EU numeric formats such as:

1.234,56

64,00

### ✔ Business Rules

| Rule                                 | Rationale                     |
| ------------------------------------ | ----------------------------- |
| net_total = sum(line_total)          | Ensures totals are consistent |
| gross_total = net_total + tax_amount | Financial correctness         |
| quantity × price = line_total        | Prevents extraction errors    |
| No negative amounts                  | Data integrity                |
| Duplicate invoices flagged           | Prevent duplicate ingestion   |

## 4. Architecture
### Extraction Pipeline
The extraction module reads PDF files using pdfplumber, converts each page to plain text, and applies a set of regex patterns to extract structured fields such as invoice numbers, dates, totals, customer information, and line items.
Line items are identified as repeating text blocks and parsed individually.

The output is a clean Python dictionary representing one invoice
### Validation Core
The validation layer is built using Pydantic models.
Each field is type-checked, normalized (especially dates and EU-style numbers), and validated using per-field and cross-field rules.
Business rules enforce consistency:

**net_total = sum(line_totals)**

**gross_total = net_total + tax_amount**

**line_total = quantity × price**

required field checks

duplicate invoice detection

Validation returns structured error messages and an overall pass/fail flag.

### CLI
The CLI (built with argparse) provides three main commands:

**extract → PDF folder → JSON file**

**validate → JSON file → validation report**

**full-run → extract + validate in a single command**

The CLI produces a summary showing counts of valid/invalid invoices and top error types.

### API
A **FastAPI** backend exposes three endpoints:

**GET /health** → health check

**POST /validate-json** → validate a list of invoice JSON objects

**POST /extract-and-validate-pdfs** → upload PDFs, extract data, validate them, and return results

**CORS** is enabled so the frontend can call the API directly.

### Frontend

A lightweight HTML/CSS/JavaScript UI that allows users to:

Upload one or more PDFs

Paste JSON directly

Send data to the backend for extraction and validation

View invoice results in a table with status badges

Filter to show only invalid invoices

<img width="536" height="617" alt="image" src="https://github.com/user-attachments/assets/1a95393c-c056-4ff8-b092-090faf8cd81d" />

## 5. System Flow Diagram
<img width="498" height="634" alt="image" src="https://github.com/user-attachments/assets/f08a4d80-0bb0-451d-870f-3bda0b95e8cb" />



## ⚙️ 6. Setup & Installation
Python Version
```
Python 3.11+
```
Create Virtual Environment
```
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```
Install Requirements
```
pip install -r requirements.txt
```
## 🖥️ 7. Running the CLI
### Extract PDFs
```
python -m invoice_qc.cli extract --pdf-dir samples --output extracted.json
```

### Validate a JSON File
```
python -m invoice_qc.cli validate --input extracted.json --report report.json
```

### Full Run (Extract + Validate)
```
python -m invoice_qc.cli full-run --pdf-dir samples --report report.json
```

## 🌐 8. Running the API
Start Server
```
uvicorn app.main:app --reload
```

### API Endpoints
| Method | Endpoint                     | Description                       |
| ------ | ---------------------------- | --------------------------------- |
| GET    | `/health`                    | Check server status               |
| POST   | `/validate-json`             | Validate invoice JSON             |
| POST   | `/extract-and-validate-pdfs` | Upload PDFs to extract + validate |

## 📡 9. API Example Requests
### Validate JSON
```
curl -X POST http://127.0.0.1:8000/validate-json \
  -H "Content-Type: application/json" \
  -d '[{"invoice_id":1,"invoice_number":"A123", ...}]'
```
### Extract + Validate PDFs
```
curl -X POST http://127.0.0.1:8000/extract-and-validate-pdfs \
  -F "files=@invoice1.pdf" \
  -F "files=@invoice2.pdf"
```

## 🖥️ 10. Frontend (Invoice QC Console)

### Open:
```
frontend/index.html
```


#### Features:

Upload multiple PDFs

Paste raw JSON for validation

Shows table of results

Badges for valid/invalid

“Show only invalid invoices” filter

## Integration Into a Larger System

This service is designed to plug into broader document-processing pipelines:

API Integration: Upstream services can call `/extract-and-validate-pdfs` or `/validate-json` immediately after parsing documents, receiving structured QC results .

Dashboard Integration: Validation results can be pushed into a database or monitoring tool for operations teams

## 🤖 11. AI Usage Notes

### The assignment explicitly allows AI tools.

Tools Used

ChatGPT

Used For

Understanding FastAPI and Pydantic concepts

Regex refinement ideas

Boilerplate scaffolding for routes and CLI

Debugging hints (CORS, validator behavior)

### Example Where AI Was Wrong

AI suggested returning JSON strings from the extractor:

return json.dumps(invoice_data_list)


This caused FastAPI to hang (string instead of list).

My Fix:

return invoice_data_list


AI also suggested unnecessary regex inside date validators, which I corrected by implementing custom parsing logic.

### Summary

AI accelerated learning, but I:

Wrote the final code myself

Debugged issues manually

Understood every component

Corrected multiple AI mistakes



## 🧠 12. Assumptions & Limitations
### Assumptions

PDFs follow similar structure

Totals appear in expected format

Currency defaults to EUR unless explicitly extracted

### Limitations

Regex extraction may fail for highly stylized invoices


## 🎉 13. Final Notes

This project demonstrates:

End-to-end system thinking

Backend + CLI + Frontend integration

Ability to learn new frameworks quickly

Clean architecture & modular code


