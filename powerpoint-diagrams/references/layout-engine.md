# Layout-First Engine Reference

**Architecture: Define → Compute → Validate → Render**

```
DEFINE  ──QC1──▶  COMPUTE  ──QC2──▶  RENDER  ──QC3──▶  SAVE
```

Every diagram follows four phases with QC at each checkpoint. Coordinate math is separated from XML generation so bugs are caught before any XML is emitted.

---

## Phase 1: Data Model (Dataclasses)

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Rect:
    """Bounding rectangle in EMU."""
    x: int
    y: int
    cx: int
    cy: int

@dataclass
class Shape:
    """Logical shape — no coordinates yet."""
    id: str                           # unique string key (e.g. "start", "ceo")
    text: str                         # display label
    preset: str = "flowChartProcess"  # OOXML preset geometry name
    style: str = "primary"            # palette key
    group: str = ""                   # layout group (level for hierarchy, lane for swimlane)
    text_line2: str = ""              # optional second line (e.g. title in org chart)

@dataclass
class Connection:
    """Logical connection — no coordinates yet."""
    src: str              # source shape id
    tgt: str              # target shape id
    label: str = ""       # optional label (e.g. "YES")
    color: str = ""       # override color (empty = use default)

@dataclass
class Diagram:
    """Complete logical diagram definition."""
    title: str
    layout_type: str                          # "horizontal_flow", "hierarchy", "swimlane"
    shapes: list                              # list of Shape
    connections: list                          # list of Connection
    palette: str = "professional_blue"        # palette name
    title_style: str = "banner"               # "banner" (filled bar) or "text" (floating)

@dataclass
class PlacedShape:
    """Shape with computed position, resolved colors, and font size."""
    shape_id: int                    # numeric OOXML id
    key: str                         # string key from Shape.id
    text: str
    text_line2: str
    preset: str
    rect: Rect
    fill_hex: str
    border_hex: str
    text_color: str
    font_size: int                   # in 100ths of pt (1400 = 14pt)
    font_size2: int                  # second line font size
    bold: bool
    shadow: bool
    glow: bool
    gradient: bool                   # True = use gradient fill
    gradient_end_hex: str            # darker end of gradient
    z_layer: int                     # 0=bg, 1=lane, 2=connector, 3=shape, 4=label

@dataclass
class PlacedConnector:
    """Connector with computed bounding box and flip flags."""
    conn_id: int
    src_shape_id: int
    src_idx: int                     # connection point: 0=top, 1=right, 2=bottom, 3=left
    tgt_shape_id: int
    tgt_idx: int
    rect: Rect
    flip_h: bool
    flip_v: bool
    color_hex: str
    line_w: int
    connector_type: str
    head_type: str
    tail_type: str
    round_join: bool
    z_layer: int                     # always 2

@dataclass
class PlacedLabel:
    """Floating text annotation."""
    label_id: int
    text: str
    rect: Rect
    color_hex: str
    font_size: int
    bold: bool
    z_layer: int                     # always 4

@dataclass
class LaneBg:
    """Lane background rectangle."""
    lane_id: int
    label: str
    rect: Rect
    fill_hex: str
    border_hex: str
    z_layer: int                     # always 1

@dataclass
class LayoutResult:
    """Complete computed layout — ready for validation and rendering."""
    title: str
    title_style: str
    title_rect: Rect
    bg_hex: str
    placed_shapes: list              # list of PlacedShape
    placed_connectors: list          # list of PlacedConnector
    placed_labels: list              # list of PlacedLabel
    lane_bgs: list                   # list of LaneBg
```

---

## Constants

```python
# ── Slide dimensions ─────────────────────────────────────────────────────────
SLIDE_W = 9144000    # 10 inches
SLIDE_H = 5143500    # 5.625 inches
IN = 914400          # 1 inch in EMU
PT = 12700           # 1 point in EMU

# ── Color palettes ───────────────────────────────────────────────────────────
PALETTES = {
    "professional_blue": {
        "bg":       "EEF2FA",
        "dark":     ("1F3864", "16294A"),   # (fill, border)
        "primary":  ("4472C4", "2E4FA3"),
        "accent":   ("ED7D31", "C05C13"),
        "success":  ("70AD47", "507C32"),
        "neutral":  ("5D6D7E", "2C3E50"),
        "connector": "4472C4",
        "title_text": "1F3864",
    },
}

# ── Default shape dimensions ─────────────────────────────────────────────────
SHAPE_DEFAULTS = {
    "horizontal_flow": {
        "process":    (1371600, 685800),    # 1.5" x 0.75"
        "decision":   (1371600, 914400),    # 1.5" x 1.0"
        "terminator": (1371600, 571500),    # 1.5" x 0.625"
        "gap":        228600,               # 0.25"
    },
    "hierarchy": {
        "shape":      (1600200, 571500),    # 1.75" x 0.625"
        "h_gap":      304800,               # 0.333"
        "v_gap":      685800,               # 0.75"
        "margin_top": 685800,
    },
    "swimlane": {
        "component":  (1371600, 685800),    # 1.5" x 0.75"
        "col_gap":    304800,               # 0.333"
        "title_h":    457200,               # 0.5" title bar
        "lane_gap":   25400,                # thin gap between lanes
    },
}

# ── Calibri character width table (approximate widths in EMU at 100pt) ───────
# Multiply by (font_size_pts / 100) to get actual width per character.
# These are averages — uppercase is wider, lowercase narrower.
CALIBRI_CHAR_W = {
    "upper":  54000,    # average uppercase letter width at 100pt
    "lower":  42000,    # average lowercase letter width at 100pt
    "space":  25000,    # space
    "narrow": 30000,    # i, l, 1, punctuation
    "wide":   60000,    # M, W, m, w
}
CALIBRI_AVG_CHAR_W = 45000   # blended average at 100pt
```

---

## QC1: Definition Validation

### `validate_definition()`

Called immediately after defining shapes and connections. Catches bad input before any math runs.

```python
VALID_PRESETS = {
    "flowChartProcess", "flowChartDecision", "flowChartTerminator",
    "flowChartMagneticDisk", "roundRect", "rect", "ellipse",
    "hexagon", "cloud", "flowChartDocument", "flowChartPreparation",
    "flowChartInputOutput", "flowChartAlternateProcess",
    "flowChartConnector", "flowChartPredefinedProcess",
}


