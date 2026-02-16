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

## Step 1: Craft the Image Generation Prompt

Read the prompt engineering guide at `references/diagram-prompts.md` for patterns and tips.

Based on the user's request, build a detailed prompt that specifies:
- Diagram type (architecture, flowchart, network, sequence, ER, data flow, CONOPS, etc.)
- All components and their relationships
- Clean, consulting-grade design style with muted, desaturated colors
- White background, 16:9 aspect ratio
- Readable text labels on all elements
- Limited color palette (2-3 colors)
- Component count kept reasonable (5-10 major elements)
- "No watermarks, no stock photo artifacts"

## Step 2: Generate the Reference Image

```bash
python3 scripts/generate_image.py "YOUR DETAILED PROMPT HERE" -o /tmp/diagram.png
```

**QA check:** After generation, view the image file (`/tmp/diagram.png`) to verify:
- All requested components are present
- Text labels are readable
- Layout is clean and not cramped
- No artifacts or unwanted elements

If the image quality is poor or missing elements, refine the prompt and regenerate. You may need 2-3 iterations to get a good result.

This image is a **visual layout reference** — it will not be embedded in the final PPTX. It guides your JSON shape specification in Step 3.

## Step 3: Describe the Reference Image

Use `image_to_text.py` (Gemini vision) to extract a detailed structural description of the reference image. This text becomes the source-of-truth for the JSON shape spec in Step 4 — you will not view the image directly when writing JSON.

**Call 1 — Structural layout description** (the key piece):

```bash
python3 scripts/image_to_text.py -i /tmp/diagram.png "Describe the structural layout of this technical diagram in precise detail. For every shape: state its type (rectangle, rounded rectangle, diamond, oval, cylinder, cloud), approximate position (left/center/right, top/middle/bottom), approximate size relative to the slide, fill color, border color, and the exact text label inside it. For every arrow or connector: state its start element, end element, direction, line style (solid, dashed), arrowhead style, and any label text. For any background grouping boxes: state their position, size, fill color, border color, and label. For any divider lines: state orientation, position, and style. For standalone text labels: state their content, position, and styling. For any icons or visual symbols: describe their type (server, database, cloud, shield, lambda, bucket, etc.), position relative to their shape, and approximate size. For any description or annotation text below shapes: capture the exact text content. Describe the overall layout grid (how many columns/rows, spacing pattern)."
```

Save the output to `/tmp/diagram-layout.txt`.

**Call 2 — Alt text** (accessibility summary):

```bash
python3 scripts/image_to_text.py -i /tmp/diagram.png "Describe this technical diagram in 2-3 sentences for screen reader alt text. Focus on the type of diagram, the key components shown, and the main relationships or data flow depicted."
```

Review the output and trim to a concise 2-3 sentence alt text summary.

**Call 3 — Full description** (for `.description.md`):

```bash
python3 scripts/image_to_text.py -i /tmp/diagram.png "Provide a detailed description of this technical diagram. Describe each component, their relationships, data flows, and the overall purpose of the diagram."
```

## Step 4: Create JSON Shape Specification

This is the core step. You will translate the **structural text description** from Step 3 into a JSON file that `build_slide.js` renders as native PowerPoint shapes.

1. Read the structural layout description from `/tmp/diagram-layout.txt`
2. Read `references/shape-spec.md` for the full JSON schema, coordinate system, and worked examples
3. Write a JSON file (`/tmp/diagram-spec.json`) that recreates the diagram as native shapes

