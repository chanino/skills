# OOXML/DrawingML Quick Reference

## Units & Dimensions

| Unit | EMU value | Notes |
|------|-----------|-------|
| 1 inch | 914,400 EMU | 1 in = 914400 |
| 1 cm | 360,000 EMU | |
| 1 pt | 12,700 EMU | |
| Slide width (widescreen) | 9,144,000 EMU | 10 inches |
| Slide height (widescreen) | 5,143,500 EMU | 5.625 inches |
| Slide width (standard 4:3) | 9,144,000 EMU | same width |
| Slide height (standard 4:3) | 6,858,000 EMU | 7.5 inches |

**Namespace prefixes (always declare these):**
```
xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
```

---

## Shape Presets

### Basic Geometry
| Visual | Preset name | Notes |
|--------|-------------|-------|
| Rectangle | `rect` | |
| Rounded rectangle | `roundRect` | adj=corner radius |
| Ellipse / circle | `ellipse` | |
| Right triangle | `rtTriangle` | |
| Triangle | `triangle` | |
| Diamond | `diamond` | |
| Parallelogram | `parallelogram` | |
| Trapezoid | `trapezoid` | |
| Pentagon | `homePlate` | 5-sided home plate |
| Hexagon | `hexagon` | |
| Heptagon | `heptagon` | |
| Octagon | `octagon` | |
| Decagon | `decagon` | |
| Dodecagon | `dodecagon` | |
| Pie | `pie` | adj=start/end angle |
| Chord | `chord` | |
| Teardrop | `teardrop` | |
| Frame | `frame` | hollow rectangle |
| Half frame | `halfFrame` | |
| Corner | `corner` | L-shape |
| Diagonal stripe | `diagStripe` | |
| Cross | `plus` | |
| Plaque | `plaque` | rounded notch corners |
| Can / cylinder | `can` | |
| Cube | `cube` | |
| Bevel | `bevel` | |
| Donut | `donut` | |
| No symbol | `noSmoking` | circle with slash |
| Cloud | `cloud` | |
| Heart | `heart` | |
| Lightning bolt | `lightningBolt` | |
| Sun | `sun` | |
| Moon | `moon` | |
| Smiley face | `smileyFace` | |
| Folded corner | `folderCorner` | note/sticky shape |
| Block arc | `blockArc` | |
| Snip corner rect | `snip1Rect` / `snip2SameRect` / `snip2DiagRect` / `snipRoundRect` | |
| Round corner rect | `round1Rect` / `round2SameRect` / `round2DiagRect` | |

### Arrow Shapes
| Visual | Preset name |
|--------|-------------|
| Right arrow | `rightArrow` |
| Left arrow | `leftArrow` |
| Up arrow | `upArrow` |
| Down arrow | `downArrow` |
| Left-right arrow | `leftRightArrow` |
| Up-down arrow | `upDownArrow` |
| Quad arrow | `quadArrow` |
| Left-right-up arrow | `leftRightUpArrow` |
| Bent arrow | `bentArrow` |
| U-turn arrow | `uturnArrow` |
| Curved right arrow | `curvedRightArrow` |
| Curved left arrow | `curvedLeftArrow` |
| Curved up arrow | `curvedUpArrow` |
| Curved down arrow | `curvedDownArrow` |
| Striped right arrow | `stripedRightArrow` |
| Notched right arrow | `notchedRightArrow` |
| Pentagon arrow | `pentagonArrow` (use `homePlate`) |
| Chevron | `chevron` |
| Double chevron | `doubleWave` (use two chevrons) |
| Circular arrow | `circularArrow` |
| Left circular arrow | `leftCircularArrow` |
| Right circular arrow (180°) | `swooshArrow` |
| Callout arrows (all 4 dirs) | `leftArrowCallout`, `rightArrowCallout`, `upArrowCallout`, `downArrowCallout` |
| Quad arrow callout | `quadArrowCallout` |

