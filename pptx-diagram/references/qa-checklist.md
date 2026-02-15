# QA Checklist for Diagram Slides

Use this checklist after converting the PPTX to PNG via LibreOffice. Inspect the rendered image and check each item. If any issue is found, fix the JSON spec and rebuild.

**Maximum 2 fix cycles.** After 2 attempts, report remaining issues as known limitations.

---

## 1. Overlap

**What to look for:** Shapes, labels, or icons overlapping each other or bleeding into adjacent elements.

**Typical fix:** Increase gaps between elements by 0.2"–0.3". Shift overlapping elements apart. Reduce shape width if elements are too wide for the available space.

```json
// Before: shapes too close
{ "x": 2.0, "w": 2.0 },  // ends at 4.0
{ "x": 4.0, "w": 2.0 }   // starts at 4.0 — touching

// After: add 0.3" gap
{ "x": 2.0, "w": 2.0 },  // ends at 4.0
{ "x": 4.3, "w": 2.0 }   // starts at 4.3
```

## 2. Text Overflow

**What to look for:** Labels cut off, truncated, or running outside their shape boundaries.

**Typical fix:** Widen the shape (`w`), reduce `fontSize`, or shorten the label text. For multi-word labels, ensure shape width is at least `label.length * 0.12"` at fontSize 10.

```json
// Before: label too long for shape
{ "w": 1.2, "label": "Authentication Service", "fontSize": 10 }

// After: widen shape or reduce font
{ "w": 2.0, "label": "Authentication Service", "fontSize": 10 }
// or
{ "w": 1.5, "label": "Auth Service", "fontSize": 9 }
```

## 3. Out of Bounds

**What to look for:** Elements partially or fully outside the visible slide area.

**Bounds:**
- Horizontal: x ≥ 0, x + w ≤ 10
- Vertical diagram area: y ≥ 0.85, y + h ≤ 5.35
- Title bar: y = 0 to 0.75 (auto-rendered)
- Footer: y = 5.25 to 5.55 (auto-rendered)

**Typical fix:** Shift elements inward or shrink dimensions so they fit within bounds.

## 4. Spacing Consistency

**What to look for:** Uneven gaps between shapes in the same row/column. Misaligned centers.

**Typical fix:** Recalculate positions for uniform spacing. For N shapes across width W starting at offset X:
```
gap = (W - N * shapeWidth) / (N + 1)
x[i] = X + gap + i * (shapeWidth + gap)
```

## 5. Icons

**What to look for:** Icons missing (blank space where icon should be), invisible (wrong color on matching background), or wrong size.

**For architecture/cloud/network diagrams:** Verify that major components (3+ shapes) have associated icons. If the reference image shows icons, the spec must include them. Missing icons are the #1 cause of the PPTX looking "flat" compared to reference images.

**Typical fix:**
- Missing: verify `name` matches a valid react-icons export (check `icon-catalog.md`)
- Invisible: change `color` to contrast with the background (dark icon on light bg, or vice versa)
- Too small/large: adjust `w` and `h` (typical: 0.3"–0.5")

## 6. Connectors

**What to look for:** Arrows not connecting to shape edges. Arrows overlapping shapes. Arrow labels overlapping shapes or other labels.

**Typical fix:** Recalculate connector endpoints from shape edges:
- Right edge: `x1 = shape.x + shape.w`
- Left edge: `x2 = shape.x`
- Bottom edge: `y1 = shape.y + shape.h`
- Top edge: `y2 = shape.y`

```json
// Connect right edge of shape A to left edge of shape B
// Shape A: x=2.0, w=1.5 → right edge at 3.5
// Shape B: x=5.0 → left edge at 5.0
{ "x1": 3.5, "y1": 2.3, "x2": 5.0, "y2": 2.3 }
```

## 7. Color Contrast

**What to look for:** Text unreadable against its background fill. Light text on light fills, dark text on dark fills.

**Typical fix:**
- Dark fills (`4A90E2`, `3B82F6`, `333333`): use white text (`FFFFFF`)
- Light fills (`F0F4F8`, `FFFFFF`, `EFF6FF`): use dark text (`1E293B` or `333333`)
- Connector labels: use medium gray (`666666`) on white backgrounds

## 8. Reference Match

**What to look for:** Rendered layout does not structurally match the reference image from Step 2. Missing components, wrong arrangement, missing connections.

**Typical fix:** Compare the rendered PNG against the reference image. Check that:
- All components from the reference are present
- The spatial arrangement (rows, columns, groupings) matches
- All connections/arrows are accounted for
- Grouping boxes contain the correct elements

