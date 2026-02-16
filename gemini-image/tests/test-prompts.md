# Test Prompts

Curated test cases for validating gemini-image generation and analysis.

## Generation Test Cases

### G1: Simple Shape (Baseline)

```
A solid red circle on a white background, simple flat icon
```

- **Aspect:** 1:1
- **Size:** 512
- **Expected:** Clean circle, no artifacts, correct color
- **Tests:** Basic generation, color accuracy, shape fidelity

### G2: Landscape Photo

```
A serene mountain lake at sunrise with mist rising from the water, photorealistic, golden hour lighting, wide angle
```

- **Aspect:** 16:9
- **Size:** 1K
- **Expected:** Photorealistic landscape, proper lighting, wide composition
- **Tests:** Style adherence, aspect ratio utilization, mood

### G3: Technical Diagram

```
A three-tier web architecture diagram showing a load balancer connecting to three application servers which connect to a primary database with a read replica, clean vector style, horizontal left-to-right flow, white background, blue and gray color scheme
```

- **Aspect:** 16:9
- **Size:** 1K
- **Expected:** Clean diagram with recognizable components and connections
- **Tests:** Structural clarity, style consistency, layout direction

### G4: Portrait

```
A professional headshot portrait of a business executive, studio lighting, neutral gray background, sharp focus
```

- **Aspect:** 3:4
- **Size:** 1K
- **Expected:** Well-composed portrait, proper lighting, sharp focus
- **Tests:** Portrait aspect ratio, face rendering, lighting

### G5: Icon Set

```
A simple flat design icon of a cloud with an upward arrow, minimalist style, white background, single blue color
```

- **Aspect:** 1:1
- **Size:** 512
- **Expected:** Clean icon, simple shapes, single color
- **Tests:** Minimalist style, icon clarity at small sizes

### G6: Text in Image

```
A motivational poster with the text "KEEP GOING" in large bold white letters centered on a dark blue gradient background
```

- **Aspect:** 9:16
- **Size:** 1K
- **Expected:** Readable text (known challenge for AI generation)
- **Tests:** Text rendering quality, spelling accuracy

---

## Analysis Test Cases

### A1: Alt Text Generation

- **Input:** Any generated test image
- **Prompt:** (default — accessibility description)
- **Expected:** Concise, accurate description suitable for screen readers
- **Tests:** Default prompt behavior, description quality

### A2: Technical Diagram Analysis

- **Input:** G3 output (architecture diagram)
- **Prompt:** Use "Technical Diagram Analysis" template from analysis-templates.md
- **Expected:** Identifies components, connections, layers, and patterns
- **Tests:** Structured analysis, technical vocabulary

### A3: OCR Extraction

- **Input:** Screenshot with visible text
- **Prompt:** Use "OCR / Text Extraction" template
- **Expected:** All text transcribed accurately with position info
- **Tests:** Text extraction accuracy, position awareness

### A4: Photo Description

- **Input:** G2 output (landscape photo)
- **Prompt:** Use "Photo Description" template
- **Expected:** Natural prose description covering scene, mood, lighting
- **Tests:** Creative description, scene understanding

### A5: Comparison Prompt

- **Input:** Any image with multiple elements
- **Prompt:** `"Compare the left and right halves of this image. What are the key differences?"`
- **Expected:** Identifies spatial differences
- **Tests:** Spatial reasoning, comparison ability

### A6: Data Extraction

- **Input:** Chart or graph image
- **Prompt:** Use "Data Extraction from Charts" template
- **Expected:** Data values, trends, chart type identified
- **Tests:** Quantitative extraction, chart understanding

---

## Edge Cases

### E1: Empty Prompt

```bash
python3 scripts/generate_image.py "" -o /tmp/test.png
```

- **Expected:** Exit code 1, error message about empty prompt

### E2: Very Long Prompt

Generate with a 500+ word prompt.
- **Expected:** Either succeeds or fails gracefully (no crash)

### E3: Non-Image File

```bash
python3 scripts/image_to_text.py -i /etc/hostname "Describe this"
```

- **Expected:** Either fails gracefully or Gemini returns an error about invalid image

### E4: Large Image

Analyze a 5000x5000 pixel image.
- **Expected:** Succeeds or reports file size limit clearly

### E5: Missing API Key

```bash
unset GEMINI_API_KEY && python3 scripts/generate_image.py "test" -o /tmp/test.png
```

- **Expected:** Exit code 1, error message mentioning API key with link to AI Studio