### Flowchart Shapes (prefix: `flowChart`)
| Visual | Preset name |
|--------|-------------|
| Process (rect) | `flowChartProcess` |
| Decision (diamond) | `flowChartDecision` |
| Data (parallelogram) | `flowChartInputOutput` |
| Predefined process | `flowChartPredefinedProcess` |
| Internal storage | `flowChartInternalStorage` |
| Document | `flowChartDocument` |
| Multi-document | `flowChartMultidocument` |
| Terminator (stadium) | `flowChartTerminator` |
| Preparation (hexagon) | `flowChartPreparation` |
| Manual input | `flowChartManualInput` |
| Manual operation | `flowChartManualOperation` |
| Connector (circle) | `flowChartConnector` |
| Off-page connector | `flowChartOffpageConnector` |
| Punched card | `flowChartPunchedCard` |
| Punched tape | `flowChartPunchedTape` |
| Summing junction | `flowChartSummingJunction` |
| Or | `flowChartOr` |
| Collate | `flowChartCollate` |
| Sort | `flowChartSort` |
| Extract | `flowChartExtract` |
| Merge | `flowChartMerge` |
| Stored data | `flowChartStoredData` |
| Delay | `flowChartDelay` |
| Alternate process | `flowChartAlternateProcess` |
| Display | `flowChartDisplay` |
| Magnetic disk (database) | `flowChartMagneticDisk` |
| Magnetic drum | `flowChartMagneticDrum` |
| Magnetic tape | `flowChartMagneticTape` |
| Online storage | `flowChartOnlineStorage` |

### Stars and Banners
| Visual | Preset name |
|--------|-------------|
| 4-point star | `star4` |
| 5-point star | `star5` |
| 6-point star | `star6` |
| 7-point star | `star7` |
| 8-point star | `star8` |
| 10-point star | `star10` |
| 12-point star | `star12` |
| 16-point star | `star16` |
| 24-point star | `star24` |
| 32-point star | `star32` |
| Ribbon (curved banner) | `ribbon` |
| Ribbon 2 | `ribbon2` |
| Ellipse ribbon | `ellipseRibbon` |
| Ellipse ribbon 2 | `ellipseRibbon2` |
| Left/right ribbon | `leftRightRibbon` |
| Vertical scroll | `verticalScroll` |
| Horizontal scroll | `horizontalScroll` |
| Wave | `wave` |
| Double wave | `doubleWave` |
| Irregular seal 1 | `irregularSeal1` |
| Irregular seal 2 | `irregularSeal2` |

### Callout Shapes
| Visual | Preset name |
|--------|-------------|
| Rectangular callout | `wedgeRectCallout` |
| Rounded rect callout | `wedgeRoundRectCallout` |
| Ellipse callout | `wedgeEllipseCallout` |
| Cloud callout | `cloudCallout` |
| Line callout 1 | `borderCallout1` |
| Line callout 2 | `borderCallout2` |
| Line callout 3 | `borderCallout3` |
| Accent callout 1 | `accentCallout1` |
| Accent callout 2 | `accentCallout2` |
| Accent callout 3 | `accentCallout3` |
| Callout 1 (no border) | `callout1` |
| Callout 2 | `callout2` |
| Callout 3 | `callout3` |

---

## Connectors

| Tag | Bend points | Use case |
|-----|------------|----------|
| `straightConnector1` | 0 | Direct lines, technical diagrams |
| `bentConnector2` | 1 | One 90° bend |
| `bentConnector3` | 2 | **Default — orthogonal routing, proposal standard** |
| `bentConnector4` | 3 | Three bends |
| `bentConnector5` | 4 | Four bends |
| `curvedConnector2` | 1 | Gentle S-curve |
| `curvedConnector3` | 2 | S-curve bezier — use only when organic flow is intentional |
| `curvedConnector4` | 3 | Complex curve |
| `curvedConnector5` | 4 | Very complex curve |

### Connection Point Indexes
```
         0 (top)
         |
3 (left)--+--1 (right)
         |
         2 (bottom)
```

---

## Arrowhead Types

| Value | Visual |
|-------|--------|
| `none` | No arrowhead |
| `arrow` | Open arrow (chevron) |
| `triangle` | Filled triangle |
| `stealth` | Filled stealth/slim triangle |
| `diamond` | Filled diamond |
| `oval` | Filled circle |

