#!/usr/bin/env python3
"""
Org Chart — Layout-First Architecture Example
Creates a 3-level hierarchy: 1 CEO → 3 VPs → 6 Team Leads

Architecture: Define → Compute → Validate → Render

Run:
    pip install python-pptx lxml
    python org_chart.py && open org_chart.pptx
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
    shape_id: int; key: str; text: str; text_line2: str; preset: str; rect: Rect
    fill_hex: str; border_hex: str; text_color: str
    font_size: int; font_size2: int; bold: bool; shadow: bool
    gradient: bool; z_layer: int

@dataclass
class PlacedConnector:
    conn_id: int; src_shape_id: int; src_idx: int
    tgt_shape_id: int; tgt_idx: int; rect: Rect
    flip_h: bool; flip_v: bool; color_hex: str; line_w: int
    connector_type: str; head_type: str; tail_type: str
    round_join: bool; z_layer: int

# ═════════════════════════════════════════════════════════════════════════════
# PHASE 1: DEFINE — Pure data, no coordinates, no XML
# ═════════════════════════════════════════════════════════════════════════════

TITLE = "Figure 2: Organization Chart"

# Each shape: id, name (line1), title (line2), group=level
SHAPES = [
    {"id": "ceo",  "name": "Jane Smith",    "title": "Chief Executive Officer", "group": "0"},
    {"id": "vp1",  "name": "Alex Johnson",  "title": "VP Engineering",          "group": "1"},
    {"id": "vp2",  "name": "Maria Garcia",  "title": "VP Marketing",            "group": "1"},
    {"id": "vp3",  "name": "David Chen",    "title": "VP Operations",           "group": "1"},
    {"id": "l1",   "name": "Sam Lee",       "title": "Frontend Lead",           "group": "2"},
    {"id": "l2",   "name": "Priya Patel",   "title": "Backend Lead",            "group": "2"},
    {"id": "l3",   "name": "Tom Brown",     "title": "Content Lead",            "group": "2"},
    {"id": "l4",   "name": "Ana Silva",     "title": "Growth Lead",             "group": "2"},
    {"id": "l5",   "name": "Kevin Park",    "title": "DevOps Lead",             "group": "2"},
    {"id": "l6",   "name": "Lisa Wong",     "title": "Support Lead",            "group": "2"},
]

CONNECTIONS = [
    {"src": "ceo", "tgt": "vp1"},
    {"src": "ceo", "tgt": "vp2"},
    {"src": "ceo", "tgt": "vp3"},
    {"src": "vp1", "tgt": "l1"},
    {"src": "vp1", "tgt": "l2"},
    {"src": "vp2", "tgt": "l3"},
    {"src": "vp2", "tgt": "l4"},
    {"src": "vp3", "tgt": "l5"},
    {"src": "vp3", "tgt": "l6"},
]

LEVEL_COLORS = {
    "0": ("1F3864", "16294A"),  # dark navy — CEO
    "1": ("4472C4", "2E4FA3"),  # blue — VPs
    "2": ("70AD47", "507C32"),  # green — leads
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
        if conn["src"] not in id_set:
            raise ValueError(f"Connection source '{conn['src']}' not found in shapes")
        if conn["tgt"] not in id_set:
            raise ValueError(f"Connection target '{conn['tgt']}' not found in shapes")
        if conn["src"] == conn["tgt"]:
            warnings.append(f"Self-loop: '{conn['src']}' connects to itself")

    for s in shapes:
        # Empty text — warn (org chart uses "name" field)
        if not s.get("name", "").strip():
            warnings.append(f"Empty name: shape '{s['id']}'")
        # Preset check (org chart uses roundRect by default, but check if overridden)
        preset = s.get("preset", "")
        if preset and preset not in VALID_PRESETS:
            warnings.append(f"Unknown preset '{preset}' on shape '{s['id']}'")

    return warnings


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 2: COMPUTE — Pure math, no XML
# ═════════════════════════════════════════════════════════════════════════════

SLIDE_W, SLIDE_H = 9144000, 5143500
SH = 571500                  # shape height: 0.625"
V_GAP = 685800               # 0.75"
MARGIN_TOP = 685800
CALIBRI_AVG_CHAR_W = 45000
PT = 12700
SLIDE_MARGIN = 228600        # 0.25" margin on each side

# Shape widths per level — wider for fewer shapes, narrower for many
LEVEL_SW = {
    "0": 1600200,  # 1.75" — CEO (1 shape, plenty of room)
    "1": 1600200,  # 1.75" — VPs (3 shapes fit fine)
    "2": 1280160,  # 1.4"  — Leads (6 shapes must fit in 10" slide)
}
LEVEL_GAP = {
    "0": 304800,
    "1": 304800,
    "2": 182880,   # tighter gap for 6 shapes
}


def estimate_font_size(text, cx, cy, min_size=800, max_size=1100):
    if not text:
        return max_size
    usable_w = cx - 182880
    for sz in range(max_size, min_size - 1, -100):
        pts = sz / 100.0
        char_w = CALIBRI_AVG_CHAR_W * pts / 100.0
        text_w = len(text) * char_w
        line_h = pts * PT * 1.2
        if text_w <= usable_w and line_h <= cy - 91440:
            return sz
    return min_size


def text_fits(text, cx, font_size):
    if not text:
        return True
    usable_w = cx - 182880
    pts = font_size / 100.0
    char_w = CALIBRI_AVG_CHAR_W * pts / 100.0
    return len(text) * char_w <= usable_w


def center_row(n, sw, gap):
    total = n * sw + (n - 1) * gap
    left = (SLIDE_W - total) // 2
    return [left + i * (sw + gap) for i in range(n)]


def compute_connector_bbox(src_rect, tgt_rect):
    """Parent bottom → child top, with flip support."""
    sp_x = src_rect.x + src_rect.cx // 2
    sp_y = src_rect.y + src_rect.cy
    tp_x = tgt_rect.x + tgt_rect.cx // 2
    tp_y = tgt_rect.y

    flip_h = tp_x < sp_x
    flip_v = tp_y < sp_y

    x = min(sp_x, tp_x)
    y = min(sp_y, tp_y)
    cx = max(abs(tp_x - sp_x), 1)
    cy = max(abs(tp_y - sp_y), 1)
    return Rect(x, y, cx, cy), flip_h, flip_v


def compute_layout():
    _id = [2]
    def nid():
        v = _id[0]; _id[0] += 1; return v

    bg_id = nid()
    title_id = nid()
    title_rect = Rect(457200, 152400, 8229600, 400050)

    # Group shapes by level
    levels = {}
    for s in SHAPES:
        levels.setdefault(s["group"], []).append(s)
    sorted_levels = sorted(levels.keys())

    # Place shapes
    placed_shapes = []
    shape_map = {}

    for lvl_idx, lvl_key in enumerate(sorted_levels):
        shapes = levels[lvl_key]
        sw = LEVEL_SW.get(lvl_key, 1371600)
        gap = LEVEL_GAP.get(lvl_key, 304800)
        xs = center_row(len(shapes), sw, gap)
        y = MARGIN_TOP + lvl_idx * (SH + V_GAP)
        fill, border = LEVEL_COLORS[lvl_key]

        for i, s in enumerate(shapes):
            sid = nid()
            # Use the longer of name/title to determine font size
            longest = max(s["name"], s["title"], key=len)
            font_size = estimate_font_size(longest, sw, SH)
            font_size2 = max(font_size - 200, 800)

            ps = PlacedShape(
                shape_id=sid, key=s["id"],
                text=s["name"], text_line2=s["title"],
                preset="roundRect",
                rect=Rect(xs[i], y, sw, SH),
                fill_hex=fill, border_hex=border, text_color="FFFFFF",
                font_size=font_size, font_size2=font_size2, bold=True,
                shadow=True, gradient=True, z_layer=3,
            )
            placed_shapes.append(ps)
            shape_map[s["id"]] = ps

    # Place connectors
    placed_connectors = []
    for conn in CONNECTIONS:
        src = shape_map[conn["src"]]
        tgt = shape_map[conn["tgt"]]
        cid = nid()
        bbox, flip_h, flip_v = compute_connector_bbox(src.rect, tgt.rect)
        placed_connectors.append(PlacedConnector(
            conn_id=cid,
            src_shape_id=src.shape_id, src_idx=2,
            tgt_shape_id=tgt.shape_id, tgt_idx=0,
            rect=bbox, flip_h=flip_h, flip_v=flip_v,
            color_hex="AAAAAA", line_w=19050,
            connector_type="bentConnector3",
            head_type="none", tail_type="triangle",
            round_join=True, z_layer=2,
        ))

    return bg_id, title_id, title_rect, placed_shapes, placed_connectors


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 3: VALIDATE
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


def validate(placed_shapes, placed_connectors):
    """QC2: Validate computed layout before rendering."""
    warnings = []
    shape_by_id = {ps.shape_id: ps for ps in placed_shapes}

    for ps in placed_shapes:
        if not text_fits(ps.text, ps.rect.cx, ps.font_size):
            warnings.append(f"Text overflow: '{ps.text}' in {ps.key}")
        if ps.text_line2 and not text_fits(ps.text_line2, ps.rect.cx, ps.font_size2):
            warnings.append(f"Text overflow: '{ps.text_line2}' in {ps.key}")
        if ps.font_size < 800:
            warnings.append(f"Font too small: {ps.key} sz={ps.font_size}")
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
            raise ValueError(f"Connector {pc.conn_id} bad source")
        if pc.tgt_shape_id not in shape_ids:
            raise ValueError(f"Connector {pc.conn_id} bad target")

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

    # Duplicate IDs — fatal
    all_ids = ([ps.shape_id for ps in placed_shapes] +
               [pc.conn_id for pc in placed_connectors])
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
          <a:outerShdw blurRad="38100" dist="25400" dir="5400000" algn="tl" rotWithShape="0">
            <a:srgbClr val="000000"><a:alpha val="30000"/></a:srgbClr>
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
            <a:rPr lang="en-US" sz="{ps.font_size}" b="1" dirty="0">
              <a:solidFill><a:srgbClr val="{ps.text_color}"/></a:solidFill>
              <a:latin typeface="Calibri"/>
            </a:rPr>
            <a:t>{ps.text}</a:t>
          </a:r>
        </a:p>
        {line2_xml}
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
          <a:headEnd type="{pc.head_type}"/>
          <a:tailEnd type="{pc.tail_type}" w="sm" len="sm"/>
        </a:ln>
      </p:spPr>
    </p:cxnSp>'''
    spTree.append(etree.fromstring(xml.strip()))


def render_all(bg_id, title_id, title_rect, placed_shapes, placed_connectors):
    prs = Presentation()
    prs.slide_width = Emu(SLIDE_W)
    prs.slide_height = Emu(SLIDE_H)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    spTree = slide.shapes._spTree

    # Z-layer 0: Background (gradient)
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
        <a:gradFill>
          <a:gsLst>
            <a:gs pos="0"><a:srgbClr val="F8FAFF"/></a:gs>
            <a:gs pos="100000"><a:srgbClr val="EEF2FA"/></a:gs>
          </a:gsLst>
          <a:lin ang="5400000" scaled="0"/>
        </a:gradFill>
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
            <a:rPr lang="en-US" sz="2200" b="1" dirty="0">
              <a:solidFill><a:srgbClr val="1F3864"/></a:solidFill>
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

    return prs


# ═════════════════════════════════════════════════════════════════════════════
# QC3: VALIDATE RENDER — Post-render XML tree verification
# ═════════════════════════════════════════════════════════════════════════════

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
    bg_id, title_id, title_rect, shapes, connectors = compute_layout()
    print(f"Phase 2: Compute — placed {len(shapes)} shapes, {len(connectors)} connectors")
    qc2 = validate(shapes, connectors)
    if qc2:
        for w in qc2:
            print(f"  QC2 WARNING: {w}")
    else:
        print("  QC2: Layout validated — no warnings.")

    # Phase 3: Render
    print("Phase 3: Render — emit OOXML")
    prs = render_all(bg_id, title_id, title_rect, shapes, connectors)
    spTree = prs.slides[0].shapes._spTree
    expected = 1 + 1 + len(connectors) + len(shapes)  # bg + title + connectors + shapes
    qc3, actual = validate_render(spTree, expected)
    if qc3:
        for w in qc3:
            print(f"  QC3 WARNING: {w}")
    else:
        print(f"  QC3: Render validated — {actual} elements, all IDs unique, z-order correct.")

    output = "org_chart.pptx"
    prs.save(output)
    print(f"Saved: {os.path.abspath(output)}")

    try:
        subprocess.run(["open", output], check=False)
    except FileNotFoundError:
        print("Open manually: open org_chart.pptx")
