# Image Analysis Templates

Ready-to-use prompt templates for `image_to_text.py`. Copy and customize as needed.

---

## Alt Text (Accessibility)

Concise description for screen readers and accessibility compliance.

```
Provide a concise alt text description of this image suitable for a screen reader. Focus on the essential content and purpose of the image. Keep it under 125 characters if possible, or under 250 characters for complex images. Do not start with "Image of" or "Picture of".
```

**When to use:** Web images, document figures, any content that needs WCAG compliance.

---

## Full Description

Comprehensive visual description covering all elements.

```
Provide a detailed description of this image covering:
1. Main subject and focal point
2. Background and setting
3. Colors, lighting, and mood
4. Text visible in the image (transcribe exactly)
5. Spatial layout (what's left/right/top/bottom/center)
6. Notable details or secondary elements

Be thorough but organized. Use clear, factual language.
```

**When to use:** Documentation, archival, or when a complete record is needed.

---

## Structural Layout

Spatial analysis for understanding composition and element placement.

```
Analyze the structural layout of this image:
1. Identify all distinct visual elements/regions
2. Describe their positions (use quadrant or coordinate references)
3. Note the visual hierarchy (what draws attention first, second, third)
4. Describe connections or relationships between elements (arrows, lines, proximity)
5. Identify the overall layout pattern (grid, flow, radial, hierarchical, free-form)

Format as a structured list. Include approximate relative sizes where relevant.
```

**When to use:** UI analysis, diagram interpretation, layout replication.

---

## OCR / Text Extraction

Extract all readable text from the image.

```
Extract ALL text visible in this image. For each text element:
1. Transcribe the text exactly as it appears (preserve capitalization, punctuation)
2. Note its approximate position (top-left, center, bottom-right, etc.)
3. Describe its visual style (font size relative to others: large/medium/small, bold/italic/regular, color)

Group related text elements together (e.g., a heading with its body text). If text is partially obscured or unclear, indicate this with [unclear] or your best guess in [brackets].
```

**When to use:** Extracting text from screenshots, scanned documents, signs, whiteboards.

---

## Photo Description

Natural language description of photographs focusing on scene and subjects.

```
Describe this photograph naturally, as if telling someone what you see:
1. Who/what is the main subject?
2. What is happening or what action is taking place?
3. Where is this (setting, environment, location type)?
4. When might this be (time of day, season, era)?
5. What is the mood or atmosphere?
6. What photographic qualities stand out (composition, lighting, focus)?

Write in flowing prose, not bullet points.
```

**When to use:** Photo cataloging, social media descriptions, creative writing prompts.

---

## Technical Diagram Analysis

Interpret architecture diagrams, flowcharts, network diagrams, and similar technical visuals.

```
Analyze this technical diagram:

1. **Diagram type:** What kind of diagram is this? (architecture, flowchart, network, sequence, ER, etc.)
2. **Components:** List every distinct component/node with its label and type (service, database, user, process, etc.)
3. **Connections:** Describe each connection/arrow between components, including:
   - Source → Destination
   - Connection type (data flow, dependency, network link, sequence)
   - Any labels on the connection
4. **Layers/Groups:** Identify any groupings, swim lanes, or hierarchical layers
5. **Data flow:** Describe the overall flow of data or control through the system
6. **Key patterns:** Note any architectural patterns visible (microservices, event-driven, hub-and-spoke, etc.)

Format as structured markdown with headers for each section.
```

**When to use:** Understanding existing diagrams, recreating diagrams in code, documentation.

---

## Data Extraction from Charts

Extract quantitative data from charts and graphs.

```
Analyze this chart/graph and extract the data:

1. **Chart type:** (bar, line, pie, scatter, area, etc.)
2. **Title and labels:** Transcribe the chart title, axis labels, and legend entries
3. **Data points:** Extract all visible data values. For each series/category:
   - List the category/x-value and its corresponding y-value
   - Note the unit of measurement if visible
4. **Trends:** Describe the key trends (increasing, decreasing, stable, cyclical)
5. **Outliers:** Note any data points that stand out from the pattern
6. **Summary:** One-sentence summary of what the chart communicates

Present extracted data in a markdown table where possible.
```

**When to use:** Converting chart images to data, summarizing visual data for reports.

---

## UI Screenshot Analysis

Analyze user interface screenshots for design or testing purposes.

```
Analyze this UI screenshot:

1. **Screen/Page type:** What kind of screen is this? (login, dashboard, settings, form, etc.)
2. **Layout:** Describe the overall layout structure (header, sidebar, main content, footer)
3. **Components:** List all visible UI components:
   - Buttons (label, state: enabled/disabled/active)
   - Input fields (label, placeholder text, current value)
   - Navigation elements (tabs, menus, breadcrumbs)
   - Data displays (tables, cards, lists)
   - Status indicators (badges, alerts, progress bars)
4. **Content:** Transcribe all visible text content
5. **Visual state:** Note any active/selected/highlighted/error states
6. **Responsive hints:** Any indication of responsive behavior or breakpoints

Format as a structured component inventory.
```

**When to use:** UI testing, design review, accessibility audits, documentation.

---

## Comparison Analysis

Compare two or more images or elements within an image.

```
Compare the elements in this image:

1. **Similarities:** What do the compared items have in common?
2. **Differences:** What distinguishes each item? Be specific about:
   - Visual differences (color, size, shape, style)
   - Content differences (text, data, components)
   - Structural differences (layout, organization)
3. **Quality assessment:** If applicable, which version appears more polished/correct/complete?
4. **Summary:** One-sentence summary of the key difference

Present differences in a comparison table where possible.
```

**When to use:** Before/after comparisons, A/B test screenshots, version comparisons.

---

## Custom Template Skeleton

Starting point for creating your own analysis prompts.

```
Analyze this image with the following focus: [YOUR FOCUS AREA]

For each element you identify:
1. [WHAT TO EXTRACT]
2. [HOW TO DESCRIBE IT]
3. [WHAT FORMAT TO USE]

Additional requirements:
- [SPECIFIC CONSTRAINT]
- [OUTPUT FORMAT]

Respond in [FORMAT: markdown / JSON / plain text / table].
```
