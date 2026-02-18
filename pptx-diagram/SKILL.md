---
name: pptx-diagram
description: >
  Creates technical diagram slides as PPTX files with native editable shapes.
  Triggers: "architecture diagram", "flowchart", "network diagram", "sequence diagram",
  "ER diagram", "entity relationship diagram", "system diagram", "data flow diagram",
  "technical diagram", "diagram slide", "diagram presentation", "diagram pptx",
  "concept of operations", "CONOPS", "operational diagram"
  when the user wants a PowerPoint/PPTX output containing a generated diagram.
user_invocable: true
---

# PPTX Diagram Skill

You are creating a technical diagram as a polished single-slide PPTX with **native editable shapes**. The output contains real PowerPoint shapes (rectangles, diamonds, arrows, text boxes) that the user can click, move, resize, and edit directly in PowerPoint. Optionally, diagrams can include **rasterized icons** (server, database, cloud, etc.) for visual reinforcement. Follow these 6 steps in order.

## Slug & Artifact Directory

Every run is identified by a **slug** — a 2-4 word kebab-case name (max 40 chars, e.g. `three-tier-arch`). All artifacts for that run are saved to `diagrams/{slug}/` under the working directory. This keeps outputs organized and visible to the user.

## Progress Tracking

At the start of every run, create a task list with these 6 tasks (use `TaskCreate`). Mark each `in_progress` before starting and `completed` when done. Set sequential `blockedBy` dependencies so each task blocks the next.

| # | Subject | activeForm |
|---|---------|------------|
| 1 | Gather requirements and generate slug | Gathering diagram requirements |
| 2 | Generate image prompt | Generating image prompt |
| 3 | Generate reference image | Generating reference image |
| 4 | Generate JSON spec from reference | Generating JSON shape spec |
| 5 | Build PPTX from JSON spec | Building PPTX slide |
| 6 | QA and iterate on output | Running QA checks |

## Step 1: Gather Requirements

### 1a. Get high-level description

Ask the user about:
- **Diagram type** (architecture, flowchart, network, sequence, ER, data flow, CONOPS, etc.)
- **Components** — what elements should appear
- **Purpose** — what story the diagram tells
- **Preferences** — color scheme, style, specific layout requests

### 1b. Develop detailed solution

Based on the user's input, develop a detailed plan:
- Overall layout approach (horizontal flow, layered, hub-and-spoke, swim lanes, etc.)
- Component groupings and visual hierarchy
- Which icons to use (check `references/icon-catalog.md`)
- Palette selection (Corporate Blue, Warm Professional, Modern Slate, or Forest Green)

### 1c. Generate slug and create artifact directory

Generate a 2-4 word kebab-case slug (max 40 chars) that describes the diagram. Examples: `three-tier-arch`, `cicd-pipeline`, `incident-response-conops`.

**Slug collision check:** If `diagrams/{slug}/` already exists, append a differentiator (e.g., `three-tier-arch-v2`).

Create the artifact directory:
```bash
mkdir -p diagrams/{slug}
```

## Step 2: Craft the Image Generation Prompt

The user provides the image generation prompt. Use it **exactly as given** — do NOT rewrite, reorganize, paraphrase, or append to it. Save it verbatim to `diagrams/{slug}/prompt.md`.

If the user has not provided a prompt, ask them for one. Do not generate one yourself.

Show the user the saved prompt and wait for approval before proceeding to Step 3. The user may request revisions.

## Step 2b: Icons (Pre-generated Library + Custom Generation)

A library of 25 pre-generated icons is available in `assets/icons/` — these cover 90%+ of technical diagram needs (servers, databases, clouds, security, people, status indicators, etc.). See `references/icon-catalog.md` for the full catalog.

**Default workflow:** Use pre-generated icons from `assets/icons/` via the `path` field. No npm dependencies needed.

```json
{ "type": "icon", "path": "assets/icons/server_rack.png", "x": 2.5, "y": 1.5, "w": 0.35, "h": 0.35 }
```

**When to generate custom icons:** Only for concepts not in the catalog (e.g., "API gateway", "data lake", "IoT sensor").

