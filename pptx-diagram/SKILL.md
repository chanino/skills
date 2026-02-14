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

You are creating a technical diagram as a polished single-slide PPTX with **native editable shapes**. The output contains real PowerPoint shapes (rectangles, diamonds, arrows, text boxes) that the user can click, move, resize, and edit directly in PowerPoint. Follow these 5 steps in order.

## Step 1: Craft the Image Generation Prompt

Read the prompt engineering guide at `references/diagram-prompts.md` for patterns and tips.

Based on the user's request, build a detailed prompt that specifies:
- Diagram type (architecture, flowchart, network, sequence, ER, data flow, CONOPS, etc.)
- All components and their relationships
- Clean, flat, modern design style
- White background, 16:9 aspect ratio
- Readable text labels on all elements
- Limited color palette (2-3 colors)
- Component count kept reasonable (5-10 major elements)
- "No watermarks, no stock photo artifacts"

## Step 2: Generate the Reference Image

```bash
python3 /mnt/c/Users/Noah/claude/generate_image.py "YOUR DETAILED PROMPT HERE" -o /tmp/diagram.png
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
python3 /mnt/c/Users/Noah/claude/image_to_text.py -i /tmp/diagram.png "Describe the structural layout of this technical diagram in precise detail. For every shape: state its type (rectangle, rounded rectangle, diamond, oval, cylinder, cloud), approximate position (left/center/right, top/middle/bottom), approximate size relative to the slide, fill color, border color, and the exact text label inside it. For every arrow or connector: state its start element, end element, direction, line style (solid, dashed), arrowhead style, and any label text. For any background grouping boxes: state their position, size, fill color, border color, and label. For any divider lines: state orientation, position, and style. For standalone text labels: state their content, position, and styling. Describe the overall layout grid (how many columns/rows, spacing pattern)."
```

Save the output to `/tmp/diagram-layout.txt`.

**Call 2 — Alt text** (accessibility summary):

```bash
python3 /mnt/c/Users/Noah/claude/image_to_text.py -i /tmp/diagram.png "Describe this technical diagram in 2-3 sentences for screen reader alt text. Focus on the type of diagram, the key components shown, and the main relationships or data flow depicted."
```

Review the output and trim to a concise 2-3 sentence alt text summary.

**Call 3 — Full description** (for `.description.md`):

```bash
python3 /mnt/c/Users/Noah/claude/image_to_text.py -i /tmp/diagram.png "Provide a detailed description of this technical diagram. Describe each component, their relationships, data flows, and the overall purpose of the diagram."
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
- Use `connector` for arrows between shapes (absolute coordinates)
- Use `text` for standalone labels (lane names, phase headers, annotations)
- Use `divider` for separator lines
- Map described elements to appropriate shape types using the structural description
- Use consistent spacing: 0.2" gaps between shapes, 0.1" padding inside groups

## Step 5: Build the PPTX

Run the build script with the `--json` flag to generate native shapes:

```bash
node /home/noah/.claude/skills/pptx-diagram/scripts/build_slide.js \
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
node /home/noah/.claude/skills/pptx-diagram/scripts/build_slide.js \
  --image /tmp/diagram.png \
  --title "DIAGRAM TITLE" \
  --alt-text "ALT TEXT" \
  --output output.pptx
```

## Output

The build script produces up to 3 files:

| File | Purpose |
|------|---------|
| `{name}.pptx` | The PowerPoint slide with native editable shapes |
| `{name}.png` | Reference image used as layout guide (copied from `meta.referenceImage`) |
| `{name}.description.md` | Markdown file with title, alt text, description, and generation metadata |

Tell the user the output file paths and briefly describe the diagram that was generated. Emphasize that all shapes are **native and editable** — they can click, move, resize, and edit any element directly in PowerPoint.
