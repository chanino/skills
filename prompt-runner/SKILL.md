---
name: prompt-runner
description: >
  Interactive workflow for building, validating, and running prompt-dsl .prompt files
  that process data through Claude. Guides users from requirements gathering through
  .prompt file generation, validation, dry-run preview, execution, and result delivery.
  Triggers: "prompt runner", "run prompt", "batch process", "process spreadsheet",
  "process CSV", "process data with Claude", "generate from template",
  "run prompt file", "batch Claude", "prompt pipeline"
user_invocable: true
---

# prompt-runner: Interactive Batch Processing Workflow

You guide users through a 6-phase workflow to build, validate, and execute `.prompt` files using the `run_claude.py` DSL runner. The runner lives at `~/claude/prompt-dsl/run_claude.py`.

Work through each phase sequentially. Do not skip phases. Use AskUserQuestion for structured choices and confirm before executing.

---

## Setup (first-time installation)

If the user is setting up on a new system, they need these files in `~/claude/prompt-dsl/`:

```bash
# Create the working directory
mkdir -p ~/claude/prompt-dsl/tools

# Copy the runner and tools from the skill's scripts directory
# (skill installed at ~/.claude/skills/prompt-runner/)
cp ~/.claude/skills/prompt-runner/scripts/run_claude.py ~/claude/prompt-dsl/
cp ~/.claude/skills/prompt-runner/scripts/tools/md_to_docx.py ~/claude/prompt-dsl/tools/
cp ~/.claude/skills/prompt-runner/scripts/tools/xlsx_to_text.py ~/claude/prompt-dsl/tools/

# Install Python dependencies
pip install openpyxl python-docx
```

After setup the working directory should look like:
```
~/claude/prompt-dsl/
├── run_claude.py          # DSL runner (required)
├── tools/
│   ├── md_to_docx.py     # Word doc output (required for --docx)
│   └── xlsx_to_text.py   # XLSX inspection utility
└── examples/             # (optional) example .prompt files
```

---

## Phase 1: Interview — Gather Requirements

Ask these questions progressively using AskUserQuestion. Adapt follow-ups based on answers.

### 1.1 Task Type
Ask: "What kind of task do you want to perform?"
Options:
- **Summarize** — Condense content into shorter form
- **Analyze** — Extract insights, patterns, or assessments
- **Generate** — Create new content from data (reports, emails, docs)
- **Transform** — Convert content from one format/style to another

If the user picks "Other", ask them to describe freely.

### 1.2 Input Data
Ask: "What data will Claude process?"
Options:
- **Spreadsheet** — Excel (.xlsx) or CSV file with rows to process
- **JSON file** — Array of items to iterate over
- **Single document** — One file to process as a whole
- **No data file** — Just a single prompt with optional attachments

If spreadsheet/JSON/CSV: ask for the file path. Verify it exists.

If spreadsheet: ask which column contains the main content, and which column should be used as the item key/name. Show column names after reading the file.

### 1.3 Context Attachments
Ask: "Are there reference files Claude should see for every item? (e.g., style guides, templates, reference PDFs)"
Options:
- **Yes** — I have files to attach
- **No** — No additional context needed

If yes: ask for file path(s). Support multiple files.

### 1.4 Dynamic Per-Row Attachments
Only ask if data file was provided:
Ask: "Does each row have its own file to attach? (e.g., a column with file paths)"
Options:
- **Yes** — A column contains file paths
- **No** — Same context for all rows

If yes: ask which column contains the file paths.

### 1.5 Output Format
Ask: "What output format do you want?"
Options:
- **Text/Markdown** — Plain text or markdown files
- **JSON** — Structured JSON output
- **Word document (.docx)** — Formatted Word documents

### 1.6 Output Collection
Only ask if data file was provided:
Ask: "How should outputs be collected?"
Options:
- **Per-item files** — One output file per data row (Recommended)
- **Single combined file** — All results concatenated into one file
- **JSON array** — All results as a JSON array with metadata

Map to collect strategies: per_item, concatenate, append_json.

### 1.7 QC / Validation
Ask: "Should Claude review its own output for quality?"
Options:
- **Yes** — Add a QC validation step
- **No** — Single pass is fine

If yes: ask what criteria to validate against. Examples: "factual accuracy", "matches template format", "professional tone", "includes all required sections". Collect as free text.

### 1.8 Output Location
Ask: "Where should output be saved?"
Suggest a sensible default based on context (e.g., `./output/` for per_item, `./results.json` for JSON).
Options:
- **Default** — Use suggested path
- **Custom** — Specify a path

### 1.9 Model
Ask: "Which Claude model?"
Options:
- **Sonnet** — Fast and capable (Recommended)
- **Haiku** — Fastest, good for simple tasks
- **Opus** — Most capable, slower