```bash
# Single custom icon
python3 scripts/generate_icon.py "API gateway" --color "dark navy blue" -o diagrams/{slug}/icons/api_gateway.png

# Batch of custom icons
python3 scripts/generate_icon.py \
  --batch "API gateway,data lake,IoT sensor,message queue" \
  --color "dark navy blue" \
  --output-dir diagrams/{slug}/icons/
```

| Flag | Default | Description |
|------|---------|-------------|
| `description` (positional) | -- | Icon description (single mode) |
| `--batch` | -- | Comma-separated icon descriptions (batch mode) |
| `--color` | `"dark navy blue"` | Icon color |
| `--style` | `"flat minimalist technical icon"` | Style keywords |
| `--output-dir` | `/tmp/icons/` | Batch output directory |
| `-o` / `--output` | -- | Single-mode output path |
| `--icon-size` | `256` | Final PNG size in pixels |
| `--gen-size` | `1K` | Gemini generation size before post-processing |
| `--no-cache` | `false` | Skip cache lookup and force regeneration |
| `--cache-dir` | `~/.cache/pptx-diagram-icons/` | Override cache directory |

**Caching:** Icons are cached automatically after first generation. On subsequent runs with the same description, color, style, and size, the cached PNG is reused instantly (no Gemini call). Pre-generated icons in `assets/icons/` also serve as a cache tier for default-parameter requests. Use `--no-cache` to force regeneration (e.g., if quality was unsatisfactory). Cache location: `~/.cache/pptx-diagram-icons/`.

**QA check:** After generation, view the PNGs to verify icons are recognizable and visually consistent. Regenerate individual failures with adjusted prompts (use `--no-cache` to bypass the cache).

**Using custom icons in the diagram:** In Step 4's output JSON, use `path`:
```json
{ "type": "icon", "path": "diagrams/{slug}/icons/api_gateway.png", "x": 2.5, "y": 1.5, "w": 0.35, "h": 0.35 }
```

Pre-generated and custom icons can be mixed freely in the same diagram.

## Step 3: Generate the Reference Image

**IMPORTANT — File naming:** Always use a `-ref` suffix for reference images to prevent `soffice --convert-to png` from overwriting them. When soffice converts `foo.pptx` it outputs `foo.png` — if your reference image is also named `foo.png`, it gets clobbered.

```bash
python3 scripts/generate_image.py "YOUR DETAILED PROMPT HERE" -o diagrams/{slug}/{slug}-ref.png
```

**QA check:** After generation, view the image file (`diagrams/{slug}/{slug}-ref.png`) to verify:
- All requested components are present
- Text labels are readable
- Layout is clean and not cramped
- No artifacts or unwanted elements

If the image quality is poor or missing elements, refine the prompt and regenerate. You may need 2-3 iterations to get a good result.

This image is a **visual layout reference** — it will not be embedded in the final PPTX. It guides the automated JSON spec generation in Step 4.

## Step 4: Generate JSON Shape Specification

Use `image_to_spec.py` (Gemini vision) to automatically convert the reference image into a complete JSON shape specification. This single call replaces the manual describe-then-write workflow — Gemini analyzes the image and outputs build-ready JSON with all shape positions, colors, connectors, icons, alt text, and description.

```bash
python3 scripts/image_to_spec.py \
  -i diagrams/{slug}/{slug}-ref.png \
  -o diagrams/{slug}/{slug}-spec.json \
  --title "Three-Tier Architecture" \
  --palette "Corporate Blue"
```

| Flag | Default | Description |
|------|---------|-------------|
| `-i` / `--input` | required | Reference image path |
| `-o` / `--output` | required | Output JSON spec path |
| `--title` | `"Diagram"` | `meta.title` |
| `--subtitle` | — | `meta.subtitle` |
| `--palette` | `"Corporate Blue"` | Palette: Corporate Blue, Warm Professional, Modern Slate, or Forest Green |
| `--model` | `"gemini-3-pro-image-preview"` | Gemini model |
| `--api-key` | env `GEMINI_API_KEY` | API key override |
| `--no-validate` | false | Skip post-processing validation |

