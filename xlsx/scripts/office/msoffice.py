"""
Helper for converting files using native Microsoft Office apps on macOS
via AppleScript. Replaces the LibreOffice (soffice) shim for local use.

Usage:
    from office.msoffice import convert_to_pdf

    convert_to_pdf("spreadsheet.xlsx", "/tmp/output")
"""

import subprocess
import sys
from pathlib import Path


def convert_to_pdf(input_path: str, output_dir: str) -> Path:
    """Convert an XLSX file to PDF using Microsoft Excel via AppleScript."""
    input_path = Path(input_path).resolve()
    output_dir = Path(output_dir).resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / f"{input_path.stem}.pdf"

    script = f'''
    tell application "Microsoft Excel"
        open POSIX file "{input_path}"
        set theWorkbook to active workbook
        save theWorkbook in POSIX file "{pdf_path}" as PDF file format
        close theWorkbook saving no
    end tell
    '''

    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
        timeout=60,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Excel PDF conversion failed: {result.stderr.strip()}"
        )

    if not pdf_path.exists():
        raise RuntimeError(f"PDF not created at {pdf_path}")

    return pdf_path


def run_office_convert(input_path: str, output_dir: str, fmt: str = "pdf") -> Path:
    """Convert a file using the appropriate native Office app.

    Supports:
        pdf  - XLSX to PDF via Excel
    """
    if fmt == "pdf":
        return convert_to_pdf(input_path, output_dir)
    raise ValueError(f"Unsupported format: {fmt}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert files using native Office apps")
    parser.add_argument("input", help="Input file path")
    parser.add_argument("--convert-to", default="pdf", help="Output format (default: pdf)")
    parser.add_argument("--outdir", default=".", help="Output directory")
    args = parser.parse_args()

    try:
        result = run_office_convert(args.input, args.outdir, args.convert_to)
        print(f"Converted: {result}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
