# prompt-dsl Quick Reference

> Load this file when generating .prompt files. Not for end-user consumption.

## Front-Matter Keys

Placed above the `---` separator at the top of the file.

| Key      | Type    | Default        | Description                                       |
|----------|---------|----------------|---------------------------------------------------|
| `data`   | string  | none           | Path to JSON/CSV/XLSX data file to iterate over   |
| `output` | string  | results.json   | Output file path (or directory for per_item)       |
| `collect`| string  | auto-detect    | Collection strategy (see below)                   |
| `vars`   | map     | {}             | Custom variables accessible as `{{name}}`         |
| `sheet`  | string  | (first sheet)  | Excel sheet name for XLSX data files              |
| `docx`   | bool    | false          | Generate .docx companion file(s)                  |

## Collect Strategies

| Strategy     | Behavior                                                    |
|-------------|--------------------------------------------------------------|
| `raw`        | Write first result as-is (auto-detect JSON vs text)         |
| `append_json`| All results as JSON array with key/value/feedback_text      |
| `concatenate`| All results concatenated with double newlines               |
| `per_item`   | Each result as individual file in output directory           |

Auto-detection: `append_json` if `data:` is set, `raw` otherwise.

## Body Directives

### @system ... @end
System prompt prepended to every Claude call.
```
@system
You are a financial analyst. Be precise and cite sources.
@end
```

### @foreach ... @end
Loop template applied to each data item. Variables like `{{KEY}}`, `{{VALUE}}`, and column names are interpolated.
```
@foreach
Analyze the following section: {{KEY}}

Content:
{{VALUE}}
@end
```

### @step <name> ... @end
Pipeline step. Multiple steps run sequentially per item. Reference previous step output with `{{step.name}}` or `{{PREV_OUTPUT}}`.
```
@step generate
Write a summary of: {{VALUE}}
@end

@step validate
Review this output for accuracy:
{{step.generate}}

If correct, return unchanged. If issues found, fix and return corrected version.
@end
```

### @attach <path>
Static file attachment (text files embedded inline, PDFs extracted via pdftotext).
```
@attach reference_doc.pdf
@attach style_guide.md
```

### @attach_from <field>
Dynamic per-row attachment. The named field in each data row contains a file path.
```
@attach_from document_path
```

### @output <format> ... @end
Output format hint appended to prompt.
```
@output json
{
  "summary": "string",
  "score": "number 1-10"
}
@end
```

### @if / @else / @endif
Conditional sections based on variable values.
```
@if {{format}} == "detailed"
Include full analysis with citations.
@else
Provide a brief summary only.
@endif
```

### @include <path>
Include contents of another file (recursive, max depth 10).
```
@include shared_instructions.md
```

### @on_error skip|abort
Error handling strategy. Default: `skip` (continue to next item).
```
@on_error abort
```

## Built-in Variables

| Variable       | Description                              |
|----------------|------------------------------------------|
| `{{KEY}}`      | Current item's key field                 |
| `{{VALUE}}`    | Current item's value field               |
| `{{INDEX}}`    | Current item index (1-based)             |
| `{{TOTAL}}`    | Total number of items                    |
| `{{DATE}}`     | Today's date (ISO format)               |
| `{{PREV_OUTPUT}}`| Output from previous pipeline step    |
| `{{step.name}}`| Output from named pipeline step         |
| `{{column}}`   | Any column name from data (CSV/XLSX)     |

Custom variables from `vars:` front-matter are also available.

## Data Formats

**JSON**: Array of objects. Fields `key` and `value` are used by default. Single-key objects auto-map. All fields available as `{{field_name}}`.

**CSV**: Header row required. `key` defaults to `name` or `title` column. `value` defaults to `text` or `body` column. All columns available as variables.

**XLSX**: Same as CSV. Use `sheet:` to specify non-default sheet. Requires openpyxl.

## CLI Usage

```bash
python3 run_claude.py <file.prompt> [options]

# Chain multiple prompt files
python3 run_claude.py step1.prompt step2.prompt

# Options
--data <path>         Override data file
--output <path>       Override output path
--model <name>        Model: sonnet (default), haiku, opus
--timeout <seconds>   Subprocess timeout (default: 300)
--dry-run             Preview prompts without calling Claude
--debug               Show full prompts sent to CLI
--docx                Generate .docx companion file(s)
```

## Common Patterns

### Per-Item Output with Docx
```yaml
data: employees.csv
output: reports/
collect: per_item
docx: true
---
@system
You are an HR report writer.
@end

@foreach
Write a performance summary for {{name}} ({{department}}).

Key metrics: {{metrics}}
@end
```

### QC Pipeline
```yaml
data: items.json
output: reviewed/
collect: per_item
---
@system
You are an expert editor.
@end

@step generate
{{VALUE}}

Write a detailed analysis of the above.
@end

@step validate
Review this analysis for factual accuracy and completeness:

{{step.generate}}

If it meets quality standards, return it unchanged.
If issues found, fix them and return the corrected version.
@end
```

### Single Prompt with Attachments
```yaml
output: analysis.md
docx: true
---
@system
You are a document analyst.
@end

@attach report.pdf
@attach supplementary_data.csv

Analyze the attached report and data. Provide key findings and recommendations.
```
