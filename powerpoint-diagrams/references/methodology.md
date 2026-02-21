# Diagram Design Methodology

Cognitive architecture for designing novel, contextually appropriate diagrams. This is a **reference** — consult specific sections as needed during design phases, not a sequential tutorial.

---

## 0. Define the Contract Before You Draw

Before any visual work, establish three things:

1. **Purpose statement** — one sentence: "This diagram answers: ___." (e.g., "How does a request flow from the user to the database?")
2. **Primary audience** — pick ONE: Executive / PM / Developer / Security / Ops. Secondary audiences get separate views.
3. **Diagram level** (C4-inspired) — Context / Container / Component / Sequence / Deployment. Never mix levels in one view.

**Do**: Write the purpose statement before opening a code editor.
**Don't**: Try to satisfy every persona in one view. Don't start styling before structure is fixed.

---

## 1. Strategic Semiotics & Cognitive Mapping

Before touching shapes, decompose the subject into semantic primitives.

### Semantic Inventory

Classify every element in the user's request:

| Primitive | Definition | Examples |
|-----------|-----------|----------|
| **Node** | Discrete entity with identity | Service, person, step, component |
| **Edge** | Relationship between nodes | Data flow, dependency, sequence, reports-to |
| **Container** | Grouping boundary that owns children | Layer, swimlane, subsystem, team |
| **Annotation** | Metadata not part of the domain model | Title, legend, label, caption |

### Visual Rhetoric Selection

The relationship pattern between nodes determines the diagram's visual rhetoric:

| Rhetoric | When to use | Primary scan path | Edge character |
|----------|-------------|-------------------|----------------|
| **Sequential flow** | Steps in order, pipelines, processes | Left-to-right or top-to-bottom | Directed, uniform weight |
| **Hierarchy** | Reporting structures, taxonomies, inheritance | Top-to-bottom, center-outward | Parent-to-child, no crossover |
| **Containment** | Layers, subsystems, scope boundaries | Outside-in (container label then children) | Implicit (membership), explicit for cross-boundary |
| **Radial/Hub-spoke** | Central coordinator, API gateway, event bus | Center-outward | Uniform length, symmetric |
| **Network/Mesh** | Peer services, bidirectional dependencies | No dominant path (consider restructuring) | Bidirectional, variable weight |
| **Dependency** | Build systems, import graphs, prerequisites | Bottom-to-top or right-to-left | Directed, potential cycles |

### Scan Path Rules

- **Single dominant direction**: Every diagram should have one primary scan direction. Mixed directions create cognitive load.
- **Entry point**: The reader's eye must land on the logical starting node first (top-left for LTR cultures, center for radial).
- **Terminal emphasis**: End states should be visually distinct (different shape or color) to signal completion.

**Default placement**: Entry points (User/Client/API Gateway) go top-left. Data stores go lower. External dependencies on sides. Observability/monitoring off to one side.

**Don't**: Put critical entry points in the center with equal visual weight as everything else.

---

## 2. Layout Algorithm Selection

The highest-impact design decision. Choose based on the semantic inventory.

| Algorithm | Best for | Node limit | Key constraint |
|-----------|----------|------------|----------------|
| **Layered / Hierarchical** | DAGs, org charts, class hierarchies | 15-25 per slide | Minimize edge crossings between layers |
| **Hub-and-Spoke (Radial)** | API gateways, event buses, central coordinators | 8-12 spokes | Equal angular spacing; hub must be visually dominant |
| **Orthogonal / Grid** | Mesh networks, matrix organizations, comparison charts | 16-20 (4x5) | Strict row/column alignment; edges route on grid lines |
| **Swimlane** | Cross-cutting concerns, layered architectures, responsibility mapping | 3-5 lanes, 4-6 nodes per lane | Lane labels must be readable; inter-lane edges route vertically |
| **Timeline / Phased** | Roadmaps, migration plans, sprint sequences | 5-8 phases | Equal phase width; milestones on a shared horizontal axis |
| **Force-directed (manual)** | Exploratory/organic relationships, brainstorming | 8-12 | Use only when no hierarchy exists; manually balance forces |

### Grid and Spacing System

Use an **8-pt base grid** (73152 EMU per 8px at 96dpi). All positions and dimensions should snap to multiples of this grid.

