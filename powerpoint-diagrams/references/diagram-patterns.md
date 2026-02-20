# Diagram Layout Patterns & Design Guide

> **Preferred Architecture: Layout-First.** See `layout-engine.md` for the 4-phase approach (define → compute → validate → render) that fixes connector routing, z-ordering, text overflow, and elbow softening issues. The patterns below provide layout recipes and design guidance to use WITH that architecture.

---

## Z-Ordering Rules

Render order determines visual stacking. Always emit elements in this order:
1. **Background** (z=0) — full-slide fill, inserted at `spTree.insert(2, ...)`
2. **Lane backgrounds** (z=1) — swimlane rects
3. **Title** (z=1.5) — figure title text
4. **Connectors** (z=2) — BELOW shapes so lines don't overlap shape boundaries
5. **Shapes** (z=3) — ABOVE connectors, hiding any overlap at connection points
6. **Labels** (z=4) — floating text annotations, topmost

This ensures connector lines never visibly cross over shape fills.

## Text Sizing Guidelines

Use `estimate_font_size()` from `layout-engine.md` to auto-compute the largest font that fits. Key rules:
- **Minimum readable**: 8pt (`sz=800`) — never go smaller
- **Usable width** = shape width - 2 × 0.1" inset (182,880 EMU total)
- **Calibri average char width** ≈ 45,000 EMU at 100pt — scale linearly
- **Validate before render**: `text_fits()` catches overflow before any XML is emitted
- For two-line text (name + title), use primary font for line 1 and 2pt smaller for line 2

---

## Color Palettes

### Professional Blue
```
Primary:    #4472C4  (deep blue)
Secondary:  #2E4FA3  (darker blue for borders)
Accent:     #70AD47  (green for success/positive)
Background: #EEF2FA  (light blue-gray)
Text:       #FFFFFF  (white on dark)
Dark text:  #1F2D3D  (near-black for readability)
```

### Modern Green (tech/sustainability)
```
Primary:    #27AE60  (emerald green)
Secondary:  #1A7A41  (darker green)
Accent:     #F39C12  (amber for highlights)
Background: #F0FAF4  (light green-white)
Text:       #FFFFFF
```

### Neutral Gray (corporate)
```
Primary:    #5D6D7E  (slate gray)
Secondary:  #2C3E50  (dark navy)
Accent:     #E74C3C  (red for critical/alerts)
Background: #F5F6FA  (off-white)
Text:       #FFFFFF
```

### AWS Orange (cloud/infrastructure)
```
Primary:    #FF9900  (AWS orange)
Secondary:  #232F3E  (AWS dark navy)
Accent:     #1A9C3E  (AWS green)
Background: #F8F9FA  (light gray)
Text:       #232F3E  (dark on light shapes)
```

### Dark Mode
```
Primary:    #7B68EE  (medium slate blue)
Secondary:  #4B4B8F  (darker purple)
Background: #1E1E2E  (near-black)
Surface:    #2D2D44  (dark surface for shapes)
Text:       #E0E0FF  (light lavender)
```

---

## Flowchart Layouts

### Horizontal 5-Step (most common)
```
Slide: 9,144,000 x 5,143,500 EMU (10" x 5.625")

Shape sizes:
  Process box:  cx=1,371,600  cy=685,800   (1.5" x 0.75")
  Decision:     cx=1,371,600  cy=914,400   (1.5" x 1.0")
  Terminator:   cx=1,371,600  cy=571,500   (1.5" x 0.625")

5-step horizontal spacing (equal gaps):
  Gap between shapes: 228,600 EMU (0.25")
  Total content width: 5*1,371,600 + 4*228,600 = 7,772,400
  Left margin: (9,144,000 - 7,772,400) / 2 = 685,800

  Shape x positions:
    Step 1: x = 685,800
    Step 2: x = 685,800 + 1,371,600 + 228,600 = 2,286,000
    Step 3: x = 2,286,000 + 1,371,600 + 228,600 = 3,886,200
    Step 4: x = 3,886,200 + 1,371,600 + 228,600 = 5,486,400
    Step 5: x = 5,486,400 + 1,371,600 + 228,600 = 7,086,600

  Vertical center (all shapes same y):
    y = (5,143,500 - 685,800) / 2 = 2,228,850
```

Python formula for n shapes with gap g and shape width sw:
```python
SW, SH = 1371600, 685800   # shape width, height
GAP = 228600
n = 5
total_w = n * SW + (n - 1) * GAP
left = (9144000 - total_w) // 2
y_center = (5143500 - SH) // 2

shapes_x = [left + i * (SW + GAP) for i in range(n)]
```

