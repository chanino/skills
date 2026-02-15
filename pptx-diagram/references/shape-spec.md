# JSON Shape Specification Reference

This document defines the JSON schema that `build_slide.js --json` accepts for rendering native editable PowerPoint shapes.

## Coordinate System

- **Slide dimensions:** 10" wide × 5.625" tall (16:9 layout)
- **Title bar:** y=0 to y=0.75 (rendered automatically from `meta`)
- **Usable diagram area:** y=0.85 to y=5.35 (4.5" tall)
- **Footer area:** y=5.25 to y=5.55 (rendered automatically if `meta.footer` is set)
- **All coordinates are in inches** from the top-left corner of the slide

## Top-Level Schema

```json
{
  "meta": {
    "title": "Diagram Title",
    "subtitle": "Optional subtitle",
    "footer": "Optional footer text",
    "bgColor": "FFFFFF",
    "titleColor": "1E293B",
    "titleBgColor": "F8FAFC",
    "altText": "Accessibility alt text",
    "description": "Full description for companion .description.md"
  },
  "elements": [
    { "type": "group", ... },
    { "type": "shape", ... },
    { "type": "connector", ... },
    { "type": "text", ... },
    { "type": "divider", ... }
  ]
}
```

**Z-order:** Array order = draw order. First element is drawn first (behind everything). Put `group` backgrounds first, then `divider`s, then `shape`s, then `connector`s and `text` labels on top.

### Meta Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `title` | string | `"Diagram"` | Title shown in the title bar |
| `subtitle` | string | — | Subtitle below the title |
| `footer` | string | — | Small centered footer text |
| `bgColor` | hex string | `"FFFFFF"` | Slide background color (no `#` prefix) |
| `titleColor` | hex string | `"1E293B"` | Title text color |
| `titleBgColor` | hex string | `"F8FAFC"` | Title bar background color |
| `altText` | string | — | Accessibility alt text |
| `description` | string | — | Full description for .description.md |
| `referenceImage` | string | — | Path to reference PNG; copied alongside output as `{name}.png` |

---

## Element Types

### `shape` — Rectangles, diamonds, ovals, cylinders, etc.

Renders as a PowerPoint shape with optional centered label text.

```json
{
  "type": "shape",
  "id": "api",
  "shapeType": "roundedRect",
  "x": 2.5, "y": 1.2, "w": 1.8, "h": 0.6,
  "label": "API Gateway",
  "fill": "4A90E2",
  "fillTransparency": 0,
  "lineColor": "2C5F8A",
  "lineWidth": 1,
  "lineDash": "solid",
  "fontSize": 10,
  "fontColor": "FFFFFF",
  "fontBold": false,
  "fontItalic": false,
  "fontUnderline": false,
  "fontFace": "Calibri",
  "fit": "shrink",
  "rectRadius": 0.1,
  "shadow": { "blur": 3, "offset": 3, "angle": 45, "color": "000000", "opacity": 0.35 }
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | string | — | Optional unique identifier for connector anchoring |
| `shapeType` | string | `"roundedRect"` | Shape type (see Shape Type Catalog below) |
| `x`, `y` | number | — | **Required.** Top-left position in inches |
| `w`, `h` | number | — | **Required.** Width and height in inches |
| `label` | string | — | Text displayed centered inside the shape |
| `fill` | hex string | `"FFFFFF"` | Fill color |
| `fillTransparency` | number | `0` | Fill transparency (0–100) |
| `lineColor` | hex string | `"333333"` | Border color |
| `lineWidth` | number | `1` | Border width in points |
| `lineDash` | string | `"solid"` | Border dash style (see Dash Types) |
| `fontSize` | number | `10` | Label font size in points |
| `fontColor` | hex string | `"333333"` | Label text color |
| `fontBold` | boolean | `false` | Label bold styling |
| `fontItalic` | boolean | `false` | Label italic styling |
| `fontUnderline` | boolean | `false` | Label underline styling |
| `fontFace` | string | `"Calibri"` | Font family name |
| `fit` | string | — | Set to `"shrink"` to auto-shrink text to fit the shape |
| `rectRadius` | number | — | Corner radius for rounded rectangles (inches) |
| `shadow` | object | — | Drop shadow (see Shadow Properties below) |

### `connector` — Lines/arrows between shapes or points

Connectors can reference shapes by `id` (recommended) or use absolute coordinates as a fallback.

**Shape-anchored connector** (preferred — endpoints auto-calculated from shape edges):

```json
{
  "type": "connector",
  "from": "api", "fromSide": "right",
  "to": "db", "toSide": "left",
  "lineColor": "333333",
  "lineWidth": 1.5,
  "endArrow": "triangle",
  "label": "SQL Queries"
}
```

**Absolute coordinate connector** (legacy — still fully supported):

```json
{
  "type": "connector",
  "x1": 4.3, "y1": 1.5, "x2": 5.5, "y2": 1.5,
  "lineColor": "333333",
  "lineWidth": 1.5,
  "endArrow": "triangle",
  "label": "REST API"
}
```

**Elbow (orthogonal) connector** — renders as a 3-segment L-shaped path:

```json
{
  "type": "connector",
  "from": "api", "fromSide": "bottom",
  "to": "cache", "toSide": "top",
  "route": "elbow",
  "endArrow": "triangle"
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `from` | string | — | Source element `id` for shape-anchored mode |
| `fromSide` | string | `"right"` | Which edge of the source shape: `"left"`, `"right"`, `"top"`, `"bottom"` |
| `to` | string | — | Target element `id` for shape-anchored mode |
| `toSide` | string | `"left"` | Which edge of the target shape: `"left"`, `"right"`, `"top"`, `"bottom"` |
| `x1`, `y1` | number | — | Start point in inches (used when `from` is not set) |
| `x2`, `y2` | number | — | End point in inches (used when `to` is not set) |
| `route` | string | `"straight"` | Routing mode: `"straight"` (direct line) or `"elbow"` (orthogonal L-path) |
| `lineColor` | hex string | `"333333"` | Line color |
| `lineWidth` | number | `1.5` | Line width in points |
| `lineDash` | string | `"solid"` | Line dash style |
| `startArrow` | string | `"none"` | Arrow at start point (see Arrow Types) |
| `endArrow` | string | `"triangle"` | Arrow at end point |
| `label` | string | — | Text label at the midpoint (straight) or bend point (elbow) |
| `labelFontSize` | number | `8` | Label font size |
| `labelColor` | hex string | `"666666"` | Label text color |
| `fontFace` | string | `"Calibri"` | Label font family |

**Anchor resolution:** When `from`/`to` reference element IDs, the build script auto-calculates edge midpoints:
- `"right"` → `(x + w, y + h/2)`
- `"left"` → `(x, y + h/2)`
- `"top"` → `(x + w/2, y)`
- `"bottom"` → `(x + w/2, y + h)`

**Elbow routing:** Renders 3 LINE segments. Horizontal-first if `|dx| ≥ |dy|`, vertical-first otherwise. The label is placed at the bend point.

**Fallback:** If `from`/`to` are not set or reference unknown IDs, the connector falls back to `x1,y1,x2,y2` absolute coordinates (full backward compatibility).

### `text` — Standalone text labels

For lane names, phase headers, annotations, and any text not inside a shape.

```json
{
  "type": "text",
  "id": "header1",
  "x": 0.2, "y": 0.8, "w": 1.5, "h": 0.5,
  "text": "SOC Analyst",
  "fontSize": 11,
  "fontColor": "1E293B",
  "fontBold": true,
  "fontItalic": false,
  "fontUnderline": false,
  "fontFace": "Calibri",
  "align": "left",
  "valign": "middle"
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | string | — | Optional unique identifier |
| `x`, `y` | number | — | **Required.** Top-left position in inches |
| `w`, `h` | number | — | **Required.** Width and height in inches |
| `text` | string | `""` | The text content |
| `fontSize` | number | `11` | Font size in points |
| `fontColor` | hex string | `"1E293B"` | Text color |
| `fontBold` | boolean | `false` | Bold styling |
| `fontItalic` | boolean | `false` | Italic styling |
| `fontUnderline` | boolean | `false` | Underline styling |
| `fontFace` | string | `"Calibri"` | Font family name |
| `fit` | string | — | Set to `"shrink"` to auto-shrink text to fit |
| `align` | string | `"left"` | Horizontal alignment: `"left"`, `"center"`, `"right"` |
| `valign` | string | `"middle"` | Vertical alignment: `"top"`, `"middle"`, `"bottom"` |

### `divider` — Separator lines

Horizontal or vertical lines to separate diagram sections (no arrowheads).

```json
{
  "type": "divider",
  "x1": 0, "y1": 2.0, "x2": 10, "y2": 2.0,
  "lineColor": "CCCCCC",
  "lineWidth": 1,
  "lineDash": "solid"
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `x1`, `y1` | number | — | **Required.** Start point |
| `x2`, `y2` | number | — | **Required.** End point |
| `lineColor` | hex string | `"CCCCCC"` | Line color |
| `lineWidth` | number | `1` | Line width in points |
| `lineDash` | string | `"solid"` | Line dash style |

### `group` — Visual grouping rectangles

Background rectangles that visually group other elements. Always place these first in the `elements` array so they render behind everything else.

```json
{
  "type": "group",
  "id": "vpc",
  "x": 1.5, "y": 0.8, "w": 8.0, "h": 1.5,
  "fill": "F0F4F8",
  "fillTransparency": 0,
  "lineColor": "CBD5E1",
  "lineWidth": 1,
  "lineDash": "solid",
  "label": "Cloud VPC",
  "labelFontSize": 9,
  "labelColor": "64748B",
  "labelPosition": "topLeft",
  "shadow": { "blur": 3, "offset": 3, "angle": 45, "color": "000000", "opacity": 0.35 }
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | string | — | Optional unique identifier |
| `x`, `y` | number | — | **Required.** Top-left position |
| `w`, `h` | number | — | **Required.** Width and height |
| `fill` | hex string | `"F0F4F8"` | Background fill color |
| `fillTransparency` | number | `0` | Fill transparency (0–100) |
| `lineColor` | hex string | `"CBD5E1"` | Border color |
| `lineWidth` | number | `1` | Border width |
| `lineDash` | string | `"solid"` | Border dash style |
| `label` | string | — | Group label text |
| `labelFontSize` | number | `9` | Label font size |
| `labelColor` | hex string | `"64748B"` | Label text color |
| `labelPosition` | string | `"topLeft"` | Label position: `"topLeft"`, `"topRight"`, `"bottomLeft"`, `"bottomRight"` |
| `fontFace` | string | `"Calibri"` | Label font family |
| `shadow` | object | — | Drop shadow (see Shadow Properties below) |

### `icon` — Rasterized react-icons images

Renders a react-icons icon as a rasterized PNG embedded in the slide. Requires `react`, `react-dom`, `react-icons`, and `sharp` to be installed globally. If dependencies are missing, icon elements are skipped gracefully.

```json
{
  "type": "icon",
  "name": "FaServer",
  "library": "fa",
  "x": 2.5, "y": 1.5, "w": 0.4, "h": 0.4,
  "color": "4A90E2"
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | — | **Required.** react-icons export name (e.g. `FaServer`, `SiAmazonaws`) |
| `library` | string | `"fa"` | Icon pack: `fa` (Font Awesome), `md` (Material Design), `hi` (Heroicons), `bs` (Bootstrap), `si` (Simple Icons), `tb` (Tabler) |
| `x`, `y` | number | — | **Required.** Top-left position in inches |
| `w`, `h` | number | — | **Required.** Display size in inches |
| `color` | hex string | `"333333"` | Icon fill color (no `#` prefix) |

See `references/icon-catalog.md` for a curated list of icons organized by category.

**Placement tips:**
- Place icons slightly above or to the left of their associated shape label
- Typical icon size: 0.3"–0.5" for inline icons, 0.5"–0.8" for standalone icons
- Icons render as images, not native shapes — they cannot be recolored in PowerPoint

---

## Shadow Properties

Optional drop shadow for `shape` and `group` elements. Only outer shadows are supported (inner shadows cause pptxgenjs file corruption).

```json
{
  "shadow": {
    "blur": 3,
    "offset": 3,
    "angle": 45,
    "color": "000000",
    "opacity": 0.35
  }
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `blur` | number | `3` | Shadow blur radius in points |
| `offset` | number | `3` | Shadow offset distance in points |
| `angle` | number | `45` | Shadow angle in degrees (0–360) |
| `color` | hex string | `"000000"` | Shadow color |
| `opacity` | number | `0.35` | Shadow opacity (0–1) |

---

## Shape Type Catalog

| `shapeType` value | PowerPoint shape | Use for |
|---|---|---|
| `rect` | Rectangle | Generic boxes, process steps |
| `roundedRect` | Rounded Rectangle | Services, activities, most boxes |
| `oval` | Oval | Actors, data flow processes |
| `diamond` | Diamond | Decision points, gates |
| `cylinder` | Can/Cylinder | Databases, data stores |
| `cloud` | Cloud | External/cloud services |
| `triangle` | Isosceles Triangle | Warnings, hierarchy roots |
| `hexagon` | Hexagon | Process nodes, hub elements |
| `parallelogram` | Parallelogram | Data/IO elements |
| `trapezoid` | Trapezoid | Funnel stages, transformation steps |
| `pentagon` | Pentagon | Milestone markers, process phases |
| `octagon` | Octagon | Stop/alert indicators |
| `cube` | Cube | 3D storage, infrastructure blocks |
| `gear6` | 6-tooth Gear | Settings, configuration |
| `gear9` | 9-tooth Gear | Complex processing, engines |
| `star5` | 5-pointed Star | Highlights, ratings, key items |
| `rightArrow` | Right Arrow | Direction indicators, next steps |
| `leftArrow` | Left Arrow | Back/return indicators |
| `upArrow` | Up Arrow | Upload, improvement |
| `downArrow` | Down Arrow | Download, degradation |
| `leftRightArrow` | Left-Right Arrow | Bidirectional flow |
| `flowProcess` | Flowchart Process | Flowchart process steps |
| `flowDecision` | Flowchart Decision | Flowchart decision nodes |
| `flowTerminator` | Flowchart Terminator | Flowchart start/end |
| `flowDocument` | Flowchart Document | Document shapes |
| `flowData` | Flowchart Data | Data step shapes |
| `flowAlternateProcess` | Flowchart Alternate Process | Alternative process steps |
| `flowPredefinedProcess` | Flowchart Predefined Process | Subroutine/predefined process |
| `flowManualInput` | Flowchart Manual Input | Manual data entry steps |
| `flowPreparation` | Flowchart Preparation | Setup/initialization steps |
| `flowMultidocument` | Flowchart Multidocument | Multiple document outputs |

## Arrow Types

For `startArrow` and `endArrow` on connectors:

| Value | Description |
|-------|-------------|
| `"none"` | No arrowhead |
| `"arrow"` | Simple arrow |
| `"triangle"` | Filled triangle (most common) |
| `"stealth"` | Stealth/notched arrow |
| `"diamond"` | Diamond arrowhead |
| `"oval"` | Oval/circle arrowhead |

## Dash Types

For `lineDash` on any element with a border or line:

| Value | Description |
|-------|-------------|
| `"solid"` | Solid line (default) |
| `"dash"` | Dashed line |
| `"lgDash"` | Long dashes |
| `"dashDot"` | Dash-dot pattern |
| `"lgDashDot"` | Long dash-dot |
| `"sysDot"` | Dotted line |

---

## Worked Examples

### Example 1: Simple Three-Tier Architecture

Three boxes connected by arrows: Frontend → API → Database. Uses element IDs with shape-anchored connectors and shadows.

```json
{
  "meta": {
    "title": "Three-Tier Architecture",
    "altText": "Three-tier architecture with frontend, API server, and database connected by arrows."
  },
  "elements": [
    {
      "type": "shape", "id": "frontend", "shapeType": "roundedRect",
      "x": 1.0, "y": 2.0, "w": 2.0, "h": 0.8,
      "label": "React Frontend", "fill": "4A90E2", "fontColor": "FFFFFF",
      "lineColor": "2C5F8A", "rectRadius": 0.1,
      "shadow": { "blur": 3, "offset": 2, "angle": 45, "opacity": 0.3 }
    },
    {
      "type": "shape", "id": "api", "shapeType": "roundedRect",
      "x": 4.0, "y": 2.0, "w": 2.0, "h": 0.8,
      "label": "Node.js API", "fill": "4A90E2", "fontColor": "FFFFFF",
      "lineColor": "2C5F8A", "rectRadius": 0.1,
      "shadow": { "blur": 3, "offset": 2, "angle": 45, "opacity": 0.3 }
    },
    {
      "type": "shape", "id": "db", "shapeType": "cylinder",
      "x": 7.0, "y": 1.8, "w": 2.0, "h": 1.2,
      "label": "PostgreSQL", "fill": "34D399", "fontColor": "FFFFFF",
      "lineColor": "059669",
      "shadow": { "blur": 3, "offset": 2, "angle": 45, "opacity": 0.3 }
    },
    {
      "type": "connector",
      "from": "frontend", "fromSide": "right",
      "to": "api", "toSide": "left",
      "label": "REST", "endArrow": "triangle"
    },
    {
      "type": "connector",
      "from": "api", "fromSide": "right",
      "to": "db", "toSide": "left",
      "label": "SQL", "endArrow": "triangle"
    }
  ]
}
```

### Example 2: Swim Lane CONOPS

Actors in horizontal lanes with activities across phases.

```json
{
  "meta": {
    "title": "Incident Response CONOPS",
    "subtitle": "Swim Lane Operational View",
    "altText": "Swim lane diagram showing incident response across four actors and three phases."
  },
  "elements": [
    { "type": "group", "x": 1.8, "y": 0.85, "w": 8.0, "h": 1.2, "fill": "EFF6FF", "lineColor": "BFDBFE", "label": "Field Team", "labelPosition": "topLeft" },
    { "type": "group", "x": 1.8, "y": 2.15, "w": 8.0, "h": 1.2, "fill": "F0FDF4", "lineColor": "BBF7D0", "label": "SOC Analyst", "labelPosition": "topLeft" },
    { "type": "group", "x": 1.8, "y": 3.45, "w": 8.0, "h": 1.2, "fill": "FFF7ED", "lineColor": "FED7AA", "label": "Incident Commander", "labelPosition": "topLeft" },

    { "type": "text", "x": 3.0, "y": 0.85, "w": 2.0, "h": 0.3, "text": "Detection", "fontSize": 9, "fontBold": true, "fontColor": "64748B", "align": "center" },
    { "type": "text", "x": 5.5, "y": 0.85, "w": 2.0, "h": 0.3, "text": "Triage", "fontSize": 9, "fontBold": true, "fontColor": "64748B", "align": "center" },
    { "type": "text", "x": 7.8, "y": 0.85, "w": 2.0, "h": 0.3, "text": "Containment", "fontSize": 9, "fontBold": true, "fontColor": "64748B", "align": "center" },

    { "type": "divider", "x1": 4.9, "y1": 0.85, "x2": 4.9, "y2": 4.65, "lineColor": "E2E8F0", "lineDash": "dash" },
    { "type": "divider", "x1": 7.4, "y1": 0.85, "x2": 7.4, "y2": 4.65, "lineColor": "E2E8F0", "lineDash": "dash" },

    { "type": "shape", "shapeType": "roundedRect", "x": 2.5, "y": 1.3, "w": 1.6, "h": 0.5, "label": "Detect Anomaly", "fill": "3B82F6", "fontColor": "FFFFFF", "fontSize": 8 },
    { "type": "shape", "shapeType": "roundedRect", "x": 5.5, "y": 2.5, "w": 1.6, "h": 0.5, "label": "Analyze & Triage", "fill": "22C55E", "fontColor": "FFFFFF", "fontSize": 8 },
    { "type": "shape", "shapeType": "diamond", "x": 7.8, "y": 3.55, "w": 1.0, "h": 0.8, "label": "Approve?", "fill": "F97316", "fontColor": "FFFFFF", "fontSize": 8 },
    { "type": "shape", "shapeType": "roundedRect", "x": 8.2, "y": 1.3, "w": 1.4, "h": 0.5, "label": "Execute", "fill": "3B82F6", "fontColor": "FFFFFF", "fontSize": 8 },

    { "type": "connector", "x1": 4.1, "y1": 1.55, "x2": 5.5, "y2": 2.75, "endArrow": "triangle", "lineColor": "94A3B8" },
    { "type": "connector", "x1": 7.1, "y1": 2.75, "x2": 7.8, "y2": 3.95, "endArrow": "triangle", "lineColor": "94A3B8" },
    { "type": "connector", "x1": 8.8, "y1": 3.95, "x2": 8.9, "y2": 1.8, "endArrow": "triangle", "lineColor": "94A3B8", "label": "Yes" }
  ]
}
```

### Example 3: Flowchart with Decisions

```json
{
  "meta": {
    "title": "User Login Flow",
    "altText": "Flowchart showing user login with credential validation and MFA check."
  },
  "elements": [
    {
      "type": "shape", "shapeType": "flowTerminator",
      "x": 4.0, "y": 1.0, "w": 2.0, "h": 0.6,
      "label": "Start", "fill": "10B981", "fontColor": "FFFFFF"
    },
    {
      "type": "shape", "shapeType": "roundedRect",
      "x": 4.0, "y": 2.0, "w": 2.0, "h": 0.6,
      "label": "Enter Credentials", "fill": "3B82F6", "fontColor": "FFFFFF"
    },
    {
      "type": "shape", "shapeType": "diamond",
      "x": 4.0, "y": 3.0, "w": 2.0, "h": 1.0,
      "label": "Valid?", "fill": "F59E0B", "fontColor": "FFFFFF"
    },
    {
      "type": "shape", "shapeType": "roundedRect",
      "x": 7.0, "y": 3.2, "w": 2.0, "h": 0.6,
      "label": "Show Error", "fill": "EF4444", "fontColor": "FFFFFF"
    },
    {
      "type": "shape", "shapeType": "flowTerminator",
      "x": 4.0, "y": 4.5, "w": 2.0, "h": 0.6,
      "label": "Dashboard", "fill": "10B981", "fontColor": "FFFFFF"
    },
    { "type": "connector", "x1": 5.0, "y1": 1.6, "x2": 5.0, "y2": 2.0, "endArrow": "triangle" },
    { "type": "connector", "x1": 5.0, "y1": 2.6, "x2": 5.0, "y2": 3.0, "endArrow": "triangle" },
    { "type": "connector", "x1": 6.0, "y1": 3.5, "x2": 7.0, "y2": 3.5, "endArrow": "triangle", "label": "No", "labelColor": "EF4444" },
    { "type": "connector", "x1": 5.0, "y1": 4.0, "x2": 5.0, "y2": 4.5, "endArrow": "triangle", "label": "Yes", "labelColor": "10B981" },
    { "type": "connector", "x1": 8.0, "y1": 3.2, "x2": 8.0, "y2": 2.3, "endArrow": "triangle", "lineDash": "dash" },
    { "type": "connector", "x1": 8.0, "y1": 2.3, "x2": 6.0, "y2": 2.3, "endArrow": "triangle", "lineDash": "dash", "label": "Retry" }
  ]
}
```

---

## Layout Tips

### Spacing Conventions
- **Gap between shapes:** 0.2" minimum, 0.5"–1.0" typical for readability
- **Padding inside groups:** 0.1"–0.2" from the group border to contained shapes
- **Shape heights:** 0.5"–0.8" for process boxes, 0.8"–1.2" for cylinders/diamonds
- **Shape widths:** 1.5"–2.5" for labeled boxes
- **Connector label clearance:** Labels at midpoint should not overlap shapes

### Alignment Guidance
- Align shape centers horizontally or vertically for clean rows/columns
- For horizontal flows: keep y-coordinates consistent, vary x
- For vertical flows: keep x-coordinates consistent, vary y
- Center the diagram in the usable area (x: 0.5–9.5, y: 0.85–5.35)

### Color Palettes

**Blue/gray (professional, default):**
- Primary: `4A90E2` (shapes), `2C5F8A` (borders)
- Secondary: `34D399` (databases/success), `059669` (borders)
- Text on dark: `FFFFFF`, Text on light: `1E293B`
- Groups: `F0F4F8` fill, `CBD5E1` border

**Warm (decisions, warnings):**
- Process: `3B82F6`, Decision: `F59E0B`, Error: `EF4444`, Success: `10B981`

**CONOPS (operational):**
- Human activities: `3B82F6` (blue)
- Automated steps: `22C55E` (green)
- Decision points: `F97316` (orange)
- Lane backgrounds: `EFF6FF`, `F0FDF4`, `FFF7ED`, `FDF2F8`

### Connector Math Reference

**Preferred: Shape-anchored connectors** — assign `id` to shapes, then use `from`/`to`:
```json
{ "from": "shapeA", "fromSide": "right", "to": "shapeB", "toSide": "left" }
```
The build script auto-calculates edge midpoints. No manual coordinate math needed.

**Elbow routing** — add `"route": "elbow"` for orthogonal L-shaped paths:
```json
{ "from": "shapeA", "fromSide": "bottom", "to": "shapeB", "toSide": "top", "route": "elbow" }
```

**Fallback: Absolute coordinates** (still supported for backward compatibility):

Horizontal arrow (left to right): `x1 < x2`, same `y1 = y2`
```json
{ "x1": 3.0, "y1": 2.0, "x2": 5.0, "y2": 2.0 }
```

Vertical arrow (top to bottom): same `x1 = x2`, `y1 < y2`
```json
{ "x1": 5.0, "y1": 1.5, "x2": 5.0, "y2": 3.0 }
```

Diagonal arrow (any direction): different x and y values
```json
{ "x1": 2.0, "y1": 1.0, "x2": 5.0, "y2": 3.0 }
```

Right-to-left arrow: `x1 > x2` (flip handled automatically)
```json
{ "x1": 7.0, "y1": 2.0, "x2": 4.0, "y2": 2.0 }
```
