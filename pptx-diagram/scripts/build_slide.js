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

  if (el.label) {
    slide.addText(el.label, {
      ...opts,
      shape: shapeType,
      fontSize: el.fontSize || 10,
      fontFace: "Calibri",
      color: fontColor,
      bold: el.fontBold || false,
      align: "center",
      valign: "middle",
      margin: [3, 5, 3, 5],
    });
  } else {
    slide.addShape(shapeType, opts);
  }
}

function renderConnector(slide, pres, el) {
  const dx = el.x2 - el.x1;
  const dy = el.y2 - el.y1;
  const x = Math.min(el.x1, el.x2);
  const y = Math.min(el.y1, el.y2);
  const w = Math.abs(dx) || 0.001;
  const h = Math.abs(dy) || 0.001;
  const flipH = dx < 0;
  const flipV = dy < 0;

  const lineColor = (el.lineColor || "333333").replace(/^#/, "");

  slide.addShape(pres.shapes.LINE, {
    x,
    y,
    w,
    h,
    flipH,
    flipV,
    line: {
      color: lineColor,
      width: el.lineWidth || 1.5,
      dashType: el.lineDash || "solid",
      beginArrowType: el.startArrow || "none",
      endArrowType: el.endArrow || "triangle",
    },
  });

  if (el.label) {
    const mx = (el.x1 + el.x2) / 2;
    const my = (el.y1 + el.y2) / 2;
    const labelColor = (el.labelColor || "666666").replace(/^#/, "");
    slide.addText(el.label, {
      x: mx - 0.5,
      y: my - 0.2,
      w: 1.0,
      h: 0.25,
      fontSize: el.labelFontSize || 8,
      color: labelColor,
      align: "center",
      valign: "middle",
      fontFace: "Calibri",
    });
  }
}

function renderText(slide, el) {
  const fontColor = (el.fontColor || "1E293B").replace(/^#/, "");
  slide.addText(el.text || "", {
    x: el.x,
    y: el.y,
    w: el.w,
    h: el.h,
    fontSize: el.fontSize || 11,
    fontFace: "Calibri",
    color: fontColor,
    bold: el.fontBold || false,
    align: el.align || "left",
    valign: el.valign || "middle",
  });
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

  slide.addShape(pres.shapes.RECTANGLE, {
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
  });

  if (el.label) {
    const labelColor = (el.labelColor || "64748B").replace(/^#/, "");
    const pos = el.labelPosition || "topLeft";
    const lx = pos.includes("Right") ? el.x + el.w - 1.5 : el.x + 0.1;
    const ly = pos.includes("bottom") || pos.includes("Bottom")
      ? el.y + el.h - 0.3
      : el.y + 0.05;
    const align = pos.includes("Right") ? "right" : "left";

    slide.addText(el.label, {
      x: lx,
      y: ly,
      w: 1.5,
      h: 0.25,
      fontSize: el.labelFontSize || 9,
      fontFace: "Calibri",
      color: labelColor,
      bold: false,
      align,
      valign: "top",
    });
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

  const titleTextParts = [
    {
      text: spec.meta.title,
      options: {
        fontSize: 20,
        fontFace: "Calibri",
        color: spec.meta.titleColor,
        bold: true,
      },
    },
  ];

  if (spec.meta.subtitle) {
    titleTextParts[0].options.breakLine = true;
    titleTextParts.push({
      text: spec.meta.subtitle,
      options: {
        fontSize: 12,
        fontFace: "Calibri",
        color: spec.meta.titleColor,
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

  // Render elements in order (z-order: first = behind)
  for (const el of spec.elements) {
    switch (el.type) {
      case "group":
        renderGroup(slide, pres, el);
        break;
      case "shape":
        renderShape(slide, pres, shapeMap, el);
        break;
      case "connector":
        renderConnector(slide, pres, el);
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