### Vertical Flow
```
Shape sizes: cx=1,828,800 cy=571,500 (2" x 0.625")
Gap: 457,200 (0.5")
x center: (9,144,000 - 1,828,800) / 2 = 3,657,600

y positions (5 steps):
  total_h = 5*571,500 + 4*457,200 = 4,686,300
  top = (5,143,500 - 4,686,300) / 2 = 228,600
  step_i_y = 228,600 + i * (571,500 + 457,200)
```

### Decision Branch (Y-split)
```
Main flow: left-to-right
Decision diamond at center
  YES branch: continues right
  NO branch: drops down, then continues right (or loops back)

Connector from diamond bottom (idx=2) to NO-path shape top (idx=0)
Connector from diamond right (idx=1) to YES-path shape left (idx=3)
```

---

## Org Chart Layout

### 1-3-6 Hierarchy (standard)
```
Level 0 (CEO):    1 shape, centered
Level 1 (VPs):    3 shapes, evenly distributed
Level 2 (Leads):  6 shapes, 2 under each VP

Shape: roundRect, cx=1,371,600 cy=571,500

Vertical spacing between levels: 685,800 EMU (0.75")

Level 0 y: 228,600
Level 1 y: 228,600 + 571,500 + 685,800 = 1,485,900
Level 2 y: 1,485,900 + 571,500 + 685,800 = 2,743,200
```

Centering algorithm:
```python
SLIDE_W = 9144000
SW, SH = 1371600, 571500
H_GAP = 685800   # horizontal gap between siblings
V_GAP = 685800   # vertical gap between levels

def center_group(n, sw=SW, gap=H_GAP):
    """Return x positions for n shapes centered on slide."""
    total = n * sw + (n - 1) * gap
    left = (SLIDE_W - total) // 2
    return [left + i * (sw + gap) for i in range(n)]

level0_x = center_group(1)   # [3886200]
level1_x = center_group(3)   # 3 evenly spaced
level2_x = center_group(6)   # 6 evenly spaced
```

### Color per Level
```python
level_colors = {
    0: ("1F3864", "16294A"),  # dark navy — CEO
    1: ("4472C4", "2E4FA3"),  # blue — VPs
    2: ("70AD47", "507C32"),  # green — leads
    3: ("ED7D31", "C05C13"),  # orange — staff
}
```

### Connectors
Use `bentConnector3` from parent bottom (idx=2) to child top (idx=0).

Bounding box:
```python
# parent shape: (px, py, pcx, pcy); child shape: (cx_, cy_, ccx, ccy)
conn_x = px + pcx // 2   # center of parent (x)
conn_y = py + pcy         # bottom of parent
conn_cx = cx_ + ccx // 2 - conn_x  # to center of child (may be negative → flip xfrm)
conn_cy = cy_ - conn_y   # gap height
```

---

## Architecture Diagram (Swimlane)

### 3-Lane Layout
```
Slide: 9,144,000 x 5,143,500 EMU

Lane heights (equal thirds):
  Lane height: 5,143,500 / 3 = 1,714,500 each

  Presentation layer: y=0,        h=1,714,500, fill=#EBF3FB
  Business Logic:     y=1,714,500, h=1,714,500, fill=#E8F8E8
  Data layer:         y=3,429,000, h=1,714,500, fill=#FEF9E7

Lane label: x=50,000, y=lane_y+50,000, font 10pt bold, color #666666
Component shapes start at x=457,200 (0.5" margin)
```

Lane background rects should be inserted at z-bottom:
```python
# Insert in reverse order so bottom lane is drawn first
for lane in reversed(lanes):
    add_lane_background(spTree, next_id(), ...)
```

### Component Placement per Lane
```
Within each lane, center components vertically:
  comp_y = lane_y + (lane_height - comp_cy) // 2

Horizontal positions (4 components per lane at 2" intervals):
  x positions: 685,800 | 2,743,200 | 4,800,600 | 6,858,000
```

---

## Network / Hub-and-Spoke

### Radial Layout
```python
import math

def radial_positions(n, center_x, center_y, radius):
    """Return (x, y) positions for n nodes arranged in a circle."""
    positions = []
    for i in range(n):
        angle = 2 * math.pi * i / n - math.pi / 2  # start at top
        x = center_x + int(radius * math.cos(angle))
        y = center_y + int(radius * math.sin(angle))
        positions.append((x, y))
    return positions

# Example: 6 nodes around a hub
HUB_X, HUB_Y = 4572000, 2571750   # slide center
RADIUS = 1828800                    # 2 inches
node_positions = radial_positions(6, HUB_X, HUB_Y, RADIUS)
```

