#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

// Resolve pptxgenjs from global npm install if not in NODE_PATH
let pptxgen;
try {
  pptxgen = require("pptxgenjs");
} catch {
  const globalDir = path.join(
    require("os").homedir(),
    ".npm-global",
    "lib",
    "node_modules"
  );
  pptxgen = require(path.join(globalDir, "pptxgenjs"));
}

// --- Icon rendering dependencies (optional) ---
let iconDepsAvailable = null; // null = not checked, true/false = result
let React, ReactDOMServer, sharp;

function resolveFromGlobal(moduleName) {
  const globalDir = path.join(
    require("os").homedir(),
    ".npm-global",
    "lib",
    "node_modules"
  );
  return require(path.join(globalDir, moduleName));
}

function loadIconDeps() {
  if (iconDepsAvailable !== null) return iconDepsAvailable;
  try {
    try { React = require("react"); } catch { React = resolveFromGlobal("react"); }
    try { ReactDOMServer = require("react-dom/server"); } catch { ReactDOMServer = resolveFromGlobal("react-dom/server"); }
    try { sharp = require("sharp"); } catch { sharp = resolveFromGlobal("sharp"); }
    iconDepsAvailable = true;
  } catch (err) {
    console.warn(`Icon dependencies not available (${err.message}). Icon elements will be skipped.`);
    console.warn("Install with: npm install -g react react-dom react-icons sharp");
    iconDepsAvailable = false;
  }
  return iconDepsAvailable;
}

function resolveIconComponent(name, library) {
  const lib = library || "fa";
  const modulePath = `react-icons/${lib}`;
  let mod;
  try { mod = require(modulePath); } catch { mod = resolveFromGlobal(`react-icons/${lib}`); }
  const Component = mod[name];
  if (!Component) {
    throw new Error(`Icon "${name}" not found in react-icons/${lib}`);
  }
  return Component;
}

