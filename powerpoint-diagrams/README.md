# PowerPoint Diagrams Plugin

Create professional `.pptx` diagrams programmatically using `python-pptx` and direct OOXML/DrawingML XML manipulation.

## Requirements

```bash
pip install python-pptx lxml
```

Requires PowerPoint (macOS/Windows) or LibreOffice Impress to view output files.

## Quick Start

```bash
# Run a built-in example
python skills/powerpoint-diagrams/examples/flowchart.py
open flowchart.pptx

python skills/powerpoint-diagrams/examples/org_chart.py
open org_chart.pptx

python skills/powerpoint-diagrams/examples/architecture_diagram.py
open architecture_diagram.pptx
```

## Triggering the Skill

Ask Claude Code to:
- "Create a PowerPoint flowchart for a user authentication flow"
- "Make an org chart for my team"
- "Generate a PPTX architecture diagram for a microservices system"
- "Draw a decision flowchart in PowerPoint"

## Capabilities

- **Flowcharts** — process boxes, decision diamonds, terminators, data shapes
- **Org charts** — multi-level hierarchy with gradient fills per level
- **Architecture diagrams** — swimlane layouts with layer backgrounds
- **Network diagrams** — hub-and-spoke, radial, mesh topologies
- **Custom shapes** — 200+ OOXML preset geometries
- **Orthogonal connectors** — `bentConnector3` (Manhattan routing) via XML injection — proposal standard
- **Curved connectors** — `curvedConnector3` available when organic flow is intentional
- **Gradient fills** — top-to-bottom, left-to-right, diagonal
- **Drop shadows & glow** — `<a:outerShdw>`, `<a:glow>` effects
- **Swimlane backgrounds** — z-ordered lane rectangles with labels

## How It Works

This plugin uses a **generative-first** approach. Instead of copying and adapting example files, Claude generates diagram scripts from scratch using structured reference documentation:

1. **`references/define-phase.md`** provides decision trees, shape/connection tables, and a script skeleton for translating requests into data definitions
2. **`references/layout-engine.md`** provides dataclasses, layout functions, connector math, and render functions for Phases 2-4
3. **Supporting references** (`ooxml-spec.md`, `diagram-patterns.md`, `python-pptx-api.md`) supply OOXML details, palettes, and low-level helpers

Examples in `examples/` are available as optional references but are not required starting points.

## File Structure

```
skills/powerpoint-diagrams/
├── SKILL.md                    ← skill trigger + workflow guide
├── references/
│   ├── define-phase.md         ← Phase 1: request → data definitions
│   ├── layout-engine.md        ← Phases 2-4: layout, validation, render
│   ├── ooxml-spec.md           ← 200+ shape presets, connector XML, effects
│   ├── python-pptx-api.md      ← low-level helper functions
│   └── diagram-patterns.md     ← layout recipes, color palettes
└── examples/                   ← optional references (not required starting points)
    ├── flowchart.py            ← 5-step flow with orthogonal connectors
    ├── org_chart.py            ← 3-level hierarchy with bentConnector3
    └── architecture_diagram.py ← 3-lane swimlane with effects
```

## Technical Notes

**Orthogonal connectors**: The default connector is `bentConnector3` — orthogonal (Manhattan) routing with horizontal-vertical-horizontal segments and 90° elbows. python-pptx's public API does not expose these connectors correctly. This plugin uses `lxml.etree.fromstring()` to inject `<p:cxnSp>` elements directly into `slide.shapes._spTree`. This is stable and the correct approach.

**Shape IDs**: Must be unique integers per slide, starting at 2 (ID 1 is reserved). Connector `<a:stCxn>` and `<a:endCxn>` reference these same IDs.

**Z-ordering**: XML element order in `<p:spTree>` determines render order (first = bottom). Background lane rects are inserted at index 2 (after mandatory preamble elements).

**Connector bounding box**: The `<a:xfrm>` on a connector is the bounding rectangle spanning the gap between shapes — PowerPoint calculates the actual elbow positions automatically.
