import json
import argparse
import sys
from pathlib import Path

from invoice_qc.extractor import extract_invoice_data_from_folder
from invoice_qc.validator import Invoice



# ----------------------------
# Utility Functions
# ----------------------------

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def print_summary(valid_count, invalid_count, errors_list=None):
    total = valid_count + invalid_count

    print("\n==== INVOICE SUMMARY ====")
    print(f"Total invoices: {total}")
    print(f"Valid invoices: {valid_count}")
    print(f"Invalid invoices: {invalid_count}")

    if errors_list:
        print("\nTop error types:")
        counts = {}
        for e in errors_list:
            counts[e] = counts.get(e, 0) + 1

        for err, cnt in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"  {err}: {cnt}")


# ----------------------------
# Extract
# ----------------------------

def run_extract(pdf_dir, output_json):
    extracted = extract_invoice_data_from_folder(pdf_dir)


    # Your extractor returns a list of raw invoice dicts
    # We store them as-is, no wrapper
    result = extracted

    save_json(output_json, result)
    print(f"Extraction complete → {output_json}")
    print(f"Total invoices processed: {len(result)}")


# ----------------------------
# Validate
# ----------------------------

def run_validate(input_json, report_path):
    invoices = load_json(input_json)

    report = []
    invalid_errors = []
    valid_count = 0
    invalid_count = 0

    for inv in invoices:
        filename = f"invoice_{inv.get('invoice_id')}"  # synthetic filename
        try:
            Invoice(**inv)
            report.append({"invoice_id": inv.get("invoice_id"), "valid": True})
            valid_count += 1
        except Exception as e:
            msg = str(e)
            report.append({"invoice_id": inv.get("invoice_id"), "valid": False, "error": msg})
            invalid_errors.append(msg)
            invalid_count += 1

    save_json(report_path, report)
    print_summary(valid_count, invalid_count, invalid_errors)

    if invalid_count > 0:
        sys.exit(1)
# ----------------------------
# Full run: Extract + Validate
# ----------------------------

def run_full(pdf_dir, report_path):
    temp_path = "_temp_extract.json"

    run_extract(pdf_dir, temp_path)
    run_validate(temp_path, report_path)

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


# ----------------------------
# CLI Entrypoint
# ----------------------------

def main():
    parser = argparse.ArgumentParser(description="Invoice QC CLI Tool")
    sub = parser.add_subparsers(dest="command")

    # extract
    cmd_extract = sub.add_parser("extract")
    cmd_extract.add_argument("--pdf-dir", required=True)
    cmd_extract.add_argument("--output", required=True)

    # validate
    cmd_validate = sub.add_parser("validate")
    cmd_validate.add_argument("--input", required=True)
    cmd_validate.add_argument("--report", required=True)

    # full-run
    cmd_full = sub.add_parser("full-run")
    cmd_full.add_argument("--pdf-dir", required=True)
    cmd_full.add_argument("--report", required=True)

    args = parser.parse_args()

    if args.command == "extract":
        run_extract(args.pdf_dir, args.output)

    elif args.command == "validate":
        run_validate(args.input, args.report)

    elif args.command == "full-run":
        run_full(args.pdf_dir, args.report)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
