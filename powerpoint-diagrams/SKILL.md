---
description: "This skill should be used when the user asks to 'create a PowerPoint diagram', 'make a flowchart in PowerPoint', 'create an org chart', 'make an architecture diagram', 'generate a PPTX diagram', 'create a .pptx file', 'draw a diagram in PowerPoint', or wants to create any visual diagram or chart to be saved as a .pptx file."
---

# PowerPoint Diagrams Skill

Generate `.pptx` diagrams using `python-pptx` + OOXML/DrawingML XML. Each diagram is designed from first principles — not copied from examples.

## Prerequisites

```bash
pip install python-pptx lxml
pip install cairosvg  # optional: enables icon support via Iconify API
```

## Workflow: 6-Phase Design Process

Phases 1-2 are internal analysis. Do not narrate design decisions to the user unless asked. Only surface issues that require user input.

### Phase 0: Interview & Scope

Clarify the request before any design work. Ask the user when information is missing or ambiguous:

- **Purpose**: "What question should this diagram answer?" (explain a flow? show deployment? compare options?)
- **Audience**: Executive / PM / Developer / Security / Ops — pick one primary
- **Diagram level**: Context / Container / Component / Sequence / Deployment (C4-inspired — don't mix levels in one view)
- **Constraints**: Slide count, print vs screen, brand colors, existing notation conventions

**Smart gating** — If the user's request already specifies purpose, audience, and scope clearly, skip the interview. Don't ask questions you can answer from context.

Examples:
- "Make a flowchart of our auth flow" → skip interview (diagram type and content are evident)
- "Create an architecture diagram showing how our microservices communicate" → skip interview (purpose and scope are clear)
- "Make me a diagram" → interview needed (purpose and scope are ambiguous)
- "Diagram our system" → interview needed (which level? which audience?)

> **Gate**: Is purpose, audience, and diagram level clear? If not → ask the user before proceeding.

### Phase 1: Analyze & Deconstruct

Build a semantic inventory of the user's request:

1. **Classify elements** as node, edge, container, or annotation (see `methodology.md` §1)
2. **Identify visual rhetoric**: sequential flow, hierarchy, containment, radial, network, or dependency
3. **Assess complexity**: count nodes, edges, nesting levels. If >10 nodes or >3 nesting levels, plan multi-slide progressive disclosure.
4. **Select layout algorithm** using this decision table:

| Algorithm | Best for | Node limit | Key constraint |
|-----------|----------|------------|----------------|
| **Layered / Hierarchical** | DAGs, org charts, class hierarchies | 15-25 | Minimize edge crossings between layers |
| **Hub-and-Spoke (Radial)** | API gateways, event buses, central coordinators | 8-12 spokes | Equal angular spacing; hub visually dominant |
| **Orthogonal / Grid** | Mesh networks, matrix orgs, comparison charts | 16-20 | Strict row/column alignment |
| **Swimlane** | Cross-cutting concerns, layered architectures | 3-5 lanes | Lane labels readable; inter-lane edges route vertically |
| **Timeline / Phased** | Roadmaps, migration plans, sprint sequences | 5-8 phases | Equal phase width; shared horizontal axis |
| **Force-directed (manual)** | Organic relationships, brainstorming | 8-12 | Use only when no hierarchy exists |

> **Gate**: Can every element be classified unambiguously as node/edge/container/annotation? Is there exactly one layout algorithm selected? If not → re-read the request; ask user if domain is ambiguous.

### Phase 2: Design Visual Grammar

Before writing any code:

1. **Shape mapping**: Assign a shape preset to each semantic role. Limit to 2-4 core shapes (see `methodology.md` §5).
2. **Color assignment**: Pick 3-5 semantic colors from a palette in `reference.md`. Each color = one meaning across the diagram set.
3. **Stroke hierarchy**: Primary flow = 2pt solid, secondary = 1.5pt solid, optional = 1pt dashed
4. **Size hierarchy**: Hub/primary = 1.3x, standard = 1.0x, secondary = 0.85x
5. **Scan path**: Define the reader's eye movement (L→R for flow, top→down for hierarchy, center→out for radial). Entry points top-left, data stores lower (see `methodology.md` §1).
6. **Typography**: One font family (Calibri default). Node labels 10-12pt, connector labels 9-10pt (see `methodology.md` §5.5).
7. **Legend placement**: If the diagram uses 3+ semantic colors or 2+ line styles, plan a legend. Identify which corner has the most available space (default: bottom-right).
8. **Icon assignment** (optional): If the diagram benefits from icons (architecture, deployment, hub-spoke), identify which shapes should have icons and assign Iconify keys (e.g., `mdi:database`, `tabler:cloud`) or local file paths. Icons are NOT appropriate for abstract flowcharts, org charts, or decision diagrams where shape presets already carry semantic meaning. See `methodology.md` §5.6.

> **Gate**: Does the shape grammar use ≤4 core shapes? Are colors distinguishable under simulated color blindness (pair color with shape/line style)? If not → simplify; add secondary encoding.

### Phase 3: Generate Script

Write a standalone Python script using python-pptx for layout + OOXML XML for visual effects.

**Anti-pattern warning**: Do NOT copy an example and change labels. Generate from scratch based on Phase 1-2 analysis. Examples demonstrate techniques, not templates.

While generating, apply:
- **Grid alignment**: Snap to 8-pt grid; consistent margins (see `methodology.md` §2, §9)
- **Gestalt grouping**: proximity for same-group nodes, common region for containers, similarity for same-role nodes (see `methodology.md` §3)
- **Data-ink ratio**: every visual effect must encode information. Functional gradients/shadows only — no decorative effects (see `methodology.md` §4)
- **Connector discipline**: one connector style, orthogonal routing, ≤2 crossings per region (see `methodology.md` §5)
- **Label hygiene**: nouns for nodes, verb phrases for connectors, max 2 lines per box (see `methodology.md` §5.5)
- **Mental squint test**: if you blur the layout, can you still see the group structure and flow direction?
- **Legend**: If the diagram uses 3+ semantic colors or 2+ line styles, include a `make_legend_xml()` call (see `references/reference.md`). Build entries from the `STYLE_COLORS` dict (or equivalent). Place the legend as the **last element** in z-order (on top). Default to **bottom-right**; use **bottom-left** if bottom-right is occupied by diagram content.
- **Icons** (optional): If Phase 2 identified icon assignments, add an `ICONS` dict to the data section mapping component IDs to icon keys (Iconify `prefix:name` or local file paths). Include `resolve_icon()`, `enrich_shape_with_icon()`, and `enrich_pptx_with_icons()` helpers (see `references/reference.md`), and call `enrich_pptx_with_icons()` after `prs.save()`. Icons require `cairosvg` for SVG-to-PNG conversion.

> **Gate**: Does the script run without errors? Does the PPTX open cleanly? If not → fix the code before continuing.

#### Phase 3b: Run & Render

After the script passes the Phase 3 gate:

1. **Run the script**: `python3 <script>.py`
2. **Render to PNG** (macOS): `qlmanage -t -s 1920 -o /tmp <output>.pptx`
3. Output is at `/tmp/<output>.pptx.png`

> **Gate**: Script runs without errors, PPTX file created, PNG rendered successfully. If not → fix and re-run.

#### Phase 3c: Enrich with Icons (Optional)

If the diagram uses icons (defined by an `ICONS` dict in the script):

1. The script's `enrich_pptx_with_icons()` call post-processes the saved PPTX
2. For each icon assignment:
   - Resolves the icon key (Iconify API download, SVG→PNG conversion, caching in `/tmp/diagram_icons/`)
   - Places the icon centered in the upper portion of the target shape
   - Adjusts text body to bottom-anchor, pushing the label below the icon
3. Re-saves the PPTX

Prerequisites: `pip install cairosvg` (in addition to python-pptx, lxml)

If cairosvg is not installed, the enrichment step is skipped gracefully — the diagram is still valid without icons. A warning is printed listing which icons were skipped.

> **Gate**: Icons render at correct size and position. Text labels remain readable below icons. If icons are missing (resolution failed), the diagram is still structurally valid.

### Phase 4: Validate (Structural + Visual)

Two-stage validation: programmatic checks first, then visual inspection.

#### Phase 4a: Structural Checks (Programmatic)

Copy the QC function below into a temp script (e.g., `/tmp/qc_check.py`), run it against the generated PPTX, and fix any reported issues before proceeding to visual inspection.

```python
"""Structural QC checker for python-pptx diagrams."""
from pptx import Presentation
from pptx.util import Inches, Emu
import sys

def run_qc(pptx_path):
    prs = Presentation(pptx_path)
    slide_w = prs.slide_width
    slide_h = prs.slide_height
    issues = []

    for slide_idx, slide in enumerate(prs.slides):
        shapes = list(slide.shapes)
        rects = []  # (left, top, right, bottom, name, is_bg)

        for s in shapes:
            if not hasattr(s, 'left') or s.left is None:
                continue
            l, t = s.left, s.top
            r, b = l + s.width, t + s.height
            name = s.name or "(unnamed)"

            # Out-of-bounds check
            if r > slide_w:
                over = (r - slide_w) / 914400
                issues.append(f"Slide {slide_idx+1}: '{name}' extends {over:.2f}\" past right edge")
            if b > slide_h:
                over = (b - slide_h) / 914400
                issues.append(f"Slide {slide_idx+1}: '{name}' extends {over:.2f}\" past bottom edge")

            # Tight margin check (0.05" = 45720 EMU) — skip background and full-span shapes
            is_bg = (s.width > slide_w * 0.9 and s.height > slide_h * 0.9)
            is_full_span = (s.width > slide_w * 0.85 or s.height > slide_h * 0.85)
            margin = 45720
            if not is_full_span:
                if l < margin:
                    issues.append(f"Slide {slide_idx+1}: '{name}' within 0.05\" of left edge")
                if t < margin:
                    issues.append(f"Slide {slide_idx+1}: '{name}' within 0.05\" of top edge")
                if r > slide_w - margin:
                    issues.append(f"Slide {slide_idx+1}: '{name}' within 0.05\" of right edge")
                if b > slide_h - margin:
                    issues.append(f"Slide {slide_idx+1}: '{name}' within 0.05\" of bottom edge")

            rects.append((l, t, r, b, name, is_bg))

            # Text-to-shape fit check
            if s.has_text_frame:
                text = s.text_frame.text.strip()
                if text:
                    w_inches = s.width / 914400
                    h_inches = s.height / 914400
                    # Rough heuristic: 7pt per char width, 18pt per line height
                    lines = text.split('\n')
                    max_chars = max(len(line) for line in lines)
                    needed_w = max_chars * 0.07 + 0.2  # 0.2" padding
                    needed_h = len(lines) * 0.25 + 0.15  # 0.15" padding
                    if w_inches < needed_w * 0.7:
                        issues.append(f"Slide {slide_idx+1}: '{name}' may be too narrow for text '{text[:30]}...' ({w_inches:.1f}\" vs ~{needed_w:.1f}\" needed)")
                    if h_inches < needed_h * 0.7:
                        issues.append(f"Slide {slide_idx+1}: '{name}' may be too short for text '{text[:30]}...' ({h_inches:.1f}\" vs ~{needed_h:.1f}\" needed)")

        # Overlap check — skip containment pairs and connector-on-connector
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                l1, t1, r1, b1, n1, bg1 = rects[i]
                l2, t2, r2, b2, n2, bg2 = rects[j]
                if bg1 or bg2:
                    continue
                # Check if one fully contains the other (intentional containment)
                if (l1 <= l2 and t1 <= t2 and r1 >= r2 and b1 >= b2):
                    continue
                if (l2 <= l1 and t2 <= t1 and r2 >= r1 and b2 >= b1):
                    continue
                # Check overlap
                ox = max(0, min(r1, r2) - max(l1, l2))
                oy = max(0, min(b1, b2) - max(t1, t2))
                overlap_area = (ox / 914400) * (oy / 914400)  # sq inches
                if overlap_area > 0.02:
                    # Skip if either shape is a connector/arrow (endpoint overlaps are by design)
                    if any(k in n1.lower() for k in ("connector", "arrow", "line")):
                        continue
                    if any(k in n2.lower() for k in ("connector", "arrow", "line")):
                        continue
                    issues.append(f"Slide {slide_idx+1}: '{n1}' and '{n2}' overlap by {overlap_area:.2f} sq in")

    if issues:
        print(f"QC FAILED — {len(issues)} issue(s):")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("QC PASSED — no structural issues found.")
    return issues

if __name__ == "__main__":
    run_qc(sys.argv[1])
```

Run: `python3 /tmp/qc_check.py <output>.pptx`

Fix any reported issues in the generation script, re-run the script, re-check until clean.

> **Gate**: Structural checker returns zero issues. If not → fix generation script and re-run.

#### Phase 4b: Visual Inspection

After structural checks pass:

1. **Render** (or re-render): `qlmanage -t -s 1920 -o /tmp <output>.pptx`
2. **View the PNG** using the Read tool on `/tmp/<output>.pptx.png`
3. **Assess against visual checklist**:
   - [ ] All text readable — no invisible/tiny labels
   - [ ] Balanced layout — content uses available space; no excessive whitespace or crowding
   - [ ] Shapes have clear boundaries — no floating text without containers
   - [ ] Connectors route cleanly — minimal crossings, no arrows through shapes/text
   - [ ] Title separated from content — no overlaps between title and diagram elements
   - [ ] Nothing clipped at edges — all shapes fully visible
   - [ ] Legend present when diagram uses 3+ colors — entries match actual color→role mapping
   - [ ] Legend does not overlap diagram content
   - [ ] Icons (if present) are visible, correctly sized, and centered within shapes
   - [ ] Text labels below icons are not clipped or overlapping the icon
   - [ ] Icon style is consistent (all monochrome white, or all colored for vendor icons)
   - [ ] Professional appearance at presentation scale

4. **Fix → re-run → re-render → re-inspect.** Max 3 total visual passes. After 3, report remaining issues to the user rather than looping indefinitely.

> **Gate**: Structural checks return zero issues AND visual inspection passes all checklist items. If not → iterate (up to 3 passes), then report.

### Phase 5: Iterate

Based on user feedback or QC findings:

- Split into context + detail slides (see `methodology.md` §6)
- Reduce secondary node size
- Collapse symmetric branches with "x N" annotation
- Remove optional edges from overview slide
- Fix any anti-patterns identified in validation

**Important**: When iterating based on user feedback, re-run the full QC loop (Phase 4a structural checks + Phase 4b visual inspection) — not just the specific feedback item. Changes often have side effects on layout and spacing.

## Platform Note

The visual QC workflow (Phases 3b and 4b) uses `qlmanage`, which is macOS-native (Quick Look). On non-macOS platforms, skip the render/visual steps and rely on Phase 4a structural checks only. Note this limitation to the user.

**qlmanage rendering limitation**: Quick Look does not render fills for certain shape presets (`flowChartProcess`, `flowChartTerminator`, `flowChartMagneticDisk`). These appear as invisible/empty shapes in the PNG. Use `roundRect` for shapes that must be visible during QC. The `flowChartDecision`, `roundRect`, `hexagon`, and `ellipse` presets render correctly. The affected presets DO render properly in actual PowerPoint — this is a qlmanage-only limitation.

## Anti-Patterns to Watch For

These are the most common diagram failures. If you catch yourself doing any of these, stop and restructure:

- **"Everything in one diagram" mega-canvas** — split into a diagram set
- **Random icon styles mixed together** — pick one style or use shape presets
- **Many-to-many direct connections without hubs/buses** — introduce a hub node
- **Decorative effects instead of structure** — keep only functional gradients/shadows
- **Color used for aesthetics rather than encoding** — each color = one meaning
- **Loops/cycles as tangled arrows** — use separate sequence view or route back-edges outside
- **Paragraphs inside boxes** — max 2 lines; move detail to sub-diagram
- **Mixing diagram levels in one view** — one level per view (context OR container OR component)

See `methodology.md` §8 for the full anti-patterns reference.

## Shape Preset Quick Reference

| Element | Preset name |
|---------|-------------|
| Process box | `flowChartProcess` |
| Decision diamond | `flowChartDecision` |
| Start/End (stadium) | `flowChartTerminator` |
| Database cylinder | `flowChartMagneticDisk` |
| Document | `flowChartDocument` |
| Rectangle | `rect` |
| Rounded rectangle | `roundRect` |
| Ellipse / circle | `ellipse` |
| Hexagon | `hexagon` |
| Cloud | `cloud` |
| Right arrow | `rightArrow` |
| Chevron | `chevron` |
| Note / sticky | `folderCorner` |
| Speech bubble | `wedgeRoundRectCallout` |

## Connecting Shapes

For orthogonal routing with smooth curved elbows (the professional standard), use the `build_routed_connector_xml()` helper from `references/reference.md`. It creates custom geometry paths (`a:custGeom`) with `a:arcTo` quarter-circle arcs at each turn — producing strictly horizontal/vertical lines with rounded corners, all as a single selectable shape. Define waypoints as `(x, y)` tuples where each consecutive pair differs in only x or y.

For simple straight arrows where source and target are aligned, a basic `straightConnector1` XML element also works.

For radial/hub-spoke layouts, straight connectors from hub center to spoke centers work well.

## Color Palettes

See `references/reference.md` for 7 curated palettes including Professional Blue, Modern Green, AWS Orange, Dark Mode, and more.

## Script Pattern

```python
from pptx import Presentation
from pptx.util import Inches, Emu
from lxml import etree

prs = Presentation()
prs.slide_width = Emu(9144000)   # 10"
prs.slide_height = Emu(5143500)  # 5.625"
slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank layout
spTree = slide.shapes._spTree

# Add shapes via python-pptx API for positioning
shape = slide.shapes.add_shape(...)
shape.left, shape.top, shape.width, shape.height = ...

# Inject OOXML XML for visual effects python-pptx doesn't expose
xml = '''<p:sp xmlns:p="..." xmlns:a="...">...</p:sp>'''
spTree.append(etree.fromstring(xml))

prs.save("diagram.pptx")
```

After generating, open with: `open diagram.pptx` (macOS) / `start diagram.pptx` (Windows)

## Resources

- **`references/reference.md`** — OOXML visual techniques, color palettes, DrawingML recipes, connector helpers
- **`references/methodology.md`** — Design methodology: contract definition, semiotics, layout algorithms, Gestalt laws, Tufte principles, typography, accessibility, anti-patterns, default spec
- **`examples/flowchart.py`** — Horizontal sequential flow with gradient fills
- **`examples/org_chart.py`** — 3-level layered hierarchy with gradient cards
- **`examples/architecture_diagram.py`** — Swimlane layout with containment regions
- **`examples/branching_flowchart.py`** — Decision logic with double coding and loop-back routing
- **`examples/hub_spoke_diagram.py`** — Radial hub-and-spoke with trigonometric positioning
