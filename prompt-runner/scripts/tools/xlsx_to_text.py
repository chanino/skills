#!/usr/bin/env python3
"""
xlsx_to_text.py — Convert XLSX spreadsheets to human-readable pipe-delimited text.

Standalone utility (separate from run_claude.py).
Requires: pandas, openpyxl

Usage:
    python xlsx_to_text.py data.xlsx
    python xlsx_to_text.py data.xlsx --head 20
    python xlsx_to_text.py data.xlsx --sheets "Sheet1,Sheet2"
"""

import argparse
import sys
import unicodedata
import re

try:
    import pandas as pd
except ImportError:
    print("Error: pandas is required. Install with: pip install pandas openpyxl", file=sys.stderr)
    sys.exit(1)


def clean_text(text: str) -> str:
    """Normalize unicode and collapse whitespace."""
    if not isinstance(text, str):
        return str(text) if text is not None else ""
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def xlsx_to_text(path: str, sheet_names: list[str] | None = None,
                 head: int | None = None) -> str:
    """Convert XLSX to pipe-delimited text output."""
    xls = pd.ExcelFile(path, engine="openpyxl")
    sheets = sheet_names if sheet_names else xls.sheet_names

    sections = []
    for sheet in sheets:
        if sheet not in xls.sheet_names:
            sections.append(f"=== Sheet: {sheet} (NOT FOUND) ===\n")
            continue

        df = pd.read_excel(xls, sheet_name=sheet)
        if head:
            df = df.head(head)

        # Clean all string cells
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].apply(clean_text)

        header = " | ".join(str(c) for c in df.columns)
        sep = "-" * len(header)
        rows = []
        for _, row in df.iterrows():
            rows.append(" | ".join(clean_text(str(v)) for v in row.values))

        section = f"=== Sheet: {sheet} ({len(df)} rows) ===\n"
        section += header + "\n" + sep + "\n"
        section += "\n".join(rows)
        sections.append(section)

    return "\n\n".join(sections)


def main():
    parser = argparse.ArgumentParser(description="Convert XLSX to readable text")
    parser.add_argument("file", help="Path to .xlsx file")
    parser.add_argument("--head", type=int, default=None,
                        help="Only show first N rows per sheet")
    parser.add_argument("--sheets", type=str, default=None,
                        help="Comma-separated sheet names to include")
    args = parser.parse_args()

    sheet_list = [s.strip() for s in args.sheets.split(",")] if args.sheets else None
    print(xlsx_to_text(args.file, sheet_names=sheet_list, head=args.head))


if __name__ == "__main__":
    main()
