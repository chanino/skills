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
| `titleFontSize` | number | `20` | Title text font size |
| `titleFontFace` | string | `"Calibri"` | Title font family |
| `titleCharSpacing` | number | `1.5` | Title character spacing in points |
| `subtitleFontSize` | number | `12` | Subtitle font size |
| `subtitleColor` | hex string | — | Subtitle text color (defaults to `titleColor`) |
| `subtitleCharSpacing` | number | — | Subtitle character spacing in points |

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
| `fit` | string | `"shrink"` | Text fit mode — default auto-shrinks text to fit shape |
| `wrap` | boolean | — | Enable/disable text wrapping |
| `rotate` | number | — | Shape rotation in degrees (-360 to 360) |
| `rectRadius` | number | — | Corner radius for rounded rectangles (inches) |
| `shadow` | object | — | Drop shadow (see Shadow Properties below) |
| `charSpacing` | number | — | Character spacing in points (1-2 for elegance) |
| `lineSpacing` | number | — | Line spacing in points |
| `lineSpacingMultiple` | number | — | Line spacing multiplier (e.g. 1.2) |
| `paraSpaceAfter` | number | — | Space after paragraph in points |
| `paraSpaceBefore` | number | — | Space before paragraph in points |
| `glow` | object | — | Text glow effect (see Text Glow Properties below) |
| `textOutline` | object | — | Text outline/stroke (see Text Outline Properties below) |
| `align` | string | `"center"` | Horizontal text alignment: `"left"`, `"center"`, `"right"` |
| `valign` | string | `"middle"` | Vertical text alignment: `"top"`, `"middle"`, `"bottom"` |
| `margin` | array | `[5,8,5,8]` | Text margin [top, right, bottom, left] in points |
| `textRuns` | array | — | Rich text runs for mixed formatting (see Rich Text below) |

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
| `route` | string | `"elbow"` | Routing mode: `"elbow"` (orthogonal L-path, default) or `"straight"` (direct line — use only when shapes share exact same X or Y) |
| `lineColor` | hex string | `"333333"` | Line color |
| `lineWidth` | number | `2.0` | Line width in points |
| `lineDash` | string | `"solid"` | Line dash style |
| `startArrow` | string | `"none"` | Arrow at start point (see Arrow Types) |
| `endArrow` | string | `"triangle"` | Arrow at end point |
| `label` | string | — | Text label at the midpoint (straight) or bend point (elbow) |
| `labelFontSize` | number | `9` | Label font size |
| `labelColor` | hex string | `"666666"` | Label text color |
| `fontFace` | string | `"Calibri"` | Label font family |
| `labelItalic` | boolean | `false` | Label italic styling |
| `labelCharSpacing` | number | — | Label character spacing in points |
| `labelOffset` | number | `0` | Shift label along connector path in inches (positive = toward `to`) |
| `labelW` | number | auto | Override auto-calculated label width in inches |

**Anchor resolution:** When `from`/`to` reference element IDs, the build script auto-calculates edge midpoints:
- `"right"` → `(x + w, y + h/2)`
- `"left"` → `(x, y + h/2)`
- `"top"` → `(x + w/2, y)`
- `"bottom"` → `(x + w/2, y + h)`