**Size modifiers** (for `<a:headEnd>` and `<a:tailEnd>`):
- `w`: width — `sm`, `med`, `lg`
- `len`: length — `sm`, `med`, `lg`

---

## Line Styles (`<a:ln>`)

```xml
<a:ln w="25400" cap="flat" cmpd="sng">
  <!-- w in EMU: 12700=1pt, 25400=2pt, 38100=3pt -->
  <!-- cap: flat | rnd | sq -->
  <!-- cmpd: sng | dbl | thickThin | thinThick | tri -->
  <a:solidFill><a:srgbClr val="4472C4"/></a:solidFill>
  <a:prstDash val="solid"/>
  <!-- prstDash values: solid | dot | dash | lgDash | dashDot | lgDashDot | lgDashDotDot | sysDash | sysDot | sysDashDot | sysDashDotDot -->
  <a:headEnd type="none" w="med" len="med"/>
  <a:tailEnd type="triangle" w="med" len="med"/>
</a:ln>
```

---

## Fill Types

### Solid Fill
```xml
<a:solidFill>
  <a:srgbClr val="4472C4"/>  <!-- hex, no # -->
</a:solidFill>
```

### Gradient Fill
```xml
<a:gradFill>
  <a:gsLst>
    <a:gs pos="0">      <!-- 0 = start, 100000 = end -->
      <a:srgbClr val="4472C4"/>
    </a:gs>
    <a:gs pos="100000">
      <a:srgbClr val="2E4FA3"/>
    </a:gs>
  </a:gsLst>
  <a:lin ang="5400000" scaled="0"/>
  <!-- ang: 0=left-to-right, 5400000=top-to-bottom, 10800000=right-to-left, 16200000=bottom-to-top -->
</a:gradFill>
```

**Common gradient angles:**
| Direction | ang value |
|-----------|-----------|
| Left → Right | `0` |
| Top-Left → Bottom-Right | `2700000` |
| Top → Bottom | `5400000` |
| Top-Right → Bottom-Left | `8100000` |
| Right → Left | `10800000` |
| Bottom-Right → Top-Left | `13500000` |
| Bottom → Top | `16200000` |

### Pattern Fill
```xml
<a:pattFill prst="smGrid">
  <a:fgClr><a:srgbClr val="4472C4"/></a:fgClr>
  <a:bgClr><a:srgbClr val="FFFFFF"/></a:bgClr>
</a:pattFill>
<!-- prst values: smGrid, lgGrid, smCheck, lgCheck, horiz, vert, diagCross, etc. -->
```

### No Fill
```xml
<a:noFill/>
```

---

## Effects

### Outer Shadow
```xml
<a:effectLst>
  <a:outerShdw blurRad="50800" dist="38100" dir="5400000" algn="tl" rotWithShape="0">
    <!-- blurRad: blur radius EMU (50800 = 4pt) -->
    <!-- dist: shadow offset EMU (38100 = 3pt) -->
    <!-- dir: direction in 60000ths of degree (5400000 = 90° = down) -->
    <!-- algn: tl | t | tr | l | ctr | r | bl | b | br -->
    <a:srgbClr val="000000">
      <a:alpha val="40000"/>  <!-- 0-100000; 40000 = 40% opacity -->
    </a:srgbClr>
  </a:outerShdw>
</a:effectLst>
```

### Glow
```xml
<a:effectLst>
  <a:glow rad="63500">  <!-- radius EMU -->
    <a:srgbClr val="4472C4">
      <a:alpha val="40000"/>
    </a:srgbClr>
  </a:glow>
</a:effectLst>
```

### Soft Edge
```xml
<a:effectLst>
  <a:softEdge rad="63500"/>
</a:effectLst>
```

### Inner Shadow
```xml
<a:effectLst>
  <a:innerShdw blurRad="50800" dist="0" dir="5400000">
    <a:srgbClr val="000000">
      <a:alpha val="50000"/>
    </a:srgbClr>
  </a:innerShdw>
</a:effectLst>
```

### Reflection
```xml
<a:effectLst>
  <a:reflection blurRad="6350" stA="52000" stPos="0" endA="300" endPos="90000"
                dist="0" dir="5400000" fadeDir="5400000" sx="100000" sy="-100000"
                kx="0" ky="0" algn="bl" rotWithShape="0"/>
</a:effectLst>
```

