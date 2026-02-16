#!/usr/bin/env python3
"""Convert a reference diagram image to a JSON shape specification using Gemini vision.

Sends a diagram image to Gemini with embedded shape-spec knowledge and returns
a complete JSON specification that build_slide.js can render as native PowerPoint shapes.

Usage:
    python3 scripts/image_to_spec.py -i /tmp/diagram-ref.png -o /tmp/diagram-spec.json

    python3 scripts/image_to_spec.py \
      -i /tmp/diagram-ref.png \
      -o /tmp/diagram-spec.json \
      --title "Three-Tier Architecture" \
      --palette "Corporate Blue"

Environment:
    GEMINI_API_KEY: Google AI Studio API key (or pass --api-key)
                    Get one at https://aistudio.google.com/apikey
"""

import argparse
import json
import os
import re
import sys
import time


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

from google import genai
from google.genai import types


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_RETRIES = 3
RETRY_BASE_DELAY = 2  # seconds
TRANSIENT_CODES = {429, 500, 502, 503, 504}

PALETTES = {
    "Corporate Blue": {
        "Primary": "2E5090",
        "Secondary": "5B8DB8",
        "Accent": "C4A35A",
        "Neutral": "6B7280",
        "Light": "F1F5F9",
    },
    "Warm Professional": {
        "Primary": "7C3A2D",
        "Secondary": "C4734F",
        "Accent": "D4A847",
        "Neutral": "6B7280",
        "Light": "FDF6F0",
    },
    "Modern Slate": {
        "Primary": "334155",
        "Secondary": "64748B",
        "Accent": "0EA5E9",
        "Neutral": "94A3B8",
        "Light": "F1F5F9",
    },
    "Forest Green": {
        "Primary": "1B5E42",
        "Secondary": "3D8B6E",
        "Accent": "D4A847",
        "Neutral": "6B7280",
        "Light": "F0F9F4",
    },
}

EXT_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}

