---
triggers:
  - "generate image"
  - "create image"
  - "describe image"
  - "analyze image"
  - "image to text"
  - "alt text"
  - "gemini image"
---

# gemini-image

General-purpose image generation and analysis using Google Gemini. Two independent workflows: generate images from text prompts, or analyze/describe existing images.

## Prerequisites

| Dependency | Install |
|---|---|
| Python 3.10+ | `python3 --version` |
| `google-genai` | `pip install google-genai` |
| `python-dotenv` | `pip install python-dotenv` |
| `GEMINI_API_KEY` | Export env var or add to `.env`. Get a key at https://aistudio.google.com/apikey |

## Workflow A — Image Generation

Use this workflow when the user wants to create, generate, or produce an image from a text description.

### Step 1: Understand the Request

Parse the user's request to identify:
- **Subject**: What should be depicted (object, scene, concept)
- **Style**: Photorealistic, illustration, diagram, watercolor, etc.
- **Aspect ratio**: Landscape (16:9), square (1:1), portrait (9:16), standard (4:3)
- **Size**: 512, 1K (default), or 2K
- **Output path**: Where to save the result

If the user is vague, ask clarifying questions before generating.

### Step 2: Read the Prompt Guide

Read `references/prompt-guide.md` for prompt engineering best practices. Key principles:
- Lead with the subject, then style, then details
- Be specific about composition and lighting
- Use negative descriptions sparingly ("no text", "no watermark")
- Match aspect ratio to content (landscapes → 16:9, portraits → 9:16)

### Step 3: Craft the Prompt

Write a detailed generation prompt following the guide. A good prompt includes:
1. Subject and action
2. Visual style / medium
3. Composition details (foreground, background, lighting)
4. Color palette or mood

Example: `"A modern cloud architecture diagram showing three availability zones connected by a load balancer, clean vector style, white background, blue and gray color scheme"`

### Step 4: Generate the Image

Run the generation script:

```bash
python3 scripts/generate_image.py "<prompt>" -o <output_path> --aspect <ratio> --size <size>
```

**Parameters:**
| Flag | Values | Default |
|---|---|---|
| `--aspect` | `16:9`, `1:1`, `9:16`, `4:3`, `3:4` | `16:9` |
| `--size` | `512`, `1K`, `2K` | `1K` |
| `--model` | Any Gemini model ID | `gemini-3-pro-image-preview` |
| `-o` | File path or `-` for stdout | `output.png` |

The prompt can also be piped via stdin:
```bash
echo "A red apple on white background" | python3 scripts/generate_image.py -o apple.png
```

### Step 5: QA the Output

Review the generated image against `references/qa-checklist.md`. Check for:
1. Prompt fidelity — does it match what was requested?
2. Text rendering — any garbled or misspelled text?
3. Visual artifacts — distortion, extra limbs, blurring?
4. Composition — balanced, properly framed?

**If issues are found**, refine the prompt and regenerate. Maximum **3 refinement attempts**. Common fixes:
- Add specificity to underrepresented elements
- Adjust style keywords
- Change aspect ratio if composition is cramped

Present the final image path to the user.

---

## Workflow B — Image Analysis

Use this workflow when the user wants to describe, analyze, extract text from, or understand an existing image.

### Step 1: Identify the Goal

Determine what kind of analysis the user needs:
- **Alt text**: Concise accessibility description
- **Full description**: Detailed visual description
- **Layout analysis**: Structural/spatial breakdown
- **OCR / text extraction**: Read text from the image
- **Technical analysis**: Diagram interpretation, chart data extraction
- **Photo description**: People, objects, setting, mood

### Step 2: Select Analysis Template

Read `references/analysis-templates.md` and select the appropriate prompt template for the user's goal. Templates provide optimized prompts for each analysis type.

If no template fits, craft a custom prompt that:
- States the output format clearly
- Specifies the level of detail needed
- Mentions any domain-specific context

### Step 3: Run the Analysis

```bash
python3 scripts/image_to_text.py -i <image_path> "<prompt>" -o <output_path>
```

**Parameters:**
| Flag | Values | Default |
|---|---|---|
| `-i` | Image file path or `-` for stdin | stdin |
| `-o` | Output text file or `-` for stdout | `-` (stdout) |
| `--model` | Any Gemini model ID | `gemini-3-pro-image-preview` |

Pipe from stdin:
```bash
cat photo.png | python3 scripts/image_to_text.py "Describe this image"
```

### Step 4: Review and Refine

Check the analysis output for:
- **Completeness**: Does it cover all visible elements?
- **Accuracy**: Are descriptions factually correct?
- **Format**: Does it match the requested output format?

If the output is insufficient, try:
1. A more specific prompt
2. A different analysis template
3. Breaking the analysis into multiple focused queries

Return the final analysis to the user.

---

## Script Reference

### `scripts/generate_image.py`

```
usage: generate_image.py [-h] [--model MODEL] [--api-key KEY]
                         [--aspect {16:9,1:1,9:16,4:3,3:4}]
                         [--size {512,1K,2K}]
                         [-o OUTPUT] [prompt]

Generate an image using Google Gemini.

positional arguments:
  prompt          Text prompt (or pipe via stdin)

options:
  --aspect        Aspect ratio (default: 16:9)
  --size          Image size (default: 1K)
  --model         Model ID (default: gemini-3-pro-image-preview)
  --api-key       Google AI Studio API key
  -o, --output    Output file path or '-' for stdout (default: output.png)
```

### `scripts/image_to_text.py`

```
usage: image_to_text.py [-h] [-i INPUT] [-o OUTPUT] [--model MODEL]
                        [--api-key KEY] [prompt]

Analyze an image using Google Gemini vision.

positional arguments:
  prompt          Analysis prompt (default: accessibility description)

options:
  -i, --input     Image file path or '-' for stdin (default: stdin)
  -o, --output    Output text file or '-' for stdout (default: stdout)
  --model         Model ID (default: gemini-3-pro-image-preview)
  --api-key       Google AI Studio API key
```

---

## Output Files

| Workflow | Output |
|---|---|
| Generation | PNG image at specified `-o` path |
| Analysis | Text at specified `-o` path (default: stdout) |
