# Claude Code Skills

A collection of personal skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Skills

### [deep-research](./deep-research/)

Multi-step iterative deep research with query decomposition, parallel web search via subagents, source verification, and citation-backed report generation.

**Usage:** `/deep-research [quick|standard|deep] <your research question>`

| Mode     | Search Threads | Iterations | Min Sources | Word Target    |
|----------|---------------|------------|-------------|----------------|
| quick    | 3             | 1          | 5           | 1,500–3,000    |
| standard | 5             | 2          | 10          | 3,000–6,000    |
| deep     | 8             | 3          | 15          | 6,000–10,000   |

**Output:** Research report saved to `~/Documents/research/[topic-slug]_[YYYYMMDD]/report.md` with companion `sources.md`.

### [gemini-image](./gemini-image/)

General-purpose image generation and analysis using Google Gemini. Generate images from text prompts or analyze/describe existing images with vision.

**Triggers:** "generate image", "create image", "describe image", "analyze image", "image to text", "alt text", "gemini image"

**Workflows:**
- **Image Generation** — text prompt → Gemini → PNG output (with aspect ratio and size control)
- **Image Analysis** — image + prompt → Gemini vision → text description/analysis

**Output:** PNG image (generation) or text description (analysis)

**Dependencies:** `google-genai`, `python-dotenv`, `GEMINI_API_KEY` environment variable

### [pptx-diagram](./pptx-diagram/)

Creates technical diagram slides as PPTX files with native editable PowerPoint shapes. Generates a reference image via Gemini, extracts a structural description via Gemini vision, translates it into a JSON shape spec, and builds the PPTX with real shapes (rectangles, diamonds, arrows, connectors) that you can click, move, resize, and edit directly in PowerPoint.

**Triggers:** "architecture diagram", "flowchart", "network diagram", "sequence diagram", "ER diagram", "system diagram", "data flow diagram", "CONOPS", "technical diagram"

**Supported diagram types:** Architecture (basic, cloud, layered, integration), CONOPS (swim lane, phased timeline, operational context), Flowchart, Network, Sequence, ER, Data Flow

**Output:** `{name}.pptx` + `{name}.png` (reference image) + `{name}.description.md` (alt text & metadata)

**Dependencies:** Requires `scripts/generate_image.py` and `scripts/image_to_text.py` (Gemini API key via `GEMINI_API_KEY`), and `pptxgenjs` installed via npm.

## Installation

Copy (or symlink) a skill directory into `~/.claude/skills/`:

```bash
# Example: install skills
cp -r deep-research ~/.claude/skills/deep-research
cp -r gemini-image ~/.claude/skills/gemini-image
cp -r pptx-diagram ~/.claude/skills/pptx-diagram
```

For gemini-image and pptx-diagram, install the Python dependencies:

```bash
pip install google-genai python-dotenv
```

For pptx-diagram, also install the Node dependency:

```bash
npm install -g pptxgenjs
```

## License

MIT