def validate_definition(shapes, connections):
    """QC1: Validate definition data before compute. Raises on fatal, warns on quality."""
    warnings = []

    # Duplicate shape IDs — fatal
    ids = [s["id"] for s in shapes]
    if len(ids) != len(set(ids)):
        dupes = [x for x in ids if ids.count(x) > 1]
        raise ValueError(f"Duplicate shape IDs: {set(dupes)}")

    id_set = set(ids)

    for conn in connections:
        # Connection references non-existent shape — fatal
        if conn["src"] not in id_set:
            raise ValueError(f"Connection source '{conn['src']}' not found in shapes")
        if conn["tgt"] not in id_set:
            raise ValueError(f"Connection target '{conn['tgt']}' not found in shapes")
        # Self-loop — warn
        if conn["src"] == conn["tgt"]:
            warnings.append(f"Self-loop: '{conn['src']}' connects to itself")

    for s in shapes:
        # Empty text — warn
        if not s.get("text", "").strip():
            warnings.append(f"Empty text: shape '{s['id']}'")
        # Unknown preset — warn
        preset = s.get("preset", "")
        if preset and preset not in VALID_PRESETS:
            warnings.append(f"Unknown preset '{preset}' on shape '{s['id']}'")

    return warnings
```

| Check | Fatal? | Rationale |
|-------|--------|-----------|
| Duplicate shape IDs | Raise | Would cause silent overwrites in shape_map |
| Connection src/tgt references non-existent shape ID | Raise | Would crash in compute phase |
| Empty shape text | Warn | Might be intentional but usually a bug |
| Unknown preset name (not in VALID_PRESETS) | Warn | PowerPoint will show a rect fallback |
| Connection src == tgt (self-loop) | Warn | Usually unintended |

---

## Phase 2: Layout Computation

### `layout_horizontal_flow()`

```python
def layout_horizontal_flow(diagram, id_counter):
    """Compute layout for a left-to-right flowchart."""
    pal = PALETTES[diagram.palette]
    defaults = SHAPE_DEFAULTS["horizontal_flow"]
    gap = defaults["gap"]

    # Determine shape dimensions based on preset
    def shape_dims(preset):
        if "Decision" in preset or "decision" in preset.lower():
            return defaults["decision"]
        elif "Terminator" in preset or "terminator" in preset.lower():
            return defaults["terminator"]
        else:
            return defaults["process"]

    n = len(diagram.shapes)
    sw = defaults["process"][0]  # all shapes same width for alignment
    total_w = n * sw + (n - 1) * gap
    left = (SLIDE_W - total_w) // 2
    base_y = (SLIDE_H - defaults["process"][1]) // 2

    # Title
    title_rect = Rect(457200, 228600, 8229600, 457200)

    # Place shapes
    placed_shapes = []
    shape_map = {}  # key -> PlacedShape (for connector lookup)
    xs = [left + i * (sw + gap) for i in range(n)]

    for i, shape in enumerate(diagram.shapes):
        sid = id_counter[0]; id_counter[0] += 1
        cx, cy = shape_dims(shape.preset)
        y = base_y + (defaults["process"][1] - cy) // 2  # vertically center

        colors = pal.get(shape.style, pal["primary"])
        fill_hex, border_hex = colors

        font_size = estimate_font_size(shape.text, cx, cy)

        ps = PlacedShape(
            shape_id=sid, key=shape.id, text=shape.text, text_line2="",
            preset=shape.preset,
            rect=Rect(xs[i], y, cx, cy),
            fill_hex=fill_hex, border_hex=border_hex, text_color="FFFFFF",
            font_size=font_size, font_size2=0, bold=True,
            shadow=True, glow=False, gradient=False, gradient_end_hex="",
            z_layer=3,
        )
        placed_shapes.append(ps)
        shape_map[shape.id] = ps

    # Place connectors
    placed_connectors = []
    for conn in diagram.connections:
        src = shape_map[conn.src]
        tgt = shape_map[conn.tgt]
        cid = id_counter[0]; id_counter[0] += 1

        color = conn.color if conn.color else pal["connector"]
        bbox, flip_h, flip_v, src_idx, tgt_idx = compute_connector_bbox(
            src.rect, tgt.rect, "right_to_left"
        )

        placed_connectors.append(PlacedConnector(
            conn_id=cid,
            src_shape_id=src.shape_id, src_idx=src_idx,
            tgt_shape_id=tgt.shape_id, tgt_idx=tgt_idx,
            rect=bbox, flip_h=flip_h, flip_v=flip_v,
            color_hex=color, line_w=25400,
            connector_type="bentConnector3",
            head_type="none", tail_type="triangle",
            round_join=True, z_layer=2,
        ))

    # Place labels
    placed_labels = []
    for conn in diagram.connections:
        if conn.label:
            src = shape_map[conn.src]
            tgt = shape_map[conn.tgt]
            lid = id_counter[0]; id_counter[0] += 1
            lx = src.rect.x + src.rect.cx + gap // 4
            ly = base_y + defaults["process"][1] // 2 - 342900
            placed_labels.append(PlacedLabel(
                label_id=lid, text=conn.label,
                rect=Rect(lx, ly, 228600, 228600),
                color_hex="27AE60", font_size=1000, bold=True, z_layer=4,
            ))

    return LayoutResult(
        title=diagram.title, title_style=diagram.title_style,
        title_rect=title_rect, bg_hex=pal["bg"],
        placed_shapes=placed_shapes,
        placed_connectors=placed_connectors,
        placed_labels=placed_labels, lane_bgs=[],
    )
