"""Accept all tracked changes in a DOCX file using Microsoft Word.

macOS: AppleScript via osascript
Windows: COM automation via pywin32
"""

import argparse
import shutil
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


def _accept_changes_macos(abs_output: str) -> tuple[None, str | None]:
    script = f'''
    tell application "Microsoft Word"
        activate
        open POSIX file "{abs_output}"
        delay 1
        set theDocument to active document
        accept all revisions of theDocument
        save theDocument
        close theDocument saving no
    end tell
    '''

    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return None, "Error: Word timed out accepting changes"

    if result.returncode != 0:
        return None, f"Error: Word failed: {result.stderr.strip()}"

    return None, None


def _accept_changes_win32(abs_output: str) -> tuple[None, str | None]:
    if win32com is None:
        return None, (
            "Error: pywin32 is required for Office automation on Windows. "
            "Install it with: pip install pywin32"
        )

    app = win32com.client.Dispatch("Word.Application")
    app.Visible = False
    doc = None
    try:
        doc = app.Documents.Open(abs_output)
        doc.Revisions.AcceptAll()
        doc.Save()
    except Exception as e:
        return None, f"Error: Word failed: {e}"
    finally:
        if doc is not None:
            doc.Close(SaveChanges=False)

    return None, None


def accept_changes(
    input_file: str,
    output_file: str,
) -> tuple[None, str]:
    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.exists():
        return None, f"Error: Input file not found: {input_file}"

    if not input_path.suffix.lower() == ".docx":
        return None, f"Error: Input file is not a DOCX file: {input_file}"

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(input_path, output_path)
    except Exception as e:
        return None, f"Error: Failed to copy input file to output location: {e}"

    abs_output = str(output_path.resolve())

    if IS_WINDOWS:
        _, error = _accept_changes_win32(abs_output)
    elif IS_MACOS:
        _, error = _accept_changes_macos(abs_output)
    else:
        return None, f"Error: Unsupported platform: {sys.platform}"

    if error is not None:
        return None, f"{error}: {input_file}"

    return (
        None,
        f"Successfully accepted all tracked changes: {input_file} -> {output_file}",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Accept all tracked changes in a DOCX file"
    )
    parser.add_argument("input_file", help="Input DOCX file with tracked changes")
    parser.add_argument(
        "output_file", help="Output DOCX file (clean, no tracked changes)"
    )
    args = parser.parse_args()

    _, message = accept_changes(args.input_file, args.output_file)
    print(message)

    if "Error" in message:
        raise SystemExit(1)