async function renderIcon(slide, el) {
  // Path-based icon: read PNG directly from disk (bypasses react-icons)
  if (el.path) {
    let iconPath = path.resolve(el.path);
    if (!fs.existsSync(iconPath)) {
      // Fallback: resolve relative to skill root (parent of scripts/)
      const skillDir = path.resolve(__dirname, "..");
      iconPath = path.resolve(skillDir, el.path);
    }
    if (!fs.existsSync(iconPath)) {
      console.warn(`Skipping icon — file not found: ${el.path}`);
      return;
    }
    const buf = fs.readFileSync(iconPath);
    slide.addImage({
      data: `image/png;base64,${buf.toString("base64")}`,
      x: el.x, y: el.y, w: el.w, h: el.h,
    });
    return;
  }

  // Deprecated fallback: react-icons rendering (use path-based icons instead)
  if (el.name) {
    console.warn(`[DEPRECATED] Icon "${el.name}" uses react-icons. Prefer path-based icons from assets/icons/.`);
  }

  if (!loadIconDeps()) {
    console.warn(`Skipping icon element "${el.name}" — icon dependencies not installed.`);
    return;
  }

  const color = (el.color || "333333").replace(/^#/, "");

  let Component;
  try {
    Component = resolveIconComponent(el.name, el.library);
  } catch (err) {
    console.warn(`Skipping icon "${el.name}": ${err.message}`);
    return;
  }

  // Render to SVG string
  const svgBody = ReactDOMServer.renderToStaticMarkup(
    React.createElement(Component, { color: `#${color}`, size: 256 })
  );

  // Wrap in proper SVG document if not already
  let svgString = svgBody;
  if (!svgBody.startsWith("<?xml") && !svgBody.startsWith("<svg")) {
    svgString = `<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256">${svgBody}</svg>`;
  }

  // Rasterize to PNG via sharp
  const pngBuffer = await sharp(Buffer.from(svgString))
    .resize(256, 256)
    .png()
    .toBuffer();

  const base64 = `image/png;base64,${pngBuffer.toString("base64")}`;

  slide.addImage({
    data: base64,
    x: el.x,
    y: el.y,
    w: el.w,
    h: el.h,
  });
}

// --- Shape type mapping ---
function getShapeMap(pres) {
  return {
    rect: pres.shapes.RECTANGLE,
    roundedRect: pres.shapes.ROUNDED_RECTANGLE,
    oval: pres.shapes.OVAL,
    diamond: pres.shapes.DIAMOND,
    cylinder: pres.shapes.CAN,
    cloud: pres.shapes.CLOUD,
    triangle: pres.shapes.ISOSCELES_TRIANGLE,
    hexagon: pres.shapes.HEXAGON,
    parallelogram: pres.shapes.PARALLELOGRAM,
    flowProcess: pres.shapes.FLOWCHART_PROCESS,
    flowDecision: pres.shapes.FLOWCHART_DECISION,
    flowTerminator: pres.shapes.FLOWCHART_TERMINATOR,
    flowDocument: pres.shapes.FLOWCHART_DOCUMENT,
    flowData: pres.shapes.FLOWCHART_DATA,
    trapezoid: pres.shapes.TRAPEZOID,
    pentagon: pres.shapes.PENTAGON,
    octagon: pres.shapes.OCTAGON,
    cube: pres.shapes.CUBE,
    gear6: pres.shapes.GEAR_6,
    gear9: pres.shapes.GEAR_9,
    star5: pres.shapes.STAR_5_POINTS,
    rightArrow: pres.shapes.RIGHT_ARROW,
    leftArrow: pres.shapes.LEFT_ARROW,
    upArrow: pres.shapes.UP_ARROW,
    downArrow: pres.shapes.DOWN_ARROW,
    leftRightArrow: pres.shapes.LEFT_RIGHT_ARROW,
    flowAlternateProcess: pres.shapes.FLOWCHART_ALTERNATE_PROCESS,
    flowPredefinedProcess: pres.shapes.FLOWCHART_PREDEFINED_PROCESS,
    flowManualInput: pres.shapes.FLOWCHART_MANUAL_INPUT,
    flowPreparation: pres.shapes.FLOWCHART_PREPARATION,
    flowMultidocument: pres.shapes.FLOWCHART_MULTIDOCUMENT,
  };
}

// --- JSON mode: parse and validate spec ---
function parseJsonSpec(filePath) {
  const resolved = path.resolve(filePath);
  if (!fs.existsSync(resolved)) {
    console.error(`Error: JSON spec file not found: ${resolved}`);
    process.exit(1);
  }
  const raw = fs.readFileSync(resolved, "utf-8");
  const spec = JSON.parse(raw);

  // Apply defaults for meta
  spec.meta = spec.meta || {};
  spec.meta.title = spec.meta.title || "Diagram";
  spec.meta.bgColor = (spec.meta.bgColor || "FFFFFF").replace(/^#/, "");
  spec.meta.titleColor = (spec.meta.titleColor || "1E293B").replace(/^#/, "");
  spec.meta.titleBgColor = (spec.meta.titleBgColor || "F8FAFC").replace(/^#/, "");
  spec.elements = spec.elements || [];

  return spec;
}

// --- Shadow helper ---
function buildShadow(shadowSpec) {
  if (!shadowSpec) return undefined;
  return {
    type: "outer", // only outer — inner shadows cause pptxgenjs file corruption
    blur: shadowSpec.blur != null ? shadowSpec.blur : 3,
    offset: shadowSpec.offset != null ? shadowSpec.offset : 3,
    angle: shadowSpec.angle != null ? shadowSpec.angle : 45,
    color: (shadowSpec.color || "000000").replace(/^#/, ""),
    opacity: shadowSpec.opacity != null ? shadowSpec.opacity : 0.35,
  };
}

// --- Connector anchor resolution ---
function resolveConnectorEndpoints(el, elementPositions) {
  // If from/to are set, resolve to absolute coordinates from element positions
  if (el.from && el.to && elementPositions[el.from] && elementPositions[el.to]) {
    const fromPos = elementPositions[el.from];
    const toPos = elementPositions[el.to];
    const fromSide = el.fromSide || "right";
    const toSide = el.toSide || "left";

    const sidePoint = (pos, side) => {
      switch (side) {
        case "right":  return { x: pos.x + pos.w, y: pos.y + pos.h / 2 };
        case "left":   return { x: pos.x, y: pos.y + pos.h / 2 };
        case "top":    return { x: pos.x + pos.w / 2, y: pos.y };
        case "bottom": return { x: pos.x + pos.w / 2, y: pos.y + pos.h };
        default:       return { x: pos.x + pos.w, y: pos.y + pos.h / 2 };
      }
    };

    const fp = sidePoint(fromPos, fromSide);
    const tp = sidePoint(toPos, toSide);
    return { x1: fp.x, y1: fp.y, x2: tp.x, y2: tp.y };
  }
  // Fallback: use existing absolute coordinates
  return { x1: el.x1, y1: el.y1, x2: el.x2, y2: el.y2 };
}

// --- Element renderers ---
function renderShape(slide, pres, shapeMap, el) {
  const shapeType = shapeMap[el.shapeType] || pres.shapes.ROUNDED_RECTANGLE;
  const fill = (el.fill || "FFFFFF").replace(/^#/, "");
  const lineColor = (el.lineColor || "333333").replace(/^#/, "");
  const fontColor = (el.fontColor || "333333").replace(/^#/, "");

  const opts = {
    x: el.x,
    y: el.y,
    w: el.w,
    h: el.h,
    fill: { color: fill, transparency: el.fillTransparency || 0 },
    line: {
      color: lineColor,
      width: el.lineWidth || 1,
      dashType: el.lineDash || "solid",
    },
  };
  if (el.rectRadius) opts.rectRadius = el.rectRadius;
  if (el.rotate != null) opts.rotate = el.rotate;

  const shadow = buildShadow(el.shadow);
  if (shadow) opts.shadow = shadow;

  if (el.label || el.textRuns) {
    const textOpts = {
      ...opts,
      shape: shapeType,
      fontSize: el.fontSize || 10,
      fontFace: el.fontFace || "Calibri",
      color: fontColor,
      bold: el.fontBold || false,
      italic: el.fontItalic || false,
      underline: el.fontUnderline || false,
      align: el.align || "center",
      valign: el.valign || "middle",
      margin: el.margin || [5, 8, 5, 8],
    };
    textOpts.fit = el.fit || "shrink";
    if (el.wrap != null) textOpts.wrap = el.wrap;
    if (el.charSpacing != null) textOpts.charSpacing = el.charSpacing;
    if (el.lineSpacing != null) textOpts.lineSpacing = el.lineSpacing;
    if (el.lineSpacingMultiple != null) textOpts.lineSpacingMultiple = el.lineSpacingMultiple;
    if (el.paraSpaceAfter != null) textOpts.paraSpaceAfter = el.paraSpaceAfter;
    if (el.paraSpaceBefore != null) textOpts.paraSpaceBefore = el.paraSpaceBefore;
    if (el.glow) textOpts.glow = { color: (el.glow.color || "000000").replace(/^#/, ""), size: el.glow.size || 2, opacity: el.glow.opacity || 0.35 };
    if (el.textOutline) textOpts.outline = { color: (el.textOutline.color || "000000").replace(/^#/, ""), size: el.textOutline.size || 0.5 };

    if (el.textRuns) {
      // Rich text: array of text run objects with mixed formatting
      const runs = el.textRuns.map((run) => ({
        text: run.text || "",
        options: {
          fontSize: run.fontSize || el.fontSize || 10,
          fontFace: run.fontFace || el.fontFace || "Calibri",
          color: (run.fontColor || el.fontColor || "333333").replace(/^#/, ""),
          bold: run.bold != null ? run.bold : false,
          italic: run.italic != null ? run.italic : false,
          breakLine: run.breakLine || false,
          ...(run.charSpacing != null ? { charSpacing: run.charSpacing } : {}),
        },
      }));
      slide.addText(runs, textOpts);
    } else {
      slide.addText(el.label, textOpts);
    }
  } else {
    slide.addShape(shapeType, opts);
  }
}

function renderConnectorLabel(slide, el, cx, cy, bgColor) {
  const labelColor = (el.labelColor || "666666").replace(/^#/, "");
  const labelW = el.labelW || Math.max(0.5, Math.min(2.5, el.label.length * 0.08 + 0.2));
  const ox = el.labelOffset || 0;
  const labelOpts = {
    x: cx - labelW / 2 + ox, y: cy - 0.15, w: labelW, h: 0.25,
    fontSize: el.labelFontSize || 10,
    color: labelColor,
    align: "center", valign: "middle",
    fontFace: el.fontFace || "Calibri",
    italic: el.labelItalic || false,
    fit: "shrink",
    fill: { color: (el.labelBgColor || bgColor || "FFFFFF").replace(/^#/, "") },
  };
  if (el.labelCharSpacing != null) labelOpts.charSpacing = el.labelCharSpacing;
  slide.addText(el.label, labelOpts);
}

// Chamfer radius for elbow connector corners (inches)
const ELBOW_RADIUS = 0.06;

function renderElbowSegments(slide, pres, lineOpts, el, segments) {
  // Try to chamfer each bend between consecutive segments.
  // A chamfer shortens the two meeting segments by ELBOW_RADIUS and inserts
  // a short diagonal segment between the shortened endpoints.
  // Graceful degradation: if a segment is shorter than 2× radius, skip chamfer.

  const chamferSegs = [];
  for (let i = 0; i < segments.length; i++) {
    const seg = { ...segments[i] };
    const segLen = Math.abs(seg.x2 - seg.x1) + Math.abs(seg.y2 - seg.y1);

    // Shorten end of this segment toward next bend
    if (i < segments.length - 1) {
      const next = segments[i + 1];
      const nextLen = Math.abs(next.x2 - next.x1) + Math.abs(next.y2 - next.y1);
      if (segLen >= 2 * ELBOW_RADIUS && nextLen >= 2 * ELBOW_RADIUS) {
        // Direction of this segment's endpoint → next segment start
        const edx = seg.x2 === seg.x1 ? 0 : (seg.x2 > seg.x1 ? -1 : 1);
        const edy = seg.y2 === seg.y1 ? 0 : (seg.y2 > seg.y1 ? -1 : 1);
        const shortenedEnd = { x: seg.x2 + edx * ELBOW_RADIUS, y: seg.y2 + edy * ELBOW_RADIUS };

        // Direction of next segment from its start
        const ndx = next.x2 === next.x1 ? 0 : (next.x2 > next.x1 ? 1 : -1);
        const ndy = next.y2 === next.y1 ? 0 : (next.y2 > next.y1 ? 1 : -1);
        const shortenedStart = { x: next.x1 + ndx * ELBOW_RADIUS, y: next.y1 + ndy * ELBOW_RADIUS };

        seg.x2 = shortenedEnd.x;
        seg.y2 = shortenedEnd.y;
        chamferSegs.push(seg);
        // Insert chamfer diagonal
        chamferSegs.push({ x1: shortenedEnd.x, y1: shortenedEnd.y, x2: shortenedStart.x, y2: shortenedStart.y, _chamfer: true });
        // Shorten start of next segment (mutate in place for next iteration)
        segments[i + 1] = { ...next, x1: shortenedStart.x, y1: shortenedStart.y };
      } else {
        // Segments too short for chamfer — keep sharp corner
        chamferSegs.push(seg);
      }
    } else {
      chamferSegs.push(seg);
    }
  }

  chamferSegs.forEach((seg, i) => {
    const sdx = seg.x2 - seg.x1;
    const sdy = seg.y2 - seg.y1;
    const sx = Math.min(seg.x1, seg.x2);
    const sy = Math.min(seg.y1, seg.y2);
    const sw = Math.abs(sdx) || 0.001;
    const sh = Math.abs(sdy) || 0.001;
    const segLine = { ...lineOpts };
    segLine.beginArrowType = i === 0 ? (el.startArrow || "none") : "none";
    segLine.endArrowType = i === chamferSegs.length - 1 ? (el.endArrow || "triangle") : "none";

    slide.addShape(pres.shapes.LINE, {
      x: sx, y: sy, w: sw, h: sh,
      flipH: sdx < 0, flipV: sdy < 0,
      line: segLine,
    });
  });
}

function renderConnector(slide, pres, el, elementPositions, bgColor) {
  const coords = resolveConnectorEndpoints(el, elementPositions);
  const { x1, y1, x2, y2 } = coords;

  const lineColor = (el.lineColor || "333333").replace(/^#/, "");
  const lineOpts = {
    color: lineColor,
    width: el.lineWidth || 2.0,
    dashType: el.lineDash || "solid",
  };

  // Default to elbow routing; use straight only when explicitly requested
  const route = el.route || "elbow";

  if (route === "elbow") {
    // Elbow routing: 3-segment orthogonal path with chamfered corners
    const dx = x2 - x1;
    const dy = y2 - y1;
    let segments;
    if (Math.abs(dx) >= Math.abs(dy)) {
      // Horizontal-first: H → V → H
      const midX = x1 + dx / 2;
      segments = [
        { x1, y1, x2: midX, y2: y1 },
        { x1: midX, y1, x2: midX, y2: y2 },
        { x1: midX, y1: y2, x2, y2 },
      ];
    } else {
      // Vertical-first: V → H → V
      const midY = y1 + dy / 2;
      segments = [
        { x1, y1, x2: x1, y2: midY },
        { x1, y1: midY, x2, y2: midY },
        { x1: x2, y1: midY, x2, y2 },
      ];
    }

    renderElbowSegments(slide, pres, lineOpts, el, segments);

    // Label at bend point
    if (el.label) {
      let lx, ly;
      if (Math.abs(dx) >= Math.abs(dy)) {
        lx = x1 + dx / 2;
        ly = y1;
      } else {
        lx = x1;
        ly = y1 + dy / 2;
      }
      renderConnectorLabel(slide, el, lx, ly, bgColor);
    }
  } else {
    // Straight connector (explicit opt-in)
    const dx = x2 - x1;
    const dy = y2 - y1;
    const x = Math.min(x1, x2);
    const y = Math.min(y1, y2);
    const w = Math.abs(dx) || 0.001;
    const h = Math.abs(dy) || 0.001;
    const flipH = dx < 0;
    const flipV = dy < 0;

    slide.addShape(pres.shapes.LINE, {
      x, y, w, h, flipH, flipV,
      line: {
        ...lineOpts,
        beginArrowType: el.startArrow || "none",
        endArrowType: el.endArrow || "triangle",
      },
    });

    if (el.label) {
      const mx = (x1 + x2) / 2;
      const my = (y1 + y2) / 2;
      renderConnectorLabel(slide, el, mx, my, bgColor);
    }
  }
}

function renderText(slide, el) {
  const fontColor = (el.fontColor || "1E293B").replace(/^#/, "");
  const opts = {
    x: el.x,
    y: el.y,
    w: el.w,
    h: el.h,
    fontSize: el.fontSize || 11,
    fontFace: el.fontFace || "Calibri",
    color: fontColor,
    bold: el.fontBold || false,
    italic: el.fontItalic || false,
    underline: el.fontUnderline || false,
    align: el.align || "left",
    valign: el.valign || "middle",
  };
  opts.fit = el.fit || "shrink";
  if (el.wrap != null) opts.wrap = el.wrap;
  if (el.margin) opts.margin = el.margin;
  if (el.charSpacing != null) opts.charSpacing = el.charSpacing;
  if (el.lineSpacing != null) opts.lineSpacing = el.lineSpacing;
  if (el.lineSpacingMultiple != null) opts.lineSpacingMultiple = el.lineSpacingMultiple;
  if (el.paraSpaceAfter != null) opts.paraSpaceAfter = el.paraSpaceAfter;
  if (el.paraSpaceBefore != null) opts.paraSpaceBefore = el.paraSpaceBefore;
  if (el.rotate != null) opts.rotate = el.rotate;
  if (el.glow) opts.glow = { color: (el.glow.color || "000000").replace(/^#/, ""), size: el.glow.size || 2, opacity: el.glow.opacity || 0.35 };
  if (el.textOutline) opts.outline = { color: (el.textOutline.color || "000000").replace(/^#/, ""), size: el.textOutline.size || 0.5 };

  if (el.textRuns) {
    const runs = el.textRuns.map((run) => ({
      text: run.text || "",
      options: {
        fontSize: run.fontSize || el.fontSize || 11,
        fontFace: run.fontFace || el.fontFace || "Calibri",
        color: (run.fontColor || el.fontColor || "1E293B").replace(/^#/, ""),
        bold: run.bold != null ? run.bold : false,
        italic: run.italic != null ? run.italic : false,
        breakLine: run.breakLine || false,
        ...(run.charSpacing != null ? { charSpacing: run.charSpacing } : {}),
      },
    }));
    slide.addText(runs, opts);
  } else {
    slide.addText(el.text || "", opts);
  }
}

function renderDivider(slide, pres, el) {
  const dx = el.x2 - el.x1;
  const dy = el.y2 - el.y1;
  const x = Math.min(el.x1, el.x2);
  const y = Math.min(el.y1, el.y2);
  const w = Math.abs(dx) || 0.001;
  const h = Math.abs(dy) || 0.001;
  const flipH = dx < 0;
  const flipV = dy < 0;

  const lineColor = (el.lineColor || "CCCCCC").replace(/^#/, "");

  slide.addShape(pres.shapes.LINE, {
    x,
    y,
    w,
    h,
    flipH,
    flipV,
    line: {
      color: lineColor,
      width: el.lineWidth || 1,
      dashType: el.lineDash || "solid",
    },
  });
}

function renderGroup(slide, pres, el) {
  const fill = (el.fill || "F0F4F8").replace(/^#/, "");
  const lineColor = (el.lineColor || "CBD5E1").replace(/^#/, "");

  const shapeType = el.rectRadius ? pres.shapes.ROUNDED_RECTANGLE : pres.shapes.RECTANGLE;
  const opts = {
    x: el.x,
    y: el.y,
    w: el.w,
    h: el.h,
    fill: { color: fill, transparency: el.fillTransparency || 0 },
  };

  // Borderless mode: no line at all (consulting pattern where shadow defines edges)
  if (el.borderless || el.lineWidth === 0) {
    opts.line = { width: 0 };
  } else {
    opts.line = {
      color: lineColor,
      width: el.lineWidth || 1,
      dashType: el.lineDash || "solid",
    };
  }

  if (el.rectRadius) opts.rectRadius = el.rectRadius;

  const shadow = buildShadow(el.shadow);
  if (shadow) opts.shadow = shadow;

  slide.addShape(shapeType, opts);

  if (el.label) {
    const labelColor = (el.labelColor || "64748B").replace(/^#/, "");
    const pos = el.labelPosition || "topLeft";
    const labelW = el.labelW || Math.min(el.w - 0.2, Math.max(1.5, el.label.length * 0.1));
    const lx = pos.includes("Right") ? el.x + el.w - labelW - 0.1 : el.x + 0.1;
    const ly = pos.includes("bottom") || pos.includes("Bottom")
      ? el.y + el.h - 0.3
      : el.y + 0.05;
    const align = pos.includes("Right") ? "right" : "left";

    const labelOpts = {
      x: lx,
      y: ly,
      w: labelW,
      h: 0.25,
      fontSize: el.labelFontSize || 9,
      fontFace: el.fontFace || "Calibri",
      color: labelColor,
      bold: el.labelBold || false,
      align,
      valign: "top",
    };
    if (el.labelCharSpacing != null) labelOpts.charSpacing = el.labelCharSpacing;
    labelOpts.fit = "shrink";
    slide.addText(el.label, labelOpts);
  }
}

// --- Build slide from JSON spec ---
async function buildSlideFromJson(spec) {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9"; // 10" x 5.625"
  pres.title = spec.meta.title;

  const slide = pres.addSlide();
  slide.background = { color: spec.meta.bgColor };

  const shapeMap = getShapeMap(pres);

  // Title bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0,
    y: 0,
    w: 10,
    h: 0.75,
    fill: { color: spec.meta.titleBgColor },
  });

  const titleCharSpacing = spec.meta.titleCharSpacing != null ? spec.meta.titleCharSpacing : 1.5;
  const titleOpts = {
    fontSize: spec.meta.titleFontSize || 20,
    fontFace: spec.meta.titleFontFace || "Calibri",
    color: spec.meta.titleColor,
    bold: true,
  };
  if (titleCharSpacing) titleOpts.charSpacing = titleCharSpacing;

  const titleTextParts = [
    {
      text: spec.meta.title,
      options: titleOpts,
    },
  ];

  if (spec.meta.subtitle) {
    titleTextParts[0].options.breakLine = true;
    const subtitleOpts = {
      fontSize: spec.meta.subtitleFontSize || 12,
      fontFace: spec.meta.titleFontFace || "Calibri",
      color: (spec.meta.subtitleColor || spec.meta.titleColor).replace(/^#/, ""),
      bold: false,
    };
    if (spec.meta.subtitleCharSpacing != null) subtitleOpts.charSpacing = spec.meta.subtitleCharSpacing;
    titleTextParts.push({
      text: spec.meta.subtitle,
      options: subtitleOpts,
    });
  }

  slide.addText(titleTextParts, {
    x: 0.4,
    y: 0,
    w: 9.2,
    h: 0.75,
    valign: "middle",
    margin: 0,
  });

  // Two-pass render:
  //   Pass 1: Render all non-connector elements, collect positions by id
  //   Pass 2: Render connectors (resolving from/to anchors against collected positions)

  const elementPositions = {};
  const connectorElements = [];

  for (const el of spec.elements) {
    if (el.type === "connector") {
      connectorElements.push(el);
      continue;
    }

    // Collect position for elements with an id
    if (el.id && el.x != null && el.y != null && el.w != null && el.h != null) {
      elementPositions[el.id] = { x: el.x, y: el.y, w: el.w, h: el.h };
    }

    switch (el.type) {
      case "group":
        renderGroup(slide, pres, el);
        break;
      case "shape":
        renderShape(slide, pres, shapeMap, el);
        break;
      case "text":
        renderText(slide, el);
        break;
      case "divider":
        renderDivider(slide, pres, el);
        break;
      case "icon":
        await renderIcon(slide, el);
        break;
      default:
        console.warn(`Unknown element type: ${el.type}, skipping`);
    }
  }

  // Pass 2: Render connectors with resolved endpoints
  for (const el of connectorElements) {
    renderConnector(slide, pres, el, elementPositions, spec.meta.bgColor);
  }

  // Footer
  if (spec.meta.footer) {
    slide.addText(spec.meta.footer, {
      x: 0.4,
      y: 5.25,
      w: 9.2,
      h: 0.3,
      fontSize: 9,
      fontFace: "Calibri",
      color: "94A3B8",
      align: "center",
      valign: "middle",
    });
  }

  return pres;
}

// --- Save companion artifacts for JSON mode ---
function saveJsonCompanionArtifacts(spec, outputPath) {
  const dir = path.dirname(outputPath);
  const basename = path.basename(outputPath, path.extname(outputPath));

  const mdDest = path.join(dir, `${basename}.description.md`);
  let md = `# ${spec.meta.title}\n\n`;
  if (spec.meta.altText) {
    md += `## Alt Text\n${spec.meta.altText}\n\n`;
  }
  if (spec.meta.description) {
    md += `## Description\n${spec.meta.description}\n\n`;
  }
  md += `## Source\nGenerated: ${new Date().toISOString()}\nMode: native shapes (JSON spec)\n`;
  fs.writeFileSync(mdDest, md);
  console.log(`Description saved to: ${mdDest}`);

  // Copy reference image alongside PPTX if specified
  if (spec.meta.referenceImage) {
    const refImg = path.resolve(spec.meta.referenceImage);
    if (fs.existsSync(refImg)) {
      const pngDest = path.join(dir, `${basename}.png`);
      fs.copyFileSync(refImg, pngDest);
      console.log(`Reference image saved to: ${pngDest}`);
    }
  }
}

// --- Legacy image mode: parse CLI arguments ---
function parseArgs(argv) {
  const args = {
    image: null,
    title: null,
    altText: null,
    output: "output.pptx",
    subtitle: null,
    bgColor: "FFFFFF",
    titleColor: "1E293B",
    titleBgColor: "F8FAFC",
    footer: null,
    description: null,
    noArtifacts: false,
  };

  for (let i = 2; i < argv.length; i++) {
    switch (argv[i]) {
      case "--image":
        args.image = argv[++i];
        break;
      case "--title":
        args.title = argv[++i];
        break;
      case "--alt-text":
        args.altText = argv[++i];
        break;
      case "--output":
        args.output = argv[++i];
        break;
      case "--subtitle":
        args.subtitle = argv[++i];
        break;
      case "--bg-color":
        args.bgColor = argv[++i];
        break;
      case "--title-color":
        args.titleColor = argv[++i];
        break;
      case "--title-bg-color":
        args.titleBgColor = argv[++i];
        break;
      case "--footer":
        args.footer = argv[++i];
        break;
      case "--description":
        args.description = argv[++i];
        break;
      case "--no-artifacts":
        args.noArtifacts = true;
        break;
      default:
        console.error(`Unknown argument: ${argv[i]}`);
        process.exit(1);
    }
  }

  // Strip # from hex colors if provided
  args.bgColor = args.bgColor.replace(/^#/, "");
  args.titleColor = args.titleColor.replace(/^#/, "");
  args.titleBgColor = args.titleBgColor.replace(/^#/, "");

  if (!args.image) {
    console.error("Error: --image is required");
    process.exit(1);
  }
  if (!args.title) {
    console.error("Error: --title is required");
    process.exit(1);
  }
  if (!args.altText) {
    console.error("Error: --alt-text is required");
    process.exit(1);
  }
  if (!fs.existsSync(args.image)) {
    console.error(`Error: Image file not found: ${args.image}`);
    process.exit(1);
  }

  return args;
}

function buildSlide(args) {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9"; // 10" x 5.625"
  pres.title = args.title;

  const slide = pres.addSlide();
  slide.background = { color: args.bgColor };

  // Title bar background rectangle (full width, top)
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0,
    y: 0,
    w: 10,
    h: 0.75,
    fill: { color: args.titleBgColor },
  });

  // Title text
  const titleTextParts = [
    {
      text: args.title,
      options: {
        fontSize: 20,
        fontFace: "Calibri",
        color: args.titleColor,
        bold: true,
      },
    },
  ];

  // Add subtitle if provided
  if (args.subtitle) {
    titleTextParts[0].options.breakLine = true;
    titleTextParts.push({
      text: args.subtitle,
      options: {
        fontSize: 12,
        fontFace: "Calibri",
        color: args.titleColor,
        bold: false,
      },
    });
  }

  slide.addText(titleTextParts, {
    x: 0.4,
    y: 0,
    w: 9.2,
    h: 0.75,
    valign: "middle",
    margin: 0,
  });

  // Diagram image — centered below title bar
  const imgPath = path.resolve(args.image);
  slide.addImage({
    path: imgPath,
    x: 0.25,
    y: 0.85,
    w: 9.5,
    h: 4.5,
    sizing: { type: "contain", w: 9.5, h: 4.5 },
    altText: args.altText,
  });

  // Optional footer
  if (args.footer) {
    slide.addText(args.footer, {
      x: 0.4,
      y: 5.25,
      w: 9.2,
      h: 0.3,
      fontSize: 9,
      fontFace: "Calibri",
      color: "94A3B8",
      align: "center",
      valign: "middle",
    });
  }

  return pres;
}

function saveCompanionArtifacts(args, outputPath) {
  const dir = path.dirname(outputPath);
  const basename = path.basename(outputPath, path.extname(outputPath));
  const imgPath = path.resolve(args.image);

  // Copy source image alongside the PPTX
  const pngDest = path.join(dir, `${basename}.png`);
  fs.copyFileSync(imgPath, pngDest);
  console.log(`Image copy saved to: ${pngDest}`);

  // Write description markdown file
  const mdDest = path.join(dir, `${basename}.description.md`);
  let md = `# ${args.title}\n\n`;
  md += `## Alt Text\n${args.altText}\n\n`;
  if (args.description) {
    md += `## Description\n${args.description}\n\n`;
  }
  md += `## Source\nGenerated: ${new Date().toISOString()}\nImage: ${imgPath}\n`;
  fs.writeFileSync(mdDest, md);
  console.log(`Description saved to: ${mdDest}`);
}

// --- Main entrypoint ---
async function main() {
  // Detect mode: --json or --image
  const jsonIdx = process.argv.indexOf("--json");
  const imageIdx = process.argv.indexOf("--image");

  if (jsonIdx !== -1 && imageIdx !== -1) {
    console.error("Error: --json and --image are mutually exclusive");
    process.exit(1);
  }

  if (jsonIdx !== -1) {
    // JSON native shapes mode
    const jsonPath = process.argv[jsonIdx + 1];
    if (!jsonPath) {
      console.error("Error: --json requires a file path");
      process.exit(1);
    }

    let outputPath = "output.pptx";
    const outIdx = process.argv.indexOf("--output");
    if (outIdx !== -1 && process.argv[outIdx + 1]) {
      outputPath = process.argv[outIdx + 1];
    }

    const noArtifacts = process.argv.includes("--no-artifacts");

    const spec = parseJsonSpec(jsonPath);
    const pres = await buildSlideFromJson(spec);

    const resolved = path.resolve(outputPath);
    await pres.writeFile({ fileName: resolved });
    console.log(`PPTX saved to: ${resolved}`);

    if (!noArtifacts) {
      saveJsonCompanionArtifacts(spec, resolved);
    }
  } else {
    // Legacy image mode
    const args = parseArgs(process.argv);
    const pres = buildSlide(args);

    const outputPath = path.resolve(args.output);
    await pres.writeFile({ fileName: outputPath });
    console.log(`PPTX saved to: ${outputPath}`);

    if (!args.noArtifacts) {
      saveCompanionArtifacts(args, outputPath);
    }
  }
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