```

### `layout_hierarchy()`

```python
def layout_hierarchy(diagram, id_counter):
    """Compute layout for a top-to-bottom org chart / hierarchy."""
    pal = PALETTES[diagram.palette]
    defaults = SHAPE_DEFAULTS["hierarchy"]
    sw, sh = defaults["shape"]
    h_gap = defaults["h_gap"]
    v_gap = defaults["v_gap"]
    margin_top = defaults["margin_top"]

    # Level colors (by group string "0", "1", "2", ...)
    level_colors = {
        "0": pal.get("dark",    pal["primary"]),
        "1": pal.get("primary", pal["primary"]),
        "2": pal.get("success", pal["primary"]),
        "3": pal.get("accent",  pal["primary"]),
    }

    # Group shapes by level
    levels = {}
    for shape in diagram.shapes:
        lvl = shape.group or "0"
        levels.setdefault(lvl, []).append(shape)

    sorted_levels = sorted(levels.keys())

    def center_row(n, shape_w=sw, gap=h_gap):
        total = n * shape_w + (n - 1) * gap
        left = (SLIDE_W - total) // 2
        return [left + i * (shape_w + gap) for i in range(n)]

    # Title
    title_rect = Rect(457200, 152400, 8229600, 400050)

    # Place shapes level by level
    placed_shapes = []
    shape_map = {}

    for lvl_idx, lvl_key in enumerate(sorted_levels):
        shapes_in_level = levels[lvl_key]
        xs = center_row(len(shapes_in_level))
        y = margin_top + lvl_idx * (sh + v_gap)
        colors = level_colors.get(lvl_key, pal["primary"])
        fill_hex, border_hex = colors

        for i, shape in enumerate(shapes_in_level):
            sid = id_counter[0]; id_counter[0] += 1

            font_size = estimate_font_size(shape.text_line2 or shape.text, sw, sh)
            font_size2 = max(font_size - 200, 800) if shape.text_line2 else 0

            ps = PlacedShape(
                shape_id=sid, key=shape.id,
                text=shape.text_line2,       # name on first line
                text_line2=shape.text,        # title on second line
                preset=shape.preset or "roundRect",
                rect=Rect(xs[i], y, sw, sh),
                fill_hex=fill_hex, border_hex=border_hex, text_color="FFFFFF",
                font_size=font_size, font_size2=font_size2, bold=True,
                shadow=True, glow=False,
                gradient=True, gradient_end_hex=border_hex,
                z_layer=3,
            )
            placed_shapes.append(ps)
            shape_map[shape.id] = ps

    # Place connectors (parent bottom → child top)
    placed_connectors = []
    for conn in diagram.connections:
        src = shape_map[conn.src]
        tgt = shape_map[conn.tgt]
        cid = id_counter[0]; id_counter[0] += 1

        bbox, flip_h, flip_v, src_idx, tgt_idx = compute_connector_bbox(
            src.rect, tgt.rect, "top_to_bottom"
        )

        placed_connectors.append(PlacedConnector(
            conn_id=cid,
            src_shape_id=src.shape_id, src_idx=src_idx,
            tgt_shape_id=tgt.shape_id, tgt_idx=tgt_idx,
            rect=bbox, flip_h=flip_h, flip_v=flip_v,
            color_hex="AAAAAA", line_w=19050,
            connector_type="bentConnector3",
            head_type="none", tail_type="triangle",
            round_join=True, z_layer=2,
        ))

    return LayoutResult(
        title=diagram.title, title_style="text",
        title_rect=title_rect, bg_hex="gradient:F8FAFF:EEF2FA",
        placed_shapes=placed_shapes,
        placed_connectors=placed_connectors,
        placed_labels=[], lane_bgs=[],
    )
```

### `layout_swimlane()`

```python
def layout_swimlane(diagram, id_counter):
    """Compute layout for a multi-lane architecture diagram."""
    pal = PALETTES[diagram.palette]
    defaults = SHAPE_DEFAULTS["swimlane"]
    comp_w, comp_h = defaults["component"]
    col_gap = defaults["col_gap"]
    title_h = defaults["title_h"]
    lane_gap = defaults["lane_gap"]

    # Lane definitions — derive from unique groups in shape order
    lane_order = []
    lane_set = set()
    for shape in diagram.shapes:
        if shape.group and shape.group not in lane_set:
            lane_order.append(shape.group)
            lane_set.add(shape.group)

    n_lanes = len(lane_order)
    usable_h = SLIDE_H - title_h - 50000  # below title bar
    lane_h = (usable_h - (n_lanes - 1) * lane_gap) // n_lanes

    # Lane style lookup
    LANE_STYLES = {
        "presentation": {"label": "PRESENTATION LAYER",   "fill": "EBF3FB", "border": "C5D9F1"},
        "business":     {"label": "BUSINESS LOGIC LAYER",  "fill": "E8F8E8", "border": "C5E8B0"},
        "data":         {"label": "DATA LAYER",            "fill": "FEF9E7", "border": "F9E3A6"},
    }
    # Allow custom lane names — fall back to generic style
    default_fills = [("EBF3FB", "C5D9F1"), ("E8F8E8", "C5E8B0"), ("FEF9E7", "F9E3A6"),
                     ("F3E8FB", "D9C5F1"), ("FBE8E8", "F1C5C5")]

    lane_bgs = []
    lane_y_map = {}
    for li, lane_key in enumerate(lane_order):
        y = title_h + 50000 + li * (lane_h + lane_gap)
        lane_y_map[lane_key] = y

        style = LANE_STYLES.get(lane_key, {})
        label = style.get("label", lane_key.upper() + " LAYER")
        fill = style.get("fill", default_fills[li % len(default_fills)][0])
        border = style.get("border", default_fills[li % len(default_fills)][1])

        lid = id_counter[0]; id_counter[0] += 1
        lane_bgs.append(LaneBg(
            lane_id=lid, label=label,
            rect=Rect(0, y, SLIDE_W, lane_h),
            fill_hex=fill, border_hex=border, z_layer=1,
        ))

    # Group shapes by lane, then assign columns
    lane_shapes = {}
    for shape in diagram.shapes:
        lane_shapes.setdefault(shape.group, []).append(shape)

    def col_positions(n_cols):
        total = n_cols * comp_w + (n_cols - 1) * col_gap
        left = (SLIDE_W - total) // 2
        return [left + c * (comp_w + col_gap) for c in range(n_cols)]

    # Component colors by lane position
    comp_colors = [pal["primary"], pal["primary"], pal["success"], pal["accent"]]

    # Title
    title_rect = Rect(0, 0, SLIDE_W, title_h)

    # Place shapes
    placed_shapes = []
    shape_map = {}

    for li, lane_key in enumerate(lane_order):
        shapes = lane_shapes.get(lane_key, [])
        xs = col_positions(len(shapes))
        lane_y = lane_y_map[lane_key]
        comp_y = lane_y + (lane_h - comp_h) // 2

        for ci, shape in enumerate(shapes):
            sid = id_counter[0]; id_counter[0] += 1
            colors = pal.get(shape.style, comp_colors[ci % len(comp_colors)])
            if isinstance(colors, str):
                colors = (colors, colors)
            fill_hex, border_hex = colors

            font_size = estimate_font_size(shape.text, comp_w, comp_h)

            ps = PlacedShape(
                shape_id=sid, key=shape.id,
                text=shape.text, text_line2="",
                preset=shape.preset or "flowChartProcess",
                rect=Rect(xs[ci], comp_y, comp_w, comp_h),
                fill_hex=fill_hex, border_hex=border_hex, text_color="FFFFFF",
                font_size=font_size, font_size2=0, bold=True,
                shadow=True, glow=(shape.style == "accent"),
                gradient=False, gradient_end_hex="",
                z_layer=3,
            )
            placed_shapes.append(ps)
            shape_map[shape.id] = ps

    # Place connectors
    placed_connectors = []
    for conn in diagram.connections:
        src = shape_map[conn.src]
        tgt = shape_map[conn.tgt]
        cid = id_counter[0]; id_counter[0] += 1

        color = conn.color if conn.color else "888888"

        # Determine direction based on relative position
        dy = tgt.rect.y - src.rect.y
        dx = tgt.rect.x - src.rect.x
        if abs(dy) > abs(dx):
            direction = "top_to_bottom"
        else:
            direction = "right_to_left"

        bbox, flip_h, flip_v, src_idx, tgt_idx = compute_connector_bbox(
            src.rect, tgt.rect, direction
        )

        placed_connectors.append(PlacedConnector(
            conn_id=cid,
            src_shape_id=src.shape_id, src_idx=src_idx,
            tgt_shape_id=tgt.shape_id, tgt_idx=tgt_idx,
            rect=bbox, flip_h=flip_h, flip_v=flip_v,
            color_hex=color, line_w=19050,
            connector_type="bentConnector3",
            head_type="none", tail_type="stealth",
            round_join=True, z_layer=2,
        ))

    return LayoutResult(
        title=diagram.title, title_style="banner",
        title_rect=title_rect, bg_hex="F5F6FA",
        placed_shapes=placed_shapes,
        placed_connectors=placed_connectors,
        placed_labels=[], lane_bgs=lane_bgs,
    )
