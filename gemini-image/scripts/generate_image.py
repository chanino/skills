#!/usr/bin/env python3
"""Generate images using Google Gemini.

Sends a text prompt to Gemini and saves the generated image.

Usage:
    # Basic generation
    python3 generate_image.py "A red apple on white background" -o apple.png

    # With aspect ratio and size
    python3 generate_image.py "Mountain landscape at sunset" -o landscape.png --aspect 16:9 --size 2K

    # Pipe prompt from stdin
    echo "A futuristic city skyline" | python3 generate_image.py -o city.png

    # Stream to stdout
    python3 generate_image.py "A blue circle" -o -

Environment:
    GEMINI_API_KEY: Google AI Studio API key (or pass --api-key)
                    Get one at https://aistudio.google.com/apikey
"""

import mimetypes
import os
import argparse
import sys
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retry configuration for transient API errors
MAX_RETRIES = 3
RETRY_BASE_DELAY = 2  # seconds

# Transient HTTP status codes worth retrying
TRANSIENT_CODES = {429, 500, 502, 503, 504}


def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)
    print(f"File saved to: {file_name}", file=sys.stderr)


def _is_transient(exc):
    """Check if an exception looks like a transient API error."""
    msg = str(exc).lower()
    # Check for HTTP status codes in the error message
    for code in TRANSIENT_CODES:
        if str(code) in str(exc):
            return True
    if "timeout" in msg or "rate" in msg or "unavailable" in msg:
        return True
    return False


def generate(prompt, model, output_path, api_key=None, aspect_ratio="16:9", image_size="1K"):
    client = genai.Client(
        api_key=api_key or os.environ.get("GEMINI_API_KEY"),
    )

    if output_path != "-":
        print(f"Generating image for prompt: '{prompt}' using model: '{model}'...", file=sys.stderr)

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        image_config=types.ImageConfig(
            aspect_ratio=aspect_ratio,
            image_size=image_size,
        ),
        response_modalities=[
            "IMAGE",
            "TEXT",
        ],
    )

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            image_found = False
            file_index = 0
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                if chunk.parts is None:
                    continue
                if chunk.parts[0].inline_data and chunk.parts[0].inline_data.data:
                    inline_data = chunk.parts[0].inline_data
                    data_buffer = inline_data.data
                    file_extension = mimetypes.guess_extension(inline_data.mime_type)

                    if output_path == "-":
                        sys.stdout.buffer.write(data_buffer)
                        sys.stdout.buffer.flush()
                    else:
                        if not image_found:
                            final_output = output_path
                        else:
                            base, ext = os.path.splitext(output_path)
                            final_output = f"{base}_{file_index}{ext}"
                        save_binary_file(final_output, data_buffer)

                    image_found = True
                    file_index += 1
                else:
                    print(chunk.text, file=sys.stderr)

            if not image_found:
                print("Error: No image was returned by the model.", file=sys.stderr)
                return 1
            return 0

        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES - 1 and _is_transient(e):
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                print(f"Transient error (attempt {attempt + 1}/{MAX_RETRIES}): {e}", file=sys.stderr)
                print(f"Retrying in {delay}s...", file=sys.stderr)
                time.sleep(delay)
            else:
                print(f"Error during image generation: {e}", file=sys.stderr)
                return 1

    print(f"Failed after {MAX_RETRIES} attempts. Last error: {last_error}", file=sys.stderr)
    return 1


def main():
    parser = argparse.ArgumentParser(description="Generate an image using Google Gemini.")
    parser.add_argument("prompt", type=str, nargs="?",
                        help="The text prompt for the image. If omitted, reads from stdin.")
    parser.add_argument("--model", type=str, default="gemini-3-pro-image-preview",
                        help="The model ID to use (default: gemini-3-pro-image-preview).")
    parser.add_argument("--api-key", type=str, help="Your Google AI Studio API Key.")
    parser.add_argument("--aspect", type=str, default="16:9",
                        choices=["16:9", "1:1", "9:16", "4:3", "3:4"],
                        help="Aspect ratio (default: 16:9).")
    parser.add_argument("--size", type=str, default="1K",
                        choices=["512", "1K", "2K"],
                        help="Image size (default: 1K).")
    parser.add_argument("-o", "--output", type=str, default="output.png",
                        help="Output file path. Use '-' for stdout.")

    args = parser.parse_args()

    # Read prompt from stdin if not provided
    prompt = args.prompt
    if not prompt:
        if not sys.stdin.isatty():
            prompt = sys.stdin.read().strip()
        else:
            print("Error: No prompt provided. Either pass it as an argument or pipe it via stdin.", file=sys.stderr)
            sys.exit(1)

    if not prompt:
        print("Error: Empty prompt.", file=sys.stderr)
        sys.exit(1)

    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: No API key found. Set GEMINI_API_KEY environment variable or pass --api-key.", file=sys.stderr)
        print("Get a free API key at: https://aistudio.google.com/apikey", file=sys.stderr)
        sys.exit(1)

    sys.exit(generate(prompt, args.model, args.output, api_key, args.aspect, args.size))


if __name__ == "__main__":
    main()
