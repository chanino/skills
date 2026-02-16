# Image QA Checklist

Use this checklist after generating an image. All 8 checks should pass before delivering to the user. If any check fails, refine the prompt and regenerate (max 3 attempts).

## Checklist

### 1. Prompt Fidelity

Does the image match what was requested?

- [ ] Main subject is present and recognizable
- [ ] Requested style/medium is reflected
- [ ] All specified elements are included (nothing major missing)
- [ ] No unrequested elements that distract or confuse

**Common fix:** Add more specific descriptions for missing elements; remove ambiguous terms.

### 2. Text Rendering

Is text in the image correct? (If text was requested)

- [ ] All words are spelled correctly
- [ ] Text is legible at intended viewing size
- [ ] Font style matches the overall image style
- [ ] No garbled, duplicated, or phantom text

**Common fix:** Minimize text in prompts — AI image generators struggle with text. Consider adding text in post-processing instead.

### 3. Visual Artifacts

Is the image free of AI generation artifacts?

- [ ] No distorted body parts or extra limbs (for people/animals)
- [ ] No blurring or smearing in focal areas
- [ ] No unnatural transitions between elements
- [ ] No repeating patterns that look like tiling errors

**Common fix:** Simplify the composition; reduce the number of subjects; use a more specific style keyword.

### 4. Composition

Is the image well-composed?

- [ ] Subject is properly framed (not cut off unexpectedly)
- [ ] Visual balance is appropriate (not lopsided)
- [ ] Appropriate use of whitespace/negative space
- [ ] No important elements pushed to extreme edges

**Common fix:** Adjust aspect ratio; specify "centered composition" or "balanced layout"; reduce the number of elements.

### 5. Style Consistency

Is the visual style consistent throughout?

- [ ] Same rendering style across all elements
- [ ] No mixing of photorealistic and cartoon elements (unless intended)
- [ ] Consistent level of detail across the image
- [ ] Color palette is cohesive

**Common fix:** Reinforce the style keyword; add "consistent style throughout" to the prompt.

### 6. Resolution and Clarity

Is the image sharp enough for its intended use?

- [ ] No pixelation or excessive compression artifacts
- [ ] Fine details are distinguishable
- [ ] Image size is appropriate for the use case (presentation, web, print)

**Common fix:** Increase `--size` to `2K` for detailed content; use `1K` minimum for presentations.

### 7. Color Accuracy

Are colors appropriate and functional?

- [ ] Colors match any specified palette
- [ ] Sufficient contrast for readability
- [ ] No unintended color casts or tints
- [ ] Colors work for intended context (print-safe, screen-friendly, accessible)

**Common fix:** Specify colors by name ("navy blue", "forest green") rather than hex codes; add "high contrast" for readability.

### 8. Aspect Ratio

Does the aspect ratio serve the content?

- [ ] No important content cropped by the frame
- [ ] Aspect ratio matches the intended display context
- [ ] Subject fills the frame appropriately (no excessive empty space)

**Common fix:** Switch to a more appropriate ratio — see `prompt-guide.md` for ratio guidance.

## Scoring

| Result | Criteria |
|---|---|
| **Pass** | All 8 checks pass |
| **Acceptable** | 6-7 pass, failures are minor and noted to user |
| **Needs refinement** | 5 or fewer pass — refine prompt and regenerate |

## Refinement Process

1. Identify which checks failed
2. Consult `prompt-guide.md` for the relevant fix pattern
3. Modify the prompt — change one or two things at a time
4. Regenerate and re-check
5. Maximum 3 refinement attempts before presenting best result with caveats