**Translation process:**
1. Map each described shape → `shapeType` values (rounded rectangle → `roundedRect`, diamond → `diamond`, etc.)
2. Convert described positions → inch coordinates on the 10" × 5.625" slide
3. Map described colors → hex values
4. Create connectors between described elements
5. Set `meta.referenceImage` to `/tmp/diagram.png`
6. Set `meta.altText` and `meta.description` from Step 3 outputs

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
- Use `"route": "elbow"` for connectors that need orthogonal L-shaped paths
- **Select a consulting palette** from shape-spec.md (Corporate Blue, Warm Professional, Modern Slate, or Forest Green). Use max 3 fill colors. **Never use bright saturated primaries** (`3B82F6`, `EF4444`, `10B981`, `F59E0B`)
- **Apply visual weight hierarchy** — use the 3-tier shadow/border system from shape-spec.md: Tier 1 (primary: dark fill, borderless, strong shadow), Tier 2 (secondary: medium fill, thin border, light shadow), Tier 3 (backgrounds: light fill, soft shadow)
- **Typography polish** — add `charSpacing: 1` on primary shape labels, `charSpacing: 1.5` on title via `meta.titleCharSpacing`, use `margin: [8,10,8,10]` for breathing room inside shapes
- **Generous spacing** — minimum 0.4" gap between adjacent shapes, 0.2" padding inside groups
- **Data-ink ratio** — every visual element (border, shadow, decoration) must convey information. Apply the removal test: if removing it doesn't reduce clarity, remove it. Don't add borders to Tier 1 shapes that already have dark fills + strong shadows
- **Spacing scale** — use the modular scale from shape-spec.md: xs(0.1"), sm(0.2"), md(0.4"), lg(0.6"), xl(0.8"). Every gap should map to a token. Ad-hoc values break visual rhythm
- **Composition** — align the primary flow on the diagram's center axis. Make the entry-point shape the most visually prominent. Use proximity to group related shapes (md gaps within groups, lg gaps between groups)
- **Grayscale-first** — verify that your tier hierarchy works by mentally converting to grayscale before choosing palette colors. If Tier 1/2/3 shapes aren't distinguishable by fill darkness alone, adjust relative lightness before adding color. Color should add meaning on top of an already-clear hierarchy
- Use `textRuns` for primary shapes that need title + subtitle formatting (e.g., service name + version or role)
- Use `text` for standalone labels (lane names, phase headers, annotations)
- Use `divider` for separator lines
- Use `icon` for visual icons — **strongly recommended** for architecture, cloud, and network diagrams. Place a 0.35"×0.35" icon above or inside each major shape. See `references/icon-catalog.md` for names. Skip only for abstract concepts with no clear icon mapping
- Map described elements to appropriate shape types using the structural description
- Use `fontFace` for font control (default: "Calibri"), `fontItalic`/`fontUnderline` for styling. Text auto-shrinks to fit by default (`fit: "shrink"`) — this is a safety net, not a substitute for proper sizing

**Minimum shape sizes:**
- Shape with `label`: min `w` = `max(1.5, label.length * 0.13)` at fontSize 10
- Shape with `textRuns`: min `w` = 2.0", min `h` = 0.8"
- Diamond: min 1.8" × 1.0"
- Cylinder: min `h` = 1.0"
- Architecture diagram shapes: min `w` = 1.8", recommended 2.0"+ to accommodate icon + label
- Leave 0.05" gap between icon and shape top, 0.05" gap between shape bottom and description text
- Always rely on default `fit: "shrink"` as safety net

**Component stack pattern** (architecture diagrams):
For each major component, create a vertical stack:
1. `icon` element (0.35" × 0.35") centered above the shape
2. `shape` element with bold service name (min 1.8" wide)
3. `text` element below with 1-2 line italic description (fontSize 7, fontColor "64748B")

Example — one Lambda component:
  icon:  { x: 5.55, y: 1.5, w: 0.35, h: 0.35, name: "FaCode", color: "FFFFFF" }
  shape: { x: 5.0,  y: 1.9, w: 1.8,  h: 0.6,  label: "Products Lambda" }
  text:  { x: 5.0,  y: 2.55, w: 1.8, h: 0.4, text: "Product Catalog\nLogic & Management", fontSize: 7, fontItalic: true, align: "center" }

This pattern makes diagrams instantly scannable — users recognize components by icon before reading text.

**Description text:** For architecture and cloud diagrams, add a small italic `text` element (fontSize 7-8, fontColor "64748B") below each major shape with a 1-2 line role description. This is what makes reference images feel information-rich.

**Swim lane pattern:** For CONOPS/swim lane diagrams:
1. Create `group` elements for lane backgrounds with NO `label`
2. Create separate `text` elements for lane names positioned LEFT of the groups (`x: 0.2, w: 1.5, align: "right"`)
3. Start groups at `x: 1.8` to leave room for lane name text
4. Create separate `text` elements for phase headers ABOVE the diagram area

**Connector routing strategy:**
- Horizontal flows: straight connectors, `fromSide: "right"` → `toSide: "left"`
- Vertical flows: straight connectors, `fromSide: "bottom"` → `toSide: "top"`
- Cross-lane: use `route: "elbow"`
- Use `labelOffset` to shift labels away from shape overlap

## Step 5: Build the PPTX

Run the build script with the `--json` flag to generate native shapes:

```bash
node scripts/build_slide.js \
  --json /tmp/diagram-spec.json \
  --output output.pptx
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
  --image /tmp/diagram.png \
  --title "DIAGRAM TITLE" \
  --alt-text "ALT TEXT" \
  --output output.pptx
```

## Step 6: QA and Iteration

After building the PPTX, verify the output visually and fix any issues.

### 6a. Convert PPTX to PNG

```bash
soffice --headless --convert-to png --outdir /tmp output.pptx
```

### 6b. Inspect the rendered PNG

View the converted PNG and run through the QA checklist (`references/qa-checklist.md`):

1. **Overlap** — shapes, labels, or icons overlapping
2. **Text overflow** — labels cut off or running outside shapes
3. **Out of bounds** — elements outside the visible slide area (0–10" x 0.85–5.35")
4. **Spacing** — inconsistent gaps between shapes in the same row/column
5. **Icons** — missing, invisible, or wrong size
6. **Connectors** — arrows not connecting to shape edges, labels overlapping shapes
7. **Color contrast** — text unreadable against its background
8. **Reference match** — rendered layout structurally matches the reference image from Step 2
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

The build script produces up to 3 files:

| File | Purpose |
|------|---------|
| `{name}.pptx` | The PowerPoint slide with native editable shapes |
| `{name}.png` | Reference image used as layout guide (copied from `meta.referenceImage`) |
| `{name}.description.md` | Markdown file with title, alt text, description, and generation metadata |

Tell the user the output file paths and briefly describe the diagram that was generated. Emphasize that all shapes are **native and editable** — they can click, move, resize, and edit any element directly in PowerPoint.
