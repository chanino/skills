# Canonical version maintained in gemini-image skill.
# This is a local copy for pptx-diagram self-containment.

import mimetypes
import os
import argparse
import sys
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def save_binary_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close()
    print(f"File saved to: {file_name}", file=sys.stderr)


def generate(prompt, model, output_path, api_key=None):
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
    tools = [
        types.Tool(googleSearch=types.GoogleSearch(
        )),
    ]
    generate_content_config = types.GenerateContentConfig(
        image_config = types.ImageConfig(
            aspect_ratio="16:9",
            image_size="1K"
        ),
        response_modalities=[
            "IMAGE",
            "TEXT",
        ],
        tools=tools,
    )

    image_found = False
    file_index = 0
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.parts is None
        ):
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


def main():
    parser = argparse.ArgumentParser(description="Generate an image using Gemini 3 Pro.")
    parser.add_argument("prompt", type=str, nargs="?", help="The text prompt for the image. If omitted, reads from stdin.")
    parser.add_argument("--model", type=str, default="gemini-3-pro-image-preview", help="The model ID to use.")
    parser.add_argument("--api-key", type=str, help="Your Google AI Studio API Key.")
    parser.add_argument("-o", "--output", type=str, default="output.png", help="Output file path. Use '-' for stdout.")

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
        print("Error: No API key found. Set GEMINI_API_KEY in .env or pass --api-key.", file=sys.stderr)
        sys.exit(1)

    sys.exit(generate(prompt, args.model, args.output, api_key))

if __name__ == "__main__":
    main()