- **Canvas margins**: at least 48px equivalent (~438912 EMU) on all sides
- **Intra-group gap**: 0.15" (137160 EMU)
- **Inter-group gap**: 0.35" (320040 EMU)

**Do**: Align all shapes to the grid. Use consistent spacing.
**Don't**: Eyeball spacing. Allow minor misalignments — they create visual noise.

### Edge Routing by Algorithm

| Algorithm | Preferred routing | Connector type |
|-----------|-------------------|----------------|
| Layered | Orthogonal, down/right | `build_routed_connector_xml` with waypoints |
| Hub-spoke | Straight radial | `straightConnector1` or straight waypoints |
| Grid | Orthogonal, Manhattan | `build_routed_connector_xml` |
| Swimlane | Vertical between lanes | `build_routed_connector_xml` |
| Timeline | Horizontal along axis | Straight arrows |

### Cycle Resolution

If the domain contains cycles (retry loops, feedback paths):
1. Route the back-edge **outside** the main flow (below or to the side).
2. Use **dashed stroke** to visually separate it from the primary flow.
3. Keep no more than **1 back-edge visible** per slide. If there are more, split into multiple slides or use a separate sequence view.

---

## 3. Gestalt Laws Applied to Diagrams

Use perceptual grouping to reduce cognitive load without adding visual elements.

| Law | Diagram application | OOXML implementation |
|-----|---------------------|----------------------|
| **Proximity** | Nodes in the same logical group are placed closer together than nodes in different groups | Layout constants: intra-group gap < inter-group gap (e.g., 0.15" vs 0.35") |
| **Similarity** | Same-role nodes share fill color, shape preset, and size | Consistent `(preset, fill, border)` tuples per role in the data model |
| **Common region** | Containers (lanes, subsystems) have a visible background rect | Semi-transparent fill rect inserted at z-index 2, with subtle border |
| **Continuity** | Edges follow smooth, predictable paths — no unnecessary bends | `build_routed_connector_xml` with consistent `radius`; minimize waypoints |
| **Common fate** | Parallel processes move in the same direction with equal spacing | Same y-coordinate, equal x-offsets; parallel arrows have same length |
| **Figure-ground** | The diagram content (figure) must clearly separate from the slide background (ground) | Background uses a subtle gradient or flat muted color; shapes use saturated fills with shadows for elevation |

### Grouping Priority

When multiple grouping strategies conflict, prioritize:
1. **Common region** (strongest — a container boundary always wins)
2. **Proximity** (physical closeness)
3. **Similarity** (shared visual properties)

### Boundary and Zone Rules

- **Hard boundaries** (network, trust, security): solid line border
- **Conceptual boundaries** (domain, team, responsibility): dashed line border
- **Zone fills**: subtle, low-contrast region fills (10-15% opacity)

**Don't**: Nest more than 3 boundary levels in one view. If deeper nesting is needed, split into separate diagrams.

---

## 4. Tufte Paradigm

Maximize the data-ink ratio: every pixel should convey information.

### Core Rules

- **Visual prominence ∝ importance**: Primary nodes get larger shapes, bolder colors, thicker borders. Secondary nodes are smaller, muted, thinner.
- **Consistent encoding**: If blue means "service" somewhere, it means "service" everywhere.
- **Quantitative integrity**: Represent scale with explicit annotations ("P95 latency: 120ms", "~5k rps"). Don't make minor services visually equal to core pipeline.
- **Emphasis hierarchy**: size → whitespace → contrast (in that order). Use the minimum channels needed.
- **Functional effects only**: Keep gradients that encode hierarchy, shadows for figure-ground separation. Ban decorative gradients, uniform shadows, glow on all nodes.

**Don't**: Emphasize everything. Use 3D effects that distort relative sizes.

### Chartjunk Checklist

Before adding a visual effect, ask: **does this encode information the viewer needs?**

| Effect | Functional (keep) | Decorative (remove) |
|--------|-------------------|---------------------|
| Gradient | Encodes hierarchy level or state | "Makes it look modern" |
| Shadow | Separates overlapping layers | Applied uniformly to everything |
| Glow | Highlights one critical/active node | Applied to all nodes |
| 3D bevel | Encodes deployment layer | "Looks premium" |

