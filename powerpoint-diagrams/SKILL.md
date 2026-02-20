---
description: "This skill should be used when the user asks to 'create a PowerPoint diagram', 'make a flowchart in PowerPoint', 'create an org chart', 'make an architecture diagram', 'generate a PPTX diagram', 'create a .pptx file', 'draw a diagram in PowerPoint', 'add orthogonal connectors', or wants to create any visual diagram or chart to be saved as a .pptx file."
---

# PowerPoint Diagrams Skill

Generate professional `.pptx` diagrams programmatically using `python-pptx` + direct OOXML/DrawingML XML injection.

## Prerequisites

```bash
pip install python-pptx lxml
```

Requires PowerPoint (or LibreOffice Impress) locally to view the result. After generating, open with:
```bash
open diagram.pptx          # macOS
start diagram.pptx         # Windows
libreoffice diagram.pptx   # Linux
```

## Workflow

> **Use TaskCreate/TaskUpdate** to track each phase.

### Step 0: Check for prior context (optional)

Ask if the user has:
- A **cached plan** (Shape/Connection data from a previous diagram to reuse/modify)
- An **existing .py script** to adapt
- A **specific example** from `examples/` to start from

If none (the common case), generate from scratch in Step 1.

### Step 1: Extract diagram data from the prompt

Use `references/define-phase.md` as your primary guide:
1. Classify diagram type (Request-to-Type table)
2. Enumerate shapes, roles, labels
3. Map roles to OOXML presets (Type-to-Shape tables)
4. Derive connections from relationships
5. Select palette and title
6. Run the Extraction Checklist
7. Write Shape/Connection/Diagram definitions as Python data

→ TaskCreate: "Define diagram data" · status: in_progress

### Step 2: Write Define phase + QC1

Write the Define section using the script skeleton from `references/define-phase.md` Section 9.
Copy dataclass definitions from `references/layout-engine.md` Phase 1.
Run validate_definition() — QC1.

→ TaskUpdate: completed · TaskCreate: "Compute layout + QC2" · status: in_progress

### Step 3: Write Compute + Validate + QC2

Use `references/layout-engine.md` Phase 2 for layout functions and
`references/diagram-patterns.md` for spacing/palettes.
Run validate_layout() — QC2.

→ TaskUpdate: completed · TaskCreate: "Render and verify" · status: in_progress

### Step 4: Write Render phase + QC3

Use `references/layout-engine.md` Phase 4 for render functions and
`references/ooxml-spec.md` for XML. Emit in z-order.
Run validate_render() — QC3.

### Step 5: Run the script

Execute, save .pptx, open and verify.
→ TaskUpdate: completed

## Shape Selection Guide

| Diagram element         | Preset name             |
|------------------------|------------------------|
| Process box            | `flowChartProcess`      |
| Decision diamond       | `flowChartDecision`     |
| Start/End (stadium)    | `flowChartTerminator`   |
| Database cylinder      | `flowChartMagneticDisk` |
| Document              | `flowChartDocument`     |
| Rectangle             | `rect`                  |
| Rounded rectangle     | `roundRect`             |
| Ellipse / circle      | `ellipse`               |
| Hexagon               | `hexagon`               |
| Cloud                 | `cloud`                 |
| Right arrow           | `rightArrow`            |
| Chevron               | `chevron`               |
| Note / sticky         | `folderCorner`          |
| Speech bubble         | `wedgeRoundRectCallout` |
| Star                  | `star5`                 |

See `references/ooxml-spec.md` for all 200+ preset names.

## Connector Selection Guide

| Connector type         | Tag                  | Use when                              |
|-----------------------|---------------------|---------------------------------------|
| Orthogonal (default)  | `bentConnector3`    | **Most diagrams — proposal standard** |
| Curved                | `curvedConnector3`  | Only when organic flow is intentional |
| Straight              | `straightConnector1`| Minimalist / technical diagrams       |

**Always use `bentConnector3` (orthogonal routing) unless the user specifies otherwise.** Professional proposal diagrams use orthogonal (Manhattan) routing — connectors run parallel or perpendicular to slide margins. python-pptx's public connector API does not expose these connectors correctly — use the XML injection pattern from `references/python-pptx-api.md`.

### Connection point indexes
- `0` = top center
- `1` = right center
- `2` = bottom center
- `3` = left center

## Quality Checklist

QC runs at every phase: **DEFINE → QC1 → COMPUTE → QC2 → RENDER → QC3 → SAVE**

Before presenting the result:
- [ ] Script runs without errors (`python diagram.py`)
- [ ] **QC1**: `validate_definition()` passes — no duplicate IDs, no bad refs, no unknown presets
- [ ] **QC2**: `validate_layout()` passes — no text overflow, no overlaps, endpoints aligned, flips consistent
- [ ] **QC3**: `validate_render()` passes — element count matches, all XML IDs unique, z-order correct
- [ ] File opens in PowerPoint without repair prompts
- [ ] All arrows point in the correct direction (connectors use `flipH`/`flipV` when target is left/above source)
- [ ] All text is visible (no overflow, font >= 10pt — validated by `estimate_font_size()`)
- [ ] 90° elbows are visibly softened (`<a:prstDash>` BEFORE `<a:round/>` in `<a:ln>`)
- [ ] Shape outlines have softened corners (`<a:round/>` inside shape `<a:ln>`)
- [ ] Shape IDs are unique per slide (start at 2)
- [ ] Connector bounding boxes span the gap between shapes (not zero-size)
- [ ] Connectors rendered BELOW shapes (z-layer 2 < 3) — no lines visible on top of shapes
- [ ] No shapes overlap unintentionally
- [ ] Connectors use orthogonal routing (`bentConnector3`) — no diagonal or curved paths
- [ ] Diagram follows 3-phase pattern with QC at each checkpoint: define → compute → render

## Additional Resources

### Primary references (use these to generate)
- **`references/define-phase.md`** — **Phase 1 guide** — decision trees, preset tables, script skeleton, worked examples
- **`references/layout-engine.md`** — **Phases 2-4 guide** — dataclasses, layout functions, connector math, validation, render

### Supporting references
- `references/ooxml-spec.md` — shape presets, connector XML, effects, fills, units
- `references/python-pptx-api.md` — low-level helpers
- `references/diagram-patterns.md` — layout recipes, color palettes, typography

### Examples (optional — not starting points)
- `examples/flowchart.py` — reference: 5-step horizontal flow
- `examples/org_chart.py` — reference: 3-level hierarchy
- `examples/architecture_diagram.py` — reference: 3-lane swimlane

> Do NOT copy an example and adapt it. Generate from scratch using the reference docs above.
