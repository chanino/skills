#!/usr/bin/env python3
"""Generate individual icons via Gemini and post-process with Pillow.

Calls ../gemini-image/scripts/generate_image.py to produce one icon per API call,
then uses Pillow to crop, pad, and resize into a clean square PNG.

Usage:
    # Single icon
    python3 scripts/generate_icon.py "server rack" -o /tmp/icons/server.png

    # Single icon with custom color
    python3 scripts/generate_icon.py "server rack" --color "slate gray" -o /tmp/icons/server.png

    # Batch mode (generates each icon sequentially)
    python3 scripts/generate_icon.py \
      --batch "server,database,cloud,lambda function,shield" \
      --color "dark navy blue" \
      --output-dir /tmp/icons/

Output (batch mode):
    Prints a JSON mapping of {name: path} to stdout, e.g.:
    {"server": "/tmp/icons/server.png", "database": "/tmp/icons/database.png", ...}
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile


def _load_env_file(filepath):
    """Manually parse a .env file and inject into os.environ."""
    try:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip("'\"")
                if key and key not in os.environ:
                    os.environ[key] = value
    except (IOError, OSError):
        pass


# Load .env from cwd and walk up from script directory
_load_env_file(os.path.join(os.getcwd(), ".env"))
_dir = os.path.dirname(os.path.abspath(__file__))
for _i in range(5):
    _candidate = os.path.join(_dir, ".env")
    if os.path.exists(_candidate):
        _load_env_file(_candidate)
        break
    _dir = os.path.dirname(_dir)

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)


def sanitize_name(name):
    """Convert an icon description to a safe filename stem."""
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = s.strip("_")
    return s or "icon"


DEFAULT_COLOR = "dark navy blue"
DEFAULT_STYLE = "flat minimalist technical icon"
DEFAULT_ICON_SIZE = 256
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "pptx-diagram-icons")


def _cache_key(description, color, style, icon_size):
    """Compute a deterministic cache key for an icon."""
    raw = f"{description.strip().lower()}|{color.strip().lower()}|{style.strip().lower()}|{icon_size}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _cache_filename(description, color, style, icon_size):
    """Build a human-readable cache filename with hash suffix."""
    sanitized = sanitize_name(description)
    h = _cache_key(description, color, style, icon_size)
    return f"{sanitized}_{h}.png"


def _check_assets_cache(description, color, style, icon_size, script_dir):
    """Tier 1: check pre-generated icons in assets/icons/ (default params only)."""
    if (color.strip().lower() != DEFAULT_COLOR
            or style.strip().lower() != DEFAULT_STYLE
            or icon_size != DEFAULT_ICON_SIZE):
        return None
    candidate = os.path.join(script_dir, "..", "assets", "icons", f"{sanitize_name(description)}.png")
    candidate = os.path.normpath(candidate)
    if os.path.isfile(candidate):
        return candidate
    return None


def _check_persistent_cache(description, color, style, icon_size, cache_dir):
    """Tier 2: check hash-keyed persistent cache directory."""
    filename = _cache_filename(description, color, style, icon_size)
    candidate = os.path.join(cache_dir, filename)
    if os.path.isfile(candidate):
        return candidate
    return None


def _save_to_cache(output_path, description, color, style, icon_size, cache_dir):
    """Copy a generated icon into the persistent cache."""
    os.makedirs(cache_dir, exist_ok=True)
    filename = _cache_filename(description, color, style, icon_size)
    cache_path = os.path.join(cache_dir, filename)
    shutil.copy2(output_path, cache_path)


def build_prompt(description, color, style):
    """Build a Gemini prompt for a single icon."""
    return (
        f"Generate a single {style} of: {description}\n"
        f"\n"
        f"Style requirements:\n"
        f"- Flat, minimalist technical icon style\n"
        f"- {color} colored icon on a pure white background\n"
        f"- No text, no labels, no annotations\n"
        f"- No shadows, no gradients, no 3D effects\n"
        f"- Clean crisp edges, uniform line weight\n"
        f"- Simple recognizable silhouette\n"
        f"- Icon should fill approximately 80% of the canvas\n"
        f"- Centered in the image\n"
        f"- Professional technical diagram quality\n"
        f"- Single icon only, no decorative elements"
    )


def _find_content_bbox(img, threshold=240):
    """Find bounding box of non-white content in an RGBA image."""
    pixels = img.load()
    w, h = img.size
    min_x, min_y = w, h
    max_x, max_y = 0, 0
    found = False

    for y in range(h):
        for x in range(w):
            px = pixels[x, y]
            # Skip fully transparent pixels
            if len(px) == 4 and px[3] < 10:
                continue
            r, g, b = px[0], px[1], px[2]
            if r < threshold or g < threshold or b < threshold:
                found = True
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    if not found:
        return None
    return (min_x, min_y, max_x + 1, max_y + 1)


def _pad_square(img, padding_pct=0.10):
    """Add padding and make the image square with transparent background."""
    w, h = img.size
    size = max(w, h)
    pad = int(size * padding_pct)
    final_size = size + 2 * pad

    result = Image.new("RGBA", (final_size, final_size), (0, 0, 0, 0))
    offset_x = (final_size - w) // 2
    offset_y = (final_size - h) // 2
    result.paste(img, (offset_x, offset_y))
    return result


def postprocess_icon(raw_path, output_path, icon_size=256):
    """Post-process a raw Gemini-generated icon image.

    Pipeline:
    1. Find content bounding box (skip near-white pixels, threshold 240)
    2. Crop to content
    3. Add 10% padding, center in square canvas
    4. Resize to target size (256x256)
    5. Save as optimized RGBA PNG (transparent background)
    """
    img = Image.open(raw_path).convert("RGBA")

    # Find and crop to content
    bbox = _find_content_bbox(img, threshold=240)
    if bbox is not None:
        img = img.crop(bbox)

    # Pad to square with 10% padding
    img = _pad_square(img, padding_pct=0.10)

    # Resize to target size
    img = img.resize((icon_size, icon_size), Image.LANCZOS)

    # Save as optimized PNG (preserve RGBA transparency)
    img.save(output_path, "PNG", optimize=True)


def generate_single_icon(description, color, style, output_path, gen_size, icon_size, gen_script,
                          cache_dir=None, no_cache=False):
    """Generate a single icon via Gemini and post-process it.

    Returns True on success (generated or cached), False on failure.
    """
    if cache_dir is None:
        cache_dir = CACHE_DIR

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Cache lookup (skip if --no-cache)
    if not no_cache:
        # Tier 1: pre-generated assets
        cached = _check_assets_cache(description, color, style, icon_size, script_dir)
        if cached:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            shutil.copy2(cached, output_path)
            print(f"  Cached: {description}", file=sys.stderr)
            return True

        # Tier 2: persistent cache
        cached = _check_persistent_cache(description, color, style, icon_size, cache_dir)
        if cached:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            shutil.copy2(cached, output_path)
            print(f"  Cached: {description}", file=sys.stderr)
            return True

    prompt = build_prompt(description, color, style)
    print(f"  Generating: {description}", file=sys.stderr)

    # Create temp file for raw Gemini output
    tmp_fd, raw_path = tempfile.mkstemp(suffix=".png")
    os.close(tmp_fd)

    try:
        cmd = [
            sys.executable, gen_script,
            prompt,
            "-o", raw_path,
            "--aspect", "1:1",
            "--size", gen_size,
        ]

        # Pass API key explicitly
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            cmd.extend(["--api-key", api_key])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.stderr:
            print(result.stderr, file=sys.stderr)
        if result.returncode != 0:
            print(f"  Error: generation failed for '{description}' (exit code {result.returncode})", file=sys.stderr)
            return False

        if not os.path.exists(raw_path):
            print(f"  Error: raw image not created for '{description}'", file=sys.stderr)
            return False

        # Post-process
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        postprocess_icon(raw_path, output_path, icon_size)
        print(f"  Saved: {output_path}", file=sys.stderr)

        # Save to persistent cache
        _save_to_cache(output_path, description, color, style, icon_size, cache_dir)
        return True

    finally:
        if os.path.exists(raw_path):
            os.remove(raw_path)


def main():
    parser = argparse.ArgumentParser(
        description="Generate individual icons via Gemini and post-process with Pillow."
    )
    parser.add_argument(
        "description", nargs="?", default=None,
        help="Icon description (single mode)"
    )
    parser.add_argument(
        "--batch", type=str, default=None,
        help="Comma-separated icon descriptions (batch mode)"
    )
    parser.add_argument(
        "--color", type=str, default="dark navy blue",
        help="Icon color (default: 'dark navy blue')"
    )
    parser.add_argument(
        "--style", type=str, default="flat minimalist technical icon",
        help="Style keywords (default: 'flat minimalist technical icon')"
    )
    parser.add_argument(
        "--output-dir", type=str, default="/tmp/icons/",
        help="Batch output directory (default: /tmp/icons/)"
    )
    parser.add_argument(
        "-o", "--output", type=str, default=None,
        help="Single-mode output path"
    )
    parser.add_argument(
        "--icon-size", type=int, default=256,
        help="Final PNG size in pixels (default: 256)"
    )
    parser.add_argument(
        "--gen-size", type=str, default="1K",
        choices=["512", "1K", "2K"],
        help="Gemini generation size before post-processing (default: 1K)"
    )
    parser.add_argument(
        "--no-cache", action="store_true", default=False,
        help="Skip cache lookup and force regeneration (still saves to cache)"
    )
    parser.add_argument(
        "--cache-dir", type=str, default=CACHE_DIR,
        help=f"Cache directory (default: {CACHE_DIR})"
    )

    args = parser.parse_args()

    # Validate args
    if not args.description and not args.batch:
        parser.error("Either a positional description or --batch is required")

    # Determine path to generate_image.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    gen_script = os.path.join(script_dir, "..", "..", "gemini-image", "scripts", "generate_image.py")
    gen_script = os.path.normpath(gen_script)

    if not os.path.exists(gen_script):
        print(f"Error: generate_image.py not found at: {gen_script}", file=sys.stderr)
        sys.exit(1)

    if args.batch:
        # Batch mode
        icons = [s.strip() for s in args.batch.split(",") if s.strip()]
        if not icons:
            print("Error: No icons specified in --batch.", file=sys.stderr)
            sys.exit(1)

        os.makedirs(args.output_dir, exist_ok=True)
        print(f"Generating {len(icons)} icons...", file=sys.stderr)

        results = {}
        failures = []
        cached_count = 0

        for desc in icons:
            safe_name = sanitize_name(desc)
            out_path = os.path.join(args.output_dir, f"{safe_name}.png")

            # Pre-check if this will be a cache hit (before generate adds to cache)
            will_cache_hit = False
            if not args.no_cache:
                t1 = _check_assets_cache(desc, args.color, args.style, args.icon_size, script_dir)
                t2 = _check_persistent_cache(desc, args.color, args.style, args.icon_size, args.cache_dir)
                will_cache_hit = bool(t1 or t2)

            ok = generate_single_icon(
                desc, args.color, args.style, out_path,
                args.gen_size, args.icon_size, gen_script,
                cache_dir=args.cache_dir, no_cache=args.no_cache,
            )
            if ok:
                results[safe_name] = out_path
                if will_cache_hit:
                    cached_count += 1
            else:
                failures.append(desc)

        if failures:
            print(f"\nFailed ({len(failures)}): {', '.join(failures)}", file=sys.stderr)

        generated_count = len(results) - cached_count
        print(f"\nGenerated {generated_count}/{len(icons)} icons ({cached_count} cached).", file=sys.stderr)

        # Output JSON mapping to stdout
        print(json.dumps(results, indent=2))

    else:
        # Single mode
        desc = args.description
        if args.output:
            out_path = args.output
        else:
            safe_name = sanitize_name(desc)
            out_path = os.path.join(args.output_dir, f"{safe_name}.png")

        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

        ok = generate_single_icon(
            desc, args.color, args.style, out_path,
            args.gen_size, args.icon_size, gen_script,
            cache_dir=args.cache_dir, no_cache=args.no_cache,
        )
        if ok:
            print(json.dumps({sanitize_name(desc): out_path}))
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