---

## 5. Standardized Visual Grammar

Defaults for consistent output across all diagrams.

### Shape Grammar

Limit to **2-4 core shapes** per diagram. Additional shapes are allowed only when they encode a distinct semantic role. The table below provides defaults — pick only the shapes relevant to your diagram.

| Semantic role | Default preset | Override when |
|---------------|---------------|---------------|
| Process / step | `roundRect` | Domain uses specific notation (BPMN, UML) |
| Decision / gate | `flowChartDecision` | — |
| Start / end | `flowChartTerminator` | — |
| Data store / DB | `flowChartMagneticDisk` | — |
| External system | `cloud` | — |
| API / gateway | `hexagon` | — |
| Queue / bus | `chevron` or `rightArrow` | — |
| Person / actor | `ellipse` with text | — |
| Note / callout | `wedgeRoundRectCallout` | — |

**Don't**: Use more than 4 core shapes in a single diagram. Remove novelty shapes that don't encode a distinct role.

### Connector Discipline

- Use arrows **only when direction matters**. Undirected associations can use plain lines.
- **One connector style** per diagram (don't mix orthogonal and curved).
- Prefer **orthogonal routing** for professional diagrams.
- If more than **2 line crossings** occur in any region, restructure: introduce a hub/bus, reorder nodes, or split the diagram.

**Don't**: Use double-headed arrows unless the relationship is truly bidirectional. Don't accept spaghetti — restructure instead.

### Stroke Hierarchy

| Level | Width | Style | Use |
|-------|-------|-------|-----|
| Primary flow | 2pt (`25400`) | Solid | Main sequence, happy path |
| Secondary flow | 1.5pt (`19050`) | Solid | Alternate paths, supporting edges |
| Optional / async | 1pt (`12700`) | Dashed (`lgDash`) | Optional steps, async messages |
| Back-edge / loop | 1pt (`12700`) | Dashed (`dash`) | Retry, feedback loops |

### Size Hierarchy

| Role | Relative size | Typical dimensions |
|------|--------------|-------------------|
| Primary node | 1.0x (baseline) | 1.5" x 0.75" (1371600 x 685800) |
| Central hub | 1.3x | 2.0" x 1.0" (1828800 x 914400) |
| Secondary node | 0.85x | 1.3" x 0.65" (1188720 x 594360) |
| Annotation label | 0.5x | 0.5" x 0.25" (text only, no visible shape) |

### Color Assignment

- Assign **3-5 semantic colors** per diagram. Each color maps to a role or category.
- Use a single palette from `reference.md` as the base, then adjust for the specific domain.
- Reserve **red/orange** for warnings, errors, or decision points.
- Reserve **green** for success, approval, or completion.
- Use **gray** for infrastructure, connectors, and de-emphasized elements.
- **Each color = exactly one category** across the entire diagram set.

**Don't**: Use color for aesthetics. Every color must encode meaning.

---

## 5.5. Typography and Labeling

### Font

One font family per diagram set. Default: **Calibri**.

### Size Hierarchy

| Role | Point size | sz value | Bold |
|------|-----------|----------|------|
| Slide title | 18-24pt | `1800`-`2400` | Yes |
| Region / container label | 12-14pt | `1200`-`1400` | Yes |
| Node label | 10-12pt | `1000`-`1200` | Yes |
| Connector / edge label | 9-10pt | `900`-`1000` | No |
| Caption / annotation | 9-10pt | `900`-`1000` | No |

### Labeling Rules

- **Sentence case** for all labels (not ALLCAPS for normal labels)
- **Nouns** for node labels (e.g., "Auth Service", "User DB")
- **Verb phrases** for connector labels (e.g., "validates", "queries", "returns 200")
- Maximum **2 lines of text** inside any shape. If you need more, the box is too detailed — move detail to a sub-diagram or annotation.

**Don't**: Use all-caps for normal labels (reserve for acronyms). Don't put paragraphs inside boxes.

---

## 6. Progressive Disclosure

### When to Split Slides

| Trigger | Action |
|---------|--------|
| >10 primary nodes on a single slide | Split into overview + detail slides |
| >3 nesting levels (container in container in container) | Flatten to 2 levels; use a separate slide for the inner detail |
| >15 edges visible simultaneously | Group related edges; use a context slide showing groups, then detail slides per group |
| Mixed audiences (executive + technical) | Create a summary slide (5-7 nodes, key relationships) followed by technical detail slides |

### Diagram Set Strategy

Ship as a **set**, not a single frame:
- **L1 Context** → L2 Container → L3 Component → Sequence diagrams for loops/cycles
- Keep **cross-diagram consistency**: same names, same icons, same color meanings
- Navigation cue: consistent color coding between context and detail slides

**Don't**: Combine deployment + code-level + business workflow in one frame. Don't mix diagram levels.

### Single-Slide Density Management

When splitting is not desired:
- Reduce secondary node size to 0.7x
- Use abbreviations in labels (provide a legend)
- Collapse parallel/symmetric branches into a single representative node with a "x N" annotation
- Remove optional edges; show only the primary flow

---

## 7. Cognitive Diagnostics & Accessibility

### Squint Test

Before finalizing, mentally blur the diagram. You should still be able to identify:
1. The **number of groups** (via common region or proximity)
2. The **primary flow direction** (via edge alignment)
3. The **most important node** (via size or color dominance)

If any of these fail, adjust the visual hierarchy.

### Double Coding

For critical states, encode with **both** color and a secondary channel:

| State | Color | Secondary encoding |
|-------|-------|-------------------|
| Error / failure | Red | Dashed border or different shape |
| Success / complete | Green | Thicker border or bold text |
| Active / current | Blue highlight | Glow effect (`<a:glow>`) |
| Deprecated / disabled | Gray | Reduced opacity (`<a:alpha val="50000"/>`) |

### Color-Blind Robustness

- Pair color with shape, line style, or icon — never rely on color alone
- If two categories could blur under deuteranopia (red/green), add pattern or shape differences
- Test at 100% and 200% zoom

**Don't**: Use thin low-contrast text. Don't bake tiny legends.

### Contrast & Cultural Neutrality

- Body text on shapes: 4.5:1 contrast (WCAG AA). Large text (>18pt): 3:1.
- **Practical rule**: White text on dark fills (< `808080`), dark text on light fills (> `808080`).
- Default flow: left-to-right. Avoid culture-specific color meanings and symbolic shapes.

---

## 8. Common Anti-Patterns

Quick-reference checklist of things to avoid. Per-section don'ts provide more detail.

| Anti-pattern | Why it fails | Fix |
|--------------|-------------|-----|
| **"Everything in one diagram" mega-canvas** | Overwhelms viewer; no clear story | Split into diagram set (§6) |
| **Random icon styles mixed together** | Breaks visual similarity; looks unprofessional | Pick one icon style or stick to shape presets |
| **Many-to-many direct connections without hubs/buses** | Creates spaghetti; impossible to trace | Introduce hub node or bus lane (§5) |
| **Decorative effects instead of structure** | Adds visual noise without information | Apply functional effects only (§4) |
| **Color used for aesthetics rather than encoding** | Viewer can't decode meaning | Each color = one category (§5) |
| **Loops/cycles as tangled arrows** | Confuses flow direction | Separate into sequence view or route back-edges outside (§2) |
| **Paragraphs inside boxes** | Unreadable at slide size | Max 2 lines; move detail to sub-diagram (§5.5) |
| **Mixing diagram levels in one view** | Inconsistent abstraction confuses scope | One level per view (§0) |

---

## 9. Default Specification

Baseline values for consistent output. Override per-diagram only when the design rationale demands it.

| Property | Default value | EMU equivalent |
|----------|--------------|----------------|
| Grid unit | 8pt | 73152 |
| Canvas margins | 48px | ~438912 |
| Node corner radius | Small, consistent | — |
| Primary line weight | 2pt | 25400 |
| Secondary line weight | 1.5pt | 19050 |
| Arrowhead style | `triangle`, `med`/`med` | — |
| Font family | Calibri | — |
| Node label size | 10-12pt | `1000`-`1200` |
| Connector label size | 9-10pt | `900`-`1000` |
| Palette structure | Neutral grays + 5 category colors | — |
| Focal accent | 1 accent color reserved for primary path | — |