---

## Text Body (`<p:txBody>`)

```xml
<p:txBody>
  <a:bodyPr wrap="square" lIns="91440" rIns="91440" tIns="45720" bIns="45720"
             anchor="ctr">
    <!-- anchor: t | ctr | b -->
    <!-- lIns/rIns: left/right inset EMU (91440 = 0.1 inch) -->
    <!-- tIns/bIns: top/bottom inset EMU (45720 = 0.05 inch) -->
    <a:normAutofit/>  <!-- or <a:spAutoFit/> for auto-resize shape -->
  </a:bodyPr>
  <a:lstStyle/>
  <a:p>
    <a:pPr algn="ctr"/>  <!-- algn: l | ctr | r | just | dist -->
    <a:r>
      <a:rPr lang="en-US" sz="1400" b="1" dirty="0">
        <!-- sz: font size in 100ths of pt (1400 = 14pt, 1000 = 10pt, 1800 = 18pt) -->
        <!-- b: bold (0 or 1), i: italic, u: sng/dbl/heavy -->
        <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
        <a:latin typeface="Calibri" panose="020F0502020204030204"/>
      </a:rPr>
      <a:t>Your text here</a:t>
    </a:r>
  </a:p>
</p:txBody>
```

---

## Z-Ordering

XML element order in `<p:spTree>` = render order (first = bottom, last = top).

```xml
<p:spTree>
  <p:nvGrpSpPr>...</p:nvGrpSpPr>  <!-- always first, do not touch -->
  <p:grpSpPr>...</p:grpSpPr>      <!-- always second, do not touch -->
  <!-- insert background shapes here (index 2) -->
  <!-- insert connectors here -->
  <!-- insert foreground shapes last (top of stack) -->
</p:spTree>
```

To insert at z-bottom (after mandatory preamble):
```python
spTree = slide.shapes._spTree
spTree.insert(2, new_element)   # inserts at bottom of draw order
spTree.append(new_element)      # appends at top of draw order
```

---

## Full Shape XML Skeleton

```xml
<p:sp>
  <p:nvSpPr>
    <p:cNvPr id="2" name="Shape 2"/>   <!-- id must be unique int per slide, start at 2 -->
    <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
    <p:nvPr/>
  </p:nvSpPr>
  <p:spPr>
    <a:xfrm>
      <a:off x="914400" y="457200"/>   <!-- position in EMU -->
      <a:ext cx="1828800" cy="685800"/> <!-- size in EMU -->
    </a:xfrm>
    <a:prstGeom prst="flowChartProcess">
      <a:avLst/>
    </a:prstGeom>
    <!-- fill -->
    <a:solidFill><a:srgbClr val="4472C4"/></a:solidFill>
    <!-- line -->
    <a:ln w="25400">
      <a:solidFill><a:srgbClr val="2E4FA3"/></a:solidFill>
    </a:ln>
    <!-- effects (optional) -->
    <a:effectLst>
      <a:outerShdw blurRad="50800" dist="38100" dir="5400000" algn="tl" rotWithShape="0">
        <a:srgbClr val="000000"><a:alpha val="40000"/></a:srgbClr>
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

## Orthogonal Connector Full XML Template

The orthogonal (bent) connector is the default. It routes connectors in horizontal-vertical-horizontal (or V-H-V) segments with 90° elbows — the professional standard for proposal graphics.

### Sharp corners (default — proposal standard)
```xml
<p:cxnSp>
  <p:nvCxnSpPr>
    <p:cNvPr id="10" name="Connector 10"/>
    <p:cNvCxnSpPr>
      <a:stCxn id="2" idx="1"/>   <!-- shape id=2, right side (idx=1) -->
      <a:endCxn id="3" idx="3"/>  <!-- shape id=3, left side (idx=3) -->
    </p:cNvCxnSpPr>
    <p:nvPr/>
  </p:nvCxnSpPr>
  <p:spPr>
    <a:xfrm>
      <a:off x="2743200" y="685800"/>
      <a:ext cx="457200" cy="457200"/>
    </a:xfrm>
    <a:prstGeom prst="bentConnector3">
      <a:avLst/>
    </a:prstGeom>
    <a:noFill/>
    <a:ln w="25400">
      <a:solidFill><a:srgbClr val="4472C4"/></a:solidFill>
      <a:headEnd type="none"/>
      <a:tailEnd type="triangle" w="med" len="med"/>
    </a:ln>
  </p:spPr>
