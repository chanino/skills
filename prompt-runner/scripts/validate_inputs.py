#!/usr/bin/env python3
"""
validate_inputs.py — Pre-flight validation for prompt-runner workflows.

Checks data files, attachments, and dependencies before running a .prompt file.
Reports [OK], [WARN], or [FAIL] for each check.

Usage:
    python3 validate_inputs.py \
        --data <path> \
        --attachments <file1> <file2> \
        --output-format <text|json|docx> \
        --collect <strategy>
"""

import argparse
import csv
import json
import os
import shutil
import sys


def check_data_file(path: str) -> bool:
    """Validate data file exists and is parseable. Reports row count + columns."""
    if not path or path.lower() == "none":
        print("[OK]  No data file specified (single-prompt mode)")
        return True

    if not os.path.isfile(path):
        print(f"[FAIL] Data file not found: {path}")
        return False

    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".csv":
            with open(path, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                cols = reader.fieldnames or []
            print(f"[OK]  Data file: {path}")
            print(f"      Format: CSV | Rows: {len(rows)} | Columns: {', '.join(cols)}")
            return True

        elif ext in (".xlsx", ".xls"):
            try:
                import openpyxl
            except ImportError:
                print(f"[FAIL] openpyxl required for {ext} files. Install: pip install openpyxl")
                return False
            wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
            ws = wb.active
            rows_iter = ws.iter_rows()
            headers = [str(c.value) if c.value else f"col{i}" for i, c in enumerate(next(rows_iter))]
            row_count = sum(1 for _ in rows_iter)
            wb.close()
            print(f"[OK]  Data file: {path}")
            print(f"      Format: XLSX | Rows: {row_count} | Columns: {', '.join(headers)}")
            return True

        else:
            # Assume JSON
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                print(f"[FAIL] Data JSON must be an array, got {type(data).__name__}")
                return False
            # Peek at first item for fields
            fields = list(data[0].keys()) if data and isinstance(data[0], dict) else ["(scalar items)"]
            print(f"[OK]  Data file: {path}")
            print(f"      Format: JSON | Items: {len(data)} | Fields: {', '.join(fields)}")
            return True

    except Exception as e:
        print(f"[FAIL] Could not parse data file {path}: {e}")
        return False


def check_attachment(path: str) -> bool:
    """Validate an attachment file exists and is a supported type."""
    if not os.path.isfile(path):
        print(f"[FAIL] Attachment not found: {path}")
        return False

    ext = os.path.splitext(path)[1].lower()
    text_exts = {
        ".txt", ".md", ".csv", ".tsv", ".json", ".jsonl",
        ".xml", ".html", ".htm", ".yaml", ".yml", ".toml",
        ".py", ".js", ".ts", ".java", ".c", ".cpp", ".h",
        ".rs", ".go", ".rb", ".sh", ".bash", ".sql", ".r",
        ".cfg", ".ini", ".conf", ".log", ".prompt",
    }

    size_mb = os.path.getsize(path) / (1024 * 1024)

    if ext in text_exts:
        print(f"[OK]  Attachment: {path} ({ext}, {size_mb:.1f} MB)")
        return True

    if ext == ".pdf":
        if shutil.which("pdftotext"):
            print(f"[OK]  Attachment: {path} (PDF, {size_mb:.1f} MB, pdftotext available)")
        else:
            print(f"[WARN] Attachment: {path} (PDF, {size_mb:.1f} MB, pdftotext NOT found — text extraction may fail)")
        return True

    print(f"[WARN] Attachment: {path} ({ext}, {size_mb:.1f} MB) — binary file, may not embed correctly via CLI")
    return True


def check_dependencies(output_format: str, collect: str) -> bool:
    """Check required tools and libraries are available."""
    ok = True

    # Claude CLI
    if shutil.which("claude"):
        print("[OK]  claude CLI found in PATH")
    else:
        print("[FAIL] claude CLI not found in PATH")
        ok = False

    # python-docx (if docx output requested)
    if output_format == "docx":
        try:
            import docx  # noqa: F401
            print("[OK]  python-docx available")
        except ImportError:
            print("[FAIL] python-docx required for .docx output. Install: pip install python-docx")
            ok = False

    # pdftotext (advisory)
    if shutil.which("pdftotext"):
        print("[OK]  pdftotext available (PDF text extraction)")
    else:
        print("[WARN] pdftotext not found (PDF attachments will use fallback)")

    # openpyxl (advisory)
    try:
        import openpyxl  # noqa: F401
        print("[OK]  openpyxl available (XLSX support)")
    except ImportError:
        print("[WARN] openpyxl not installed (XLSX data files won't work)")

    return ok


def main():
    parser = argparse.ArgumentParser(description="Pre-flight validation for prompt-runner")
    parser.add_argument("--data", default=None, help="Path to data file")
    parser.add_argument("--attachments", nargs="*", default=[], help="Attachment file paths")
    parser.add_argument("--output-format", default="text", choices=["text", "json", "docx"],
                        help="Expected output format")
    parser.add_argument("--collect", default="append_json",
                        choices=["raw", "append_json", "concatenate", "per_item"],
                        help="Collection strategy")
    args = parser.parse_args()

    print("=" * 60)
    print("  prompt-runner pre-flight validation")
    print("=" * 60)
    print()

    failures = 0

    # 1. Data file
    if not check_data_file(args.data):
        failures += 1
    print()

    # 2. Attachments
    for att in args.attachments:
        if not check_attachment(att):
            failures += 1
    if args.attachments:
        print()

    # 3. Dependencies
    if not check_dependencies(args.output_format, args.collect):
        failures += 1
    print()

    # Summary
    print("=" * 60)
    if failures:
        print(f"  RESULT: {failures} check(s) FAILED — fix before running")
        print("=" * 60)
        sys.exit(1)
    else:
        print("  RESULT: All checks passed")
        print("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    main()
