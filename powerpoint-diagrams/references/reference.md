# OOXML/DrawingML Visual Reference

> For diagram design principles (layout selection, Gestalt grouping, accessibility), see `methodology.md`. This document covers OOXML/DrawingML implementation techniques.

Consolidated reference for creating visually polished PowerPoint diagrams with python-pptx + direct XML injection.

---

## Units

| Unit | EMU value |
|------|-----------|
| 1 inch | 914,400 |
| 1 cm | 360,000 |
| 1 pt | 12,700 |
| Slide width (16:9) | 9,144,000 (10") |
| Slide height (16:9) | 5,143,500 (5.625") |

**Namespaces** (always include in XML strings):
```
xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
```

---

## Color Palettes

### Professional Blue
```
Primary: #4472C4    Secondary: #2E4FA3    Accent: #70AD47
Background: #EEF2FA    Text: #FFFFFF    Dark text: #1F2D3D
```

### Modern Green (tech/sustainability)
```
Primary: #27AE60    Secondary: #1A7A41    Accent: #F39C12
Background: #F0FAF4    Text: #FFFFFF
```

### Neutral Gray (corporate)
```
Primary: #5D6D7E    Secondary: #2C3E50    Accent: #E74C3C
Background: #F5F6FA    Text: #FFFFFF
```

### AWS Orange (cloud/infrastructure)
```
Primary: #FF9900    Secondary: #232F3E    Accent: #1A9C3E
Background: #F8F9FA    Text: #232F3E
```

### Dark Mode
```
Primary: #7B68EE    Secondary: #4B4B8F    Background: #1E1E2E
Surface: #2D2D44    Text: #E0E0FF
```

### Ocean Gradient (modern SaaS)
```
Primary: #0077B6    Secondary: #023E8A    Accent: #00B4D8
Background: #F0F8FF    Text: #FFFFFF
```

### Warm Sunset (creative)
```
Primary: #E63946    Secondary: #A8201A    Accent: #F4A261
Background: #FFF5F0    Text: #FFFFFF    Dark text: #264653
```

---

## Shape Presets

### Common Shapes
| Element | Preset | Notes |
|---------|--------|-------|
| Rectangle | `rect` | |
| Rounded rectangle | `roundRect` | adj=corner radius |
| Ellipse / circle | `ellipse` | |
| Hexagon | `hexagon` | |
| Cloud | `cloud` | |
| Can / cylinder | `can` | |
| Cube | `cube` | |
| Diamond | `diamond` | |
| Right arrow | `rightArrow` | |
| Chevron | `chevron` | |
| Folded corner | `folderCorner` | sticky note |
| Speech bubble | `wedgeRoundRectCallout` | |

### Flowchart Shapes (prefix: `flowChart`)
| Element | Preset |
|---------|--------|
| Process (rect) | `flowChartProcess` |
| Decision (diamond) | `flowChartDecision` |
| Terminator (stadium) | `flowChartTerminator` |
| Data (parallelogram) | `flowChartInputOutput` |
| Database (cylinder) | `flowChartMagneticDisk` |
| Document | `flowChartDocument` |
| Multi-document | `flowChartMultidocument` |
| Predefined process | `flowChartPredefinedProcess` |
| Preparation (hexagon) | `flowChartPreparation` |
| Connector (circle) | `flowChartConnector` |
| Alternate process | `flowChartAlternateProcess` |

### Stars and Banners
`star4`, `star5`, `star6`, `star8`, `star12`, `star16`, `star24`, `star32`
`ribbon`, `ribbon2`, `wave`, `doubleWave`

---

## Gradient Fills

### Basic Two-Stop Gradient (Top to Bottom)
```xml
<a:gradFill>
  <a:gsLst>
    <a:gs pos="0"><a:srgbClr val="4472C4"/></a:gs>
    <a:gs pos="100000"><a:srgbClr val="2E4FA3"/></a:gs>
  </a:gsLst>
  <a:lin ang="5400000" scaled="0"/>
</a:gradFill>
```

### Glossy / Glass Effect (3 stops)
```xml
<a:gradFill>
  <a:gsLst>
    <a:gs pos="0"><a:srgbClr val="6B9FD4"/></a:gs>
    <a:gs pos="50000"><a:srgbClr val="4472C4"/></a:gs>
    <a:gs pos="100000"><a:srgbClr val="2E5090"/></a:gs>
  </a:gsLst>
  <a:lin ang="5400000" scaled="0"/>
</a:gradFill>
```

### Metallic / Chrome Effect
```xml
<a:gradFill>
  <a:gsLst>
    <a:gs pos="0"><a:srgbClr val="E8E8E8"/></a:gs>
    <a:gs pos="35000"><a:srgbClr val="F5F5F5"/></a:gs>
    <a:gs pos="65000"><a:srgbClr val="C0C0C0"/></a:gs>
    <a:gs pos="100000"><a:srgbClr val="A0A0A0"/></a:gs>
  </a:gsLst>
  <a:lin ang="5400000" scaled="0"/>
</a:gradFill>
```

### Radial Gradient (spotlight)
```xml
<a:gradFill>
  <a:gsLst>
    <a:gs pos="0"><a:srgbClr val="6B9FD4"/></a:gs>
    <a:gs pos="100000"><a:srgbClr val="2E4FA3"/></a:gs>
  </a:gsLst>
  <a:path path="circle">
    <a:fillToRect l="50000" t="50000" r="50000" b="50000"/>
  </a:path>
</a:gradFill>
```

### Alpha Modulation (semi-transparent gradient)
```xml
<a:gs pos="0">
  <a:srgbClr val="4472C4">
    <a:alpha val="80000"/>  <!-- 80% opacity -->
  </a:srgbClr>
</a:gs>
```

### Luminance Modulation (lighten/darken without changing hex)
```xml
<a:srgbClr val="4472C4">
  <a:lumMod val="75000"/>   <!-- darken to 75% -->
</a:srgbClr>

<a:srgbClr val="4472C4">
  <a:lumMod val="60000"/>
  <a:lumOff val="40000"/>   <!-- lighten: 60% mod + 40% offset -->
</a:srgbClr>
```

**Gradient angle values:**
| Direction | ang |
|-----------|-----|
| Left to Right | `0` |
| Top-Left to Bottom-Right | `2700000` |
| Top to Bottom | `5400000` |
| Top-Right to Bottom-Left | `8100000` |

---

## Shadow Effects

### Standard Outer Shadow
```xml
<a:effectLst>
  <a:outerShdw blurRad="50800" dist="38100" dir="5400000" algn="tl" rotWithShape="0">
    <a:srgbClr val="000000"><a:alpha val="40000"/></a:srgbClr>
  </a:outerShdw>
</a:effectLst>
```

### Soft Diffuse Shadow (modern/flat design)
```xml
<a:effectLst>
  <a:outerShdw blurRad="127000" dist="25400" dir="5400000" algn="ctr" rotWithShape="0">
    <a:srgbClr val="000000"><a:alpha val="20000"/></a:srgbClr>
  </a:outerShdw>
</a:effectLst>
```

### Inner Shadow (recessed / inset look)
```xml
<a:effectLst>
  <a:innerShdw blurRad="50800" dist="0" dir="5400000">
    <a:srgbClr val="000000"><a:alpha val="50000"/></a:srgbClr>
  </a:innerShdw>
</a:effectLst>
```

---

## Glow Effect

```xml
<a:effectLst>
  <a:glow rad="63500">
    <a:srgbClr val="4472C4"><a:alpha val="40000"/></a:srgbClr>
  </a:glow>
</a:effectLst>
```

Combine with shadow (order matters — `outerShdw` first):
```xml
<a:effectLst>
  <a:outerShdw blurRad="50800" dist="38100" dir="5400000" algn="tl" rotWithShape="0">
    <a:srgbClr val="000000"><a:alpha val="35000"/></a:srgbClr>
  </a:outerShdw>
  <a:glow rad="63500">
    <a:srgbClr val="4472C4"><a:alpha val="40000"/></a:srgbClr>
  </a:glow>
</a:effectLst>
```

---

## 3D Effects

### Scene + Camera Setup
```xml
<a:scene3d>
  <a:camera prst="orthographicFront"/>
  <a:lightRig rig="threePt" dir="t"/>
</a:scene3d>
```

### Shape 3D Properties (Bevel + Depth)
```xml
<a:sp3d>
  <a:bevelT w="63500" h="25400" prst="circle"/>
  <!-- prst: circle | relaxedInset | cross | coolSlant | angle | softRound | convex | slope | divot | riblet | hardEdge | artDeco -->
</a:sp3d>
```

### Material Types
Set on `<a:sp3d>` as `prstMaterial` attribute:
- `plastic` — shiny, color-preserving (default)
- `metal` — reflective, metallic sheen
- `matte` — flat, no specular highlights
- `warmMatte` — soft warm diffuse
- `dkEdge` — dark edge emphasis
- `flat` — no 3D shading

### 3D Lighting Rigs
Set on `<a:lightRig>` as `rig` attribute:
- `threePt` — standard 3-point lighting (default)
- `balanced` — even illumination
- `soft` — gentle, no harsh shadows
- `harsh` — dramatic contrast
- `flood` — broad, even fill
- `contrasting` — strong directional
- `morning` / `sunset` / `chilly` — mood lighting

### Full 3D Shape Example
```xml
<p:spPr>
  <a:xfrm>...</a:xfrm>
  <a:prstGeom prst="roundRect"><a:avLst/></a:prstGeom>
  <a:gradFill>
    <a:gsLst>
      <a:gs pos="0"><a:srgbClr val="5B9BD5"/></a:gs>
      <a:gs pos="100000"><a:srgbClr val="2E75B6"/></a:gs>
    </a:gsLst>
    <a:lin ang="5400000" scaled="0"/>
  </a:gradFill>
  <a:ln w="12700"><a:solidFill><a:srgbClr val="1F4E79"/></a:solidFill><a:round/></a:ln>
  <a:effectLst>
    <a:outerShdw blurRad="50800" dist="38100" dir="5400000" algn="tl" rotWithShape="0">
      <a:srgbClr val="000000"><a:alpha val="35000"/></a:srgbClr>
    </a:outerShdw>
  </a:effectLst>
  <a:scene3d>
    <a:camera prst="orthographicFront"/>
    <a:lightRig rig="threePt" dir="t"/>
  </a:scene3d>
  <a:sp3d prstMaterial="plastic">
    <a:bevelT w="38100" h="12700" prst="relaxedInset"/>
  </a:sp3d>
</p:spPr>
```

---

## Line Styles

```xml
<a:ln w="25400" cap="flat">
  <!-- w in EMU: 12700=1pt, 25400=2pt, 38100=3pt -->
  <a:solidFill><a:srgbClr val="4472C4"/></a:solidFill>
  <a:prstDash val="solid"/>
  <!-- prstDash: solid | dot | dash | lgDash | dashDot | lgDashDot -->
  <a:round/>  <!-- softened corners; alternatives: <a:miter/> | <a:bevel/> -->
  <a:headEnd type="none"/>
  <a:tailEnd type="triangle" w="med" len="med"/>
</a:ln>
```

**Element order inside `<a:ln>` matters:**
1. Fill (`<a:solidFill>`)
2. `<a:prstDash>`
3. Join (`<a:round/>`, `<a:miter/>`)
4. `<a:headEnd>`
5. `<a:tailEnd>`

### Arrowhead Types
`none`, `arrow` (open), `triangle` (filled), `stealth` (slim), `diamond`, `oval`

Size: `w` and `len` attributes — `sm`, `med`, `lg`

---

## Connectors

| Tag | Use |
|-----|-----|
| `straightConnector1` | Direct line between shapes |
| `bentConnector3` | Right-angle routing (professional standard) |
| `curvedConnector3` | S-curve (organic diagrams only) |

### Simple Straight Arrow (XML)
```xml
<p:cxnSp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
         xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvCxnSpPr>
    <p:cNvPr id="10" name="Arrow 10"/>
    <p:cNvCxnSpPr/>
    <p:nvPr/>
  </p:nvCxnSpPr>
  <p:spPr>
    <a:xfrm>
      <a:off x="START_X" y="START_Y"/>
      <a:ext cx="WIDTH" cy="HEIGHT"/>
    </a:xfrm>
    <a:prstGeom prst="straightConnector1"><a:avLst/></a:prstGeom>
    <a:noFill/>
    <a:ln w="19050">
      <a:solidFill><a:srgbClr val="888888"/></a:solidFill>
      <a:prstDash val="solid"/>
      <a:round/>
      <a:tailEnd type="triangle" w="med" len="med"/>
    </a:ln>
  </p:spPr>
</p:cxnSp>
```

For `bentConnector3`, use the same pattern but change `prst="bentConnector3"`. Add `flipH="1"` on `<a:xfrm>` when target is left of source, `flipV="1"` when target is above.

---

## Text Body

```xml
<p:txBody>
  <a:bodyPr wrap="square" lIns="91440" rIns="91440" tIns="45720" bIns="45720" anchor="ctr">
    <a:normAutofit/>
  </a:bodyPr>
  <a:lstStyle/>
  <a:p>
    <a:pPr algn="ctr"/>  <!-- l | ctr | r | just -->
    <a:r>
      <a:rPr lang="en-US" sz="1400" b="1" dirty="0">
        <!-- sz: 100ths of pt (1400=14pt, 1000=10pt) -->
        <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
        <a:latin typeface="Calibri"/>
      </a:rPr>
      <a:t>Your text here</a:t>
    </a:r>
  </a:p>
</p:txBody>
```

### Two-Line Text (name + title)
```xml
<a:p>
  <a:pPr algn="ctr"/>
  <a:r><a:rPr lang="en-US" sz="1100" b="1" dirty="0">
    <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
    <a:latin typeface="Calibri"/>
  </a:rPr><a:t>Jane Smith</a:t></a:r>
</a:p>
<a:p>
  <a:pPr algn="ctr"/>
  <a:r><a:rPr lang="en-US" sz="900" b="0" dirty="0">
    <a:solidFill><a:srgbClr val="FFFFFF"><a:alpha val="80000"/></a:srgbClr></a:solidFill>
    <a:latin typeface="Calibri"/>
  </a:rPr><a:t>Chief Executive Officer</a:t></a:r>
</a:p>
```

---

## Typography Guidelines

> For design rationale (size hierarchy, labeling rules, do/don't guidance), see `methodology.md` §5.5. This section covers OOXML implementation values.

| Role | Size (sz) | Bold | Color |
|------|-----------|------|-------|
| Slide title | `2400`-`2800` | Yes | Dark or white |
| Primary label | `1200`-`1400` | Yes | White on dark |
| Secondary label | `900`-`1100` | No | White (80% alpha) |
| Caption / small | `900`-`1000` | No | #666666 |
| Lane header | `900`-`1000` | Yes | #888888 |

**Safe fonts**: Calibri (default), Arial, Helvetica, Georgia (serif)
**Minimum readable**: 8pt (`sz="800"`)

---

## Z-Ordering

XML element order in `<p:spTree>` = render order (first = bottom, last = top).

```python
spTree = slide.shapes._spTree
spTree.insert(2, bg_element)   # background at bottom
spTree.append(shape_element)   # content shapes on top
```

Recommended order:
1. Background rect (insert at index 2)
2. Lane/section backgrounds
3. Title
4. Connectors/arrows
5. Content shapes (on top, so lines don't cross over them)

---

## Full Shape XML Template

```xml
<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
      xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr>
    <p:cNvPr id="2" name="Shape 2"/>
    <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
    <p:nvPr/>
  </p:nvSpPr>
  <p:spPr>
    <a:xfrm><a:off x="914400" y="457200"/><a:ext cx="1828800" cy="685800"/></a:xfrm>
    <a:prstGeom prst="roundRect"><a:avLst/></a:prstGeom>
    <a:gradFill>
      <a:gsLst>
        <a:gs pos="0"><a:srgbClr val="5B9BD5"/></a:gs>
        <a:gs pos="100000"><a:srgbClr val="2E75B6"/></a:gs>
      </a:gsLst>
      <a:lin ang="5400000" scaled="0"/>
    </a:gradFill>
    <a:ln w="19050"><a:solidFill><a:srgbClr val="1F4E79"/></a:solidFill><a:round/></a:ln>
    <a:effectLst>
      <a:outerShdw blurRad="50800" dist="38100" dir="5400000" algn="tl" rotWithShape="0">
        <a:srgbClr val="000000"><a:alpha val="35000"/></a:srgbClr>
      </a:outerShdw>
    </a:effectLst>
  </p:spPr>
  <p:txBody>
    <a:bodyPr wrap="square" anchor="ctr"><a:normAutofit/></a:bodyPr>
    <a:lstStyle/>
    <a:p>
      <a:pPr algn="ctr"/>
      <a:r>
        <a:rPr lang="en-US" sz="1400" b="1" dirty="0">
          <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
          <a:latin typeface="Calibri"/>
        </a:rPr>
        <a:t>Label</a:t>
      </a:r>
    </a:p>
  </p:txBody>
</p:sp>
```

---

## Layout Recipes

### Horizontal Flow (n shapes)
```python
SLIDE_W = 9144000
SW, SH = 1371600, 685800  # 1.5" x 0.75"
GAP = 228600               # 0.25"
n = 5
total_w = n * SW + (n - 1) * GAP
left = (SLIDE_W - total_w) // 2
y = (5143500 - SH) // 2
positions = [(left + i * (SW + GAP), y) for i in range(n)]
```

### Centered Row (reusable)
```python
def center_row(n, sw, gap, slide_w=9144000):
    total = n * sw + (n - 1) * gap
    left = (slide_w - total) // 2
    return [left + i * (sw + gap) for i in range(n)]
```

### Swimlane Layout
```python
TITLE_H = 457200
n_lanes = 3
usable_h = 5143500 - TITLE_H
lane_h = usable_h // n_lanes
for i in range(n_lanes):
    lane_y = TITLE_H + i * lane_h
    # place components centered vertically within lane
    comp_y = lane_y + (lane_h - comp_h) // 2
```

---

## Validation (Simple)

```python
def validate(shapes, slide_w=9144000, slide_h=5143500):
    """Quick sanity check before saving."""
    ids = [s['id'] for s in shapes]
    assert len(ids) == len(set(ids)), f"Duplicate IDs: {ids}"
    for s in shapes:
        r = s['rect']
        assert r['x'] >= 0 and r['y'] >= 0, f"Negative position: {s['id']}"
        assert r['x'] + r['cx'] <= slide_w, f"Off-slide right: {s['id']}"
        assert r['y'] + r['cy'] <= slide_h, f"Off-slide bottom: {s['id']}"
```

---

## Orthogonal Routing with Curved Elbows

OOXML's built-in connectors (`bentConnector3`) don't support rounded corners. For professional orthogonal arrows with smooth curved elbows, use **custom geometry** (`a:custGeom`) inside a regular `p:sp` shape, combining `a:lnTo` (straight segments) with `a:arcTo` (quarter-circle arcs at turns).

### Arc Angle Lookup Table

All angles in 60,000ths of a degree. `swAng` positive = counter-clockwise, negative = clockwise.

| Turn | stAng | swAng |
|------|-------|-------|
| Right→Down | 16200000 | 5400000 |
| Right→Up | 5400000 | -5400000 |
| Left→Down | 16200000 | -5400000 |
| Left→Up | 5400000 | 5400000 |
| Down→Right | 10800000 | -5400000 |
| Down→Left | 0 | 5400000 |
| Up→Right | 10800000 | 5400000 |
| Up→Left | 0 | -5400000 |

### Helper Function: `build_routed_connector_xml()`

```python
def build_routed_connector_xml(waypoints, sid, name="Connector",
                                color="888888", width=19050,
                                dash="solid", tail="triangle",
                                head="none", radius=150000):
    """Build an orthogonal connector with curved elbows using custom geometry.

    Args:
        waypoints: list of (x, y) tuples in EMU (absolute slide coords).
                   Each consecutive pair must differ in only x or y.
        sid: unique shape ID (int).
        name: shape name string.
        color: 6-hex color string (no #).
        width: line width in EMU (19050 = 1.5pt).
        dash: "solid", "dot", "dash", "lgDash", "dashDot".
        tail: arrowhead type at end — "none", "triangle", "stealth", "arrow".
        head: arrowhead type at start.
        radius: corner radius in EMU (150000 ≈ 0.16").

    Returns:
        XML string for a <p:sp> element to append to spTree.
    """
    # Bounding box
    xs = [p[0] for p in waypoints]
    ys = [p[1] for p in waypoints]
    min_x, min_y = min(xs), min(ys)
    max_x, max_y = max(xs), max(ys)
    bbox_w = max(max_x - min_x, 1)
    bbox_h = max(max_y - min_y, 1)

    # Convert to local coordinates
    pts = [(x - min_x, y - min_y) for x, y in waypoints]

    # Direction between two points
    def direction(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        if dx > 0: return 'R'
        if dx < 0: return 'L'
        if dy > 0: return 'D'
        return 'U'

    # Arc lookup: (from_dir, to_dir) -> (stAng, swAng)
    ARC = {
        ('R', 'D'): (16200000, 5400000),   ('R', 'U'): (5400000, -5400000),
        ('L', 'D'): (16200000, -5400000),  ('L', 'U'): (5400000, 5400000),
        ('D', 'R'): (10800000, -5400000),  ('D', 'L'): (0, 5400000),
        ('U', 'R'): (10800000, 5400000),   ('U', 'L'): (0, -5400000),
    }

    # Build path commands
    path_cmds = [f'<a:moveTo><a:pt x="{pts[0][0]}" y="{pts[0][1]}"/></a:moveTo>']

    for i in range(1, len(pts)):
        if i < len(pts) - 1:
            # Corner point — shorten segments and add arc
            prev_dir = direction(pts[i-1], pts[i])
            next_dir = direction(pts[i], pts[i+1])

            # Clamp radius to half the shorter adjacent segment
            seg_before = abs(pts[i][0]-pts[i-1][0]) + abs(pts[i][1]-pts[i-1][1])
            seg_after = abs(pts[i+1][0]-pts[i][0]) + abs(pts[i+1][1]-pts[i][1])
            r = min(radius, seg_before // 2, seg_after // 2)

            # Point before corner (end of straight segment, R away from corner)
            bx, by = pts[i][0], pts[i][1]
            if prev_dir == 'R': bx -= r
            elif prev_dir == 'L': bx += r
            elif prev_dir == 'D': by -= r
            elif prev_dir == 'U': by += r
            path_cmds.append(f'<a:lnTo><a:pt x="{bx}" y="{by}"/></a:lnTo>')

            # Arc
            st, sw = ARC[(prev_dir, next_dir)]
            path_cmds.append(f'<a:arcTo wR="{r}" hR="{r}" stAng="{st}" swAng="{sw}"/>')
        else:
            # Final point — straight line to end
            path_cmds.append(
                f'<a:lnTo><a:pt x="{pts[i][0]}" y="{pts[i][1]}"/></a:lnTo>'
            )

    path_data = ''.join(path_cmds)

    head_xml = f'<a:headEnd type="{head}" w="med" len="med"/>' if head != "none" else '<a:headEnd type="none"/>'
    tail_xml = f'<a:tailEnd type="{tail}" w="med" len="med"/>' if tail != "none" else '<a:tailEnd type="none"/>'

    return f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
       xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr>
    <p:cNvPr id="{sid}" name="{name}"/>
    <p:cNvSpPr/>
    <p:nvPr/>
  </p:nvSpPr>
  <p:spPr>
    <a:xfrm><a:off x="{min_x}" y="{min_y}"/><a:ext cx="{bbox_w}" cy="{bbox_h}"/></a:xfrm>
    <a:custGeom>
      <a:avLst/>
      <a:gdLst/>
      <a:ahLst/>
      <a:cxnLst/>
      <a:rect l="0" t="0" r="{bbox_w}" b="{bbox_h}"/>
      <a:pathLst>
        <a:path w="{bbox_w}" h="{bbox_h}">
          {path_data}
        </a:path>
      </a:pathLst>
    </a:custGeom>
    <a:noFill/>
    <a:ln w="{width}">
      <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
      <a:prstDash val="{dash}"/>
      <a:round/>
      {head_xml}
      {tail_xml}
    </a:ln>
  </p:spPr>
  <p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr lang="en-US" dirty="0"/></a:p></p:txBody>
</p:sp>'''
```

### Usage Example

```python
from lxml import etree

# Straight horizontal arrow (2 waypoints, no corners)
xml = build_routed_connector_xml(
    waypoints=[(1000000, 2000000), (3000000, 2000000)],
    sid=10, color="4472C4", tail="triangle"
)
spTree.append(etree.fromstring(xml))

# L-shaped: right then down (3 waypoints, 1 corner)
xml = build_routed_connector_xml(
    waypoints=[(1000000, 1000000), (3000000, 1000000), (3000000, 3000000)],
    sid=11, color="4472C4", tail="triangle"
)
spTree.append(etree.fromstring(xml))

# Z-shaped: down, right, down (4 waypoints, 2 corners)
xml = build_routed_connector_xml(
    waypoints=[(2000000, 500000), (2000000, 1500000),
               (5000000, 1500000), (5000000, 2500000)],
    sid=12, color="888888", tail="stealth"
)
spTree.append(etree.fromstring(xml))
```

**How it works**: For each corner waypoint, the preceding straight segment is shortened by `radius`, an `arcTo` draws a quarter-circle, then the next segment starts `radius` past the corner. The radius is automatically clamped when segments are shorter than `2 * radius`.

---

## Legend / Key

When a diagram uses 3+ semantic colors or 2+ line styles, add a legend so viewers can decode the visual grammar without guessing. The `make_legend_xml()` helper renders a compact legend box with color swatches and optional line-style entries.

### Layout

```
┌─ Legend ──────────────┐
│ ■ Interface           │  ← 0.18" × 0.18" mini roundRect swatch + 9pt label
│ ■ Data Store          │
│ ■ Search              │
│ ── Primary Flow       │  ← 0.4" mini line + 9pt label
│ ╌╌ Optional/Async     │
└───────────────────────┘
```

- **Width**: ~1.8" (configurable via `legend_w`)
- **Row height**: 0.28" per entry
- **Title**: 10pt bold, `#2C3E50`
- **Labels**: 9pt regular, `#2C3E50`
- **Background**: white at 85% opacity, 1pt `#B0B0B0` border, small corner radius
- **Default position**: bottom-right with 0.15" margin from slide edges

### Helper Function: `make_legend_xml()`

```python
def make_legend_xml(
    sid,                      # shape ID counter start
    color_entries,            # list of (label, fill_hex)
    line_entries=None,        # list of (label, color_hex, is_dashed)
    x=None, y=None,           # position (defaults to bottom-right)
    slide_w=9144000,          # for default positioning
    slide_h=5143500,
    legend_w=1645920,         # ~1.8"
):
    """Build a legend box with color swatches and optional line-style entries.

    Returns:
        (xml_list, next_sid) — list of XML strings to append to spTree,
        and the next available shape ID.
    """
    line_entries = line_entries or []
    n_color = len(color_entries)
    n_line = len(line_entries)
    n_total = n_color + n_line

    # Sizing constants (EMU)
    row_h = 256032          # ~0.28"
    title_h = 274320        # ~0.30"
    pad_top = 45720         # 0.05"
    pad_bottom = 68580      # 0.075"
    legend_h = pad_top + title_h + n_total * row_h + pad_bottom

    margin = 137160         # 0.15" from slide edges
    if x is None:
        x = slide_w - legend_w - margin
    if y is None:
        y = slide_h - legend_h - margin

    swatch_size = 164592    # ~0.18"
    swatch_left = 91440     # 0.1" from legend left edge
    label_left = swatch_left + swatch_size + 68580  # swatch + 0.075" gap
    label_w = legend_w - label_left - 45720

    line_sample_w = 365760  # 0.4"
    line_sample_left = swatch_left

    xmls = []

    # --- Container box: semi-transparent white with gray border ---
    container_xml = f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
       xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr>
    <p:cNvPr id="{sid}" name="Legend Box"/>
    <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
    <p:nvPr/>
  </p:nvSpPr>
  <p:spPr>
    <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{legend_w}" cy="{legend_h}"/></a:xfrm>
    <a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 3200"/></a:avLst></a:prstGeom>
    <a:solidFill><a:srgbClr val="FFFFFF"><a:alpha val="85000"/></a:srgbClr></a:solidFill>
    <a:ln w="12700"><a:solidFill><a:srgbClr val="B0B0B0"/></a:solidFill><a:round/></a:ln>
  </p:spPr>
  <p:txBody>
    <a:bodyPr wrap="square" anchor="t" lIns="91440" tIns="45720" rIns="91440" bIns="0">
      <a:normAutofit/>
    </a:bodyPr>
    <a:lstStyle/>
    <a:p><a:pPr algn="l"/>
      <a:r><a:rPr lang="en-US" sz="1000" b="1" dirty="0">
        <a:solidFill><a:srgbClr val="2C3E50"/></a:solidFill>
        <a:latin typeface="Calibri"/>
      </a:rPr><a:t>Legend</a:t></a:r>
    </a:p>
  </p:txBody>
</p:sp>'''
    xmls.append(container_xml)
    sid += 1

    # --- Color swatch entries ---
    for i, (label, fill_hex) in enumerate(color_entries):
        ey = y + pad_top + title_h + i * row_h
        swatch_y = ey + (row_h - swatch_size) // 2

        # Mini filled roundRect swatch
        swatch_xml = f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
       xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr>
    <p:cNvPr id="{sid}" name="Legend Swatch {i}"/>
    <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
    <p:nvPr/>
  </p:nvSpPr>
  <p:spPr>
    <a:xfrm><a:off x="{x + swatch_left}" y="{swatch_y}"/><a:ext cx="{swatch_size}" cy="{swatch_size}"/></a:xfrm>
    <a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 10000"/></a:avLst></a:prstGeom>
    <a:solidFill><a:srgbClr val="{fill_hex}"/></a:solidFill>
    <a:ln w="6350"><a:solidFill><a:srgbClr val="{fill_hex}"/></a:solidFill><a:round/></a:ln>
  </p:spPr>
  <p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr lang="en-US" dirty="0"/></a:p></p:txBody>
</p:sp>'''
        xmls.append(swatch_xml)
        sid += 1

        # Label text
        label_xml = f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
       xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr>
    <p:cNvPr id="{sid}" name="Legend Label {i}"/>
    <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
    <p:nvPr/>
  </p:nvSpPr>
  <p:spPr>
    <a:xfrm><a:off x="{x + label_left}" y="{ey}"/><a:ext cx="{label_w}" cy="{row_h}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
    <a:noFill/>
    <a:ln><a:noFill/></a:ln>
  </p:spPr>
  <p:txBody>
    <a:bodyPr wrap="square" anchor="ctr" lIns="0" tIns="0" rIns="0" bIns="0">
      <a:normAutofit/>
    </a:bodyPr>
    <a:lstStyle/>
    <a:p><a:pPr algn="l"/>
      <a:r><a:rPr lang="en-US" sz="900" b="0" dirty="0">
        <a:solidFill><a:srgbClr val="2C3E50"/></a:solidFill>
        <a:latin typeface="Calibri"/>
      </a:rPr><a:t>{label}</a:t></a:r>
    </a:p>
  </p:txBody>
</p:sp>'''
        xmls.append(label_xml)
        sid += 1

    # --- Line style entries ---
    for j, (label, color_hex, is_dashed) in enumerate(line_entries):
        ey = y + pad_top + title_h + (n_color + j) * row_h
        line_y = ey + row_h // 2
        dash_val = "dash" if is_dashed else "solid"

        # Mini line sample using custom geometry
        line_xml = f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
       xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr>
    <p:cNvPr id="{sid}" name="Legend Line {j}"/>
    <p:cNvSpPr/>
    <p:nvPr/>
  </p:nvSpPr>
  <p:spPr>
    <a:xfrm><a:off x="{x + line_sample_left}" y="{line_y}"/><a:ext cx="{line_sample_w}" cy="1"/></a:xfrm>
    <a:custGeom>
      <a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/>
      <a:rect l="0" t="0" r="{line_sample_w}" b="1"/>
      <a:pathLst>
        <a:path w="{line_sample_w}" h="1">
          <a:moveTo><a:pt x="0" y="0"/></a:moveTo>
          <a:lnTo><a:pt x="{line_sample_w}" y="0"/></a:lnTo>
        </a:path>
      </a:pathLst>
    </a:custGeom>
    <a:noFill/>
    <a:ln w="19050">
      <a:solidFill><a:srgbClr val="{color_hex}"/></a:solidFill>
      <a:prstDash val="{dash_val}"/>
      <a:round/>
    </a:ln>
  </p:spPr>
  <p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr lang="en-US" dirty="0"/></a:p></p:txBody>
</p:sp>'''
        xmls.append(line_xml)
        sid += 1

        # Label text for line entry
        line_label_left = line_sample_left + line_sample_w + 68580
        line_label_w = legend_w - line_label_left - 45720

        line_label_xml = f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
       xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr>
    <p:cNvPr id="{sid}" name="Legend Line Label {j}"/>
    <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
    <p:nvPr/>
  </p:nvSpPr>
  <p:spPr>
    <a:xfrm><a:off x="{x + line_label_left}" y="{ey}"/><a:ext cx="{line_label_w}" cy="{row_h}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
    <a:noFill/>
    <a:ln><a:noFill/></a:ln>
  </p:spPr>
  <p:txBody>
    <a:bodyPr wrap="square" anchor="ctr" lIns="0" tIns="0" rIns="0" bIns="0">
      <a:normAutofit/>
    </a:bodyPr>
    <a:lstStyle/>
    <a:p><a:pPr algn="l"/>
      <a:r><a:rPr lang="en-US" sz="900" b="0" dirty="0">
        <a:solidFill><a:srgbClr val="2C3E50"/></a:solidFill>
        <a:latin typeface="Calibri"/>
      </a:rPr><a:t>{label}</a:t></a:r>
    </a:p>
  </p:txBody>
</p:sp>'''
        xmls.append(line_label_xml)
        sid += 1

    return xmls, sid
```

### Usage Example

```python
from lxml import etree

# Color entries from STYLE_COLORS dict
color_entries = [
    ("Interface", "4472C4"),
    ("Event Bus", "ED7D31"),
    ("Data Store", "70AD47"),
    ("External", "5D6D7E"),
]

# Optional line style entries
line_entries = [
    ("Primary flow", "888888", False),
    ("Optional/Async", "888888", True),
]

legend_xmls, sid = make_legend_xml(sid, color_entries, line_entries)
for xml_str in legend_xmls:
    spTree.append(etree.fromstring(xml_str))
```

### Integration Pattern

When generating a diagram script, build the legend from the existing `STYLE_COLORS` dict (or equivalent) at the end, after all diagram shapes:

```python
# At end of script, after all diagram shapes:
legend_entries = [(k.replace("_", " ").title(), v[0]) for k, v in STYLE_COLORS.items()]
line_entries = [("Primary flow", "888888", False), ("Optional", "888888", True)]
legend_xmls, sid = make_legend_xml(sid, legend_entries, line_entries)
for xml_str in legend_xmls:
    spTree.append(etree.fromstring(xml_str))
```

The legend is appended **last** in z-order so it renders on top of all other elements. Default position is **bottom-right** (matching PowerPoint/Excel chart legend convention and natural scan-path termination). Override `x`, `y` to place elsewhere if the bottom-right is occupied.

---

## Icon Embedding

Add recognizable icons inside diagram shapes to improve semantic transparency — viewers recognize a component's purpose before reading the label. Icons are added as a **post-processing** step after the base PPTX is saved, keeping the diagram valid even if icon resolution fails.

**Pipeline**: SVG → PNG via CairoSVG → embed via `add_picture()` (python-pptx cannot embed SVG natively).

**Prerequisites**: `pip install cairosvg` (optional — only needed for Iconify API icons; local PNG files work without it).

### Helper Function: `resolve_icon()`

```python
def resolve_icon(icon_key, size=64, tint="FFFFFF", cache_dir="/tmp/diagram_icons"):
    """Resolve an icon key to a local PNG file path.

    Resolution chain:
    1. Local file path (contains / or ends in .png/.svg)
    2. Iconify API (prefix:name format, e.g., "mdi:database")
    3. Returns None if resolution fails

    Args:
        icon_key: Icon identifier string.
        size: Icon size in pixels (width=height).
        tint: Hex color for monochrome SVGs (e.g., "FFFFFF" for white).
              Set to None to preserve original colors.
        cache_dir: Directory for cached PNG files.

    Returns:
        Path to PNG file, or None if resolution failed.
    """
    import os
    os.makedirs(cache_dir, exist_ok=True)

    # --- Local file path ---
    if "/" in icon_key or "\\" in icon_key or icon_key.endswith((".png", ".svg")):
        if icon_key.endswith(".png"):
            return icon_key if os.path.exists(icon_key) else None
        if icon_key.endswith(".svg"):
            if not os.path.exists(icon_key):
                return None
            try:
                import cairosvg
                png_path = os.path.join(cache_dir, os.path.basename(icon_key) + ".png")
                with open(icon_key, "r") as f:
                    svg_data = f.read()
                if tint:
                    svg_data = svg_data.replace("currentColor", f"#{tint}")
                cairosvg.svg2png(bytestring=svg_data.encode(), write_to=png_path,
                                 output_width=size, output_height=size)
                return png_path
            except ImportError:
                print(f"  Warning: cairosvg not installed, cannot convert {icon_key}")
                return None
        return None

    # --- Iconify API (prefix:name) ---
    if ":" in icon_key:
        tint_suffix = f"_{tint}" if tint else "_orig"
        cache_name = f"{icon_key.replace(':', '_')}_{size}{tint_suffix}.png"
        png_path = os.path.join(cache_dir, cache_name)
        if os.path.exists(png_path):
            return png_path
        try:
            import cairosvg
            import urllib.request
            prefix, name = icon_key.split(":", 1)
            url = f"https://api.iconify.design/{prefix}/{name}.svg?width={size}&height={size}"
            req = urllib.request.Request(url, headers={"User-Agent": "python-pptx-diagrams/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                svg_data = resp.read().decode("utf-8")
            if tint:
                svg_data = svg_data.replace("currentColor", f"#{tint}")
            cairosvg.svg2png(bytestring=svg_data.encode(), write_to=png_path,
                             output_width=size, output_height=size)
            return png_path
        except ImportError:
            print(f"  Warning: cairosvg not installed, skipping icon '{icon_key}'")
            return None
        except Exception as e:
            print(f"  Warning: Failed to resolve icon '{icon_key}': {e}")
            return None

    return None
```

### Helper Function: `enrich_shape_with_icon()`

```python
def enrich_shape_with_icon(slide, shape_name, icon_path, icon_size_inches=0.35):
    """Add an icon image above the text label inside a named shape.

    Places a PNG picture element centered horizontally in the upper portion
    of the shape, and modifies the shape's text body to push text below the icon.

    Args:
        slide: python-pptx Slide object.
        shape_name: The name attribute of the target shape.
        icon_path: Path to a PNG file.
        icon_size_inches: Icon width and height in inches (square).

    Returns:
        True if icon was added, False if shape not found or error.
    """
    from pptx.util import Inches, Emu

    target = None
    for shape in slide.shapes:
        if shape.name == shape_name:
            target = shape
            break
    if target is None:
        print(f"  Warning: Shape '{shape_name}' not found")
        return False

    icon_w = icon_h = Inches(icon_size_inches)
    icon_left = target.left + (target.width - icon_w) // 2
    icon_top = target.top + Emu(91440)  # 0.1" from top of shape

    try:
        slide.shapes.add_picture(icon_path, icon_left, icon_top, icon_w, icon_h)
    except Exception as e:
        print(f"  Warning: Failed to add icon to '{shape_name}': {e}")
        return False

    # Adjust text body — push text below icon
    if target.has_text_frame:
        ns = "http://schemas.openxmlformats.org/drawingml/2006/main"
        body_pr = target.text_frame._txBody.find(f"{{{ns}}}bodyPr")
        if body_pr is not None:
            body_pr.set("tIns", "365760")  # 0.4" top inset
            body_pr.set("anchor", "b")     # anchor text to bottom

    return True
```

### Helper Function: `enrich_pptx_with_icons()`

```python
def enrich_pptx_with_icons(pptx_path, icon_map, output_path=None,
                            icon_size=64, icon_size_inches=0.35,
                            tint="FFFFFF", slide_index=0):
    """Post-process a PPTX file to add icons to named shapes.

    Args:
        pptx_path: Path to existing PPTX file.
        icon_map: Dict of {shape_name: icon_key} mappings.
        output_path: Output path (defaults to overwriting pptx_path).
        icon_size: Icon resolution in pixels for download/conversion.
        icon_size_inches: Icon display size in the slide (inches).
        tint: Default tint color for monochrome icons ("FFFFFF" = white).
              Set to None to preserve original colors.
        slide_index: Which slide to modify (0-indexed).

    Returns:
        List of (shape_name, success_bool) tuples.
    """
    from pptx import Presentation

    prs = Presentation(pptx_path)
    slide = prs.slides[slide_index]
    results = []

    for shape_name, icon_key in icon_map.items():
        icon_path = resolve_icon(icon_key, size=icon_size, tint=tint)
        if icon_path:
            ok = enrich_shape_with_icon(slide, shape_name, icon_path, icon_size_inches)
            results.append((shape_name, ok))
        else:
            results.append((shape_name, False))

    prs.save(output_path or pptx_path)
    return results
```

### Usage Example

```python
# After generating and saving the base diagram:
ICONS = {
    "web":    "mdi:web",
    "auth":   "mdi:lock",
    "udb":    "mdi:database",
    "cache":  "mdi:flash",
}

results = enrich_pptx_with_icons("diagram.pptx", ICONS, tint="FFFFFF")
added = sum(1 for _, ok in results if ok)
print(f"Icons: {added}/{len(ICONS)} added successfully")
```

### Icon Key Formats

| Format | Example | Resolution |
|--------|---------|------------|
| Local PNG | `/path/to/icon.png` | Used directly |
| Local SVG | `./icons/db.svg` | Converted to PNG via CairoSVG |
| Iconify | `mdi:database` | Downloaded from Iconify API, converted, cached |
| Iconify | `tabler:cloud` | Same — any Iconify prefix:name works |
| Iconify | `logos:aws-lambda` | Multi-color vendor logo (use `tint=None`) |

### Common Iconify Prefixes for Diagrams

| Prefix | Set | Icons | Style |
|--------|-----|-------|-------|
| `mdi` | Material Design Icons | ~7,000 | Filled, clean |
| `tabler` | Tabler Icons | ~5,800 | 2px stroke, outline |
| `ph` | Phosphor Icons | ~6,000 | Multiple weights |
| `lucide` | Lucide | ~1,555 | Minimalist outline |
| `logos` | SVG Logos | ~1,500 | Full-color brand logos |
