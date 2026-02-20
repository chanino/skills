# python-pptx API Patterns

> **Preferred approach:** Use `layout-engine.md` for new diagrams. It provides the layout-first architecture (define → compute → validate → render) with dataclasses, connector math with `flipH`/`flipV`, text estimation, and validation. The patterns below are low-level building blocks — use them as reference when extending the layout engine.

---

## Imports and Presentation Setup

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from lxml import etree
import copy

# Namespaces — always use these constants
nsmap = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}

def qn(tag):
    """Qualify a tag name with its namespace. E.g. qn('p:sp') -> '{...}sp'"""
    prefix, local = tag.split(':')
    return f'{{{nsmap[prefix]}}}{local}'

# Create presentation
prs = Presentation()
prs.slide_width = Emu(9144000)   # 10 inches (widescreen)
prs.slide_height = Emu(5143500)  # 5.625 inches

# Add blank slide
blank_layout = prs.slide_layouts[6]  # index 6 = blank
slide = prs.slides.add_slide(blank_layout)
spTree = slide.shapes._spTree

# Shape ID counter (start at 2; ID 1 reserved for slide background)
shape_id_counter = [2]

def next_id():
    id_ = shape_id_counter[0]
    shape_id_counter[0] += 1
    return id_
```

---

## `add_shape_xml()` — Add Any Preset Geometry Shape

```python
def add_shape_xml(spTree, shape_id, name, preset, x, y, cx, cy,
                  fill_hex="4472C4", line_hex="2E4FA3", line_w=25400,
                  text="", font_size=1400, bold=True, text_color="FFFFFF",
                  shadow=False):
    """
    Add a preset geometry shape via XML injection.

    Args:
        spTree: slide.shapes._spTree
        shape_id: unique int per slide (use next_id())
        name: display name string
        preset: OOXML preset geometry name (e.g. 'flowChartProcess')
        x, y: position in EMU
        cx, cy: size in EMU
        fill_hex: fill color hex string (no #)
        line_hex: border color hex string (no #)
        line_w: border width in EMU (25400 = 2pt)
        text: label text
        font_size: in 100ths of pt (1400 = 14pt)
        bold: True/False
        text_color: hex string
        shadow: True to add outer drop shadow
    """
    shadow_xml = ""
    if shadow:
        shadow_xml = '''
        <a:effectLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <a:outerShdw blurRad="50800" dist="38100" dir="5400000" algn="tl" rotWithShape="0">
            <a:srgbClr val="000000"><a:alpha val="40000"/></a:srgbClr>
          </a:outerShdw>
        </a:effectLst>'''

    bold_attr = "1" if bold else "0"
    xml_str = f'''
    <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
          xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
      <p:nvSpPr>
        <p:cNvPr id="{shape_id}" name="{name}"/>
        <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm>
          <a:off x="{x}" y="{y}"/>
          <a:ext cx="{cx}" cy="{cy}"/>
        </a:xfrm>
        <a:prstGeom prst="{preset}"><a:avLst/></a:prstGeom>
        <a:solidFill><a:srgbClr val="{fill_hex}"/></a:solidFill>
        <a:ln w="{line_w}">
          <a:solidFill><a:srgbClr val="{line_hex}"/></a:solidFill>
        </a:ln>
        {shadow_xml}
      </p:spPr>
      <p:txBody>
        <a:bodyPr wrap="square" anchor="ctr"><a:normAutofit/></a:bodyPr>
        <a:lstStyle/>
        <a:p>
          <a:pPr algn="ctr"/>
          <a:r>
            <a:rPr lang="en-US" sz="{font_size}" b="{bold_attr}" dirty="0">
              <a:solidFill><a:srgbClr val="{text_color}"/></a:solidFill>
              <a:latin typeface="Calibri"/>
            </a:rPr>
            <a:t>{text}</a:t>
          </a:r>
        </a:p>
      </p:txBody>
    </p:sp>'''
    elem = etree.fromstring(xml_str.strip())
    spTree.append(elem)
    return elem
