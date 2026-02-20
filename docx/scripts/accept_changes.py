"""Accept all tracked changes in a DOCX file using Microsoft Word via AppleScript.

Requires Microsoft Word (macOS).
"""

import argparse
import shutil
import subprocess
from pathlib import Path


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

    script = f'''
    tell application "Microsoft Word"
        open POSIX file "{abs_output}"
        set theDocument to active document
        accept all revisions theDocument
        save theDocument
        close theDocument
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
        return (
            None,
            f"Error: Word timed out accepting changes: {input_file}",
        )

    if result.returncode != 0:
        return None, f"Error: Word failed: {result.stderr.strip()}"

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
