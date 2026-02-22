> **Source:** Copied from `~/prompt-dsl/docs/dsl-reference.md`.
> To refresh: `cp ~/prompt-dsl/docs/dsl-reference.md ~/.claude/skills/prompt-builder/references/dsl-reference.md`

# prompt-dsl: DSL Syntax Reference

This document is the complete reference for the `.prompt` file format used by prompt-dsl.

A `.prompt` file is a plain-text file with two sections:

1. **Front-matter** -- key-value configuration at the top of the file
2. **Body** -- directives and prompt text that define what the AI should do

---

## Front-matter

Front-matter appears at the top of the file as `key: value` lines, terminated by a line containing only `---`.

```
data: articles.csv
output: summaries/output.md
collect: concatenate
vars:
  tone: professional
  max_words: 500
---
```

If no `---` separator is present, the entire file is treated as body content with no front-matter.

### Front-matter Keys

| Key       | Type   | Default | Description                                                   |
|-----------|--------|---------|---------------------------------------------------------------|
| `data`    | path   | (none)  | Path to a JSON, CSV, or XLSX data file (relative to `.prompt` file). Optional when using `@foreach <source>` inline syntax. |
| `output`  | path   | (none)  | Output file or directory path                                 |
| `collect` | string | `raw`   | How to combine results: `raw`, `append_json`, `concatenate`, `per_item` |
| `vars`    | map    | (none)  | User-defined variables available via `{{var_name}}`           |
| `sheet`   | string | (none)  | Excel sheet name (for XLSX data files)                        |
| `on_error`| string | `skip`  | Error strategy: `skip` (continue on failure) or `abort` (stop immediately) |

### The `vars` Block

The `vars` key accepts a nested block of key-value pairs, indented with at least two spaces:

```
vars:
  language: English
  style: academic
  include_citations: true
---
```

These variables become available as `{{language}}`, `{{style}}`, and `{{include_citations}}` in the body. Boolean values `true` and `false` are recognized and stored accordingly.

### The `collect` Modes

| Mode          | Behavior                                                      |
|---------------|---------------------------------------------------------------|
| `raw`         | Keep only the last result (default)                           |
| `concatenate` | Join all results with double newlines                         |
| `append_json` | Parse each result as JSON and collect into a JSON array       |
| `per_item`    | Write each result as a separate file in the output directory  |

---

## Body Directives

The body section (everything after `---`) contains directives and prompt text. Directives are lines that begin with `@`.

### @foreach / @end

Iterates over each item in a data source. The template inside is rendered once per data item, with row-specific variables substituted.

#### Inline source (preferred)

The data source can be specified directly on the `@foreach` line:

```
output: descriptions/
collect: per_item
---
@foreach products.csv
You are a product copywriter.

Write a compelling product description for:

Product: {{name}}
Category: {{category}}
Price: {{price}}

Target audience: {{audience}}
@end
```

This is equivalent to the older syntax with `data:` in front-matter (see below), but keeps the data source and iteration directive together for clarity.

#### Front-matter source (backward compatible)

The data source can also be specified via the `data:` front-matter key:

```
data: products.csv
output: descriptions/
collect: per_item
---
@foreach
...
@end
```

If both an inline source and `data:` front-matter are present, the inline source takes priority and a warning is printed.

#### Directory source

Iterate over all text files in a directory:

```
@foreach docs/
Summarize this section:

Filename: {{FILENAME}}

{{VALUE}}
@end
```

Each file becomes a data item with these variables:
- `{{KEY}}` -- file stem (name without extension)
- `{{VALUE}}` -- file contents
- `{{FILENAME}}` -- full filename with extension
- `{{PATH}}` -- path relative to the directory
- `{{EXT}}` -- file extension (including dot)

Hidden files (starting with `.`) are skipped silently. Binary files are skipped with a warning.

#### Glob source

Iterate over files matching a glob pattern:

```
@foreach reports/*.md
Summarize: {{FILENAME}}
{{VALUE}}
@end
```

Supports standard glob syntax including `**` for recursive matching:

```
@foreach src/**/*.py
Review this Python file:
{{VALUE}}
@end
```

If the pattern matches no files, a `DataError` is raised.

#### XLSX bracket syntax

Specify an Excel sheet name inline using brackets:

```
@foreach data.xlsx[Sheet1]
Process row: {{name}}
@end
```

This is equivalent to using `data:` and `sheet:` front-matter keys together. If both bracket syntax and the `sheet:` front-matter key are present, the bracket syntax takes priority.

When `@foreach` is present, the prompt inside the block is executed once for every item in the data source. Each item's fields are available as `{{field_name}}` variables.

### @step name / @end