```

---

## Connector Math

### `compute_connector_bbox()`

This is the critical function that fixes misrouted connectors. It computes the bounding box AND flip flags mathematically.

```python
def compute_connector_bbox(src_rect, tgt_rect, direction):
    """
    Compute connector bounding box and flip flags.

    Returns: (Rect, flip_h, flip_v, src_idx, tgt_idx)

    direction: "right_to_left" (horizontal flow) or "top_to_bottom" (hierarchy)
    """
    if direction == "right_to_left":
        # Source right edge → Target left edge
        src_point_x = src_rect.x + src_rect.cx       # right edge center
        src_point_y = src_rect.y + src_rect.cy // 2
        tgt_point_x = tgt_rect.x                      # left edge center
        tgt_point_y = tgt_rect.y + tgt_rect.cy // 2
        src_idx, tgt_idx = 1, 3   # right → left

    elif direction == "top_to_bottom":
        # Source bottom edge → Target top edge
        src_point_x = src_rect.x + src_rect.cx // 2  # bottom center
        src_point_y = src_rect.y + src_rect.cy
        tgt_point_x = tgt_rect.x + tgt_rect.cx // 2  # top center
        tgt_point_y = tgt_rect.y
        src_idx, tgt_idx = 2, 0   # bottom → top

    elif direction == "left_to_right":
        # Source left edge → Target right edge
        src_point_x = src_rect.x                       # left edge center
        src_point_y = src_rect.y + src_rect.cy // 2
        tgt_point_x = tgt_rect.x + tgt_rect.cx        # right edge center
        tgt_point_y = tgt_rect.y + tgt_rect.cy // 2
        src_idx, tgt_idx = 3, 1   # left → right

    elif direction == "bottom_to_top":
        # Source top edge → Target bottom edge
        src_point_x = src_rect.x + src_rect.cx // 2
        src_point_y = src_rect.y
        tgt_point_x = tgt_rect.x + tgt_rect.cx // 2
        tgt_point_y = tgt_rect.y + tgt_rect.cy
        src_idx, tgt_idx = 0, 2   # top → bottom

    else:
        raise ValueError(f"Unknown direction: {direction}")

    # Compute flip flags — target is "before" source in that axis
    flip_h = tgt_point_x < src_point_x
    flip_v = tgt_point_y < src_point_y

    # Bounding box: always positive dimensions
    x = min(src_point_x, tgt_point_x)
    y = min(src_point_y, tgt_point_y)
    cx = max(abs(tgt_point_x - src_point_x), 1)   # minimum 1 EMU
    cy = max(abs(tgt_point_y - src_point_y), 1)

    return Rect(x, y, cx, cy), flip_h, flip_v, src_idx, tgt_idx
```

---

## Text Estimation

### `estimate_font_size()`

```python
def estimate_font_size(text, shape_cx, shape_cy, min_size=800, max_size=1400):
    """
    Find the largest font size (in 100ths of pt) that fits text within shape.

    Uses Calibri character-width estimation. Returns font size in 100ths of pt.
    Falls back to min_size if text is too long.
    """
    if not text:
        return max_size

    # Usable width = shape width minus left/right insets (0.1" each = 182880 EMU total)
    usable_w = shape_cx - 182880
    # Usable height = shape height minus top/bottom insets (0.05" each = 91440 EMU total)
    usable_h = shape_cy - 91440

    for sz in range(max_size, min_size - 1, -100):  # step down by 1pt
        pts = sz / 100.0
        # Average character width at this font size
        char_w = CALIBRI_AVG_CHAR_W * pts / 100.0
        text_w = len(text) * char_w
        # Line height ~ 1.2 * font size in EMU
        line_h = pts * PT * 1.2

        if text_w <= usable_w and line_h <= usable_h:
            return sz

    return min_size


def text_fits(text, shape_cx, shape_cy, font_size):
    """Check if text fits within shape at given font size. Returns bool."""
    if not text:
        return True
    usable_w = shape_cx - 182880
    pts = font_size / 100.0
    char_w = CALIBRI_AVG_CHAR_W * pts / 100.0
    text_w = len(text) * char_w
    return text_w <= usable_w