```

---

## `set_shape_text()` — Update Text on an Existing Shape Element

```python
def set_shape_text(sp_elem, text, font_size=1400, bold=True,
                   text_color="FFFFFF", align="ctr"):
    """Replace text in a shape XML element."""
    a_ns = 'http://schemas.openxmlformats.org/drawingml/2006/main'

    # Remove existing txBody paragraphs
    txBody = sp_elem.find(f'{{{a_ns[0]}}}txBody') or \
             sp_elem.find('.//{http://schemas.openxmlformats.org/presentationml/2006/main}txBody')

    # Simpler: rebuild XML with text substitution (see add_shape_xml pattern above)
    pass  # In practice, use add_shape_xml() with text= parameter directly
```

---

## `add_connector()` — Orthogonal Connector via XML Injection

```python
def add_connector(spTree, conn_id, name,
                  src_id, src_idx,   # source shape id, connection point (0=top,1=right,2=bottom,3=left)
                  tgt_id, tgt_idx,   # target shape id, connection point
                  x, y, cx, cy,      # bounding box in EMU
                  color_hex="4472C4",
                  line_w=25400,
                  connector_type="bentConnector3",
                  head_type="none",
                  tail_type="triangle",
                  round_join=True):
    """
    Inject an orthogonal connector (<p:cxnSp>) into the slide XML.

    Uses bentConnector3 by default — orthogonal (Manhattan) routing with
    horizontal-vertical-horizontal segments and 90° elbows.

    The bounding box (x, y, cx, cy) is the rectangle that spans the gap
    between source and target shapes — PowerPoint computes the elbow positions.

    Args:
        round_join: If True, adds <a:round/> inside <a:ln> for softened corners.

    Bounding box formula (right→left connection):
        conn_x  = src_x + src_cx
        conn_y  = min(src_y + src_cy//2, tgt_y + tgt_cy//2)
        conn_cx = tgt_x - (src_x + src_cx)
        conn_cy = max(abs((src_y + src_cy//2) - (tgt_y + tgt_cy//2)), 1)
    """
    round_xml = '<a:round/>' if round_join else ''
    xml_str = f'''
    <p:cxnSp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
      <p:nvCxnSpPr>
        <p:cNvPr id="{conn_id}" name="{name}"/>
        <p:cNvCxnSpPr>
          <a:stCxn id="{src_id}" idx="{src_idx}"/>
          <a:endCxn id="{tgt_id}" idx="{tgt_idx}"/>
        </p:cNvCxnSpPr>
        <p:nvPr/>
      </p:nvCxnSpPr>
      <p:spPr>
        <a:xfrm>
          <a:off x="{x}" y="{y}"/>
          <a:ext cx="{cx}" cy="{cy}"/>
        </a:xfrm>
        <a:prstGeom prst="{connector_type}"><a:avLst/></a:prstGeom>
        <a:noFill/>
        <a:ln w="{line_w}">
          <a:solidFill><a:srgbClr val="{color_hex}"/></a:solidFill>
          {round_xml}
          <a:prstDash val="solid"/>
          <a:headEnd type="{head_type}" w="med" len="med"/>
          <a:tailEnd type="{tail_type}" w="med" len="med"/>
        </a:ln>
      </p:spPr>
    </p:cxnSp>'''
    elem = etree.fromstring(xml_str.strip())
    spTree.append(elem)
    return elem


