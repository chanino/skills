"""
Helper for converting files using native Microsoft Office apps.
macOS: AppleScript via osascript
Windows: COM automation via pywin32

Usage:
    from office.msoffice import convert_to_pdf, convert_doc_to_docx

    convert_to_pdf("document.docx", "/tmp/output")
    convert_doc_to_docx("legacy.doc", "/tmp/output")
"""

import subprocess
import sys
from pathlib import Path

IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"

if IS_WINDOWS:
    try:
        import win32com.client
    except ImportError:
        win32com = None


def _convert_to_pdf_macos(input_path: Path, pdf_path: Path) -> None:
    script = f'''
    tell application "Microsoft Word"
        open POSIX file "{input_path}"
        set theDocument to active document
        save as theDocument file name "{pdf_path}" file format format PDF
        close theDocument saving no
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
            f"Word PDF conversion failed: {result.stderr.strip()}"
        )


def _convert_to_pdf_win32(input_path: Path, pdf_path: Path) -> None:
    if win32com is None:
        raise RuntimeError(
            "pywin32 is required for Office automation on Windows. "
            "Install it with: pip install pywin32"
        )

    app = win32com.client.Dispatch("Word.Application")
    app.Visible = False
    doc = None
    try:
        doc = app.Documents.Open(str(input_path))
        doc.SaveAs(str(pdf_path), FileFormat=17)  # wdFormatPDF = 17
    finally:
        if doc is not None:
            doc.Close(SaveChanges=False)


def convert_to_pdf(input_path: str, output_dir: str) -> Path:
    """Convert a DOCX file to PDF using Microsoft Word."""
    input_path = Path(input_path).resolve()
    output_dir = Path(output_dir).resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / f"{input_path.stem}.pdf"

    if IS_WINDOWS:
        _convert_to_pdf_win32(input_path, pdf_path)
    elif IS_MACOS:
        _convert_to_pdf_macos(input_path, pdf_path)
    else:
        raise RuntimeError(f"Unsupported platform: {sys.platform}")

    if not pdf_path.exists():
        raise RuntimeError(f"PDF not created at {pdf_path}")

    return pdf_path


def _convert_doc_to_docx_macos(input_path: Path, docx_path: Path) -> None:
    script = f'''
    tell application "Microsoft Word"
        open POSIX file "{input_path}"
        set theDocument to active document
        save as theDocument file name "{docx_path}" file format format document
        close theDocument saving no
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
            f"Word DOCX conversion failed: {result.stderr.strip()}"
        )


def _convert_doc_to_docx_win32(input_path: Path, docx_path: Path) -> None:
    if win32com is None:
        raise RuntimeError(
            "pywin32 is required for Office automation on Windows. "
            "Install it with: pip install pywin32"
        )

    app = win32com.client.Dispatch("Word.Application")
    app.Visible = False
    doc = None
    try:
        doc = app.Documents.Open(str(input_path))
        doc.SaveAs(str(docx_path), FileFormat=12)  # wdFormatDocumentDefault = 12
    finally:
        if doc is not None:
            doc.Close(SaveChanges=False)


def convert_doc_to_docx(input_path: str, output_dir: str) -> Path:
    """Convert a legacy .doc file to .docx using Microsoft Word."""
    input_path = Path(input_path).resolve()
    output_dir = Path(output_dir).resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    docx_path = output_dir / f"{input_path.stem}.docx"

    if IS_WINDOWS:
        _convert_doc_to_docx_win32(input_path, docx_path)
    elif IS_MACOS:
        _convert_doc_to_docx_macos(input_path, docx_path)
    else:
        raise RuntimeError(f"Unsupported platform: {sys.platform}")

    if not docx_path.exists():
        raise RuntimeError(f"DOCX not created at {docx_path}")

    return docx_path


def run_office_convert(input_path: str, output_dir: str, fmt: str = "pdf") -> Path:
    """Convert a file using the appropriate native Office app.

    Supports:
        pdf   - DOCX to PDF via Word
        docx  - DOC to DOCX via Word
    """
    if fmt == "pdf":
        return convert_to_pdf(input_path, output_dir)
    if fmt == "docx":
        return convert_doc_to_docx(input_path, output_dir)
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
