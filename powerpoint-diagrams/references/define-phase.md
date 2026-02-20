# Define Phase Reference

> **Phase 1: Request → Data Definitions.** Use this guide to translate a user's natural-language request into `Shape`, `Connection`, and `Diagram` dataclass instances before any layout math runs.

---

## 1. Request → Diagram Type

Match keywords in the user's request to a diagram type and `layout_type`:

| Signal in request | Diagram type | `layout_type` |
|---|---|---|
| "flowchart", "process", "steps", "workflow", sequential verbs | Flowchart | `horizontal_flow` |
| "org chart", "hierarchy", "reporting structure", "team" | Org Chart | `hierarchy` |
| "architecture", "system", "layers", "services", "components" | Architecture | `swimlane` |
| "network", "hub", "spokes", "topology" | Network | `radial` |
| "timeline", "phases", "milestones" | Timeline | `horizontal_flow` |
| "comparison", "vs", "options" | Comparison | `horizontal_flow` or `swimlane` |

**Ambiguous requests:** If the request doesn't clearly match one type, default to `horizontal_flow` (flowchart). It handles the widest variety of content.

---

## 2. Diagram Type → Shape Selection

For each diagram type, map element roles to OOXML preset geometry names and style keys.

### Flowchart

| Element role | Preset | Style |
|---|---|---|
| Start / End | `flowChartTerminator` | `dark` |
| Process step | `flowChartProcess` | `primary` |
| Decision | `flowChartDecision` | `accent` |
| Document | `flowChartDocument` | `neutral` |
| Data store | `flowChartMagneticDisk` | `neutral` |
| Input / Output | `flowChartInputOutput` | `primary` |

**Default:** If the user doesn't specify roles, treat the first shape as Start (`dark`), the last shape as End (`dark`), and all middle shapes as Process (`primary`).

### Org Chart

| Element role | Preset | Style |
|---|---|---|
| All nodes | `roundRect` | Color by level: `dark` (level 0) → `primary` (level 1) → `success` (level 2) → `accent` (level 3) |

Set each shape's `group` field to its level number (`"0"`, `"1"`, `"2"`, ...).

### Architecture

| Element role | Preset | Style |
|---|---|---|
| Client / UI | `cloud` or `roundRect` | `primary` |
| Service / API | `flowChartProcess` | `primary` |
| Gateway / Router | `hexagon` | `accent` |
| Database | `flowChartMagneticDisk` | `neutral` |
| Cache / Queue | `flowChartMagneticDisk` | `accent` |

Set each shape's `group` field to its lane name (e.g. `"presentation"`, `"business"`, `"data"`).

### Network (Hub-and-Spoke)

| Element role | Preset | Style |
|---|---|---|
| Hub / central node | `ellipse` or `roundRect` | `dark` |
| Spoke nodes | `roundRect` | `primary` |

---

## 3. Connection Patterns

How to derive `Connection` objects from the user's description:

| Diagram type | Default direction | Connection pattern |
|---|---|---|
| Flowchart | `right_to_left` (horizontal) | Sequential: each shape → next shape |
| Org Chart | `top_to_bottom` | Parent → each child |
| Architecture | `top_to_bottom` (cross-lane) | Caller → callee; client → service → data |
| Network | Radial | Hub → each spoke |
| Timeline | `right_to_left` | Sequential: each milestone → next |

### Connection labels

- **Flowchart decisions:** Add `label="YES"` on the primary branch and `label="NO"` on the alternate branch.
- **Architecture:** Labels are usually unnecessary; the shape text conveys the component name.
- **Org Chart / Network / Timeline:** Labels are rarely needed.

---

## 4. Palette Selection

Choose a palette based on context (full color definitions are in `diagram-patterns.md`):

| Context | Palette | Rationale |
|---|---|---|
| Business / proposal (default) | `professional_blue` | Safe, corporate |
| Tech / sustainability | `modern_green` | Fresh, modern |
| Formal / enterprise | `neutral_gray` | Conservative |
| Cloud / infrastructure | `aws_orange` | Industry convention |
| Presentation on dark background | `dark_mode` | High contrast |

**Default:** If the user doesn't mention color, use `professional_blue`.

---

## 5. Extraction Checklist

Identify each of these from the user's request before writing code:

```
[ ] Diagram type → layout_type
[ ] Number of shapes (nodes/boxes)
[ ] Shape labels (text for each)
[ ] Shape roles → preset for each
[ ] Connections (which → which)
[ ] Connection labels (if any, e.g. "YES"/"NO")
[ ] Grouping (levels for hierarchy, lanes for swimlane)
[ ] Color preference → palette
[ ] Title text
```

If the user omits an item, apply the defaults from the tables above. If the title isn't specified, derive one from the diagram content (e.g. "User Registration Process").

---

## 6. Worked Examples

### Example 1: Flowchart

**Request:** "Create a flowchart for user registration: sign up, verify email, create profile, done"

**Extraction:**
- Diagram type: Flowchart → `horizontal_flow`
- 4 shapes: "Sign Up", "Verify Email", "Create Profile", "Done"
- Roles: Start=Sign Up, Process=Verify Email, Process=Create Profile, End=Done
- 3 sequential connections
- Palette: `professional_blue` (default)
- Title: "User Registration Process"

