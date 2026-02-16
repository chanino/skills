# Canonical version maintained in gemini-image skill.
# This is a local copy for pptx-diagram self-containment.

import mimetypes
import os
import argparse
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables from .env file
load_dotenv()

DEFAULT_PROMPT = "Provide a textual description of the attached image so that a visually impaired person has the exact same information as non-visually impaired person who can review the graphic themselves."

# Magic bytes for detecting image MIME type from binary data
MAGIC_BYTES = {
    b"\x89PNG": "image/png",
    b"\xff\xd8\xff": "image/jpeg",
    b"GIF8": "image/gif",
    b"RIFF": "image/webp",  # WebP starts with RIFF
}

# File extension to MIME type mapping
EXT_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
}


def detect_mime_from_bytes(data):
    """Detect MIME type from magic bytes at start of data."""
    for magic, mime in MAGIC_BYTES.items():
        if data[:len(magic)] == magic:
            return mime
    return "image/png"  # fallback


def detect_mime_from_path(path):
    """Detect MIME type from file extension."""
    ext = os.path.splitext(path)[1].lower()
    return EXT_MIME.get(ext, "image/png")


def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)
    print(f"File saved to: {file_name}", file=sys.stderr)


def image_to_text(image_data, mime_type, prompt, model_id, output_path, api_key=None):
    """Sends an image to Gemini and returns the text response."""

    if api_key:
        client = genai.Client(api_key=api_key)
    else:
        client = genai.Client()

    if output_path != "-":
        print(f"Analyzing image ({mime_type}) using model: '{model_id}'...", file=sys.stderr)

    try:
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(
                        mime_type=mime_type,
                        data=image_data,
                    ),
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]
        tools = [
            types.Tool(googleSearch=types.GoogleSearch()),
        ]
        generate_content_config = types.GenerateContentConfig(
            image_config=types.ImageConfig(
                aspect_ratio="16:9",
                image_size="1K",
            ),
            response_modalities=[
                "IMAGE",
                "TEXT",
            ],
            tools=tools,
        )

        text_parts = []
        file_index = 0
        for chunk in client.models.generate_content_stream(
            model=model_id,
            contents=contents,
            config=generate_content_config,
        ):
            if chunk.parts is None:
                continue
            if chunk.parts[0].inline_data and chunk.parts[0].inline_data.data:
                inline_data = chunk.parts[0].inline_data
                data_buffer = inline_data.data
                file_extension = mimetypes.guess_extension(inline_data.mime_type)
                if output_path and output_path != "-":
                    base = os.path.splitext(output_path)[0]
                    file_name = f"{base}_image_{file_index}{file_extension}"
                else:
                    file_name = f"output_image_{file_index}{file_extension}"
                save_binary_file(file_name, data_buffer)
                file_index += 1
            else:
                text_parts.append(chunk.text)

        if not text_parts:
            print("Error: No text was returned by the model.", file=sys.stderr)
            return None

        return "".join(text_parts)

    except Exception as e:
        print(f"Error during image analysis: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description="Describe an image using Gemini (Gemini 3 Pro).")
    parser.add_argument("prompt", type=str, nargs="?", default=DEFAULT_PROMPT,
                        help="Text prompt to guide the description.")
    parser.add_argument("-i", "--input", type=str, default=None,
                        help="Input image file path. Use '-' for stdin. If omitted, reads from stdin.")
    parser.add_argument("-o", "--output", type=str, default="-",
                        help="Output file path. Default: stdout. Use '-' for stdout.")
    parser.add_argument("--model", type=str, default="gemini-3-pro-image-preview", help="The model ID to use.")
    parser.add_argument("--api-key", type=str, help="Your Google AI Studio API Key.")

    args = parser.parse_args()

    # Read image data
    if args.input and args.input != "-":
        # Read from file
        if not os.path.isfile(args.input):
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        with open(args.input, "rb") as f:
            image_data = f.read()
        mime_type = detect_mime_from_path(args.input)
    else:
        # Read from stdin
        if args.input != "-" and sys.stdin.isatty():
            print("Error: No input image. Use -i FILE or pipe image data via stdin.", file=sys.stderr)
            sys.exit(1)
        image_data = sys.stdin.buffer.read()
        if not image_data:
            print("Error: No image data received from stdin.", file=sys.stderr)
            sys.exit(1)
        mime_type = detect_mime_from_bytes(image_data)

    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: No API key found. Set GEMINI_API_KEY in .env or pass --api-key.", file=sys.stderr)
        sys.exit(1)

    result = image_to_text(image_data, mime_type, args.prompt, args.model, args.output, api_key)
    if result is None:
        sys.exit(1)

    # Write output
    if args.output == "-":
        sys.stdout.write(result)
        if not result.endswith("\n"):
            sys.stdout.write("\n")
    else:
        with open(args.output, "w") as f:
            f.write(result)
        print(f"Description saved to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
