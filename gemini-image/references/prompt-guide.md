# Image Generation Prompt Guide

Best practices for crafting effective prompts with Gemini image generation.

## Prompt Structure

A strong prompt follows this order:

1. **Subject** — What is depicted (the most important element)
2. **Style / Medium** — Visual treatment (photorealistic, vector, watercolor, etc.)
3. **Composition** — Framing, perspective, layout
4. **Details** — Lighting, color palette, mood, background
5. **Negative constraints** — What to exclude (use sparingly)

### Example Breakdown

> "A modern three-tier cloud architecture diagram, clean vector style, horizontal layout with three columns, white background with blue and gray color scheme, no text labels"

| Component | Value |
|---|---|
| Subject | three-tier cloud architecture diagram |
| Style | clean vector style |
| Composition | horizontal layout with three columns |
| Details | white background, blue and gray color scheme |
| Negative | no text labels |

## Style Keywords

| Category | Keywords |
|---|---|
| Photorealistic | photorealistic, photograph, DSLR, 35mm, natural lighting |
| Illustration | digital illustration, hand-drawn, sketch, line art |
| Vector/Diagram | clean vector, flat design, infographic, technical diagram |
| Artistic | watercolor, oil painting, impressionist, abstract |
| 3D | 3D render, isometric, low-poly, CGI |
| Minimal | minimalist, simple, clean, whitespace |

## Aspect Ratio Guidance

| Ratio | Best For | Dimensions Feel |
|---|---|---|
| `16:9` | Landscapes, presentations, diagrams, wide scenes | Wide cinematic |
| `4:3` | Standard photos, UI mockups, documents | Classic monitor |
| `1:1` | Icons, avatars, social media, product shots | Square balanced |
| `9:16` | Portraits, mobile screens, vertical banners | Tall/phone |
| `3:4` | Book covers, posters, portrait photos | Tall classic |

**Rule of thumb:** Match the aspect ratio to the content's natural shape. Landscapes and diagrams → wide. People and tall objects → portrait. Symmetric subjects → square.

## Size Selection

| Size | Resolution | Use Case |
|---|---|---|
| `512` | ~512px | Quick previews, thumbnails, iteration drafts |
| `1K` | ~1024px | Standard output, presentations, web use |
| `2K` | ~2048px | High-quality prints, detailed diagrams, zoom-friendly |

Start with `1K` for most tasks. Use `512` when iterating quickly on prompt wording.

## Iterative Refinement Patterns

### Pattern 1: Progressive Detail

Start broad, then add specificity:

1. `"A cloud architecture diagram"` — test basic composition
2. `"A cloud architecture diagram with three layers: frontend, API, database"` — add structure
3. `"A cloud architecture diagram with three horizontal layers, clean vector style, blue palette, showing frontend load balancer connecting to API microservices connecting to PostgreSQL database"` — full detail

### Pattern 2: Style Transfer

Keep the subject fixed, vary the style:

1. `"A network topology diagram, technical blueprint style"`
2. `"A network topology diagram, colorful infographic style"`
3. `"A network topology diagram, minimalist line art"`

Pick the style that best communicates the content.

### Pattern 3: Composition Adjustment

Fix style, vary framing:

1. `"..., centered composition with equal spacing"`
2. `"..., left-to-right flow with arrows"`
3. `"..., top-down hierarchical layout"`

## Common Pitfalls

| Pitfall | Problem | Fix |
|---|---|---|
| Too vague | `"a diagram"` produces random output | Be specific: `"a three-tier web architecture diagram"` |
| Too long | 500+ word prompts confuse the model | Keep prompts under 200 words; be concise |
| Conflicting instructions | `"minimalist with lots of detail"` | Pick one direction |
| Text-heavy requests | AI-generated text in images is often garbled | Minimize text; add labels in post-processing |
| Wrong aspect ratio | Portrait subject in 16:9 has wasted space | Match ratio to content shape |
| Over-specifying colors | `"#3B82F6 blue with #10B981 green"` — hex codes are unreliable | Use natural language: `"bright blue with green accents"` |

## Domain-Specific Tips

### Technical Diagrams
- Use "clean vector style, white background" for clarity
- Specify layout direction: "left-to-right flow" or "top-down hierarchy"
- Name component types: "rounded rectangles for services, cylinders for databases"
- Request "no text" if you'll add labels programmatically

### Photographs
- Specify lighting: "golden hour", "soft studio lighting", "overcast natural light"
- Include camera perspective: "eye-level", "bird's eye view", "close-up macro"
- Mention depth of field: "shallow depth of field with blurred background"

### Icons and Logos
- Use 1:1 aspect ratio
- Specify "centered on transparent background" or "centered on white background"
- Keep the prompt simple — icons should be recognizable at small sizes

### Presentations
- Use 16:9 for slide backgrounds
- Request "large open areas for text overlay" if used as a background
- Specify "professional, corporate style" for business contexts
