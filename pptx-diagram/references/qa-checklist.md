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

---

## Quick Reference

| Check | Pass Criteria |
|-------|--------------|
| Overlap | No shapes/labels/icons overlap |
| Text overflow | All labels fully visible within shapes |
| Bounds | All elements within 0–10" horizontal, 0.85–5.35" vertical |
| Spacing | Consistent gaps within rows/columns (±0.1" tolerance) |
| Icons | All icon elements visible and correctly sized |
| Connectors | Arrows start/end at shape edges, labels clear of shapes |
| Contrast | All text readable against its background |
| Reference match | Layout structurally matches reference image |