**Elbow routing (default):** Renders 3 LINE segments with chamfered corners (0.06" radius). Horizontal-first if `|dx| ≥ |dy|`, vertical-first otherwise. The label is placed at the bend point. Chamfers gracefully degrade to sharp corners if segments are shorter than 2× the radius.

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
| `fit` | string | `"shrink"` | Text fit mode — default auto-shrinks text to fit |
| `wrap` | boolean | — | Enable/disable text wrapping |
| `rotate` | number | — | Element rotation in degrees (-360 to 360) |
| `align` | string | `"left"` | Horizontal alignment: `"left"`, `"center"`, `"right"` |
| `valign` | string | `"middle"` | Vertical alignment: `"top"`, `"middle"`, `"bottom"` |
| `charSpacing` | number | — | Character spacing in points |
| `lineSpacing` | number | — | Line spacing in points |
| `lineSpacingMultiple` | number | — | Line spacing multiplier |
| `paraSpaceAfter` | number | — | Space after paragraph in points |
| `paraSpaceBefore` | number | — | Space before paragraph in points |
| `margin` | array | — | Text margin [top, right, bottom, left] in points |
| `glow` | object | — | Text glow effect (see Text Glow Properties) |
| `textOutline` | object | — | Text outline/stroke (see Text Outline Properties) |
| `textRuns` | array | — | Rich text runs for mixed formatting (see Rich Text below) |

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
| `borderless` | boolean | `false` | Remove border entirely (consulting pattern where shadow defines edges) |
| `rectRadius` | number | — | Corner radius for rounded group backgrounds (inches) |
| `labelBold` | boolean | `false` | Bold styling for group label |
| `labelCharSpacing` | number | — | Character spacing for group label in points |
| `labelW` | number | auto | Override auto-calculated label width in inches |

### `icon` — Pre-generated or custom PNG icons

Embeds a PNG icon image in the slide. Use the pre-generated library in `assets/icons/` (25 icons covering common technical diagram concepts) or generate custom icons via `scripts/generate_icon.py`.

**Path-based icons** (recommended):
```json
{ "type": "icon", "path": "assets/icons/server_rack.png", "x": 2.5, "y": 1.5, "w": 0.4, "h": 0.4 }
```

Paths starting with `assets/icons/` are resolved relative to the skill root automatically. Absolute paths (e.g. `/tmp/icons/custom.png`) also work.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `path` | string | — | **Recommended.** File path to a PNG image. Resolved relative to skill root or as absolute path. |
| `x`, `y` | number | — | **Required.** Top-left position in inches |
| `w`, `h` | number | — | **Required.** Display size in inches |
| `name` | string | — | **Deprecated fallback.** react-icons export name (e.g. `FaServer`). Requires react, react-dom, react-icons, sharp installed globally. |
| `library` | string | `"fa"` | **Deprecated fallback.** Icon pack for react-icons: `fa`, `md`, `hi`, `bs`, `si`, `tb` |
| `color` | hex string | `"333333"` | Icon fill color for react-icons only (ignored for path-based icons) |

See `references/icon-catalog.md` for the full catalog of pre-generated icons organized by category.

**Placement tips:**
- Place icons slightly above or to the left of their associated shape label
- Typical icon size: 0.3"--0.5" for inline icons, 0.5"--0.8" for standalone icons
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

## Text Glow Properties

Optional glow effect for text in `shape` and `text` elements. Useful for improving readability on medium-toned fills.

```json
{
  "glow": {
    "color": "FFFFFF",
    "size": 2,
    "opacity": 0.35
  }
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `color` | hex string | `"000000"` | Glow color |
| `size` | number | `2` | Glow size in points |
| `opacity` | number | `0.35` | Glow opacity (0–1) |

**When to use:** White glow on dark fills improves text readability. Dark glow on light fills adds subtle text emphasis. Note: glow may not render in LibreOffice headless PNG export but appears in PowerPoint.

---

## Text Outline Properties

Optional text stroke/outline for `shape` and `text` elements. Useful for white-on-dark contrast on very dark fills.

```json
{
  "textOutline": {
    "color": "000000",
    "size": 0.5
  }
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `color` | hex string | `"000000"` | Outline color |
| `size` | number | `0.5` | Outline width in points |

**When to use:** Add a thin dark outline to white text on very dark fills for maximum contrast. Note: outline may not render in LibreOffice headless PNG export but appears in PowerPoint.

---

## Rich Text (textRuns)

Use `textRuns` to render mixed formatting within a single shape or text element — for example, a bold title line followed by a regular subtitle line.

```json
{
  "type": "shape",
  "shapeType": "roundedRect",
  "x": 1.0, "y": 1.0, "w": 2.5, "h": 1.0,
  "fill": "2E5090",
  "fontColor": "FFFFFF",
  "textRuns": [
    { "text": "API Gateway", "bold": true, "fontSize": 11, "charSpacing": 1 },
    { "text": "v2.1 — Production", "fontSize": 9, "italic": true, "breakLine": true }
  ]
}
```

Each run in the `textRuns` array supports:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `text` | string | `""` | The text content for this run |
| `fontSize` | number | parent `fontSize` | Font size in points |
| `fontFace` | string | parent `fontFace` | Font family |
| `fontColor` | hex string | parent `fontColor` | Text color |
| `bold` | boolean | `false` | Bold styling |
| `italic` | boolean | `false` | Italic styling |
| `breakLine` | boolean | `false` | Insert line break before this run |
| `charSpacing` | number | — | Character spacing for this run |

When `textRuns` is set, the `label` / `text` property is ignored.

---

## Component Stack Pattern

The "component stack" is the standard pattern for architecture, cloud, and network diagrams. It makes each component instantly scannable — users recognize the icon before reading text.

### Variant 1: Icon Above Shape (most common)

Place icon centered above the shape, shape below, description text below the shape.

```json
[
  {
    "type": "icon", "path": "assets/icons/lambda_function.png",
    "x": 5.725, "y": 1.5, "w": 0.35, "h": 0.35
  },
  {
    "type": "shape", "id": "lambda", "shapeType": "roundedRect",
    "x": 5.0, "y": 1.9, "w": 1.8, "h": 0.6,
    "fill": "2E5090", "fontColor": "FFFFFF",
    "lineWidth": 0, "rectRadius": 0.1,
    "label": "Products Lambda", "fontSize": 10, "fontBold": true,
    "charSpacing": 1, "margin": [8, 10, 8, 10],
    "shadow": { "blur": 5, "offset": 4, "angle": 45, "opacity": 0.4 }
  },
  {
    "type": "text",
    "x": 5.0, "y": 2.55, "w": 1.8, "h": 0.4,
    "text": "Product Catalog\nLogic & Management",
    "fontSize": 9, "fontItalic": true, "fontColor": "64748B", "align": "center"
  }
]
```

**Spacing rules:**
- Icon center aligns with shape center: `icon.x = shape.x + (shape.w - icon.w) / 2`
- 0.05" gap between icon bottom and shape top: `shape.y = icon.y + icon.h + 0.05`
- 0.05" gap between shape bottom and description: `text.y = shape.y + shape.h + 0.05`

### Variant 2: Icon Inside Shape (compact layouts)

Place icon at left of shape, label at right using textRuns. Good when vertical space is limited.

```json
{
  "type": "shape", "id": "db", "shapeType": "roundedRect",
  "x": 3.0, "y": 2.0, "w": 2.2, "h": 0.7,
  "fill": "2E5090", "fontColor": "FFFFFF",
  "lineWidth": 0, "rectRadius": 0.1,
  "margin": [8, 10, 8, 10],
  "textRuns": [
    { "text": "  DynamoDB", "bold": true, "fontSize": 10, "charSpacing": 1 },
    { "text": "  NoSQL Database", "fontSize": 9, "italic": true, "breakLine": true }
  ],
  "shadow": { "blur": 5, "offset": 4, "angle": 45, "opacity": 0.4 }
}
```

Note: For the "icon inside" variant, place a separate `icon` element overlapping the left area of the shape. The icon renders on top of the shape.

### Variant 3: Shape with Description Only (no icon)

When no clear icon mapping exists, still add the description text below.

```json
[
  {
    "type": "shape", "id": "gateway", "shapeType": "roundedRect",
    "x": 3.0, "y": 2.0, "w": 2.0, "h": 0.6,
    "fill": "334155", "fontColor": "FFFFFF",
    "lineWidth": 0, "rectRadius": 0.1,
    "label": "API Gateway", "fontSize": 10, "fontBold": true,
    "charSpacing": 1, "margin": [8, 10, 8, 10],
    "shadow": { "blur": 5, "offset": 4, "angle": 45, "opacity": 0.4 }
  },
  {
    "type": "text",
    "x": 3.0, "y": 2.65, "w": 2.0, "h": 0.35,
    "text": "Managed API Endpoint\n& Traffic Management",
    "fontSize": 9, "fontItalic": true, "fontColor": "64748B", "align": "center"
  }
]
```

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

### Example 1: Three-Tier Architecture with Component Stacks

Three components with icons above, description text below, connected by labeled arrows. This is the **standard pattern for architecture diagrams** — icon + shape + description makes each component instantly recognizable.

```json
{
  "meta": {
    "title": "Three-Tier Architecture",
    "altText": "Three-tier architecture with frontend, API server, and database, each with icons and descriptions.",
    "titleCharSpacing": 1.5
  },
  "elements": [
    {
      "type": "icon", "path": "assets/icons/desktop_computer.png",
      "x": 1.825, "y": 1.4, "w": 0.35, "h": 0.35
    },
    {
      "type": "shape", "id": "frontend", "shapeType": "roundedRect",
      "x": 1.0, "y": 1.8, "w": 2.0, "h": 0.7,
      "fill": "2E5090", "fontColor": "FFFFFF",
      "lineWidth": 0, "rectRadius": 0.1,
      "charSpacing": 1, "fontBold": true, "margin": [8, 10, 8, 10],
      "textRuns": [
        { "text": "React Frontend", "bold": true, "fontSize": 10, "charSpacing": 1 },
        { "text": "Client Application", "fontSize": 9, "italic": true, "breakLine": true }
      ],
      "shadow": { "blur": 5, "offset": 4, "angle": 45, "opacity": 0.4 }
    },
    {
      "type": "text",
      "x": 1.0, "y": 2.55, "w": 2.0, "h": 0.4,
      "text": "Single-Page App\nReact 18 + TypeScript",
      "fontSize": 9, "fontItalic": true, "fontColor": "64748B", "align": "center"
    },

    {
      "type": "icon", "path": "assets/icons/server_rack.png",
      "x": 4.825, "y": 1.4, "w": 0.35, "h": 0.35
    },
    {
      "type": "shape", "id": "api", "shapeType": "roundedRect",
      "x": 4.0, "y": 1.8, "w": 2.0, "h": 0.7,
      "fill": "2E5090", "fontColor": "FFFFFF",
      "lineWidth": 0, "rectRadius": 0.1,
      "charSpacing": 1, "fontBold": true, "margin": [8, 10, 8, 10],
      "textRuns": [
        { "text": "Node.js API", "bold": true, "fontSize": 10, "charSpacing": 1 },
        { "text": "REST Service", "fontSize": 9, "italic": true, "breakLine": true }
      ],
      "shadow": { "blur": 5, "offset": 4, "angle": 45, "opacity": 0.4 }
    },
    {
      "type": "text",
      "x": 4.0, "y": 2.55, "w": 2.0, "h": 0.4,
      "text": "Express REST API\nBusiness Logic Layer",
      "fontSize": 9, "fontItalic": true, "fontColor": "64748B", "align": "center"
    },

    {
      "type": "icon", "path": "assets/icons/database_cylinder.png",
      "x": 7.825, "y": 1.4, "w": 0.35, "h": 0.35
    },
    {
      "type": "shape", "id": "db", "shapeType": "cylinder",
      "x": 7.0, "y": 1.8, "w": 2.0, "h": 1.2,
      "label": "PostgreSQL", "fill": "5B8DB8", "fontColor": "FFFFFF",
      "lineWidth": 0, "fontSize": 10,
      "shadow": { "blur": 3, "offset": 2, "angle": 45, "opacity": 0.25 }
    },
    {
      "type": "text",
      "x": 7.0, "y": 3.05, "w": 2.0, "h": 0.4,
      "text": "Relational Database\nPostgreSQL 15",
      "fontSize": 9, "fontItalic": true, "fontColor": "64748B", "align": "center"
    },

    {
      "type": "connector",
      "from": "frontend", "fromSide": "right",
      "to": "api", "toSide": "left",
      "label": "REST / HTTPS", "endArrow": "triangle",
      "lineColor": "6B7280"
    },
    {
      "type": "connector",
      "from": "api", "fromSide": "right",
      "to": "db", "toSide": "left",
      "label": "SQL Queries", "endArrow": "triangle",
      "lineColor": "6B7280"
    }
  ]
}
```

### Example 2: Swim Lane CONOPS

Actors in horizontal lanes with activities across phases. **Key pattern:** Lane names are separate `text` elements positioned LEFT of the groups (not `group.label`). Phase headers are independent `text` elements ABOVE the diagram area.

```json
{
  "meta": {
    "title": "Incident Response CONOPS",
    "subtitle": "Swim Lane Operational View",
    "altText": "Swim lane diagram showing incident response across three actors and three phases.",
    "titleCharSpacing": 1.5
  },
  "elements": [
    { "type": "group", "x": 1.8, "y": 1.15, "w": 8.0, "h": 1.2, "fill": "F1F5F9", "borderless": true, "shadow": { "blur": 6, "offset": 4, "opacity": 0.12 } },
    { "type": "group", "x": 1.8, "y": 2.45, "w": 8.0, "h": 1.2, "fill": "F1F5F9", "borderless": true, "shadow": { "blur": 6, "offset": 4, "opacity": 0.12 } },
    { "type": "group", "x": 1.8, "y": 3.75, "w": 8.0, "h": 1.2, "fill": "F1F5F9", "borderless": true, "shadow": { "blur": 6, "offset": 4, "opacity": 0.12 } },

    { "type": "text", "x": 0.1, "y": 1.15, "w": 1.6, "h": 1.2, "text": "Field Team", "fontSize": 10, "fontBold": true, "fontColor": "334155", "align": "right", "valign": "middle", "charSpacing": 1 },
    { "type": "text", "x": 0.1, "y": 2.45, "w": 1.6, "h": 1.2, "text": "SOC Analyst", "fontSize": 10, "fontBold": true, "fontColor": "334155", "align": "right", "valign": "middle", "charSpacing": 1 },
    { "type": "text", "x": 0.1, "y": 3.75, "w": 1.6, "h": 1.2, "text": "Incident Cmdr", "fontSize": 10, "fontBold": true, "fontColor": "334155", "align": "right", "valign": "middle", "charSpacing": 1 },

    { "type": "text", "x": 3.0, "y": 0.85, "w": 2.0, "h": 0.3, "text": "Detection", "fontSize": 9, "fontBold": true, "fontColor": "64748B", "align": "center", "charSpacing": 1 },
    { "type": "text", "x": 5.5, "y": 0.85, "w": 2.0, "h": 0.3, "text": "Triage", "fontSize": 9, "fontBold": true, "fontColor": "64748B", "align": "center", "charSpacing": 1 },
    { "type": "text", "x": 7.8, "y": 0.85, "w": 2.0, "h": 0.3, "text": "Containment", "fontSize": 9, "fontBold": true, "fontColor": "64748B", "align": "center", "charSpacing": 1 },

    { "type": "divider", "x1": 4.9, "y1": 0.85, "x2": 4.9, "y2": 4.95, "lineColor": "E2E8F0", "lineDash": "dash" },
    { "type": "divider", "x1": 7.4, "y1": 0.85, "x2": 7.4, "y2": 4.95, "lineColor": "E2E8F0", "lineDash": "dash" },

    { "type": "shape", "id": "detect", "shapeType": "roundedRect", "x": 2.5, "y": 1.5, "w": 1.8, "h": 0.5, "label": "Detect Anomaly", "fill": "334155", "fontColor": "FFFFFF", "fontSize": 9, "lineWidth": 0, "shadow": { "blur": 4, "offset": 3, "opacity": 0.35 } },
    { "type": "shape", "id": "triage", "shapeType": "roundedRect", "x": 5.5, "y": 2.8, "w": 1.8, "h": 0.5, "label": "Analyze & Triage", "fill": "64748B", "fontColor": "FFFFFF", "fontSize": 9, "lineWidth": 0, "shadow": { "blur": 2, "offset": 1, "opacity": 0.2 } },
    { "type": "shape", "id": "approve", "shapeType": "diamond", "x": 7.6, "y": 3.85, "w": 1.8, "h": 1.0, "label": "Approve?", "fill": "0EA5E9", "fontColor": "FFFFFF", "fontSize": 9, "lineWidth": 0, "shadow": { "blur": 4, "offset": 3, "opacity": 0.35 } },
    { "type": "shape", "id": "execute", "shapeType": "roundedRect", "x": 8.0, "y": 1.5, "w": 1.6, "h": 0.5, "label": "Execute", "fill": "334155", "fontColor": "FFFFFF", "fontSize": 9, "lineWidth": 0, "shadow": { "blur": 4, "offset": 3, "opacity": 0.35 } },

    { "type": "connector", "from": "detect", "fromSide": "right", "to": "triage", "toSide": "left", "endArrow": "triangle", "lineColor": "94A3B8", "route": "elbow" },
    { "type": "connector", "from": "triage", "fromSide": "right", "to": "approve", "toSide": "top", "endArrow": "triangle", "lineColor": "94A3B8", "route": "elbow" },
    { "type": "connector", "from": "approve", "fromSide": "right", "to": "execute", "toSide": "bottom", "endArrow": "triangle", "lineColor": "94A3B8", "label": "Yes", "route": "elbow" }
  ]
}
```

### Example 3: Flowchart with Decisions

```json
{
  "meta": {
    "title": "User Login Flow",
    "altText": "Flowchart showing user login with credential validation and MFA check.",
    "titleCharSpacing": 1.5
  },
  "elements": [
    {
      "type": "shape", "shapeType": "flowTerminator",
      "x": 4.0, "y": 1.0, "w": 2.0, "h": 0.6,
      "label": "Start", "fill": "2E5090", "fontColor": "FFFFFF",
      "lineWidth": 0, "shadow": { "blur": 4, "offset": 3, "opacity": 0.35 }
    },
    {
      "type": "shape", "shapeType": "roundedRect",
      "x": 4.0, "y": 2.0, "w": 2.0, "h": 0.6,
      "label": "Enter Credentials", "fill": "5B8DB8", "fontColor": "FFFFFF",
      "lineWidth": 0, "shadow": { "blur": 2, "offset": 1, "opacity": 0.2 }
    },
    {
      "type": "shape", "shapeType": "diamond",
      "x": 4.0, "y": 3.0, "w": 2.0, "h": 1.0,
      "label": "Valid?", "fill": "C4A35A", "fontColor": "FFFFFF",
      "lineWidth": 0, "shadow": { "blur": 4, "offset": 3, "opacity": 0.35 }
    },
    {
      "type": "shape", "shapeType": "roundedRect",
      "x": 7.0, "y": 3.2, "w": 2.0, "h": 0.6,
      "label": "Show Error", "fill": "7C3A2D", "fontColor": "FFFFFF",
      "lineWidth": 0, "shadow": { "blur": 2, "offset": 1, "opacity": 0.2 }
    },
    {
      "type": "shape", "shapeType": "flowTerminator",
      "x": 4.0, "y": 4.5, "w": 2.0, "h": 0.6,
      "label": "Dashboard", "fill": "2E5090", "fontColor": "FFFFFF",
      "lineWidth": 0, "shadow": { "blur": 4, "offset": 3, "opacity": 0.35 }
    },
    { "type": "connector", "x1": 5.0, "y1": 1.6, "x2": 5.0, "y2": 2.0, "endArrow": "triangle", "lineColor": "6B7280" },
    { "type": "connector", "x1": 5.0, "y1": 2.6, "x2": 5.0, "y2": 3.0, "endArrow": "triangle", "lineColor": "6B7280" },
    { "type": "connector", "x1": 6.0, "y1": 3.5, "x2": 7.0, "y2": 3.5, "endArrow": "triangle", "label": "No", "labelColor": "7C3A2D", "lineColor": "6B7280" },
    { "type": "connector", "x1": 5.0, "y1": 4.0, "x2": 5.0, "y2": 4.5, "endArrow": "triangle", "label": "Yes", "labelColor": "2E5090", "lineColor": "6B7280" },
    { "type": "connector", "x1": 8.0, "y1": 3.2, "x2": 8.0, "y2": 2.3, "endArrow": "triangle", "lineDash": "dash", "lineColor": "6B7280" },
    { "type": "connector", "x1": 8.0, "y1": 2.3, "x2": 6.0, "y2": 2.3, "endArrow": "triangle", "lineDash": "dash", "label": "Retry", "lineColor": "6B7280" }
  ]
}
```

---

## Layout Tips

### Spacing Scale

Use a consistent modular scale for all spacing decisions:

| Token | Value | Use |
|-------|-------|-----|
| `xs`  | 0.1"  | Icon-to-shape gap, tight internal padding |
| `sm`  | 0.2"  | Minimum inter-shape gap, group internal padding |
| `md`  | 0.4"  | Standard inter-shape gap (preferred) |
| `lg`  | 0.6"  | Column separation, major section breaks |
| `xl`  | 0.8"  | Canvas margins, swim lane gutter width |

**Rule:** Every gap, padding, and margin should map to a scale token. Ad-hoc values like 0.35" or 0.55" break visual rhythm.

**Padding ≤ margin rule:** Internal padding within a shape or group must never exceed the gap between shapes. If group padding is `sm` (0.2"), inter-shape gaps should be `md` (0.4") or larger. Inverting this breaks Gestalt proximity — contained elements would appear more separated than independent ones.

### Alignment Guidance
- Align shape centers horizontally or vertically for clean rows/columns
- For horizontal flows: keep y-coordinates consistent, vary x
- For vertical flows: keep x-coordinates consistent, vary y
- Center the diagram in the usable area (x: 0.5–9.5, y: 0.85–5.35)

### Composition & Focal Point

- **Identify the primary flow** (the main left→right or top→bottom path) and align it on the horizontal or vertical center of the diagram area. Secondary paths branch off from it.
- **Entry point prominence:** The first shape in the flow (user, client, trigger) should be the largest or most visually distinct element — readers scan left-to-right, top-to-bottom.
- **Gestalt proximity:** Shapes that work together should be closer to each other than to unrelated shapes. Use `md` (0.4") gaps within a functional group and `lg` (0.6") between groups.
- **Whitespace is structural:** Empty space between groups communicates boundaries as effectively as borders. Don't fill every available inch.
- **Whitespace budget:** Aim for 15–20% of the diagram area as empty space. If every inch is filled, the diagram feels cramped and the eye has nowhere to rest. Whitespace between groups is as informative as the shapes themselves.

### Consulting-Quality Color Palettes

Use one of these curated palettes per diagram. Each palette provides role-based colors for consistent visual hierarchy. **Rule:** max 3 fill colors per diagram, never use saturated primaries (`3B82F6`, `EF4444`, `10B981`, `F59E0B`), connectors use the Neutral color.

**Corporate Blue** — Default for technical/enterprise diagrams:

| Role | Hex | Use |
|------|-----|-----|
| Primary | `2E5090` | Main shapes, key components |
| Secondary | `5B8DB8` | Supporting shapes |
| Accent | `C4A35A` | Highlights, decision points |
| Neutral | `6B7280` | Connectors, borders, labels |
| Light | `F1F5F9` | Group backgrounds |

**Warm Professional** — Reports, executive presentations:

| Role | Hex | Use |
|------|-----|-----|
| Primary | `7C3A2D` | Main shapes |
| Secondary | `C4734F` | Supporting shapes |
| Accent | `D4A847` | Highlights, callouts |
| Neutral | `6B7280` | Connectors, borders, labels |
| Light | `FDF6F0` | Group backgrounds |

**Modern Slate** — Cloud, DevOps, modern tech:

| Role | Hex | Use |
|------|-----|-----|
| Primary | `334155` | Main shapes |
| Secondary | `64748B` | Supporting shapes |
| Accent | `0EA5E9` | Highlights, action items |
| Neutral | `94A3B8` | Connectors, borders, labels |
| Light | `F1F5F9` | Group backgrounds |

**Forest Green** — Environmental, healthcare, sustainability:

| Role | Hex | Use |
|------|-----|-----|
| Primary | `1B5E42` | Main shapes |
| Secondary | `3D8B6E` | Supporting shapes |
| Accent | `D4A847` | Highlights, decisions |
| Neutral | `6B7280` | Connectors, borders, labels |
| Light | `F0F9F4` | Group backgrounds |

**Color rules:**
- White text (`FFFFFF`) on Primary/Secondary fills
- Dark text (`1E293B`) on Light fills
- Connector/border colors use the Neutral value from your chosen palette
- Group backgrounds use the Light value
- Darker variant of fill for borders: e.g., Primary `2E5090` → border `1E3A6A`

### Visual Weight Hierarchy

Use a 3-tier visual weight system to create depth and emphasis:

| Tier | Role | Fill | Border | Shadow | Font | charSpacing |
|------|------|------|--------|--------|------|-------------|
| **Tier 1** (primary) | Key components | Primary color, dark | Borderless | `{ "blur": 5, "offset": 4, "opacity": 0.4 }` | Bold, 10-11pt, white | `1` |
| **Tier 2** (secondary) | Supporting elements | Secondary color, medium | Borderless | `{ "blur": 3, "offset": 2, "opacity": 0.25 }` | Regular, 9-10pt | — |
| **Tier 3** (background) | Context, groups | Light fill | Subtle or borderless | `{ "blur": 6, "offset": 4, "opacity": 0.12 }` | 9pt, italic | — |

### Depth & Visual Weight Rules

1. **Never combine a visible border AND a shadow on the same shape.** Borders say "flat, contained." Shadows say "elevated, floating." Mixing both creates visual tension. All three tiers use borderless + shadow — no exceptions.
2. **Shadows imply elevation order.** Higher blur+offset = further from the canvas. Groups (background) get the lightest shadow; primary shapes get the strongest.
3. **Data-ink ratio:** Every visual element (border, shadow, gradient, icon) must earn its place. If removing an element doesn't reduce clarity, remove it. Decorative borders on Tier 1 shapes add no information — omit them.

### Depth & Visual Weight Rules

1. **Never combine a visible border AND a shadow on the same shape.** Borders say "flat, contained." Shadows say "elevated, floating." Mixing both creates visual tension. Exception: Tier 2 shapes may use a 1pt border as an accent alongside a very light shadow (opacity ≤ 0.2).
2. **Shadows imply elevation order.** Higher blur+offset = further from the canvas. Groups (background) get the lightest shadow; primary shapes get the strongest.
3. **Data-ink ratio:** Every visual element (border, shadow, gradient, icon) must earn its place. If removing an element doesn't reduce clarity, remove it. Decorative borders on Tier 1 shapes add no information — omit them.

### Typography Hierarchy

| Element | fontSize | fontBold | charSpacing | fontColor |
|---------|----------|----------|-------------|-----------|
| Slide title | 20 | true | 1.5 | `1E293B` |
| Slide subtitle | 12 | false | — | `64748B` |
| Primary shape labels | 10-11 | true | 1 | `FFFFFF` |
| Secondary shape labels | 9-10 | false | — | `FFFFFF` |
| Group labels | 9 | true | 1 | `64748B` |
| Connector labels | 9 | false | — | `6B7280` |
| Description text | 9 | false | — | `64748B` |
| Standalone text | 9-11 | varies | — | `1E293B` |

### Spacing Standards

| Measurement | Minimum | Recommended |
|-------------|---------|-------------|
| Gap between shapes | 0.3" | 0.4"–0.6" |
| Padding inside groups | 0.15" | 0.2"–0.3" |
| Shape text margin | `[5,8,5,8]` | `[8,10,8,10]` |
| Shape heights | 0.5" | 0.6"–0.8" |
| Shape widths | 1.5" | 1.8"–2.5" |
| Architecture shape widths | 1.8" | 2.0"–2.5" |
| Icon-to-shape gap | 0.05" | 0.05" |
| Shape-to-description gap | 0.05" | 0.05"–0.1" |
| Connector label clearance | 0.1" | 0.15" |

### Minimum Size Rules

| Element | Minimum | Recommended |
|---------|---------|-------------|
| Shape with label | w: 1.5" | w: max(1.8", chars×0.13") |
| Shape with textRuns | 2.0" × 0.8" | 2.2" × 0.9" |
| Diamond | 1.8" × 1.0" | 2.0" × 1.2" |
| Cylinder | h: 1.0" | h: 1.2" |

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

Right-to-left arrow: `x1 > x2` (flip handled automatically)
```json
{ "x1": 7.0, "y1": 2.0, "x2": 4.0, "y2": 2.0 }
```

**Curved connectors:** pptxgenjs only supports straight lines and elbow (orthogonal L-path) routing — no Bezier curves. If a reference image shows smooth curved arrows, use `"route": "elbow"` as the closest approximation.

**Orthogonal rule:** All connectors should be orthogonal (parallel or perpendicular to slide margins). Never use diagonal connectors. Use `route: "elbow"` for any connection between non-aligned shapes. Use `route: "straight"` only when two shapes share the exact same X or Y coordinate.

### Connector Semantics

| Style | Meaning | Properties |
|-------|---------|------------|
| Solid, 2.0pt | Primary data flow, synchronous call | `lineWidth: 2.0` |
| Dashed | Async, event-driven, or secondary flow | `lineDash: "dash"` |
| Dotted | Optional, monitoring, or out-of-band | `lineDash: "sysDot"` |

Always label connectors with the interaction verb (e.g., "Invoke", "Query", "Emit"). Unlabeled arrows force the reader to guess semantics.