def connect_right_to_left(spTree, conn_id, name, src_shape, tgt_shape,
                           color_hex="4472C4", line_w=25400):
    """
    Convenience: connect right side of src_shape to left side of tgt_shape.
    Uses orthogonal routing (bentConnector3) by default.
    src_shape and tgt_shape are dicts: {'id': int, 'x': int, 'y': int, 'cx': int, 'cy': int}
    """
    sx, sy, scx, scy = src_shape['x'], src_shape['y'], src_shape['cx'], src_shape['cy']
    tx, ty, tcx, tcy = tgt_shape['x'], tgt_shape['y'], tgt_shape['cx'], tgt_shape['cy']

    conn_x = sx + scx
    conn_y = min(sy + scy // 2, ty + tcy // 2)
    conn_cx = max(tx - (sx + scx), 1)
    conn_cy = max(abs((sy + scy // 2) - (ty + tcy // 2)), 1)

    return add_connector(
        spTree, conn_id, name,
        src_id=src_shape['id'], src_idx=1,
        tgt_id=tgt_shape['id'], tgt_idx=3,
        x=conn_x, y=conn_y, cx=conn_cx, cy=conn_cy,
        color_hex=color_hex, line_w=line_w
    )


def connect_top_to_bottom(spTree, conn_id, name, src_shape, tgt_shape,
                            color_hex="4472C4", line_w=25400):
    """
    Convenience: connect bottom of src_shape to top of tgt_shape.
    Uses orthogonal routing (bentConnector3) — ideal for org charts and architecture diagrams.
    src_shape and tgt_shape are dicts: {'id': int, 'x': int, 'y': int, 'cx': int, 'cy': int}
    """
    sx, sy, scx, scy = src_shape['x'], src_shape['y'], src_shape['cx'], src_shape['cy']
    tx, ty, tcx, tcy = tgt_shape['x'], tgt_shape['y'], tgt_shape['cx'], tgt_shape['cy']

    conn_x = min(sx + scx // 2, tx + tcx // 2)
    conn_y = sy + scy
    conn_cx = max(abs((tx + tcx // 2) - (sx + scx // 2)), 1)
    conn_cy = max(ty - (sy + scy), 1)

    return add_connector(
        spTree, conn_id, name,
        src_id=src_shape['id'], src_idx=2,
        tgt_id=tgt_shape['id'], tgt_idx=0,
        x=conn_x, y=conn_y, cx=conn_cx, cy=conn_cy,
        color_hex=color_hex, line_w=line_w
    )
```

---

## `apply_gradient()` — Gradient Fill

```python
def apply_gradient(sp_elem, start_hex, end_hex, angle=5400000):
    """
    Replace solid fill with gradient fill on an existing shape XML element.

    angle: direction (see ooxml-spec.md for values)
           0=L→R, 5400000=T→B, 10800000=R→L, 16200000=B→T
    """
    a_ns = 'http://schemas.openxmlformats.org/drawingml/2006/main'

    # Remove existing solidFill
    spPr = sp_elem.find('.//{http://schemas.openxmlformats.org/presentationml/2006/main}spPr')
    if spPr is None:
        spPr = sp_elem  # fallback

    for child in list(spPr):
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        if tag in ('solidFill', 'gradFill', 'noFill', 'pattFill'):
            spPr.remove(child)

    grad_xml = f'''
    <a:gradFill xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
      <a:gsLst>
        <a:gs pos="0"><a:srgbClr val="{start_hex}"/></a:gs>
        <a:gs pos="100000"><a:srgbClr val="{end_hex}"/></a:gs>
      </a:gsLst>
      <a:lin ang="{angle}" scaled="0"/>
    </a:gradFill>'''

    grad_elem = etree.fromstring(grad_xml.strip())
    # Insert after xfrm and prstGeom
    insert_idx = 0
    for i, child in enumerate(spPr):
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        if tag in ('xfrm', 'prstGeom'):
            insert_idx = i + 1
    spPr.insert(insert_idx, grad_elem)
```

---

## `add_drop_shadow()` — Outer Shadow Effect

```python
def add_drop_shadow(sp_elem, blur=50800, dist=38100, direction=5400000,
                    color_hex="000000", alpha=40000):
    """
    Add outer drop shadow effect to a shape XML element.

    blur: blur radius in EMU (50800 = 4pt)
    dist: shadow offset in EMU (38100 = 3pt)
    direction: in 60000ths of degree (5400000 = down)
    alpha: opacity 0-100000 (40000 = 40%)
    """
    shadow_xml = f'''
    <a:effectLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
      <a:outerShdw blurRad="{blur}" dist="{dist}" dir="{direction}"
                   algn="tl" rotWithShape="0">
        <a:srgbClr val="{color_hex}">
          <a:alpha val="{alpha}"/>
        </a:srgbClr>
      </a:outerShdw>
    </a:effectLst>'''

    shadow_elem = etree.fromstring(shadow_xml.strip())
    spPr = sp_elem.find('.//{http://schemas.openxmlformats.org/presentationml/2006/main}spPr')
    if spPr is None:
        # Try finding directly
        for child in sp_elem:
            if 'spPr' in child.tag:
                spPr = child
                break
    if spPr is not None:
        spPr.append(shadow_elem)
```

---

## `add_background()` — Full-Slide Background Rectangle

```python
def add_background(spTree, shape_id, fill_hex="F0F4F8"):
    """Add a full-slide background rectangle (insert at z-bottom)."""
    xml_str = f'''
    <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
          xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
      <p:nvSpPr>
        <p:cNvPr id="{shape_id}" name="Background"/>
        <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="9144000" cy="5143500"/>
        </a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        <a:solidFill><a:srgbClr val="{fill_hex}"/></a:solidFill>
        <a:ln><a:noFill/></a:ln>
      </p:spPr>
      <p:txBody>
        <a:bodyPr/><a:lstStyle/>
        <a:p><a:endParaRPr lang="en-US" dirty="0"/></a:p>
      </p:txBody>
    </p:sp>'''
    elem = etree.fromstring(xml_str.strip())
    spTree.insert(2, elem)  # index 2 = after mandatory preamble, at z-bottom
    return elem
```

---

## `add_lane_background()` — Swimlane Background Rectangle

```python
def add_lane_background(spTree, shape_id, x, y, cx, cy, fill_hex, label=""):
    """Add a lane background rect with optional label (for swimlane diagrams)."""
    xml_str = f'''
    <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
          xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
      <p:nvSpPr>
        <p:cNvPr id="{shape_id}" name="Lane {shape_id}"/>
        <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm>
          <a:off x="{x}" y="{y}"/>
          <a:ext cx="{cx}" cy="{cy}"/>
        </a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        <a:solidFill><a:srgbClr val="{fill_hex}"/></a:solidFill>
        <a:ln w="12700">
          <a:solidFill><a:srgbClr val="CCCCCC"/></a:solidFill>
        </a:ln>
      </p:spPr>
      <p:txBody>
        <a:bodyPr wrap="square" anchor="t"><a:normAutofit/></a:bodyPr>
        <a:lstStyle/>
        <a:p>
          <a:pPr algn="l"/>
          <a:r>
            <a:rPr lang="en-US" sz="1000" b="1" dirty="0">
              <a:solidFill><a:srgbClr val="666666"/></a:solidFill>
              <a:latin typeface="Calibri"/>
            </a:rPr>
            <a:t>{label}</a:t>
          </a:r>
        </a:p>
      </p:txBody>
    </p:sp>'''
    elem = etree.fromstring(xml_str.strip())
    spTree.insert(2, elem)  # z-bottom
    return elem
```

---

## EMU Conversion Quick Reference

```python
# Conversion constants
IN = 914400   # 1 inch in EMU
CM = 360000   # 1 cm in EMU
PT = 12700    # 1 pt in EMU

# Common sizes
W_SLIDE = 9144000   # slide width
H_SLIDE = 5143500   # slide height (widescreen)

# Helper
def inches(n): return int(n * IN)
def cm(n): return int(n * CM)
def pt(n): return int(n * PT)

# Example: 1.5 inch wide shape starting 2 inches from left
x = inches(2)
cx = inches(1.5)
```

---

## Shape ID Management

```python
# Pattern: use a mutable counter so helper functions can increment it
shape_id_counter = [2]  # list so nested functions can mutate

def next_id():
    """Get next unique shape ID and increment counter."""
    id_ = shape_id_counter[0]
    shape_id_counter[0] += 1
    return id_

# Usage:
sid = next_id()
shape_info = {'id': sid, 'x': x, 'y': y, 'cx': cx, 'cy': cy}
add_shape_xml(spTree, sid, "Process 1", "flowChartProcess", x, y, cx, cy, text="Step 1")
```

---

## Save and Open

```python
output_path = "diagram.pptx"
prs.save(output_path)
print(f"Saved: {output_path}")

# Open immediately (macOS):
import subprocess
subprocess.run(["open", output_path])
```
