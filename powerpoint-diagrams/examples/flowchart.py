#!/usr/bin/env python3
"""
Flowchart — Layout-First Architecture Example
Creates a 5-step process flow: Start → Plan → Review? → Execute → Done

Architecture: Define → Compute → Validate → Render

Run:
    pip install python-pptx lxml
    python flowchart.py && open flowchart.pptx
"""

from dataclasses import dataclass
from pptx import Presentation
from pptx.util import Emu
from lxml import etree
import subprocess
import os

# ═════════════════════════════════════════════════════════════════════════════
# DATA MODEL
# ═════════════════════════════════════════════════════════════════════════════

@dataclass
class Rect:
    x: int; y: int; cx: int; cy: int

@dataclass
class PlacedShape:
    shape_id: int; key: str; text: str; preset: str; rect: Rect
    fill_hex: str; border_hex: str; text_color: str
    font_size: int; bold: bool; shadow: bool; z_layer: int

@dataclass
class PlacedConnector:
    conn_id: int; src_shape_id: int; src_idx: int
    tgt_shape_id: int; tgt_idx: int; rect: Rect
    flip_h: bool; flip_v: bool; color_hex: str; line_w: int
    connector_type: str; head_type: str; tail_type: str
    round_join: bool; z_layer: int

@dataclass
class PlacedLabel:
    label_id: int; text: str; rect: Rect
    color_hex: str; font_size: int; bold: bool; z_layer: int

# ═════════════════════════════════════════════════════════════════════════════
# PHASE 1: DEFINE — Pure data, no coordinates, no XML
# ═════════════════════════════════════════════════════════════════════════════

TITLE = "Figure 1: Project Execution Process"

SHAPES = [
    {"id": "start",   "text": "START",   "preset": "flowChartTerminator", "style": "dark"},
    {"id": "plan",    "text": "PLAN",    "preset": "flowChartProcess",    "style": "primary"},
    {"id": "review",  "text": "REVIEW?", "preset": "flowChartDecision",   "style": "accent"},
    {"id": "execute", "text": "EXECUTE", "preset": "flowChartProcess",    "style": "primary"},
    {"id": "done",    "text": "DONE",    "preset": "flowChartTerminator", "style": "dark"},
]

CONNECTIONS = [
    {"src": "start",  "tgt": "plan"},
    {"src": "plan",   "tgt": "review"},
    {"src": "review", "tgt": "execute", "label": "YES"},
    {"src": "execute","tgt": "done"},
]

PALETTE = {
    "bg":        "EEF2FA",
    "dark":      ("1F3864", "16294A"),
    "primary":   ("4472C4", "2E4FA3"),
    "accent":    ("ED7D31", "C05C13"),
    "connector": "4472C4",
    "title":     "1F3864",
}

# ═════════════════════════════════════════════════════════════════════════════
# QC1: VALIDATE DEFINITION — Catch bad input before any math
# ═════════════════════════════════════════════════════════════════════════════

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


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 2: COMPUTE — Pure math, no XML
# ═════════════════════════════════════════════════════════════════════════════

SLIDE_W, SLIDE_H = 9144000, 5143500
IN = 914400
CALIBRI_AVG_CHAR_W = 45000  # average char width at 100pt
PT = 12700


def estimate_font_size(text, cx, cy, min_size=800, max_size=1400):
    if not text:
        return max_size
    usable_w = cx - 182880
    usable_h = cy - 91440
    for sz in range(max_size, min_size - 1, -100):
        pts = sz / 100.0
        char_w = CALIBRI_AVG_CHAR_W * pts / 100.0
        text_w = len(text) * char_w
        line_h = pts * PT * 1.2
        if text_w <= usable_w and line_h <= usable_h:
            return sz
    return min_size


def text_fits(text, cx, font_size):
    if not text:
        return True
    usable_w = cx - 182880
    pts = font_size / 100.0
    char_w = CALIBRI_AVG_CHAR_W * pts / 100.0
    return len(text) * char_w <= usable_w