```

---

## QC2: Layout Validation

### `validate_layout()`

Called after `compute_layout()`. Validates all computed positions, colors, and font sizes before rendering.

```python
def connection_point(rect, idx):
    """Get connection point coordinates for a shape rect and index."""
    if idx == 0: return (rect.x + rect.cx // 2, rect.y)            # top
    if idx == 1: return (rect.x + rect.cx, rect.y + rect.cy // 2)  # right
    if idx == 2: return (rect.x + rect.cx // 2, rect.y + rect.cy)  # bottom
    if idx == 3: return (rect.x, rect.y + rect.cy // 2)            # left


def validate_layout(layout):
    """
    QC2: Validate a computed layout before rendering. Returns list of warning strings.
    Raises ValueError on fatal errors.
    """
    warnings = []
    shape_by_id = {ps.shape_id: ps for ps in layout.placed_shapes}

    # Check text fits within every shape
    for ps in layout.placed_shapes:
        if ps.text and not text_fits(ps.text, ps.rect.cx, ps.rect.cy, ps.font_size):
            warnings.append(
                f"Text overflow: '{ps.text}' may not fit in shape {ps.key} "
                f"(cx={ps.rect.cx}, font_size={ps.font_size})"
            )
        if ps.text_line2 and not text_fits(ps.text_line2, ps.rect.cx, ps.rect.cy, ps.font_size2):
            warnings.append(
                f"Text overflow: '{ps.text_line2}' may not fit in shape {ps.key} "
                f"(cx={ps.rect.cx}, font_size2={ps.font_size2})"
            )

    # Check font sizes above minimum
    for ps in layout.placed_shapes:
        if ps.font_size < 800:
            warnings.append(f"Font too small: shape {ps.key} has font_size={ps.font_size} (min 800)")
        # Nonzero font size for non-empty text
        if ps.text.strip() and ps.font_size == 0:
            warnings.append(f"Zero font size for non-empty text: {ps.key}")

    # Check no shapes overlap (pairwise)
    for i, a in enumerate(layout.placed_shapes):
        for b in layout.placed_shapes[i+1:]:
            if rects_overlap(a.rect, b.rect):
                warnings.append(f"Shapes overlap: {a.key} and {b.key}")

    # Check all shapes within slide bounds
    for ps in layout.placed_shapes:
        r = ps.rect
        if r.x < 0 or r.y < 0 or r.x + r.cx > SLIDE_W or r.y + r.cy > SLIDE_H:
            warnings.append(f"Shape out of bounds: {ps.key} at ({r.x},{r.y})")

    # Check connector bounding boxes are non-degenerate
    for pc in layout.placed_connectors:
        if pc.rect.cx <= 0 or pc.rect.cy <= 0:
            warnings.append(
                f"Degenerate connector bbox: conn_id={pc.conn_id} "
                f"cx={pc.rect.cx} cy={pc.rect.cy}"
            )

    # Check connector source/target reference existing shapes
    shape_ids = {ps.shape_id for ps in layout.placed_shapes}
    for pc in layout.placed_connectors:
        if pc.src_shape_id not in shape_ids:
            raise ValueError(f"Connector {pc.conn_id} references non-existent source shape {pc.src_shape_id}")
        if pc.tgt_shape_id not in shape_ids:
            raise ValueError(f"Connector {pc.conn_id} references non-existent target shape {pc.tgt_shape_id}")

        # Endpoint alignment check (±1 EMU tolerance)
        src_shape = shape_by_id[pc.src_shape_id]
        tgt_shape = shape_by_id[pc.tgt_shape_id]
        sp = connection_point(src_shape.rect, pc.src_idx)
        tp = connection_point(tgt_shape.rect, pc.tgt_idx)
        exp_x = min(sp[0], tp[0])
        exp_y = min(sp[1], tp[1])
        exp_cx = max(abs(tp[0] - sp[0]), 1)
        exp_cy = max(abs(tp[1] - sp[1]), 1)
        if (abs(pc.rect.x - exp_x) > 1 or abs(pc.rect.y - exp_y) > 1 or
                abs(pc.rect.cx - exp_cx) > 1 or abs(pc.rect.cy - exp_cy) > 1):
            warnings.append(f"Connector {pc.conn_id} bbox misaligned with shape edges")

        # Flip flag consistency
        exp_flip_h = tp[0] < sp[0]
        exp_flip_v = tp[1] < sp[1]
        if pc.flip_h != exp_flip_h:
            warnings.append(f"Connector {pc.conn_id} flip_h mismatch: got {pc.flip_h}, expected {exp_flip_h}")
        if pc.flip_v != exp_flip_v:
            warnings.append(f"Connector {pc.conn_id} flip_v mismatch: got {pc.flip_v}, expected {exp_flip_v}")

    # Check no duplicate IDs
    all_ids = [ps.shape_id for ps in layout.placed_shapes]
    all_ids += [pc.conn_id for pc in layout.placed_connectors]
    all_ids += [pl.label_id for pl in layout.placed_labels]
    all_ids += [lb.lane_id for lb in layout.lane_bgs]
    if len(all_ids) != len(set(all_ids)):
        raise ValueError("Duplicate IDs detected in layout")

    return warnings


def rects_overlap(a, b):
    """Check if two Rects overlap. Returns bool."""
    return not (a.x + a.cx <= b.x or b.x + b.cx <= a.x or
                a.y + a.cy <= b.y or b.y + b.cy <= a.y)
```

| Check | Fatal? | Rationale |
|-------|--------|-----------|
| Text overflow | Warn | Text may not fit in shape |
| Font too small (<800) | Warn | Below minimum readable size |
| Nonzero font for non-empty text | Warn | estimate_font_size returned 0 |
| Shape overlap | Warn | Usually unintended |
| Shape out of bounds | Warn | Slides clip content |
| Degenerate connector bbox | Warn | Zero-size connector |
| Bad connector source/target | Raise | References non-existent shape |
| Connector endpoint alignment | Warn | Off-by-one positioning bugs |
| Flip flag consistency | Warn | Miscomputed flips |
| Duplicate IDs | Raise | PowerPoint corruption |

---

## Phase 4: Rendering

### `render()`

Emits XML elements in correct z-order:
1. Background (z=0)
2. Lane backgrounds (z=1)
3. Title (z=1.5)
4. **Connectors (z=2)** — below shapes, hiding overlap
5. **Shapes (z=3)** — above connectors
6. Labels (z=4)

```python
from pptx import Presentation
from pptx.util import Emu
from lxml import etree

def render(layout, output_path, auto_open=True):
    """Render a validated LayoutResult to a .pptx file."""
    prs = Presentation()
    prs.slide_width = Emu(SLIDE_W)
    prs.slide_height = Emu(SLIDE_H)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    spTree = slide.shapes._spTree

    # We need IDs for bg and title that don't collide
    # Collect all used IDs from layout
    used_ids = set()
    for ps in layout.placed_shapes: used_ids.add(ps.shape_id)
    for pc in layout.placed_connectors: used_ids.add(pc.conn_id)
    for pl in layout.placed_labels: used_ids.add(pl.label_id)
    for lb in layout.lane_bgs: used_ids.add(lb.lane_id)

    def fresh_id():
        i = max(used_ids) + 1 if used_ids else 2
        used_ids.add(i)
        return i

    # ── Z-layer 0: Background ────────────────────────────────────────────────
    if layout.bg_hex.startswith("gradient:"):
        _, start, end = layout.bg_hex.split(":")
        render_background_gradient(spTree, fresh_id(), start, end)
    else:
        render_background(spTree, fresh_id(), layout.bg_hex)

    # ── Z-layer 1: Lane backgrounds ──────────────────────────────────────────
    for lb in layout.lane_bgs:
        render_lane_bg(spTree, lb)

    # ── Title ────────────────────────────────────────────────────────────────
    if layout.title_style == "banner":
        render_title_banner(spTree, fresh_id(), layout.title, layout.title_rect)
    else:
        render_title_text(spTree, fresh_id(), layout.title, layout.title_rect)

    # ── Z-layer 2: Connectors (BELOW shapes) ────────────────────────────────
    for pc in layout.placed_connectors:
        render_connector(spTree, pc)

    # ── Z-layer 3: Shapes (ABOVE connectors) ────────────────────────────────
    for ps in layout.placed_shapes:
        render_shape(spTree, ps)

    # ── Z-layer 4: Labels (topmost) ─────────────────────────────────────────
    for pl in layout.placed_labels:
        render_label(spTree, pl)

    # ── Save ─────────────────────────────────────────────────────────────────
    import os, subprocess
    prs.save(output_path)
    print(f"Saved: {os.path.abspath(output_path)}")
    if auto_open:
        try:
            subprocess.run(["open", output_path], check=False)
        except FileNotFoundError:
            print(f"Open manually: open {output_path}")
```

### `render_shape()`

```python
def render_shape(spTree, ps):
    """Render a PlacedShape to XML and append to spTree."""
    r = ps.rect
    shadow_xml = ""
    if ps.shadow and ps.glow:
        shadow_xml = f'''
        <a:effectLst>
          <a:outerShdw blurRad="50800" dist="38100" dir="5400000" algn="tl" rotWithShape="0">
            <a:srgbClr val="000000"><a:alpha val="35000"/></a:srgbClr>
          </a:outerShdw>
          <a:glow rad="63500">
            <a:srgbClr val="{ps.fill_hex}"><a:alpha val="40000"/></a:srgbClr>
          </a:glow>
        </a:effectLst>'''
    elif ps.shadow:
        shadow_xml = '''
        <a:effectLst>
          <a:outerShdw blurRad="50800" dist="38100" dir="5400000" algn="tl" rotWithShape="0">
            <a:srgbClr val="000000"><a:alpha val="35000"/></a:srgbClr>
          </a:outerShdw>
        </a:effectLst>'''

    if ps.gradient:
        fill_xml = f'''
        <a:gradFill>
          <a:gsLst>
            <a:gs pos="0"><a:srgbClr val="{ps.fill_hex}"/></a:gs>
            <a:gs pos="100000">
              <a:srgbClr val="{ps.fill_hex}">
                <a:lumMod val="75000"/>
              </a:srgbClr>
            </a:gs>
          </a:gsLst>
          <a:lin ang="5400000" scaled="0"/>
        </a:gradFill>'''
    else:
        fill_xml = f'<a:solidFill><a:srgbClr val="{ps.fill_hex}"/></a:solidFill>'

    b = "1" if ps.bold else "0"

    # Second line of text (for org chart names/titles)
    line2_xml = ""
    if ps.text_line2:
        line2_xml = f'''
        <a:p>
          <a:pPr algn="ctr"/>
          <a:r>
            <a:rPr lang="en-US" sz="{ps.font_size2}" b="0" dirty="0">
              <a:solidFill><a:srgbClr val="{ps.text_color}">
                <a:alpha val="80000"/>
              </a:srgbClr></a:solidFill>
              <a:latin typeface="Calibri"/>
            </a:rPr>
            <a:t>{ps.text_line2}</a:t>
          </a:r>
        </a:p>'''

    xml_str = f'''
    <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
          xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
      <p:nvSpPr>
        <p:cNvPr id="{ps.shape_id}" name="{ps.key}"/>
        <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{r.x}" y="{r.y}"/><a:ext cx="{r.cx}" cy="{r.cy}"/></a:xfrm>
        <a:prstGeom prst="{ps.preset}"><a:avLst/></a:prstGeom>
        {fill_xml}
        <a:ln w="19050"><a:solidFill><a:srgbClr val="{ps.border_hex}"/></a:solidFill><a:round/></a:ln>
        {shadow_xml}
      </p:spPr>
      <p:txBody>
        <a:bodyPr wrap="square" anchor="ctr"><a:normAutofit/></a:bodyPr>
        <a:lstStyle/>
        <a:p>
          <a:pPr algn="ctr"/>
          <a:r>
            <a:rPr lang="en-US" sz="{ps.font_size}" b="{b}" dirty="0">
              <a:solidFill><a:srgbClr val="{ps.text_color}"/></a:solidFill>
              <a:latin typeface="Calibri"/>
            </a:rPr>
            <a:t>{ps.text}</a:t>
          </a:r>
        </a:p>
        {line2_xml}
      </p:txBody>
    </p:sp>'''
    spTree.append(etree.fromstring(xml_str.strip()))
```

### `render_connector()`

**Critical fix: OOXML element order inside `<a:ln>`**

The OOXML spec requires this order inside `<a:ln>`:
1. `<a:solidFill>` (or other fill)
2. `<a:prstDash>` — dash pattern BEFORE join
3. `<a:round/>` (or `<a:miter/>`) — join AFTER dash
4. `<a:headEnd>`
5. `<a:tailEnd>`

Previous code had `<a:round/>` before `<a:prstDash/>`, which caused PowerPoint to ignore the round join.

```python
def render_connector(spTree, pc):
    """Render a PlacedConnector to XML and append to spTree."""
    r = pc.rect

    # flipH/flipV attributes on xfrm
    flip_attrs = ""
    if pc.flip_h:
        flip_attrs += ' flipH="1"'
    if pc.flip_v:
        flip_attrs += ' flipV="1"'

    # Round join (softened elbows) — must come AFTER prstDash per OOXML spec
    round_xml = '<a:round/>' if pc.round_join else ''

    xml_str = f'''
    <p:cxnSp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
      <p:nvCxnSpPr>
        <p:cNvPr id="{pc.conn_id}" name="Conn {pc.conn_id}"/>
        <p:cNvCxnSpPr>
          <a:stCxn id="{pc.src_shape_id}" idx="{pc.src_idx}"/>
          <a:endCxn id="{pc.tgt_shape_id}" idx="{pc.tgt_idx}"/>
        </p:cNvCxnSpPr>
        <p:nvPr/>
      </p:nvCxnSpPr>
      <p:spPr>
        <a:xfrm{flip_attrs}><a:off x="{r.x}" y="{r.y}"/><a:ext cx="{r.cx}" cy="{r.cy}"/></a:xfrm>
        <a:prstGeom prst="{pc.connector_type}"><a:avLst/></a:prstGeom>
        <a:noFill/>
        <a:ln w="{pc.line_w}">
          <a:solidFill><a:srgbClr val="{pc.color_hex}"/></a:solidFill>
          <a:prstDash val="solid"/>
          {round_xml}
          <a:headEnd type="{pc.head_type}" w="med" len="med"/>
          <a:tailEnd type="{pc.tail_type}" w="med" len="med"/>
        </a:ln>
      </p:spPr>
    </p:cxnSp>'''
    spTree.append(etree.fromstring(xml_str.strip()))
```

### `render_background()`

```python
def render_background(spTree, shape_id, fill_hex):
    """Render solid-color full-slide background at z-bottom."""
    xml_str = f'''
    <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
          xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
      <p:nvSpPr>
        <p:cNvPr id="{shape_id}" name="Background"/>
        <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="0" y="0"/><a:ext cx="{SLIDE_W}" cy="{SLIDE_H}"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        <a:solidFill><a:srgbClr val="{fill_hex}"/></a:solidFill>
        <a:ln><a:noFill/></a:ln>
      </p:spPr>
      <p:txBody><a:bodyPr/><a:lstStyle/>
        <a:p><a:endParaRPr lang="en-US" dirty="0"/></a:p>
      </p:txBody>
    </p:sp>'''
    spTree.insert(2, etree.fromstring(xml_str.strip()))


def render_background_gradient(spTree, shape_id, start_hex, end_hex):
    """Render gradient full-slide background at z-bottom."""
    xml_str = f'''
    <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
          xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
      <p:nvSpPr>
        <p:cNvPr id="{shape_id}" name="Background"/>
        <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="0" y="0"/><a:ext cx="{SLIDE_W}" cy="{SLIDE_H}"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        <a:gradFill>
          <a:gsLst>
            <a:gs pos="0"><a:srgbClr val="{start_hex}"/></a:gs>
            <a:gs pos="100000"><a:srgbClr val="{end_hex}"/></a:gs>
          </a:gsLst>
          <a:lin ang="5400000" scaled="0"/>
        </a:gradFill>
        <a:ln><a:noFill/></a:ln>
      </p:spPr>
      <p:txBody><a:bodyPr/><a:lstStyle/>
        <a:p><a:endParaRPr lang="en-US" dirty="0"/></a:p>
      </p:txBody>
    </p:sp>'''
    spTree.insert(2, etree.fromstring(xml_str.strip()))
```

### `render_lane_bg()`

```python
def render_lane_bg(spTree, lb):
    """Render a lane background rectangle."""
    r = lb.rect
    xml_str = f'''
    <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
          xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
      <p:nvSpPr>
        <p:cNvPr id="{lb.lane_id}" name="Lane {lb.label}"/>
        <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{r.x}" y="{r.y}"/><a:ext cx="{r.cx}" cy="{r.cy}"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        <a:solidFill><a:srgbClr val="{lb.fill_hex}"/></a:solidFill>
        <a:ln w="12700"><a:solidFill><a:srgbClr val="{lb.border_hex}"/></a:solidFill></a:ln>
      </p:spPr>
      <p:txBody>
        <a:bodyPr wrap="square" anchor="t" lIns="91440" tIns="91440"><a:normAutofit/></a:bodyPr>
        <a:lstStyle/>
        <a:p>
          <a:pPr algn="l"/>
          <a:r>
            <a:rPr lang="en-US" sz="900" b="1" dirty="0">
              <a:solidFill><a:srgbClr val="888888"/></a:solidFill>
              <a:latin typeface="Calibri"/>
            </a:rPr>
            <a:t>{lb.label}</a:t>
          </a:r>
        </a:p>
      </p:txBody>
    </p:sp>'''
    spTree.append(etree.fromstring(xml_str.strip()))
```

### `render_title_banner()` and `render_title_text()`

```python
def render_title_banner(spTree, shape_id, title, rect):
    """Render title as a filled dark banner bar (architecture diagram style)."""
    r = rect
    xml_str = f'''
    <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
          xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
      <p:nvSpPr>
        <p:cNvPr id="{shape_id}" name="TitleBar"/>
        <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{r.x}" y="{r.y}"/><a:ext cx="{r.cx}" cy="{r.cy}"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        <a:solidFill><a:srgbClr val="1F3864"/></a:solidFill>
        <a:ln><a:noFill/></a:ln>
      </p:spPr>
      <p:txBody>
        <a:bodyPr wrap="square" anchor="ctr"><a:normAutofit/></a:bodyPr>
        <a:lstStyle/>
        <a:p>
          <a:pPr algn="ctr"/>
          <a:r>
            <a:rPr lang="en-US" sz="2200" b="1" dirty="0">
              <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
              <a:latin typeface="Calibri"/>
            </a:rPr>
            <a:t>{title}</a:t>
          </a:r>
        </a:p>
      </p:txBody>
    </p:sp>'''
    spTree.append(etree.fromstring(xml_str.strip()))


def render_title_text(spTree, shape_id, title, rect):
    """Render title as floating text (flowchart/org chart style)."""
    r = rect
    xml_str = f'''
    <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
          xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
      <p:nvSpPr>
        <p:cNvPr id="{shape_id}" name="Title"/>
        <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{r.x}" y="{r.y}"/><a:ext cx="{r.cx}" cy="{r.cy}"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        <a:noFill/><a:ln><a:noFill/></a:ln>
      </p:spPr>
      <p:txBody>
        <a:bodyPr wrap="square" anchor="ctr"><a:normAutofit/></a:bodyPr>
        <a:lstStyle/>
        <a:p>
          <a:pPr algn="ctr"/>
          <a:r>
            <a:rPr lang="en-US" sz="2400" b="1" dirty="0">
              <a:solidFill><a:srgbClr val="1F3864"/></a:solidFill>
              <a:latin typeface="Calibri"/>
            </a:rPr>
            <a:t>{title}</a:t>
          </a:r>
        </a:p>
      </p:txBody>
    </p:sp>'''
    spTree.append(etree.fromstring(xml_str.strip()))
```

### `render_label()`

```python
def render_label(spTree, pl):
    """Render a floating text label (e.g. 'YES' on a connector)."""
    r = pl.rect
    b = "1" if pl.bold else "0"
    xml_str = f'''
    <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
          xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
      <p:nvSpPr>
        <p:cNvPr id="{pl.label_id}" name="Label {pl.label_id}"/>
        <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{r.x}" y="{r.y}"/><a:ext cx="{r.cx}" cy="{r.cy}"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        <a:noFill/><a:ln><a:noFill/></a:ln>
      </p:spPr>
      <p:txBody>
        <a:bodyPr wrap="square" anchor="ctr"><a:normAutofit/></a:bodyPr>
        <a:lstStyle/>
        <a:p>
          <a:pPr algn="ctr"/>
          <a:r>
            <a:rPr lang="en-US" sz="{pl.font_size}" b="{b}" dirty="0">
              <a:solidFill><a:srgbClr val="{pl.color_hex}"/></a:solidFill>
              <a:latin typeface="Calibri"/>
            </a:rPr>
            <a:t>{pl.text}</a:t>
          </a:r>
        </a:p>
      </p:txBody>
    </p:sp>'''
    spTree.append(etree.fromstring(xml_str.strip()))
```

---

## QC3: Render Validation

### `validate_render()`

Called after `render_all()`, before save. Lightweight post-render verification of the actual XML tree.

```python
NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def validate_render(spTree, expected_count):
    """QC3: Post-render verification of the actual XML tree."""
    warnings = []

    children = list(spTree)
    content_children = [c for c in children if c.tag.endswith("}sp") or c.tag.endswith("}cxnSp")]
    actual = len(content_children)
    if actual != expected_count:
        warnings.append(f"Element count mismatch: expected {expected_count}, got {actual}")

    # All id attributes must be unique integers
    all_ids = []
    for elem in content_children:
        cNvPr = elem.find(".//{http://schemas.openxmlformats.org/presentationml/2006/main}cNvPr")
        if cNvPr is not None and "id" in cNvPr.attrib:
            all_ids.append(int(cNvPr.attrib["id"]))
    if len(all_ids) != len(set(all_ids)):
        raise ValueError(f"Duplicate IDs in rendered spTree: {all_ids}")

    # Z-order spot check: first shape element appears after last connector element
    last_connector_idx = -1
    first_shape_idx = len(content_children)
    for i, elem in enumerate(content_children):
        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        if tag == "cxnSp":
            last_connector_idx = i
        elif tag == "sp":
            cNvPr = elem.find(
                ".//{http://schemas.openxmlformats.org/presentationml/2006/main}cNvPr")
            name = cNvPr.attrib.get("name", "") if cNvPr is not None else ""
            if name not in ("Background", "Title", "TitleBar") and not name.startswith("Lane "):
                if i < first_shape_idx:
                    first_shape_idx = i

    if last_connector_idx >= 0 and first_shape_idx < len(content_children):
        if first_shape_idx < last_connector_idx:
            warnings.append("Z-order issue: shape rendered before last connector")

    # Every stCxn/endCxn id references an existing cNvPr id
    id_set = set(all_ids)
    for elem in content_children:
        for cxn_tag in ("stCxn", "endCxn"):
            cxn = elem.find(f".//{{{NS['a']}}}{cxn_tag}")
            if cxn is not None:
                ref_id = int(cxn.attrib.get("id", "0"))
                if ref_id not in id_set:
                    warnings.append(f"Orphaned {cxn_tag} references id={ref_id}")

    return warnings, actual
```

| Check | Fatal? | Rationale |
|-------|--------|-----------|
| spTree child count matches expected | Warn | Detects missing/extra elements |
| All id attributes are unique integers | Raise | PowerPoint corruption |
| Z-order: shapes after connectors | Warn | Ensures shapes render above connectors |
| stCxn/endCxn id references existing cNvPr id | Warn | Catches orphaned connector references |

---

## Quick Reference: Issue → Fix Mapping

| Issue | Root cause | Fix location |
|-------|-----------|-------------|
| Elbows not softened | `<a:round/>` before `<a:prstDash>` | `render_connector()` — dash BEFORE join |
| Shape corners sharp | Missing `<a:round/>` in shape `<a:ln>` | `render_shape()` — add `<a:round/>` after solidFill |
| Connectors misrouted | Missing `flipH`/`flipV` | `compute_connector_bbox()` → `render_connector()` |
| Lines overlap shapes | Connectors z-ordered above shapes | `render()` — connectors appended before shapes |
| Text overflow | No size validation | `estimate_font_size()` + `validate_layout()` |
| Bad definition data | No pre-compute validation | `validate_definition()` — QC1 |
| Corrupt XML tree | No post-render validation | `validate_render()` — QC3 |