Connectors: from hub center (compute nearest idx) to each spoke.

### Mesh Pattern
For fully-connected mesh (every node to every other):
```python
for i in range(n):
    for j in range(i + 1, n):
        add_connector(...)  # connect node i to node j
```
Avoid mesh with n > 5 (too many lines → cluttered).

---

## Typography Guidelines

| Role | Font size (sz) | Bold | Color |
|------|---------------|------|-------|
| Slide title | `2800` (28pt) | Yes | Dark |
| Primary label (main shapes) | `1400` (14pt) | Yes | White |
| Secondary label (sub-shapes) | `1200` (12pt) | No | White |
| Caption / small label | `1000` (10pt) | No | #666666 |
| Lane header | `1000` (10pt) | Yes | #444444 |
| Callout text | `1100` (11pt) | No | Dark |

**Safe font choices** (available on all systems):
- `Calibri` (default — clean, modern)
- `Arial`
- `Helvetica`
- `Georgia` (for serif/formal)

**Minimum readable size**: `sz="800"` (8pt) — avoid smaller.

---

## Proposal-Grade Design Standards

Best practices from Shipley method and APMP standards for professional proposal graphics.

### Connector Routing Rules
- **Always orthogonal** (Manhattan routing) — connectors run parallel or perpendicular to slide margins
- Minimize bends — prefer straight horizontal or vertical runs
- No diagonal connectors — all segments must be horizontal or vertical
- Route connectors through "alleys" between shapes, not through shapes
- Minimize crossings; when unavoidable, stagger routing to reduce visual confusion

### The 30-Second Rule
The reader must understand the diagram's message within 30 seconds. If it takes longer, simplify: reduce elements, enlarge key labels, or split into multiple diagrams.

### Visual Hierarchy
- Size, color, and position signal importance
- Most critical elements go top-center or left (the eye's natural starting point)
- Use bolder outlines or glow effects to draw attention to key nodes

### Information Flow Direction
- **Left-to-right** for process flows and timelines
- **Top-to-bottom** for hierarchies (org charts, architecture layers)
- Never mix flow directions within the same diagram

### Color Discipline
- **3–5 semantic colors maximum** — each color encodes a specific meaning
- Color represents category or status, not decoration
- Always provide a legend for non-obvious color mapping
- Consistent color usage: the same element type uses the same color throughout

### Grid Alignment
- All shapes snap to an alignment grid (48px / ~0.5" increments recommended)
- Consistent spacing between all elements — use layout constants, not magic numbers
- Shapes in the same logical group should share the same y-coordinate (horizontal) or x-coordinate (vertical)

### Action Captions
- Strategic callout annotations highlight differentiators and win themes — not just labels
- Use concise, verb-driven language ("Reduces risk by 40%", "Eliminates manual review")

### Metadata
- Every proposal diagram includes a figure title (e.g., "Figure 1: Project Execution Process")
- Include figure number and scope description for cross-referencing in the proposal text

### Shape Consistency
- Same element types use identical sizing and styling throughout the diagram
- Consistent border width, corner radius, and font size within each shape category

---

## Anti-Patterns to Avoid

| Anti-pattern | Problem | Fix |
|-------------|---------|-----|
| > 10 shapes per slide | Cluttered, hard to read | Split into multiple slides |
| Font < 8pt (`sz < 800`) | Unreadable | Increase size or abbreviate text |
| Duplicate shape IDs | PowerPoint corruption | Use `next_id()` counter |
| Zero-size connector bounding box (`cx=0` or `cy=0`) | Invisible connector | Ensure `cx >= 1` and `cy >= 1` |
| Connector referencing non-existent shape ID | PowerPoint repair prompt | Verify all `stCxn`/`endCxn` IDs exist |
| Lane backgrounds added after content | Content rendered behind lanes | Use `spTree.insert(2, ...)` for backgrounds |
| Text longer than shape width | Text overflow / clipping | Shorten text or increase shape size |
| All shapes same color | Boring, hard to parse hierarchy | Use palette variation per level/type |
| Connector from point to same point | Loop arrow (usually unintended) | Verify src_id ≠ tgt_id |
| Missing namespace declarations in XML strings | lxml parse error | Always include `xmlns:p=` and `xmlns:a=` |
| Curved/bezier connectors in formal diagrams | Looks auto-generated, unprofessional | Use orthogonal (`bentConnector3`) |
| Diagonal connector paths | Violates proposal standards | Always route orthogonally (H-V-H or V-H-V) |
| Missing figure title or legend | Diagram lacks context and traceability | Add "Figure N: Title" text box at top |