</p:cxnSp>
```

### Softened corners (round join variant)

**IMPORTANT:** Element order inside `<a:ln>` matters. `<a:prstDash>` must come BEFORE `<a:round/>` — reversing this order causes PowerPoint to ignore the round join.

```xml
    <a:ln w="25400">
      <a:solidFill><a:srgbClr val="4472C4"/></a:solidFill>
      <a:prstDash val="solid"/>
      <a:round/>
      <a:headEnd type="none"/>
      <a:tailEnd type="triangle" w="med" len="med"/>
    </a:ln>
```

### Connector `flipH` / `flipV`

When the target shape is to the LEFT of the source (for horizontal connectors) or ABOVE the source (for vertical connectors), the connector bounding box needs flip attributes on `<a:xfrm>`. Without these, connectors route in the wrong direction.

```xml
<!-- Target is left of source — add flipH -->
<a:xfrm flipH="1">
  <a:off x="..." y="..."/>
  <a:ext cx="..." cy="..."/>
</a:xfrm>

<!-- Target is above source — add flipV -->
<a:xfrm flipV="1">
  <a:off x="..." y="..."/>
  <a:ext cx="..." cy="..."/>
</a:xfrm>

<!-- Both — target is left AND above -->
<a:xfrm flipH="1" flipV="1">
  <a:off x="..." y="..."/>
  <a:ext cx="..." cy="..."/>
</a:xfrm>
```

**Computation:**
```python
flip_h = target_center_x < source_center_x  # target is left of source
flip_v = target_center_y < source_center_y  # target is above source
```

See `layout-engine.md` → `compute_connector_bbox()` for the full implementation.

**Bounding box formula — horizontal** (source right edge → target left edge):
```python
# source: x=sx, y=sy, cx=scx, cy=scy
# target: x=tx, y=ty, cx=tcx, cy=tcy
conn_x = sx + scx                        # right edge of source
conn_y = min(sy + scy/2, ty + tcy/2)    # top of bounding rect
conn_cx = tx - (sx + scx)               # gap width
conn_cy = abs((sy + scy/2) - (ty + tcy/2)) + 1  # height (min 1 EMU)
```

**Bounding box formula — vertical** (source bottom edge → target top edge):
```python
conn_x = min(sx + scx/2, tx + tcx/2)   # left of bounding rect
conn_y = sy + scy                        # bottom edge of source
conn_cx = abs((sx + scx/2) - (tx + tcx/2)) + 1  # width (min 1 EMU)
conn_cy = ty - (sy + scy)               # gap height
```

---

## Line Join Types

Line joins control the appearance of corners on connectors and shape outlines. Add inside `<a:ln>`:

| Join | XML | Result |
|------|-----|--------|
| Miter (default) | `<a:miter/>` | Sharp 90° corners — proposal standard |
| Round | `<a:round/>` | Slightly softened corners |
| Bevel | `<a:bevel/>` | Chamfered/flat corners |

**OOXML element order inside `<a:ln>`** (must be in this order):
1. Fill (`<a:solidFill>`, `<a:noFill>`, etc.)
2. `<a:prstDash>` — dash pattern
3. Join (`<a:round/>`, `<a:miter/>`, `<a:bevel/>`)
4. `<a:headEnd>`
5. `<a:tailEnd>`

```xml
<!-- Correct: orthogonal connector with softened corners -->
<a:ln w="25400">
  <a:solidFill><a:srgbClr val="4472C4"/></a:solidFill>
  <a:prstDash val="solid"/>   <!-- dash BEFORE join -->
  <a:round/>                  <!-- join AFTER dash -->
  <a:headEnd type="none"/>
  <a:tailEnd type="triangle" w="med" len="med"/>
</a:ln>
```
