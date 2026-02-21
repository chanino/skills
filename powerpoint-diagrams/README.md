# PowerPoint Diagrams Skill

Create professional `.pptx` diagrams using `python-pptx` and OOXML/DrawingML XML. Diagrams are designed from first principles using a cognitive architecture methodology — not copied from templates.

## Requirements

```bash
pip install python-pptx lxml
```

Requires PowerPoint (macOS/Windows) or LibreOffice Impress to view output files.

## Quick Start

```bash
python ~/.claude/skills/powerpoint-diagrams/examples/flowchart.py
open flowchart.pptx

python ~/.claude/skills/powerpoint-diagrams/examples/hub_spoke_diagram.py
open hub_spoke_diagram.pptx
```

## Triggering the Skill

Ask Claude Code to:
- "Create a PowerPoint flowchart for a user authentication flow"
- "Make an org chart for my team"
- "Generate a PPTX architecture diagram for a microservices system"
- "Draw a hub-and-spoke diagram for an API gateway"

## How It Works

The skill follows a **5-phase design process** (defined in `SKILL.md`):

1. **Analyze & Deconstruct** — semantic inventory, visual rhetoric, layout algorithm selection
2. **Design Visual Grammar** — shape mapping, color assignment, stroke/size hierarchy
3. **Generate Script** — python-pptx + OOXML XML, applying Gestalt grouping and data-ink principles
4. **Run & Validate** — squint test, double coding check, node density check
5. **Iterate** — progressive disclosure for dense diagrams, multi-slide strategy

Design methodology (Gestalt laws, Tufte principles, accessibility) lives in `references/methodology.md`. OOXML/DrawingML recipes live in `references/reference.md`.

## File Structure

```
powerpoint-diagrams/
├── SKILL.md                         ← Skill trigger + 5-phase workflow
├── README.md                        ← This file
├── references/
│   ├── methodology.md               ← Design methodology (semiotics, layout, Gestalt, Tufte, accessibility)
│   └── reference.md                 ← OOXML/DrawingML recipes, palettes, connector helpers
└── examples/
    ├── flowchart.py                 ← Horizontal sequential flow
    ├── org_chart.py                 ← 3-level layered hierarchy
    ├── architecture_diagram.py      ← 3-lane swimlane with containment
    ├── branching_flowchart.py       ← Decision logic with double coding & loop-back
    └── hub_spoke_diagram.py         ← Radial hub-and-spoke with trigonometric layout
```

## Technical Notes

**Orthogonal connectors**: Use `build_routed_connector_xml()` (defined in `references/reference.md` and each example) for Manhattan-routed arrows with curved elbows via `a:custGeom`.

**Shape IDs**: Must be unique integers per slide, starting at 2 (ID 1 is reserved).

**Z-ordering**: XML element order in `<p:spTree>` determines render order (first = bottom). Background rects at index 2, connectors before shapes, shapes on top.