**What the script does:**
1. Sends the reference image to Gemini with embedded shape-spec knowledge (coordinate system, shape types, palettes, connector rules, icon catalog)
2. Gemini returns structured JSON matching the `build_slide.js` spec format
3. Post-processes the JSON: sanitizes hex colors, removes `route` from connectors, applies defaults, injects CLI metadata
4. Validates the spec and prints a report to stderr (element census, connector ID resolution, bounds check, palette coverage, font floor, overlap detection)

**Review the validation report** printed to stderr:
```
=== Spec Validation Report ===
Elements: 14 total (7 shapes, 6 connectors, 1 group)
Icons: 6 (all paths valid)
Palette: 3 distinct shape fills ✓
Bounds: 0 violations ✓
Connector IDs: 12/12 resolved ✓
Font floor: 0 fixes applied
Overlap: 0 collisions ✓
→ Ready to build
```

If the report shows warnings, review and fix the JSON before building. Common fixes:
- **Missing connector IDs**: Edit `from`/`to` to match actual shape `id` values
- **Bounds violations**: Shift elements into the 0–10" × 0.85–5.35" diagram area
- **Undersized shapes**: Increase `w`/`h` to meet minimums
- **Overlapping shapes**: Adjust positions for ≥0.4" gaps

**If the automated spec quality is poor**, fall back to the manual workflow in Appendix A.

## Step 5: Build the PPTX

Run the build script with the `--json` flag to generate native shapes:

```bash
node scripts/build_slide.js \
  --json diagrams/{slug}/{slug}-spec.json \
  --output diagrams/{slug}/{slug}.pptx
```

### Optional flags

| Flag | Default | Description |
|------|---------|-------------|
| `--no-artifacts` | `false` | Skip generating companion .description.md file |

All other metadata (title, subtitle, colors, footer, alt text, description) comes from the JSON spec's `meta` object.

### Legacy image mode (backward compatible)

The old `--image` mode still works for embedding a flat PNG:

```bash
node scripts/build_slide.js \
  --image diagrams/{slug}/{slug}-ref.png \
  --title "DIAGRAM TITLE" \
  --alt-text "ALT TEXT" \
  --output diagrams/{slug}/{slug}.pptx
```

## Step 6: QA and Iteration

After building the PPTX, verify the output visually and fix any issues.

### 6a. Convert PPTX to PNG

```bash
soffice --headless --convert-to png --outdir diagrams/{slug} diagrams/{slug}/{slug}.pptx
```

Note: This outputs `{slug}.png` which overwrites the companion PNG from `build_slide.js`. This is fine — the `-ref.png` original is preserved, and the QA render is what we want.

### 6b. Inspect the rendered PNG

View the converted PNG and run through the QA checklist (`references/qa-checklist.md`):