ICON_CATALOG = [
    ("server_rack.png", "servers, compute instances, backend services"),
    ("database_cylinder.png", "databases, data stores, DB instances"),
    ("cloud.png", "cloud services, cloud platforms, SaaS"),
    ("storage_disk.png", "storage, file systems, block storage"),
    ("lambda_function.png", "serverless functions, lambdas, cloud functions"),
    ("cpu_microchip.png", "processing, compute, CPU-intensive tasks"),
    ("desktop_computer.png", "clients, frontends, user machines, workstations"),
    ("network_switch.png", "network switches, L2 switching"),
    ("shield.png", "security, protection, firewalls, WAF"),
    ("padlock.png", "authentication, authorization, locked/secure"),
    ("key.png", "API keys, credentials, secrets, encryption keys"),
    ("globe_internet.png", "internet, web, external access, public endpoints"),
    ("network_router.png", "routers, routing, load balancers, gateways"),
    ("data_exchange_arrows.png", "data flow, sync, ETL, data transfer"),
    ("broadcast_tower.png", "messaging, pub/sub, events, broadcasting"),
    ("gear_settings.png", "configuration, settings, admin, ops"),
    ("rocket_launch.png", "deployment, CI/CD, launch, go-live"),
    ("sync_refresh_arrows.png", "sync, refresh, polling, replication"),
    ("person_silhouette.png", "single user, actor, admin"),
    ("group_of_people.png", "user group, team, audience"),
    ("checkmark_circle.png", "success, complete, healthy, pass"),
    ("warning_triangle.png", "warning, degraded, caution"),
    ("error_x_circle.png", "error, failure, down, critical"),
    ("document_file.png", "documents, files, logs, reports"),
    ("bar_chart_analytics.png", "analytics, metrics, dashboards, monitoring"),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_transient(exc):
    """Check if an exception looks like a transient API error."""
    msg = str(exc).lower()
    for code in TRANSIENT_CODES:
        if str(code) in str(exc):
            return True
    if "timeout" in msg or "rate" in msg or "unavailable" in msg:
        return True
    return False


def sanitize_hex(color, fallback="333333"):
    """Strip # prefix and validate hex color. Returns 6-char hex string."""
    if not isinstance(color, str):
        return fallback
    color = color.strip().lstrip("#")
    if re.match(r'^[0-9a-fA-F]{6}$', color):
        return color
    if re.match(r'^[0-9a-fA-F]{3}$', color):
        return ''.join(c * 2 for c in color)
    return fallback


def extract_json(text):
    """Extract JSON from text, handling markdown code fences."""
    text = text.strip()
    m = re.match(r'^```(?:json)?\s*\n(.*?)```\s*$', text, re.DOTALL)
    if m:
        text = m.group(1).strip()
    return json.loads(text)


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def build_prompt(palette_name, palette):
    """Build the Gemini analysis prompt with embedded shape-spec knowledge."""
    icon_lines = "\n".join(
        f"  - {name}: {desc}" for name, desc in ICON_CATALOG
    )

    return f"""Analyze this technical diagram image and output a JSON shape specification for PowerPoint rendering.

## 1. Coordinate System
- Slide: 10" wide x 5.625" tall (16:9)
- Title bar: y=0 to y=0.75 (auto-rendered, do NOT place elements here)
- Diagram area: y=0.85 to y=5.35 (4.5" tall)
- All coordinates in inches from top-left corner
- Position guide: far-left x~0.5-1.5, center-left x~2.0-3.5, center x~4.0-6.0, center-right x~6.5-8.0, far-right x~8.5-9.5
- Top row y~0.85-2.0, middle row y~2.5-3.5, bottom row y~3.8-5.0

## 2. Shape Types
roundedRect (services, components - most common), rect (containers), diamond (decisions, min 1.8"x1.0"), cylinder (databases, min h 1.0"), oval (actors), cloud (external services), hexagon (hub elements), flowTerminator (start/end), flowDecision, flowDocument, parallelogram (data/IO), trapezoid (funnels)

## 3. Color Palette: {palette_name}
- Primary: {palette['Primary']} - key components (white text FFFFFF)
- Secondary: {palette['Secondary']} - supporting shapes (white text FFFFFF)
- Accent: {palette['Accent']} - highlights, decisions (white text FFFFFF)
- Neutral: {palette['Neutral']} - connector lines, labels
- Light: {palette['Light']} - group backgrounds (dark text 1E293B)
IMPORTANT: Use all 3 fills (Primary, Secondary, Accent). Assign Accent to at least 2 shapes. Never use bright saturated colors.

## 4. Visual Hierarchy
- Tier 1 (primary): fill=Primary, lineWidth=0, shadow={{blur:5,offset:4,angle:45,color:"000000",opacity:0.4}}, fontBold=true, fontSize=11, charSpacing=1
- Tier 2 (secondary): fill=Secondary, lineWidth=0, shadow={{blur:3,offset:2,angle:45,color:"000000",opacity:0.25}}, fontSize=10
- Tier 3 (groups): fill=Light, borderless=true, shadow={{blur:6,offset:4,angle:45,color:"000000",opacity:0.12}}
All shapes: lineWidth=0 (borderless), rectRadius=0.1 for roundedRect, margin=[8,10,8,10]

## 5. Connector Rules
- Use shape-anchored mode: "from" and "to" with shape IDs, "fromSide"/"toSide" (left/right/top/bottom)
- NEVER set "route" property (defaults to elbow routing with chamfered corners)
- Always set endArrow: "triangle"
- lineColor: "{palette['Neutral']}", lineWidth: 2.0
- Label every connector with an interaction verb

## 6. Icon Catalog
Place 0.35"x0.35" icon centered above each major shape. Path format: "assets/icons/FILENAME"
{icon_lines}

## 7. Component Stack Pattern
For each major component, create 3 elements:
1. icon: x=shape.x+(shape.w-0.35)/2, y=Y, w=0.35, h=0.35
2. shape: y=icon.y+0.40 (0.05" gap), with id, label, tier styling
3. description text: y=shape.y+shape.h+0.05, fontSize=10, fontItalic=true, fontColor="64748B", align="center"

## 8. JSON Output Structure
{{
  "meta": {{
    "title": "Title from image",
    "subtitle": "Optional subtitle",
    "altText": "2-3 sentence screen reader description",
    "description": "Detailed paragraph about all components and relationships",
    "bgColor": "FFFFFF",
    "titleColor": "1E293B",
    "titleBgColor": "F8FAFC",
    "titleCharSpacing": 1.5
  }},
  "elements": [
    {{"type":"group","x":N,"y":N,"w":N,"h":N,"fill":"{palette['Light']}","borderless":true,"shadow":{{"blur":6,"offset":4,"angle":45,"color":"000000","opacity":0.12}}}},
    {{"type":"icon","path":"assets/icons/FILE.png","x":N,"y":N,"w":0.35,"h":0.35}},
    {{"type":"shape","id":"unique_id","shapeType":"roundedRect","x":N,"y":N,"w":N,"h":N,"fill":"{palette['Primary']}","fontColor":"FFFFFF","lineWidth":0,"rectRadius":0.1,"label":"Label","fontSize":11,"fontBold":true,"charSpacing":1,"margin":[8,10,8,10],"shadow":{{"blur":5,"offset":4,"angle":45,"color":"000000","opacity":0.4}}}},
    {{"type":"text","x":N,"y":N,"w":N,"h":0.4,"text":"Description line","fontSize":10,"fontItalic":true,"fontColor":"64748B","align":"center"}},
    {{"type":"connector","from":"id1","fromSide":"right","to":"id2","toSide":"left","endArrow":"triangle","lineColor":"{palette['Neutral']}","lineWidth":2.0,"label":"Action"}}
  ]
}}

## 9. Analysis Instructions
1. Count all distinct components in the image
2. Identify layout pattern (left-to-right, top-to-bottom, hub-and-spoke, grid, swim lanes)
3. For each component: determine shapeType, position (x,y), size (w,h), read label text
4. For each arrow: identify source/target shapes, direction, label text
5. Match components to closest icon from catalog
6. Assign unique snake_case IDs to all shapes (e.g. "api_gateway", "user_db")
7. Distribute Primary, Secondary, Accent fills - alternate so adjacent shapes differ
8. Build component stacks: icon above, shape below, description below shape
9. Ensure minimum 0.4" gaps between shapes, all within bounds
10. Shapes with labels >= 1.5" wide, diamonds >= 1.8" x 1.0"
11. Font minimum 10pt everywhere. Primary labels 11pt bold. Connectors 11pt.
12. Z-order: groups first, then dividers, then icons+shapes+text, then connectors last
13. Generate altText (2-3 screen reader sentences) and description (full paragraph)"""


# ---------------------------------------------------------------------------
# Gemini API call with retry + JSON/text mode fallback
# ---------------------------------------------------------------------------

def _attempt_gemini(client, model_id, contents, use_json_mode):
    """Attempt Gemini call with retries for transient errors.

    Returns parsed JSON dict on success, raises on failure.
    """
    config_kwargs = {"temperature": 0.2}
    if use_json_mode:
        config_kwargs["response_mime_type"] = "application/json"
    config = types.GenerateContentConfig(**config_kwargs)

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=model_id, contents=contents, config=config,
            )
            text = response.text
            if not text:
                raise ValueError("Empty response from Gemini")
            return extract_json(text)
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES - 1 and _is_transient(e):
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                print(f"  Transient error (attempt {attempt + 1}/{MAX_RETRIES}): {e}", file=sys.stderr)
                print(f"  Retrying in {delay}s...", file=sys.stderr)
                time.sleep(delay)
            else:
                raise
    raise last_error