### 1.10 Custom Instructions
Ask: "Any specific instructions for Claude? (tone, format, constraints, etc.)"
Options:
- **Yes** — I have specific instructions
- **No** — The task description is sufficient

If yes: collect as free text. These become the system prompt or main body instructions.

### Summary
After all questions, present a summary table:
```
Task:           Generate performance reports
Data:           employees.xlsx (47 rows)
Attachments:    template.pdf
Per-row attach: document_path column
Output format:  Word document (.docx)
Collection:     Per-item files → ./reports/
QC:             Yes — "professional tone, all sections present"
Model:          sonnet
```
Ask user to confirm or adjust.

---

## Phase 2: Validate — Pre-flight Checks

Run the validation script:
```bash
python3 ~/.claude/skills/prompt-runner/scripts/validate_inputs.py \
  --data <data_path> \
  --attachments <file1> <file2> ... \
  --output-format <text|json|docx> \
  --collect <strategy>
```

Show the results to the user. If any checks FAIL:
- Explain what's wrong
- Suggest fixes (install commands, correct paths)
- Re-run validation after fixes

Do not proceed to Phase 3 until all checks pass.

---

## Phase 3: Generate .prompt File

Read the DSL reference: `~/.claude/skills/prompt-runner/references/dsl-reference.md`

Build the .prompt file based on interview answers:

### Front-Matter
```yaml
data: <path or omit>
output: <path>
collect: <strategy>
docx: <true if Word output requested>
sheet: <sheet name if XLSX>
vars:
  custom_var: value
```

### Body Construction

**System prompt**: Combine task type + custom instructions into an `@system` block.

**Attachments**: Add `@attach` for each static attachment. Add `@attach_from <column>` if dynamic attachments.

**Main content**: Use `@foreach` if iterating over data, otherwise plain body text.

**If QC requested**: Use pipeline steps instead of `@foreach`:
```
@step generate
<main task prompt with {{KEY}}, {{VALUE}}, column variables>
@end

@step validate
Review the following output against these quality criteria:
<translated QC criteria from interview>

OUTPUT TO REVIEW:
{{step.generate}}

If it meets all criteria, return it unchanged.
If any issues are found, fix them and return the corrected version.
@end
```

**Output format hint**: Add `@output` block if JSON output requested.

### Save and Review
- Save the .prompt file (suggest name based on task, e.g., `generate_reports.prompt`)
- Show the full file to the user
- Ask if they want to edit anything before proceeding

---

## Phase 4: Preview — Dry Run

Run a dry-run to verify the prompt structure:
```bash
python3 ~/claude/prompt-dsl/run_claude.py <file.prompt> --dry-run
```

Show the user:
- Number of items that will be processed
- A sample of the first prompt that would be sent
- Estimated scope (e.g., "Will make 47 Claude API calls")

Ask the user to confirm before executing.

---

## Phase 5: Execute

Run the prompt file:
```bash
python3 ~/claude/prompt-dsl/run_claude.py <file.prompt> --model <model>
```

Add `--docx` flag if Word output was requested and not already in the .prompt front-matter.

Show progress as it runs. The runner prints item-by-item progress.

---

## Phase 6: Deliver Results

After execution completes:

1. **Show output location**: List files in the output directory (for per_item) or show the output file path.

2. **Preview a sample**: Read and display one result file (pick the first non-empty one).

3. **Report failures**: If any items produced empty output, list them so the user knows.

4. **Remind about reuse**: Tell the user the .prompt file is saved and reusable:
   ```
   Your .prompt file is saved at: <path>
   Re-run anytime with: python3 ~/claude/prompt-dsl/run_claude.py <file.prompt>
   ```

---

## Error Recovery

### Missing data file
- Ask user to provide correct path
- Re-run validation

### Missing dependencies (openpyxl, python-docx, pdftotext)
- Provide install command: `pip install <package>`
- Re-run validation after install

### Claude CLI errors
- Check if `claude` is in PATH
- Check if running inside a Claude Code session (CLAUDECODE env var interference)
- Suggest `--debug` flag to see full prompt

### Partial failures (some items error)
- The runner skips failed items by default (`@on_error skip`)
- Show which items failed
- Offer to re-run just the failed items by creating a filtered data file

### Empty output
- Check if the prompt is too vague
- Suggest adding more specific instructions
- Try with `--debug` to inspect what was sent

---

## Key Conventions

- Always resolve file paths relative to the user's working directory
- The runner script is at `~/claude/prompt-dsl/run_claude.py`
- The validation script is at `~/.claude/skills/prompt-runner/scripts/validate_inputs.py`
- For per_item output, the `output:` path is treated as a directory
- Pipeline steps (`@step`) are the mechanism for QC — the validate step sees the generate step's output
- All column names from CSV/XLSX data are available as `{{column_name}}` variables