Defines a named step in a multi-step pipeline. Steps execute sequentially, and each step can reference the output of previous steps.

```
@step research
Research the following topic thoroughly:
{{topic}}

Provide key facts, statistics, and expert opinions.
@end

@step draft
Using the research below, write a 1000-word article:

{{PREV_OUTPUT}}

Write in a {{tone}} tone for a general audience.
@end

@step review
Review the following article for accuracy and clarity:

{{step.draft}}

Suggest specific improvements.
@end
```

Key behaviors:

- Steps run in the order they appear in the file.
- `{{PREV_OUTPUT}}` contains the output of the immediately preceding step.
- `{{step.name}}` references the output of any named step (e.g., `{{step.research}}`).
- Output instructions from `@output` are appended only to the final step.

### Simple Prompt (No Directives)

If the body contains neither `@foreach` nor `@step`, the entire body text (minus `@output` blocks) is treated as a single prompt:

```
output: result.md
---
You are a helpful assistant.

Explain the difference between TCP and UDP.
Include a comparison table.
```

This is equivalent to a single `@step main` wrapping the body text.

### @attach path

Attaches a file to the prompt. Paths are relative to the `.prompt` file.

```
@foreach
Review the following code file and identify bugs:

@attach {{filename}}

Provide your review as a numbered list.
@end
```

#### Text files

Text files (`.py`, `.txt`, `.md`, `.csv`, etc.) are inlined directly into the prompt with a header and footer:

```
--- filename.py ---
<file contents>
---
```

#### Binary files (PDF, images)

Binary files with recognized extensions are collected as multimodal attachments and sent to the backend alongside the text prompt. The supported binary extensions are:

`.pdf`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.tif`, `.webp`, `.svg`, `.heic`, `.heif`

A placeholder is left in the prompt text:

```
[Attached binary file: report.pdf]
```

**Backend support:** Currently, only the Gemini backend supports multimodal attachments (via REST API). Claude and OpenAI backends will print a warning and process the text-only prompt. If a file cannot be decoded as UTF-8 text and does not have a recognized binary extension, it is treated as binary.

#### Missing files

When the file is not found, the directive is replaced with:

```
[Attachment not found: filename.py]
```

### @attach_from field

Attaches the file whose path is stored in the named field of the current data row. This is useful when your data file contains a column of file paths.

Given a CSV:
```csv
name,source_file
Widget,src/widget.py
Gadget,src/gadget.py
```

```
data: components.csv
---
@foreach
Review the implementation of {{name}}:

@attach_from source_file

Summarize what this component does.
@end
```

This is equivalent to `@attach {{source_file}}` -- the field value is resolved to a path and the file contents are inlined.

### @output format / @end

Defines output formatting instructions that are appended to the prompt (or to the final step in a pipeline). Use this to control the structure of the AI's response.

```
@output markdown
Respond using the following structure:

## Summary
<one paragraph summary>

## Key Points
<bulleted list>

## Recommendation
<one paragraph>
@end
```

The format keyword (e.g., `markdown`) after `@output` is informational; the actual formatting instructions are in the block body.

### @validate [max_retries] / @end

Validates LLM output against a set of rules after generation. On failure, the prompt is automatically retried with validation errors appended as feedback.

```
@foreach articles.csv
Summarize {{title}} in bullet points with key facts.
@end

@validate 2
min_words: 50
max_words: 300
contains: •
not_contains: **DISCLAIMER
@end
```

The optional number after `@validate` sets the maximum retry count (default: 1). On each retry, the original prompt is resent with validation errors appended:

```
[Your previous response failed validation: output has 15 words (minimum: 50), missing required text: •. Please fix these issues.]
```

#### Supported Rules

| Rule | Syntax | Description |
|------|--------|-------------|
| `min_words` | `min_words: N` | Output must have at least N words |
| `max_words` | `max_words: N` | Output must have at most N words |
| `contains` | `contains: text` | Output must contain the literal text |
| `not_contains` | `not_contains: text` | Output must NOT contain the literal text |
| `matches` | `matches: /regex/` | Output must match the regex pattern |
| `json` | `json` | Output must be valid JSON |
| `json_keys` | `json_keys: key1, key2` | Output must be valid JSON containing these keys |

#### Behavior

- **No rules**: If the `@validate` block is empty, no validation is performed.
- **Retries exhausted**: The last output is kept and a warning is printed to stderr.
- **Without `@foreach` or `@step`**: Validation applies to the single prompt.
- **With `@step` pipeline**: Validation applies to the last step only.
- **Invalid rule syntax**: A `ParseError` is raised at parse time.
- **`max_retries: 0`**: Validate once, warn on failure but keep output (no retries).
- **Dry-run mode**: Validation is skipped (no real output to validate).

### @if / @else / @endif

Conditional blocks that include or exclude sections of the prompt based on variable values. Supports `==` and `!=` operators.

```
@foreach
Translate the following text:

{{text}}

@if {{language}} == Spanish
Translate to Spanish. Use formal "usted" form.
@else
Translate to {{language}}.
@endif

@if {{include_notes}} != false
Include translator notes about any idioms or cultural references.
@endif
@end
```

Conditions compare a variable against a literal string value:

- `{{var}} == value` -- true if the variable equals the value
- `{{var}} != value` -- true if the variable does not equal the value

Nested `@if` blocks are supported:

```
@if {{format}} == detailed
Provide a detailed analysis.
@if {{include_examples}} == true
Include at least 3 examples.
@endif
@else
Provide a brief summary.
@endif
```

If a variable referenced in a condition is not defined, it is treated as an empty string.

### @include path

Includes the contents of another file at the directive location, before any other parsing. This is useful for sharing common prompt fragments across multiple `.prompt` files.

```
@include shared/system-prompt.txt
@include shared/output-format.txt

Analyze the following data:
{{VALUE}}
```

Includes are resolved recursively (up to a depth of 10 to prevent circular references). The path is relative to the `.prompt` file.

### @on_error skip|abort

Can also be set in front-matter. Controls what happens when an AI call fails for a particular data row:

- `skip` (default) -- log the error and continue to the next item
- `abort` -- stop execution immediately

```
on_error: abort
---
@foreach
...
@end
```

---

## Variable Interpolation

Variables are referenced with double curly braces: `{{variable_name}}`. They are replaced with their values during prompt rendering.

### Variable Resolution Order

When a `{{name}}` is encountered, it is resolved in this order:

1. **Data row columns** -- column names from the current CSV/JSON/XLSX row
2. **Built-in variables** -- `KEY`, `VALUE`, `INDEX`, `TOTAL`, `DATE`, `PREV_OUTPUT`, `step.*`
3. **Front-matter `vars`** -- user-defined variables from the `vars:` block

If a variable is not found in any source, the `{{name}}` placeholder is left as-is in the output (not replaced, not removed).

### Built-in Variables

| Variable          | Available In     | Description                                              |
|-------------------|------------------|----------------------------------------------------------|
| `{{KEY}}`         | `@foreach`       | Identifier for the current item (first column or dict key) |
| `{{VALUE}}`       | `@foreach`       | Primary content of the current item                      |
| `{{INDEX}}`       | `@foreach`       | 1-based index of the current item                        |
| `{{TOTAL}}`       | `@foreach`       | Total number of data items                               |
| `{{DATE}}`        | everywhere       | Today's date in ISO format (YYYY-MM-DD)                  |
| `{{PREV_OUTPUT}}` | `@step` (2nd+)   | Output of the immediately preceding step                 |
| `{{step.name}}`   | `@step` (2nd+)   | Output of the named step                                 |

### Data Column Variables

Every column in the data file is available as a variable. For a CSV with headers `name`, `category`, `description`:

```csv
name,category,description
Widget,Tools,A versatile multi-purpose tool
Gadget,Electronics,A smart home controller
```

The variables `{{name}}`, `{{category}}`, and `{{description}}` are available inside `@foreach`.

---

## Data Sources

Data sources provide items for `@foreach` iteration. They can be specified either inline on the `@foreach` line or via the `data:` front-matter key. Supported sources:

### JSON

**Array of objects:**
```json
[
  {"name": "Alice", "role": "Engineer", "years": 5},
  {"name": "Bob", "role": "Designer", "years": 3}
]
```

`KEY` is set to the first field's value. Each object key becomes a variable.

**Key-value object:**
```json
{
  "intro": "Write an introduction chapter",
  "methods": "Describe the methodology",
  "results": "Present the findings"
}
```

`KEY` is the object key, `VALUE` is the object value.

### CSV

Standard comma-separated values with a header row:

```csv
topic,difficulty,audience
Machine Learning,intermediate,developers
Quantum Computing,beginner,students
```

The first column value is used as `KEY`.

### XLSX

Excel spreadsheets. The first row is treated as headers. Use the `sheet` front-matter key to specify a sheet name; otherwise the active sheet is used.

```
data: survey-data.xlsx
sheet: Responses
---
```

Requires `openpyxl` to be installed (`pip install prompt-dsl[xlsx]`).

Bracket syntax is also supported for specifying the sheet inline: `@foreach data.xlsx[Sheet1]`

### Directory

All text files in a directory, sorted alphabetically. Hidden files and binary files are excluded.

```
@foreach docs/
Summarize: {{FILENAME}}
{{VALUE}}
@end
```

### Glob Pattern

Files matching a glob pattern. Supports `*`, `?`, `[...]`, and `**` for recursive matching.

```
@foreach reports/**/*.md
Process: {{FILENAME}}
{{VALUE}}
@end
```

---

## Complete Examples

### Example 1: Simple Single Prompt

```
output: explanation.md
---
You are a computer science professor.