def compute_connector_bbox(src_rect, tgt_rect, direction):
    if direction == "right_to_left":
        sp_x = src_rect.x + src_rect.cx
        sp_y = src_rect.y + src_rect.cy // 2
        tp_x = tgt_rect.x
        tp_y = tgt_rect.y + tgt_rect.cy // 2
        src_idx, tgt_idx = 1, 3
    elif direction == "top_to_bottom":
        sp_x = src_rect.x + src_rect.cx // 2
        sp_y = src_rect.y + src_rect.cy
        tp_x = tgt_rect.x + tgt_rect.cx // 2
        tp_y = tgt_rect.y
        src_idx, tgt_idx = 2, 0
    else:
        raise ValueError(f"Unknown direction: {direction}")

    flip_h = tp_x < sp_x
    flip_v = tp_y < sp_y
    x = min(sp_x, tp_x)
    y = min(sp_y, tp_y)
    cx = max(abs(tp_x - sp_x), 1)
    cy = max(abs(tp_y - sp_y), 1)
    return Rect(x, y, cx, cy), flip_h, flip_v, src_idx, tgt_idx


def compute_layout():
    """Compute all positions, colors, font sizes — returns placed elements."""
    _id = [2]
    def nid():
        v = _id[0]; _id[0] += 1; return v

    # Shape dimensions by preset
    DIMS = {
        "flowChartProcess":    (1371600, 685800),
        "flowChartDecision":   (1371600, 914400),
        "flowChartTerminator": (1371600, 571500),
    }
    GAP = 228600
    n = len(SHAPES)
    sw = 1371600
    total_w = n * sw + (n - 1) * GAP
    left = (SLIDE_W - total_w) // 2
    base_cy = 685800
    base_y = (SLIDE_H - base_cy) // 2
    xs = [left + i * (sw + GAP) for i in range(n)]

    # Title
    title_id = nid()
    title_rect = Rect(457200, 228600, 8229600, 457200)
    bg_id = nid()

    # Place shapes
    placed_shapes = []
    shape_map = {}
    for i, s in enumerate(SHAPES):
        sid = nid()
        cx, cy = DIMS[s["preset"]]
        y = base_y + (base_cy - cy) // 2
        fill, border = PALETTE[s["style"]]
        font_size = estimate_font_size(s["text"], cx, cy)
        ps = PlacedShape(
            shape_id=sid, key=s["id"], text=s["text"], preset=s["preset"],
            rect=Rect(xs[i], y, cx, cy),
            fill_hex=fill, border_hex=border, text_color="FFFFFF",
            font_size=font_size, bold=True, shadow=True, z_layer=3,
        )
        placed_shapes.append(ps)
        shape_map[s["id"]] = ps

    # Place connectors
    placed_connectors = []
    for conn in CONNECTIONS:
        src = shape_map[conn["src"]]
        tgt = shape_map[conn["tgt"]]
        cid = nid()
        bbox, fh, fv, si, ti = compute_connector_bbox(src.rect, tgt.rect, "right_to_left")
        placed_connectors.append(PlacedConnector(
            conn_id=cid,
            src_shape_id=src.shape_id, src_idx=si,
            tgt_shape_id=tgt.shape_id, tgt_idx=ti,
            rect=bbox, flip_h=fh, flip_v=fv,
            color_hex=PALETTE["connector"], line_w=25400,
            connector_type="bentConnector3",
            head_type="none", tail_type="triangle",
            round_join=True, z_layer=2,
        ))

    # Place labels
    placed_labels = []
    for conn in CONNECTIONS:
        if conn.get("label"):
            src = shape_map[conn["src"]]
            lid = nid()
            lx = src.rect.x + src.rect.cx + GAP // 4
            ly = base_y + base_cy // 2 - 342900
            placed_labels.append(PlacedLabel(
                label_id=lid, text=conn["label"],
                rect=Rect(lx, ly, 228600, 228600),
                color_hex="27AE60", font_size=1000, bold=True, z_layer=4,
            ))

    return bg_id, title_id, title_rect, placed_shapes, placed_connectors, placed_labels


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 3: VALIDATE — Check before any XML
# ═════════════════════════════════════════════════════════════════════════════

def rects_overlap(a, b):
    return not (a.x + a.cx <= b.x or b.x + b.cx <= a.x or
                a.y + a.cy <= b.y or b.y + b.cy <= a.y)