## 9. Shadow Consistency

**What to look for:** Shadows applied to some shapes but not others in the same visual tier. Inconsistent shadow parameters (different blur, offset, or angle across similar shapes).

**Typical fix:** If shadows are used, apply the same shadow settings to all primary shapes uniformly. Group backgrounds may have a different (usually lighter) shadow. Use consistent values: `{ "blur": 3, "offset": 2, "angle": 45, "opacity": 0.3 }` is a safe default.

## 10. Connector Anchoring

**What to look for:** Connectors that don't visually touch their source/target shape edges. Gaps between arrow endpoints and shapes.

**Typical fix:** Use shape-anchored connectors (`from`/`to` with `fromSide`/`toSide`) instead of absolute coordinates. If using absolute coordinates, recalculate endpoints from shape edges:
- Right edge: `x1 = shape.x + shape.w`, `y1 = shape.y + shape.h/2`
- Left edge: `x2 = shape.x`, `y2 = shape.y + shape.h/2`
- Bottom edge: `x1 = shape.x + shape.w/2`, `y1 = shape.y + shape.h`
- Top edge: `x2 = shape.x + shape.w/2`, `y2 = shape.y`

## 11. Font Consistency

**What to look for:** Mixed font families across shapes and labels. Different fontFace values used without intentional design reason.

**Typical fix:** Use the same `fontFace` throughout the diagram. Default is `"Calibri"`. Only vary font if deliberately using a different face for labels vs. shape text.

## 12. Visual Weight Hierarchy

**What to look for:** All shapes at the same visual weight — same shadow, same border, same fill intensity. Primary shapes should visually "pop" more than secondary shapes.

**Typical fix:** Apply the 3-tier system from shape-spec.md:
- **Tier 1** (primary shapes): dark fill, borderless (`lineWidth: 0`), strong shadow `{ "blur": 4, "offset": 3, "opacity": 0.35 }`, bold 10-11pt, `charSpacing: 1`
- **Tier 2** (secondary shapes): medium fill, thin border (1pt), light shadow `{ "blur": 2, "offset": 1, "opacity": 0.2 }`, regular 9-10pt
- **Tier 3** (groups/backgrounds): very light fill, subtle or no border, soft shadow `{ "blur": 6, "offset": 4, "opacity": 0.12 }`, 8-9pt italic

```json
// Before: all shapes identical weight
{ "fill": "3B82F6", "lineWidth": 1, "shadow": { "blur": 3, "offset": 2, "opacity": 0.3 } }
{ "fill": "3B82F6", "lineWidth": 1, "shadow": { "blur": 3, "offset": 2, "opacity": 0.3 } }

// After: Tier 1 vs Tier 2 distinction
{ "fill": "2E5090", "lineWidth": 0, "shadow": { "blur": 4, "offset": 3, "opacity": 0.35 }, "fontBold": true, "charSpacing": 1 }
{ "fill": "5B8DB8", "lineWidth": 1, "shadow": { "blur": 2, "offset": 1, "opacity": 0.2 } }
```

## 13. Color Palette Quality

**What to look for:** Bright saturated primary colors (`3B82F6`, `EF4444`, `10B981`, `F59E0B`). More than 3 fill colors. Colors that look "developer-grade" rather than muted and professional.

**Typical fix:** Replace saturated colors with consulting palette equivalents:

| Saturated (avoid) | Muted replacement |
|-------------------|-------------------|
| `3B82F6` (bright blue) | `2E5090` or `334155` |
| `EF4444` (bright red) | `7C3A2D` |
| `10B981` (bright green) | `1B5E42` |
| `F59E0B` (bright amber) | `C4A35A` or `D4A847` |
| `22C55E` (green) | `3D8B6E` |
| `F97316` (orange) | `C4A35A` |
| `34D399` (teal) | `5B8DB8` |

Pick one consulting palette from shape-spec.md (Corporate Blue, Warm Professional, Modern Slate, or Forest Green) and apply consistently. Maximum 3 fill colors per diagram.

## 14. Typography & Spacing Polish