def call_gemini(image_data, mime_type, prompt, model_id, api_key):
    """Call Gemini vision API. Returns parsed JSON dict or None."""
    client = genai.Client(api_key=api_key) if api_key else genai.Client()

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(mime_type=mime_type, data=image_data),
                types.Part.from_text(text=prompt),
            ],
        ),
    ]

    # Try structured JSON output first
    try:
        print(f"Calling Gemini ({model_id}) with JSON mode...", file=sys.stderr)
        return _attempt_gemini(client, model_id, contents, use_json_mode=True)
    except Exception as e:
        print(f"  JSON mode failed: {e}", file=sys.stderr)

    # Fall back to text mode (parse JSON from free-text response)
    try:
        print(f"Retrying in text mode...", file=sys.stderr)
        return _attempt_gemini(client, model_id, contents, use_json_mode=False)
    except Exception as e:
        print(f"Error: Failed to get valid JSON from Gemini: {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Post-processing (Layer 1)
# ---------------------------------------------------------------------------

def postprocess_spec(spec, input_path, title, subtitle):
    """Sanitize, apply defaults, inject CLI metadata, remove route from connectors."""
    # Ensure top-level structure
    if "meta" not in spec:
        spec["meta"] = {}
    if "elements" not in spec:
        spec["elements"] = []

    meta = spec["meta"]

    # Inject CLI overrides
    meta["referenceImage"] = input_path
    if title:
        meta["title"] = title
    if subtitle:
        meta["subtitle"] = subtitle

    # Meta defaults
    meta.setdefault("title", "Diagram")
    meta.setdefault("bgColor", "FFFFFF")
    meta.setdefault("titleColor", "1E293B")
    meta.setdefault("titleBgColor", "F8FAFC")
    meta.setdefault("titleCharSpacing", 1.5)

    # Sanitize meta hex colors
    for key in ("bgColor", "titleColor", "titleBgColor"):
        if key in meta:
            meta[key] = sanitize_hex(meta[key], "FFFFFF")

    # Process elements
    for elem in spec["elements"]:
        # Sanitize hex color fields
        for field in ("fill", "lineColor", "fontColor", "labelColor", "labelBgColor"):
            if field in elem:
                elem[field] = sanitize_hex(elem[field])

        # Sanitize shadow colors
        shadow = elem.get("shadow")
        if isinstance(shadow, dict) and "color" in shadow:
            shadow["color"] = sanitize_hex(shadow["color"], "000000")

        # Remove route property from connectors (enforce elbow default)
        if elem.get("type") == "connector":
            elem.pop("route", None)

        # Ensure endArrow on connectors
        if elem.get("type") == "connector" and "endArrow" not in elem:
            elem["endArrow"] = "triangle"

    return spec


# ---------------------------------------------------------------------------
# Structural validation (Layer 2) — report printed to stderr
# ---------------------------------------------------------------------------

def validate_spec(spec):
    """Run structural checks, print report to stderr. Returns (passes, warnings)."""
    elements = spec.get("elements", [])

    # Build indexes
    shapes_by_id = {}
    type_counts = {}
    for elem in elements:
        t = elem.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
        eid = elem.get("id")
        if eid:
            shapes_by_id[eid] = elem

    passes = 0
    warnings = 0

    print("\n=== Spec Validation Report ===", file=sys.stderr)

    # 1. Element census
    total = len(elements)
    parts = []
    for t in ("shape", "connector", "icon", "group", "text", "divider"):
        c = type_counts.get(t, 0)
        if c:
            parts.append(f"{c} {t}{'s' if c > 1 else ''}")
    print(f"Elements: {total} total ({', '.join(parts)})", file=sys.stderr)

    # Icon path validity
    icon_count = 0
    icon_valid = 0
    for elem in elements:
        if elem.get("type") == "icon":
            icon_count += 1
            path = elem.get("path", "")
            if path.startswith("assets/icons/") or os.path.isabs(path):
                icon_valid += 1
    if icon_count:
        print(f"Icons: {icon_count} ({icon_valid} paths valid)", file=sys.stderr)

    # 2. Palette coverage
    shape_fills = set()
    for elem in elements:
        if elem.get("type") == "shape" and "fill" in elem:
            shape_fills.add(elem["fill"].upper())
    palette_roles = {"Primary", "Secondary", "Accent"}
    # We can't check exact palette match without knowing which palette, but count distinct fills
    coverage_ok = len(shape_fills) >= 3
    p_label = "\u2713" if coverage_ok else "\u26a0"
    print(f"Palette: {len(shape_fills)} distinct shape fills {p_label}", file=sys.stderr)
    if coverage_ok:
        passes += 1
    else:
        warnings += 1

    # 3. Bounds check
    bounds_violations = 0
    for elem in elements:
        if elem.get("type") in ("shape", "text", "icon"):
            x = elem.get("x", 0)
            y = elem.get("y", 0)
            w = elem.get("w", 0)
            h = elem.get("h", 0)
            if x < -0.1 or x + w > 10.1:
                bounds_violations += 1
            if y < 0.8:
                bounds_violations += 1
            if y + h > 5.5:
                bounds_violations += 1
    label = "\u2713" if bounds_violations == 0 else "\u26a0"
    print(f"Bounds: {bounds_violations} violations {label}", file=sys.stderr)
    if bounds_violations == 0:
        passes += 1
    else:
        warnings += bounds_violations

    # 4. Connector ID check
    connector_refs = 0
    connector_resolved = 0
    missing_ids = []
    for elem in elements:
        if elem.get("type") == "connector":
            for field in ("from", "to"):
                ref = elem.get(field)
                if ref:
                    connector_refs += 1
                    if ref in shapes_by_id:
                        connector_resolved += 1
                    else:
                        missing_ids.append(ref)
    if connector_refs:
        if missing_ids:
            print(f"Connector IDs: {connector_resolved}/{connector_refs} resolved \u26a0 missing: {', '.join(sorted(set(missing_ids)))}", file=sys.stderr)
            warnings += len(set(missing_ids))
        else:
            print(f"Connector IDs: {connector_resolved}/{connector_refs} resolved \u2713", file=sys.stderr)
            passes += 1

    # 5. Minimum shape size
    undersized = 0
    for elem in elements:
        if elem.get("type") == "shape":
            w = elem.get("w", 0)
            h = elem.get("h", 0)
            if elem.get("label") and w < 1.5:
                undersized += 1
            if elem.get("shapeType") == "diamond" and (w < 1.8 or h < 1.0):
                undersized += 1
    if undersized:
        print(f"Min size: {undersized} undersized shapes \u26a0", file=sys.stderr)
        warnings += undersized
    else:
        passes += 1

    # 6. Font floor — auto-fix any fontSize < 10
    font_fixes = 0
    for elem in elements:
        for fkey in ("fontSize", "labelFontSize"):
            if fkey in elem and isinstance(elem[fkey], (int, float)) and elem[fkey] < 10:
                elem[fkey] = 10
                font_fixes += 1
        for run in elem.get("textRuns", []):
            if "fontSize" in run and isinstance(run["fontSize"], (int, float)) and run["fontSize"] < 10:
                run["fontSize"] = 10
                font_fixes += 1
    print(f"Font floor: {font_fixes} fixes applied", file=sys.stderr)
    if font_fixes == 0:
        passes += 1
    else:
        warnings += font_fixes

    # 7. Overlap detection (bounding-box intersection on shapes)
    shapes = [e for e in elements if e.get("type") == "shape"]
    collisions = 0
    for i in range(len(shapes)):
        a = shapes[i]
        ax1, ay1 = a.get("x", 0), a.get("y", 0)
        ax2, ay2 = ax1 + a.get("w", 0), ay1 + a.get("h", 0)
        for j in range(i + 1, len(shapes)):
            b = shapes[j]
            bx1, by1 = b.get("x", 0), b.get("y", 0)
            bx2, by2 = bx1 + b.get("w", 0), by1 + b.get("h", 0)
            if ax1 < bx2 and ax2 > bx1 and ay1 < by2 and ay2 > by1:
                collisions += 1
    label = "\u2713" if collisions == 0 else "\u26a0"
    print(f"Overlap: {collisions} collisions {label}", file=sys.stderr)
    if collisions == 0:
        passes += 1
    else:
        warnings += collisions

    # Summary
    if warnings == 0:
        print(f"\u2192 Ready to build", file=sys.stderr)
    else:
        print(f"\u2192 {warnings} warning(s) \u2014 review before building", file=sys.stderr)

    return passes, warnings


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Convert a reference diagram image to a JSON shape specification using Gemini vision."
    )
    parser.add_argument("-i", "--input", required=True,
                        help="Reference image path")
    parser.add_argument("-o", "--output", required=True,
                        help="Output JSON spec path")
    parser.add_argument("--title", default="Diagram",
                        help="meta.title (default: 'Diagram')")
    parser.add_argument("--subtitle", default=None,
                        help="meta.subtitle")
    parser.add_argument("--palette", default="Corporate Blue",
                        choices=list(PALETTES.keys()),
                        help="Color palette (default: 'Corporate Blue')")
    parser.add_argument("--model", default="gemini-3-pro-image-preview",
                        help="Gemini model ID (default: gemini-3-pro-image-preview)")
    parser.add_argument("--api-key", default=None,
                        help="Gemini API key override")
    parser.add_argument("--no-validate", action="store_true",
                        help="Skip post-processing validation")

    args = parser.parse_args()

    # Validate input
    if not os.path.isfile(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Read image
    with open(args.input, "rb") as f:
        image_data = f.read()
    ext = os.path.splitext(args.input)[1].lower()
    mime_type = EXT_MIME.get(ext, "image/png")

    # API key
    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: No API key found. Set GEMINI_API_KEY environment variable or pass --api-key.", file=sys.stderr)
        print("Get a free API key at: https://aistudio.google.com/apikey", file=sys.stderr)
        sys.exit(1)

    # Build prompt
    palette = PALETTES[args.palette]
    prompt = build_prompt(args.palette, palette)

    print(f"Analyzing image: {args.input}", file=sys.stderr)
    print(f"Palette: {args.palette}", file=sys.stderr)

    # Call Gemini
    spec = call_gemini(image_data, mime_type, prompt, args.model, api_key)
    if spec is None:
        print("Error: Failed to generate spec from image.", file=sys.stderr)
        sys.exit(1)

    # Post-process
    spec = postprocess_spec(spec, args.input, args.title, args.subtitle)

    # Validate
    if not args.no_validate:
        validate_spec(spec)

    # Write output
    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(spec, f, indent=2)

    print(f"\nSpec written to: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