def connection_point(rect, idx):
    """Get connection point coordinates for a shape rect and index."""
    if idx == 0: return (rect.x + rect.cx // 2, rect.y)            # top
    if idx == 1: return (rect.x + rect.cx, rect.y + rect.cy // 2)  # right
    if idx == 2: return (rect.x + rect.cx // 2, rect.y + rect.cy)  # bottom
    if idx == 3: return (rect.x, rect.y + rect.cy // 2)            # left


def validate(placed_shapes, placed_connectors, placed_labels):
    """QC2: Validate computed layout before rendering."""
    warnings = []
    shape_by_id = {ps.shape_id: ps for ps in placed_shapes}

    for ps in placed_shapes:
        if not text_fits(ps.text, ps.rect.cx, ps.font_size):
            warnings.append(f"Text overflow: '{ps.text}' in {ps.key}")
        if ps.font_size < 800:
            warnings.append(f"Font too small: {ps.key} sz={ps.font_size}")
        # Nonzero font size for non-empty text
        if ps.text.strip() and ps.font_size == 0:
            warnings.append(f"Zero font size for non-empty text: {ps.key}")

    for i, a in enumerate(placed_shapes):
        for b in placed_shapes[i+1:]:
            if rects_overlap(a.rect, b.rect):
                warnings.append(f"Shapes overlap: {a.key} and {b.key}")
    for ps in placed_shapes:
        r = ps.rect
        if r.x < 0 or r.y < 0 or r.x + r.cx > SLIDE_W or r.y + r.cy > SLIDE_H:
            warnings.append(f"Out of bounds: {ps.key}")
    for pc in placed_connectors:
        if pc.rect.cx <= 0 or pc.rect.cy <= 0:
            warnings.append(f"Degenerate connector: id={pc.conn_id}")

    shape_ids = {ps.shape_id for ps in placed_shapes}
    for pc in placed_connectors:
        if pc.src_shape_id not in shape_ids:
            raise ValueError(f"Connector {pc.conn_id} bad source {pc.src_shape_id}")
        if pc.tgt_shape_id not in shape_ids:
            raise ValueError(f"Connector {pc.conn_id} bad target {pc.tgt_shape_id}")

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
            warnings.append(f"Connector {pc.conn_id} flip_h={pc.flip_h} but geometry expects {exp_flip_h}")
        if pc.flip_v != exp_flip_v:
            warnings.append(f"Connector {pc.conn_id} flip_v={pc.flip_v} but geometry expects {exp_flip_v}")

    all_ids = ([ps.shape_id for ps in placed_shapes] +
               [pc.conn_id for pc in placed_connectors] +
               [pl.label_id for pl in placed_labels])
    if len(all_ids) != len(set(all_ids)):
        raise ValueError("Duplicate IDs detected")

    return warnings


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 4: RENDER — Validated layout → OOXML
# ═════════════════════════════════════════════════════════════════════════════

def render_shape(spTree, ps):
    r = ps.rect
    shadow_xml = ""
    if ps.shadow:
        shadow_xml = '''
        <a:effectLst>
          <a:outerShdw blurRad="50800" dist="38100" dir="5400000" algn="tl" rotWithShape="0">
            <a:srgbClr val="000000"><a:alpha val="35000"/></a:srgbClr>
          </a:outerShdw>
        </a:effectLst>'''
    b = "1" if ps.bold else "0"
    xml = f'''
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
        <a:solidFill><a:srgbClr val="{ps.fill_hex}"/></a:solidFill>
        <a:ln w="22225"><a:solidFill><a:srgbClr val="{ps.border_hex}"/></a:solidFill><a:round/></a:ln>
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
      </p:txBody>
    </p:sp>'''
    spTree.append(etree.fromstring(xml.strip()))


def render_connector(spTree, pc):
    r = pc.rect
    flip_attrs = ""
    if pc.flip_h:
        flip_attrs += ' flipH="1"'
    if pc.flip_v:
        flip_attrs += ' flipV="1"'
    round_xml = '<a:round/>' if pc.round_join else ''

    xml = f'''
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
    spTree.append(etree.fromstring(xml.strip()))


def render_label(spTree, pl):
    r = pl.rect
    b = "1" if pl.bold else "0"
    xml = f'''
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
    spTree.append(etree.fromstring(xml.strip()))


def render_all(bg_id, title_id, title_rect, placed_shapes, placed_connectors, placed_labels):
    prs = Presentation()
    prs.slide_width = Emu(SLIDE_W)
    prs.slide_height = Emu(SLIDE_H)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    spTree = slide.shapes._spTree

    # Z-layer 0: Background
    bg_xml = f'''
    <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
          xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
      <p:nvSpPr>
        <p:cNvPr id="{bg_id}" name="Background"/>
        <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="0" y="0"/><a:ext cx="{SLIDE_W}" cy="{SLIDE_H}"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        <a:solidFill><a:srgbClr val="{PALETTE['bg']}"/></a:solidFill>
        <a:ln><a:noFill/></a:ln>
      </p:spPr>
      <p:txBody><a:bodyPr/><a:lstStyle/>
        <a:p><a:endParaRPr lang="en-US" dirty="0"/></a:p>
      </p:txBody>
    </p:sp>'''
    spTree.insert(2, etree.fromstring(bg_xml.strip()))

    # Title
    tr = title_rect
    title_xml = f'''
    <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
          xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
      <p:nvSpPr>
        <p:cNvPr id="{title_id}" name="Title"/>
        <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{tr.x}" y="{tr.y}"/><a:ext cx="{tr.cx}" cy="{tr.cy}"/></a:xfrm>
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
              <a:solidFill><a:srgbClr val="{PALETTE['title']}"/></a:solidFill>
              <a:latin typeface="Calibri"/>
            </a:rPr>
            <a:t>{TITLE}</a:t>
          </a:r>
        </a:p>
      </p:txBody>
    </p:sp>'''
    spTree.append(etree.fromstring(title_xml.strip()))

    # Z-layer 2: Connectors (BELOW shapes)
    for pc in placed_connectors:
        render_connector(spTree, pc)

    # Z-layer 3: Shapes (ABOVE connectors)
    for ps in placed_shapes:
        render_shape(spTree, ps)

    # Z-layer 4: Labels
    for pl in placed_labels:
        render_label(spTree, pl)

    return prs


# ═════════════════════════════════════════════════════════════════════════════
# QC3: VALIDATE RENDER — Post-render XML tree verification
# ═════════════════════════════════════════════════════════════════════════════

NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def validate_render(spTree, expected_count):
    """QC3: Post-render verification of the actual XML tree."""
    warnings = []

    # Count spTree children (skip the 2 default pptx elements: cNvGrpSpPr, grpSpPr)
    children = list(spTree)
    content_children = [c for c in children if c.tag.endswith("}sp") or c.tag.endswith("}cxnSp")]
    actual = len(content_children)
    if actual != expected_count:
        warnings.append(f"Element count mismatch: expected {expected_count}, got {actual}")

    # All id attributes must be unique integers
    all_ids = []
    for elem in content_children:
        cNvPr = elem.find(".//" + "{http://schemas.openxmlformats.org/presentationml/2006/main}cNvPr")
        if cNvPr is None:
            # Try inside nvCxnSpPr
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
            # Skip background, title, lane elements by checking z-order heuristic
            cNvPr = elem.find(".//{http://schemas.openxmlformats.org/presentationml/2006/main}cNvPr")
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


# ═════════════════════════════════════════════════════════════════════════════
# MAIN — Run all phases with QC at each checkpoint
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Phase 1: Define
    print(f"Phase 1: Define — {len(SHAPES)} shapes, {len(CONNECTIONS)} connections")
    qc1 = validate_definition(SHAPES, CONNECTIONS)
    if qc1:
        for w in qc1:
            print(f"  QC1 WARNING: {w}")
    else:
        print("  QC1: Definition validated — no issues.")

    # Phase 2: Compute
    bg_id, title_id, title_rect, shapes, connectors, labels = compute_layout()
    print(f"Phase 2: Compute — placed {len(shapes)} shapes, {len(connectors)} connectors")
    qc2 = validate(shapes, connectors, labels)
    if qc2:
        for w in qc2:
            print(f"  QC2 WARNING: {w}")
    else:
        print("  QC2: Layout validated — no warnings.")

    # Phase 3: Render
    print("Phase 3: Render — emit OOXML")
    prs = render_all(bg_id, title_id, title_rect, shapes, connectors, labels)
    spTree = prs.slides[0].shapes._spTree
    expected = 1 + 1 + len(connectors) + len(shapes) + len(labels)  # bg + title + connectors + shapes + labels
    qc3, actual = validate_render(spTree, expected)
    if qc3:
        for w in qc3:
            print(f"  QC3 WARNING: {w}")
    else:
        print(f"  QC3: Render validated — {actual} elements, all IDs unique, z-order correct.")

    output = "flowchart.pptx"
    prs.save(output)
    print(f"Saved: {os.path.abspath(output)}")

    try:
        subprocess.run(["open", output], check=False)
    except FileNotFoundError:
        print("Open manually: open flowchart.pptx")