**Data definitions:**
```python
shapes = [
    Shape(id="signup",  text="Sign Up",       preset="flowChartTerminator", style="dark"),
    Shape(id="verify",  text="Verify Email",   preset="flowChartProcess",    style="primary"),
    Shape(id="profile", text="Create Profile", preset="flowChartProcess",    style="primary"),
    Shape(id="done",    text="Done",           preset="flowChartTerminator", style="dark"),
]
connections = [
    Connection(src="signup",  tgt="verify"),
    Connection(src="verify",  tgt="profile"),
    Connection(src="profile", tgt="done"),
]
diagram = Diagram(
    title="User Registration Process",
    layout_type="horizontal_flow",
    shapes=shapes,
    connections=connections,
)
```

### Example 2: Org Chart

**Request:** "Make an org chart for our CTO with 3 directors under them"

**Extraction:**
- Diagram type: Org Chart → `hierarchy`
- 4 shapes: "CTO" (level 0), "Director 1", "Director 2", "Director 3" (level 1)
- 3 connections: CTO → each Director
- Palette: `professional_blue` (default)
- Title: "Organization Chart"

**Data definitions:**
```python
shapes = [
    Shape(id="cto",  text="CTO",        preset="roundRect", style="dark",    group="0"),
    Shape(id="dir1", text="Director 1",  preset="roundRect", style="primary", group="1"),
    Shape(id="dir2", text="Director 2",  preset="roundRect", style="primary", group="1"),
    Shape(id="dir3", text="Director 3",  preset="roundRect", style="primary", group="1"),
]
connections = [
    Connection(src="cto", tgt="dir1"),
    Connection(src="cto", tgt="dir2"),
    Connection(src="cto", tgt="dir3"),
]
diagram = Diagram(
    title="Organization Chart",
    layout_type="hierarchy",
    shapes=shapes,
    connections=connections,
)
```

### Example 3: Architecture Diagram

**Request:** "Architecture diagram showing React frontend talking to Node API which hits Postgres"

**Extraction:**
- Diagram type: Architecture → `swimlane`
- 3 shapes in 3 lanes: "React Frontend" (presentation), "Node API" (business), "PostgreSQL" (data)
- 2 connections: React → Node → Postgres
- Palette: `professional_blue` (default)
- Title: "System Architecture"

**Data definitions:**
```python
shapes = [
    Shape(id="react",    text="React Frontend", preset="roundRect",            style="primary", group="presentation"),
    Shape(id="node",     text="Node API",       preset="flowChartProcess",     style="primary", group="business"),
    Shape(id="postgres", text="PostgreSQL",      preset="flowChartMagneticDisk", style="neutral", group="data"),
]
connections = [
    Connection(src="react", tgt="node"),
    Connection(src="node",  tgt="postgres"),
]
diagram = Diagram(
    title="System Architecture",
    layout_type="swimlane",
    shapes=shapes,
    connections=connections,
)
```

---

## 7. Dataclass Requirements by Type

Map each diagram type to the dataclasses needed from `layout-engine.md`:

| Diagram type | Required | Optional |
|---|---|---|
| Flowchart | `Rect`, `PlacedShape`, `PlacedConnector` | `PlacedLabel` |
| Org Chart | `Rect`, `PlacedShape` (with `text_line2`, `gradient`), `PlacedConnector` | — |
| Architecture | `Rect`, `PlacedShape` (with `glow`), `PlacedConnector`, `LaneBg` | — |
| Network | `Rect`, `PlacedShape`, `PlacedConnector` | `PlacedLabel` |

---

## 8. Layout Function Selection

Map each diagram type to the appropriate layout function from `layout-engine.md`:

| Diagram type | Layout function in `layout-engine.md` | Direction |
|---|---|---|
| Flowchart | `layout_horizontal_flow()` | `right_to_left` |
| Org Chart | `layout_hierarchy()` | `top_to_bottom` |
| Architecture | `layout_swimlane()` | auto-detected |
| Network | custom (use `radial_positions()` from `diagram-patterns.md`) | radial |
| Timeline | `layout_horizontal_flow()` | `right_to_left` |

---

## 9. Script Skeleton

Use this template as the structure for every generated diagram script. Each section references the appropriate phase from `layout-engine.md` — not from `examples/`.

```python
#!/usr/bin/env python3
"""[Title] — Generated Diagram"""

from dataclasses import dataclass
from pptx import Presentation
from pptx.util import Emu
from lxml import etree
import subprocess, os

# ═══ DATA MODEL (from layout-engine.md Phase 1) ═══
# Rect, PlacedShape, PlacedConnector, [LaneBg if swimlane]

# ═══ CONSTANTS ═══
SLIDE_W, SLIDE_H = 9144000, 5143500
# Palette, shape defaults...

# ═══ PHASE 1: DEFINE (your extracted data) ═══
TITLE = "..."
SHAPES = [...]
CONNECTIONS = [...]

# ═══ QC1: validate_definition() ═══

# ═══ PHASE 2: COMPUTE (from layout-engine.md) ═══
# estimate_font_size(), compute_connector_bbox(), layout function

# ═══ QC2: validate_layout() ═══

# ═══ PHASE 3: RENDER (from layout-engine.md Phase 4) ═══
# Z-order: bg(0) → lanes(1) → title(1.5) → connectors(2) → shapes(3) → labels(4)

# ═══ QC3: validate_render() ═══

# ═══ MAIN ═══
```

Each section says **"from layout-engine.md"** — Claude composes each section by reading the reference functions, not by copying examples.