Explain how hash tables work. Include:
- The basic concept
- How collisions are handled
- Time complexity for common operations

@output markdown
Use clear headings and include a simple diagram using ASCII art.
@end
```

Run:
```
prompt-dsl run explain.prompt
```

### Example 2: Batch Processing with CSV

```
output: summaries.md
collect: concatenate
vars:
  max_words: 200
---
@foreach articles.csv
You are a technical editor who writes concise summaries.

Summarize the following article in no more than {{max_words}} words:

Title: {{title}}
Author: {{author}}

{{content}}
@end

@output markdown
## {{title}}
*By {{author}}*

<summary here>
@end
```

### Example 3: Multi-Step Pipeline

```
output: report.md
vars:
  topic: renewable energy trends 2025
---
@step research
What are the most important developments in {{topic}}?
List the top 5 with supporting data.
@end

@step analyze
Given these developments:

{{PREV_OUTPUT}}

Analyze the implications for the industry over the next 5 years.
@end

@step write
Write a professional report combining the research and analysis:

Research:
{{step.research}}

Analysis:
{{step.analyze}}

Format as a complete report with executive summary, findings, and recommendations.
@end
```

### Example 4: Conditional Processing

```
data: tasks.json
output: results/
collect: per_item
---
@foreach
@if {{type}} == code_review
Review the following code for bugs and improvements:
@attach {{file}}
@else
@if {{type}} == documentation
Write documentation for the following:
@attach {{file}}
@else
Analyze the following:
{{VALUE}}
@endif
@endif
@end
```

### Example 5: Using @include for Shared Prompts

**shared/tone.txt:**
```
Write in a professional but accessible tone.
Avoid jargon. Use short sentences.
```

**generate.prompt:**
```
data: topics.json
output: articles/
collect: per_item
---
@foreach
You are a content writer.
@include shared/tone.txt

Write an article about: {{VALUE}}
@end
```

---

## Processing Order

When a `.prompt` file is executed, processing occurs in this order:

1. **Parse front-matter** -- extract configuration keys and `vars`
2. **Resolve @include directives** -- inline included files (recursive, up to depth 10)
3. **Extract directives** -- parse `@foreach`, `@step`, `@output` blocks
4. **Load data** -- if an inline source (`@foreach <source>`) or `data` front-matter key is present, load the data source (file, directory, or glob)
5. **For each item (or once if no data):**
   a. Build variable context (built-ins + data row + vars)
   b. Process `@if` / `@else` / `@endif` conditionals
   c. Interpolate `{{variables}}` (so `@attach {{filepath}}` works)
   d. Resolve `@attach` directives (inline text files, collect binary attachments)
   e. Append `@output` instructions (on last step only)
   f. Send to AI backend (with binary attachments if present)
   g. If `@validate` present: check rules, retry on failure (up to max_retries)
6. **Collect results** -- combine outputs according to `collect` mode
7. **Write output** -- save to file(s) specified by `output`

---

## CLI Commands

### `prompt-dsl run`

Execute a `.prompt` file.

```
prompt-dsl run <prompt_file> [options]
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--backend {claude,openai,gemini}` | `-b` | auto-detect | AI backend to use |
| `--model MODEL` | `-m` | (backend default) | Model name override |
| `--timeout TIMEOUT` | `-t` | 120 | Per-call timeout in seconds |
| `--dry-run` | `-n` | off | Preview prompts without calling the AI |
| `--debug` | `-d` | off | Show debug output |
| `--docx` | | off | Convert output to Word format (.docx) |

**Examples:**
```bash
prompt-dsl run hello.prompt
prompt-dsl run summarize.prompt --backend claude --model claude-sonnet-4-5
prompt-dsl run summarize.prompt --dry-run
prompt-dsl run report.prompt --docx
```

### `prompt-dsl validate`

Validate a `.prompt` file without running it. Checks syntax, data file existence, and optionally backend availability.

```
prompt-dsl validate <prompt_file> [options]
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--backend {claude,openai,gemini}` | `-b` | (none) | Check specific backend availability |

**Examples:**
```bash
prompt-dsl validate my-prompt.prompt
prompt-dsl validate my-prompt.prompt --backend claude
```
