# invoice_qc/validator.py

from pydantic import BaseModel, field_validator, ValidationError
from typing import List, Optional, Dict, Any
from datetime import datetime
from collections import Counter

#Convert EU numbers to float safely
def parse_number(value):
    if value is None:
        return None
    if isinstance(value, (float, int)):
        return float(value)
    return float(value.replace(".", "").replace(",", "."))



# Line Item model
class LineItem(BaseModel):
    description: Optional[str]
    item_number: Optional[str]
    quantity: Optional[str]
    price_per_unit: Optional[str]
    line_total: Optional[str]

    # Convert numeric fields
    @field_validator("quantity", "price_per_unit", "line_total")
    def convert_numbers(cls, v, info):
        return parse_number(v)

    # Business rule: qty × price = line_total
    @field_validator("line_total", mode="after")
    def validate_line_total(cls, v, info):
        data = info.data  # contains quantity, price_per_unit etc.
        qty = data.get("quantity")
        ppu = data.get("price_per_unit")

        if qty is None or ppu is None or v is None:
            raise ValueError("quantity or price_per_unit or line_total is Missing")
            
        expected = round(qty * ppu, 2)
        if round(v, 2) != expected:
            raise ValueError(f"line_total_mismatch: expected {expected}, got {v}")

        return v



# Invoice model
class Invoice(BaseModel):
    invoice_id: Optional[int]
    invoice_number: Optional[str]
    reference_number: Optional[str]
    invoice_date: Optional[str]
    seller_name: Optional[str]
    buyer_name: Optional[str]
    customer_number: Optional[str]
    end_customer_number: Optional[str]
    net_total: Optional[str]
    tax_percentage: Optional[str]
    tax_amount: Optional[str]
    currency: Optional[str] = "EUR"
    gross_total: Optional[str]
    line_items: Optional[List[LineItem]]

    #REQUIRED FIELDS
    @field_validator("invoice_number", "seller_name", "buyer_name", "invoice_date","net_total","gross_total")
    def check_required_fields(cls, v, info):
        if v is None or str(v).strip() == "":
            raise ValueError(f"missing_field: {info.field_name}")
        return v

    @field_validator("line_items")
    def check_line_items_not_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError("missing_field: there should be at least one line item")
        return v

    #DATE VALIDATION
    @field_validator("invoice_date")
    def validate_date_format(cls, v):
        if not v:
            raise ValueError("invalid_invoice_date_format")

        v = v.strip()

        # Detect separator
        sep = None
        for s in (".", "-", "/"):
            if s in v:
                sep = s
                break

        if sep is None:
            raise ValueError("invalid_invoice_date_format")

        parts = v.split(sep)
        if len(parts) != 3:
            raise ValueError("invalid_invoice_date_format")

        p1, p2, p3 = parts

        # Decide format
        # If first part has 4 digits → assume YYYY-MM-DD
        try:
            if len(p1) == 4:
                fmt = f"%Y{sep}%m{sep}%d"
            else:
                fmt = f"%d{sep}%m{sep}%Y"

            dt = datetime.strptime(v, fmt)

            # Validate year range
            if dt.year < 2000 or dt.year > (datetime.now().year + 1):
                raise ValueError("invalid_invoice_date_range")

        except Exception:
            raise ValueError("invalid_invoice_date_format")

        return v


    #NUMERIC CONVERSION
    @field_validator("net_total", "tax_amount", "gross_total", "tax_percentage")
    def convert_totals(cls, v, info):
        return parse_number(v)

    #BUSINESS LOGIC RULES
    # net_total = sum(line_totals)
    @field_validator("net_total", mode="after")
    def validate_net_total(cls, net_total, info):
        data = info.data  # all validated invoice fields
        items = data.get("line_items")

        if net_total is None or not items:
            return net_total

        calculated = round(sum(i.line_total for i in items if i.line_total is not None), 2)

        if round(net_total, 2) != calculated:
            raise ValueError(f"net_total_mismatch: expected {calculated}, got {net_total}")

        return net_total

    # gross_total = net_total + tax_amount
    @field_validator("gross_total", mode="after")
    def validate_gross_total(cls, gross_total, info):
        data = info.data
        net = data.get("net_total")
        tax = data.get("tax_amount")

        if None in (gross_total, net, tax):
            return gross_total

        expected = round(net + tax, 2)
        if round(gross_total, 2) != expected:
            raise ValueError(f"gross_total_mismatch: expected {expected}, got {gross_total}")

        return gross_total
    
    # amounts should be positive
    @field_validator("net_total", "tax_amount", "gross_total")
    def validate_positive_amounts(cls, v, info):
        if v is not None and v < 0:
            raise ValueError(f"negative_amount: {info.field_name} is negative")
        return v
    #currency check
    @field_validator("currency")
    def validate_currency(cls, v):
        allowed_currencies = {"EUR", "USD", "GBP", "INR", "JPY", "AUD", "CAD", "CHF", "CNY"}
        if v not in allowed_currencies:
            raise ValueError("invalid_currency")
        return v
    




# Batch Validator (Part C)
def validate_invoices(invoices_json: List[Dict[str, Any]]):
    results = []
    error_counter = Counter()

    # ---------------------- FIRST PASS ----------------------
    for invoice in invoices_json:
        invoice_id = invoice.get("invoice_id", "unknown")

        try:
            Invoice(**invoice)
            results.append({
                "invoice_id": invoice_id,
                "is_valid": True,
                "errors": []
            })
        except ValidationError as e:
            errors = [err["msg"] for err in e.errors()]
            for msg in errors:
                error_counter[msg] += 1

            results.append({
                "invoice_id": invoice_id,
                "is_valid": False,
                "errors": errors
            })

    #DUPLICATE DETECTION
    seen = {}
    for index, invoice in enumerate(invoices_json):
        key = (invoice.get("seller_name"), invoice.get("invoice_number"), invoice.get("invoice_date"))

        if None in key:
            continue

        if key in seen:
            msg = "duplicate_invoice"
            error_counter[msg] += 1

            # previous invoice
            prev_index = seen[key]
            results[prev_index]["is_valid"] = False
            if msg not in results[prev_index]["errors"]:
                results[prev_index]["errors"].append(msg)

            # current invoice
            results[index]["is_valid"] = False
            results[index]["errors"].append(msg)

        else:
            seen[key] = index

    #SUMMARY OBJECT
    total = len(results)
    valid = sum(result["is_valid"] for result in results)
    invalid = total - valid

    summary = {
        "total_invoices": total,
        "valid_invoices": valid,
        "invalid_invoices": invalid,
        "error_counts": dict(error_counter)
    }

    return {

        "invoices": results,
        "summary": summary
    }