**What to look for:** Tight text margins, no character spacing on key labels, shapes crammed together (less than 0.3" gaps), inconsistent alignment.

**Typical fix:**
- Add `charSpacing: 1` to primary shape labels and group labels
- Increase shape text margins from `[3,5,3,5]` to `[8,10,8,10]` for breathing room
- Ensure minimum 0.4" gap between adjacent shapes
- Use `textRuns` for shapes that need title + subtitle formatting
- Add `charSpacing: 1.5` to slide title via `meta.titleCharSpacing`

```json
// Before: cramped
{ "margin": [3, 5, 3, 5], "x": 2.0 }
{ "x": 3.5 }  // only 0.0" gap (shape ends at 3.5 if w=1.5)

// After: generous
{ "margin": [8, 10, 8, 10], "charSpacing": 1, "x": 2.0, "w": 1.5 }
{ "x": 3.9 }  // 0.4" gap
```

**Note:** Text glow and text outline effects may not render in LibreOffice headless PNG export but will appear correctly when opening the PPTX in PowerPoint.

## 15. Text-to-Shape Fit

**What to look for:** Text cramped inside shapes. Shapes too narrow for their label text. textRuns shapes smaller than 2.0" × 0.8". Diamonds smaller than 1.8" × 1.0".

**Typical fix:** Apply minimum size rules:
- Shape with `label`: min `w` = `max(1.5, label.length * 0.13)` at fontSize 10
- Shape with `textRuns`: min `w` = 2.0", min `h` = 0.8"
- Diamond: min 1.8" × 1.0"
- Cylinder: min `h` = 1.0"

```json
// Before: too small for text
{ "shapeType": "diamond", "w": 1.0, "h": 0.8, "label": "Approve?" }

// After: meets minimum
{ "shapeType": "diamond", "w": 1.8, "h": 1.0, "label": "Approve?" }
```

## 16. Swim Lane Label Placement

**What to look for:** Lane names rendered inside groups via `group.label` — these often overflow or overlap group contents. Phase headers embedded in groups instead of positioned independently above.

**Typical fix:** Use the external label pattern:
1. Groups have NO `label` property
2. Separate `text` elements for lane names, positioned LEFT of groups (`x: 0.1, w: 1.6, align: "right"`)
3. Groups start at `x: 1.8` to leave room
4. Phase headers as separate `text` elements ABOVE the diagram area

```json
// Before: label inside group (overflows narrow groups)
{ "type": "group", "x": 1.8, "y": 1.0, "w": 8.0, "h": 1.2, "label": "Incident Commander" }

// After: separate text element outside group
{ "type": "group", "x": 1.8, "y": 1.0, "w": 8.0, "h": 1.2 },
{ "type": "text", "x": 0.1, "y": 1.0, "w": 1.6, "h": 1.2, "text": "Incident Commander", "align": "right", "fontBold": true }
```

## 17. Connector Label Overlap

**What to look for:** Connector labels overlapping shapes they connect. Labels clipped by nearby elements. Labels too narrow for their text.

**Typical fix:**
- Use `labelOffset` to shift the label along the connector path away from shapes
- Use `labelW` to override auto-calculated label width if needed
- Increase spacing between connected shapes

```json
// Before: label overlaps target shape
{ "type": "connector", "from": "a", "to": "b", "label": "Long Label Text" }

// After: shift label and override width
{ "type": "connector", "from": "a", "to": "b", "label": "Long Label Text", "labelOffset": -0.3, "labelW": 1.5 }
```

---

## Quick Reference

| # | Check | Pass Criteria |
|---|-------|--------------|
| 1 | Overlap | No shapes/labels/icons overlap |
| 2 | Text overflow | All labels fully visible within shapes |
| 3 | Bounds | All elements within 0–10" horizontal, 0.85–5.35" vertical |
| 4 | Spacing | Consistent gaps within rows/columns (±0.1" tolerance) |
| 5 | Icons | All icon elements visible and correctly sized; architecture diagrams have icons on major components |
| 6 | Connectors | Arrows start/end at shape edges, labels clear of shapes |
| 7 | Contrast | All text readable against its background |
| 8 | Reference match | Layout structurally matches reference image |
| 9 | Shadow consistency | Shadows applied uniformly across similar shapes |
| 10 | Connector anchoring | Connectors visually connect to shape edges |
| 11 | Font consistency | Same fontFace used throughout unless intentionally varied |
| 12 | Visual weight | Primary shapes visually heavier than secondary (shadow, fill, border) |
| 13 | Palette quality | Max 3 fill colors, all muted/desaturated, no bright primaries |
| 14 | Typography polish | charSpacing on labels, adequate margins (≥[8,10,8,10]), ≥0.4" inter-shape gaps |
| 15 | Text-to-shape fit | Shapes wide enough for labels, textRuns ≥ 2.0"×0.8", diamonds ≥ 1.8"×1.0" |
| 16 | Swim lane labels | Lane names are separate text elements outside groups, not group.label |
| 17 | Connector label overlap | Labels don't overlap shapes; use labelOffset to shift if needed |