1. **Overlap** — shapes, labels, or icons overlapping
2. **Text overflow** — labels cut off or running outside shapes
3. **Out of bounds** — elements outside the visible slide area (0–10" x 0.85–5.35")
4. **Spacing** — inconsistent gaps between shapes in the same row/column
5. **Icons** — missing, invisible, or wrong size
6. **Connectors** — arrows not connecting to shape edges, labels overlapping shapes
7. **Color contrast** — text unreadable against its background
8. **Reference match** — rendered layout structurally matches the reference image from Step 3
9. **Shadow consistency** — if shadows are used, are they applied uniformly?
10. **Connector anchoring** — do connectors visually connect to shape edges?
11. **Font consistency** — is the same fontFace used throughout?
12. **Visual weight hierarchy** — do primary shapes visually "pop" more than secondary shapes?
13. **Color palette quality** — max 3 fill colors, all muted/desaturated, no bright primaries (`3B82F6`, `EF4444`)?
14. **Typography & spacing polish** — `charSpacing` on labels, adequate margins, ≥0.4" inter-shape gaps?
15. **Text-to-shape fit** — shapes wide enough for labels, textRuns shapes ≥ 2.0" × 0.8", diamonds ≥ 1.8" × 1.0"?
16. **Swim lane label placement** — lane names are separate `text` elements outside groups, not `group.label`? Phase headers are independent `text` elements?
17. **Connector label overlap** — labels don't overlap shapes? Use `labelOffset` to shift if needed?
18. **Grayscale hierarchy** — Tier 1/2/3 elements distinguishable without color
19. **Contrast** — text-on-fill combinations meet WCAG thresholds
20. **Data-ink ratio** — no redundant borders, shadows, or decorations
21. **Spacing scale** — all gaps match xs/sm/md/lg/xl tokens (0.1/0.2/0.4/0.6/0.8")

### 6c. Fix and rebuild

If issues are found: fix the JSON spec → rebuild the PPTX → re-convert to PNG → re-inspect.

**Maximum 2 fix cycles.** Most issues are spacing or alignment problems that are quick to fix by adjusting coordinates.

### 6d. Report remaining issues

If any issues remain after 2 fix cycles, report them to the user as known limitations (e.g., "The connector label between X and Y slightly overlaps — you may want to nudge it in PowerPoint").

## Output

All artifacts are saved to `diagrams/{slug}/`:

| File | Purpose |
|------|---------|
| `diagrams/{slug}/prompt.md` | Image generation prompt |
| `diagrams/{slug}/{slug}-ref.png` | Reference image (layout guide) |
| `diagrams/{slug}/{slug}-spec.json` | JSON shape specification |
| `diagrams/{slug}/{slug}.pptx` | Final PowerPoint with native editable shapes |
| `diagrams/{slug}/{slug}.description.md` | Alt text and metadata |
| `diagrams/{slug}/{slug}.png` | QA render of the PPTX |

Tell the user the output file paths and briefly describe the diagram that was generated. Emphasize that all shapes are **native and editable** — they can click, move, resize, and edit any element directly in PowerPoint.

---

## Appendix A: Manual Fallback Workflow

Use this manual workflow when `image_to_spec.py` output is unsatisfactory or when you need fine-grained control over the spec.

### A1. Describe the Reference Image

Use `image_to_text.py` (Gemini vision) to extract a detailed structural description of the reference image. This text becomes the source-of-truth for the JSON shape spec — you will not view the image directly when writing JSON.

**Call 1 — Structural layout description** (the key piece):

```bash
python3 scripts/image_to_text.py -i diagrams/{slug}/{slug}-ref.png "Describe the structural layout of this technical diagram in precise detail. For every shape: state its type (rectangle, rounded rectangle, diamond, oval, cylinder, cloud), approximate position (left/center/right, top/middle/bottom), approximate size relative to the slide, fill color, border color, and the exact text label inside it. For every arrow or connector: state its start element, end element, direction, line style (solid, dashed), arrowhead style, and any label text. For any background grouping boxes: state their position, size, fill color, border color, and label. For any divider lines: state orientation, position, and style. For standalone text labels: state their content, position, and styling. For any icons or visual symbols: describe their type (server, database, cloud, shield, lambda, bucket, etc.), position relative to their shape, and approximate size. For any description or annotation text below shapes: capture the exact text content. Describe the overall layout grid (how many columns/rows, spacing pattern)."
```

Save the output to `diagrams/{slug}/{slug}-layout.txt`.

**Call 2 — Alt text** (accessibility summary):

```bash
python3 scripts/image_to_text.py -i diagrams/{slug}/{slug}-ref.png "Describe this technical diagram in 2-3 sentences for screen reader alt text. Focus on the type of diagram, the key components shown, and the main relationships or data flow depicted."
```

Review the output and trim to a concise 2-3 sentence alt text summary.

**Call 3 — Full description** (for `.description.md`):

```bash
python3 scripts/image_to_text.py -i diagrams/{slug}/{slug}-ref.png "Provide a detailed description of this technical diagram. Describe each component, their relationships, data flows, and the overall purpose of the diagram."
```

### A2. Create JSON Shape Specification (Manual)

This is the core manual step. You will translate the **structural text description** from A1 into a JSON file that `build_slide.js` renders as native PowerPoint shapes.

1. Read the structural layout description from `diagrams/{slug}/{slug}-layout.txt`
2. Read `references/shape-spec.md` for the full JSON schema, coordinate system, and worked examples
3. Write a JSON file (`diagrams/{slug}/{slug}-spec.json`) that recreates the diagram as native shapes

**Translation process:**
1. Map each described shape → `shapeType` values (rounded rectangle → `roundedRect`, diamond → `diamond`, etc.)
2. Convert described positions → inch coordinates on the 10" × 5.625" slide
3. Map described colors → hex values
4. Create connectors between described elements
5. Set `meta.referenceImage` to `diagrams/{slug}/{slug}-ref.png`
6. Set `meta.altText` and `meta.description` from A1 outputs

**Coordinate system:**
- Slide is 10" wide × 5.625" tall
- Title bar occupies y=0 to y=0.75
- Diagram area is y=0.85 to y=5.35
- All coordinates are in inches

**Key principles:**
- Place `group` elements first in the array (they render behind other shapes)
- Use `shape` for all boxes, ovals, diamonds, cylinders, etc.
- **Assign `id` to every shape that will have connectors.** Use `from`/`to` connector anchoring with `fromSide`/`toSide` instead of manual coordinate calculation — this is the single most effective way to eliminate visual errors
- Use `connector` for arrows between shapes. Prefer shape-anchored mode (`from`/`to`) over absolute coordinates (`x1,y1,x2,y2`)
- Connectors default to `route: "elbow"` (orthogonal L-shaped paths with chamfered corners). **CRITICAL: Never use `route: "straight"` unless shapes share the EXACT same X or Y. When in doubt, omit `route` entirely — the code defaults to elbow.**
- **Select a consulting palette** from shape-spec.md (Corporate Blue, Warm Professional, Modern Slate, or Forest Green). Use max 3 fill colors. Distribute all 3 colors across shapes. Assign Accent to at least 2 shapes per diagram. **Never use bright saturated primaries** (`3B82F6`, `EF4444`, `10B981`, `F59E0B`)
- **Apply visual weight hierarchy** — use the 3-tier shadow/border system from shape-spec.md: Tier 1 (primary: dark fill, borderless, strong shadow), Tier 2 (secondary: medium fill, borderless, moderate shadow), Tier 3 (backgrounds: light fill, soft shadow). Never combine borders and shadows on the same element
- **Typography polish** — add `charSpacing: 1` on primary shape labels, `charSpacing: 1.5` on title via `meta.titleCharSpacing`, use `margin: [8,10,8,10]` for breathing room inside shapes
- **Generous spacing** — minimum 0.4" gap between adjacent shapes, 0.2" padding inside groups
- **Data-ink ratio** — every visual element (border, shadow, decoration) must convey information. Apply the removal test: if removing it doesn't reduce clarity, remove it. Don't add borders to Tier 1 shapes that already have dark fills + strong shadows
- **Spacing scale** — use the modular scale from shape-spec.md: xs(0.1"), sm(0.2"), md(0.4"), lg(0.6"), xl(0.8"). Every gap should map to a token. Ad-hoc values break visual rhythm
- **Composition** — align the primary flow on the diagram's center axis. Make the entry-point shape the most visually prominent. Use proximity to group related shapes (md gaps within groups, lg gaps between groups)
- **Grayscale-first** — verify that your tier hierarchy works by mentally converting to grayscale before choosing palette colors. If Tier 1/2/3 shapes aren't distinguishable by fill darkness alone, adjust relative lightness before adding color. Color should add meaning on top of an already-clear hierarchy
- Use `textRuns` for primary shapes that need title + subtitle formatting (e.g., service name + version or role)
- Use `text` for standalone labels (lane names, phase headers, annotations)
- Use `divider` for separator lines
- Use `icon` for visual icons — **strongly recommended** for architecture, cloud, and network diagrams. Place a 0.35"×0.35" icon above or inside each major shape. Use pre-generated icons from `assets/icons/` via `path` field (see `references/icon-catalog.md`). Skip only for abstract concepts with no clear icon mapping
- Map described elements to appropriate shape types using the structural description
- Use `fontFace` for font control (default: "Calibri"), `fontItalic`/`fontUnderline` for styling. Text auto-shrinks to fit by default (`fit: "shrink"`) — this is a safety net, not a substitute for proper sizing

**Minimum shape sizes:**
- Shape with `label`: min `w` = `max(1.5, label.length * 0.13)` at fontSize 10
- Shape with `textRuns`: min `w` = 2.0", min `h` = 0.8"
- Diamond: min 1.8" × 1.0"
- Cylinder: min `h` = 1.0"
- Architecture diagram shapes: min `w` = 1.8", recommended 2.0"+ to accommodate icon + label
- Leave 0.05" gap between icon and shape top, 0.05" gap between shape bottom and description text
- **Typography hierarchy:** Primary shape labels 11-12pt bold, connector labels 11pt, description text 10pt, group labels 10pt. Absolute floor: 10pt — no 9pt text anywhere
- Minimum font size: 10pt absolute floor for all text elements
- Always rely on default `fit: "shrink"` as safety net

**Component stack pattern** (architecture diagrams):
For each major component, create a vertical stack:
1. `icon` element (0.35" × 0.35") centered above the shape
2. `shape` element with bold service name (min 1.8" wide)
3. `text` element below with 1-2 line italic description (fontSize 10, fontColor "64748B")

Example — one Lambda component:
  icon:  { x: 5.55, y: 1.5, w: 0.35, h: 0.35, path: "assets/icons/lambda_function.png" }
  shape: { x: 5.0,  y: 1.9, w: 1.8,  h: 0.6,  label: "Products Lambda" }
  text:  { x: 5.0,  y: 2.55, w: 1.8, h: 0.4, text: "Product Catalog\nLogic & Management", fontSize: 10, fontItalic: true, align: "center" }

This pattern makes diagrams instantly scannable — users recognize components by icon before reading text.

**Description text:** For architecture and cloud diagrams, add a small italic `text` element (fontSize 10, fontColor "64748B") below each major shape with a 1-2 line role description. This is what makes reference images feel information-rich.

**Swim lane pattern:** For CONOPS/swim lane diagrams:
1. Create `group` elements for lane backgrounds with NO `label`
2. Create separate `text` elements for lane names positioned LEFT of the groups (`x: 0.2, w: 1.5, align: "right"`)
3. Start groups at `x: 1.8` to leave room for lane name text
4. Create separate `text` elements for phase headers ABOVE the diagram area

**Connector routing strategy:**
- **Omit the `route` property entirely** — the code defaults to elbow routing with chamfered corners. This is correct for 95%+ of connectors
- Never use diagonal connectors. All lines must be parallel or perpendicular to slide margins
- Only add `route: "straight"` when you have **manually verified** that the two shapes share the exact same X coordinate (vertical line) or exact same Y coordinate (horizontal line). If in doubt, don't set `route` at all
- Horizontal flows: `fromSide: "right"` → `toSide: "left"` (elbow default handles offset Y)
- Vertical flows: `fromSide: "bottom"` → `toSide: "top"` (elbow default handles offset X)
- Cross-lane: elbow default
- Use `labelOffset` to shift labels away from shape overlap
- Labels auto-fill with `meta.bgColor`. Set `labelBgColor` on connectors over non-white group backgrounds

**Connector crossing avoidance:**
- Arrange shapes to minimize connector crossings — reposition shapes rather than accepting crossed lines
- When crossings are unavoidable, differentiate with `lineDash`: solid for primary flow, `"dash"` for secondary
- Use `labelOffset` with opposite signs on nearby connectors to separate labels (e.g., `+0.3` and `-0.3`)

**Label collision avoidance:**
- When two connectors run within 0.4" of each other, use opposite `labelOffset` values to prevent label overlap
- Connector labels have background fills that mask the line underneath — the `h: 0.30` label height covers the line cleanly
