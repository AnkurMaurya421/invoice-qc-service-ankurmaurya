# invoice-qc-service-ankurmaurya
This is an assignment for the position of SDE Intern at DeepLogic AI.

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

## 🤖 11. AI Usage Notes

### The assignment explicitly allows AI tools.

Tools Used

ChatGPT

GitHub Copilot (minimal autocomplete)

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

This demonstrates thoughtful and responsible AI usage, not blind dependence.

## 🧠 12. Assumptions & Limitations
### Assumptions

PDFs follow similar structure

Totals appear in expected format

Currency defaults to EUR unless explicitly extracted

### Limitations

Regex extraction may fail for OCR-heavy or highly stylized invoices

Complex multi-page item tables not fully supported

Duplicate detection is simple (not fuzzy-matching names)

## 🎉 13. Final Notes

This project demonstrates:

End-to-end system thinking

Backend + CLI + Frontend integration

Ability to learn new frameworks quickly

Clean architecture & modular code


