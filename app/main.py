from fastapi import FastAPI, UploadFile, File
from invoice_qc.validator import Invoice
from invoice_qc.extractor import extract_invoice_data_from_pdf
from typing import List
import tempfile
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Invoice QC Service",
    version="1.0.0",
    description="FastAPI backend for extracting & validating invoice data."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all origins
    allow_credentials=True,
    allow_methods=["*"],    # allow all HTTP methods
    allow_headers=["*"],    # allow all headers
)


# -----------------------------
# Health Check
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# -----------------------------
# Validate JSON Invoice List
# -----------------------------
@app.post("/validate-json")
def validate_json(invoices: List[dict]):
    result = []
    valid_count = 0
    invalid_count = 0
    errors = []

    for inv in invoices:
        invoice_id = inv.get("invoice_id", "unknown")
        try:
            Invoice(**inv)
            result.append({"invoice_id": invoice_id, "valid": True})
            valid_count += 1
        except Exception as e:
            msg = str(e)
            result.append({"invoice_id": invoice_id, "valid": False, "error": msg})
            errors.append(msg)
            invalid_count += 1

    summary = {
        "total": len(invoices),
        "valid": valid_count,
        "invalid": invalid_count,
        "errors": errors
    }

    return {
        "summary": summary,
        "results": result
    }

# -----------------------------
# Extract AND Validate PDFs
# -----------------------------
@app.post("/extract-and-validate-pdfs")
async def extract_and_validate_pdfs(files: List[UploadFile] = File(...)):
    all_extracted = []
    results = []
    valid_count = 0
    invalid_count = 0
    errors = []

    for uploaded in files:
        # Save PDF temporarily
        suffix = os.path.splitext(uploaded.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await uploaded.read())
            tmp_path = tmp.name

        # Extract from a single PDF (your function)
        extracted = extract_invoice_data_from_pdf(tmp_path, invoice_id=1)
        all_extracted.append(extracted)

        # Validate extracted data
        try:
            Invoice(**extracted)
            results.append({"filename": uploaded.filename, "valid": True})
            valid_count += 1
        except Exception as e:
            msg = str(e)
            results.append({"filename": uploaded.filename, "valid": False, "error": msg})
            invalid_count += 1
            errors.append(msg)

        # Cleanup temp file
        os.remove(tmp_path)

    summary = {
        "total_pdfs": len(files),
        "valid": valid_count,
        "invalid": invalid_count,
        "errors": errors
    }

    return {
        "summary": summary,
        "extracted_data": all_extracted,
        "validation_results": results
    }
