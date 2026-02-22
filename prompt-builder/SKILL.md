---
name: prompt-builder
description: >
  Build high-quality prompt-dsl .prompt files via interview, construction, QC, and hand-off.
  Helps users create batch processing workflows without writing Python.
  Triggers: "prompt builder", "build prompt", "create prompt file", "batch process",
  "process spreadsheet", "process CSV", "process data with Claude",
  "generate from template", "batch Claude", "prompt pipeline"
user_invocable: true
---

# prompt-builder: Build High-Quality .prompt Files

You guide users through a 4-phase workflow to build, validate, and optionally execute `.prompt` files using the `prompt-dsl` CLI. All artifacts are saved to a slug directory: `~/claude/[slug]_[YYYYMMDD]/`.

**Prerequisite:** `prompt-dsl` must be pip-installed (`pip install prompt-dsl[all]`). Check with `prompt-dsl --help`. If missing, tell the user to install it first.

Work through each phase sequentially. Do not skip phases.

---

## Phase 1: Understand — Smart-Gated Interview

**Smart gate:** If the user's initial request already specifies the task, data source, and desired output (e.g., "create a prompt that summarizes each row in articles.csv"), skip the interview and go directly to Phase 2 using the information provided. Confirm your understanding briefly before proceeding.

Otherwise, ask progressively using AskUserQuestion. Skip questions whose answers are already known from context.

### 1.1 Task Type
Ask: "What kind of task should the prompt perform?"
Options:
- **Summarize** — Condense content into shorter form
- **Analyze** — Extract insights, patterns, or assessments
- **Generate** — Create new content from data (reports, emails, docs)
- **Transform** — Convert content from one format/style to another

### 1.2 Data Source
Ask: "What data will the prompt iterate over?"
Options:
- **CSV/XLSX file** — Spreadsheet with rows to process
- **JSON file** — Array of items to iterate over
- **Directory/glob** — Files in a directory or matching a pattern
- **None** — Single prompt, no iteration

If a file is specified:
- Verify it exists (use Bash `ls` or Read)
- For CSV/XLSX: show column names to the user
- For XLSX: ask which sheet if multiple

### 1.3 Output Format & Collection
Ask: "What output format and collection strategy?"
Options:
- **Per-item markdown files** — One .md file per data row in output directory (Recommended)
- **Single combined file** — All results concatenated into one file
- **JSON array** — All results as a JSON array
- **Per-item with Word (.docx)** — One Word doc per data row

Map to collect strategies: `per_item`, `concatenate`, `append_json`, `per_item` + `--docx`.

### 1.4 Attachments
Ask: "Are there files to attach to the prompt?"
Options:
- **Static context files** — Same file(s) attached to every prompt (style guides, templates, reference docs)
- **Per-row dynamic files** — A data column contains file paths to attach per item
- **Both** — Static context + per-row files
- **None** — No attachments needed

If static: ask for file path(s), verify they exist.
If per-row: ask which column contains file paths.

### 1.5 QC Approach
Ask: "How should output quality be checked?"
Options:
- **Validation rules** — Automated checks (word count, required content, JSON format) with auto-retry (Recommended)
- **Pipeline QC step** — Add a second @step that reviews and fixes the first step's output
- **None** — Single pass, no QC

If validation rules: ask what rules (suggest based on task type — e.g., min_words for summaries, json for structured output).
If pipeline QC: ask what criteria the QC step should check.

### 1.6 Custom Instructions
Ask: "Any specific instructions? (tone, format, constraints, length, audience)"
Options:
- **Yes** — I have specific instructions
- **No** — The task description is sufficient

If yes: collect as free text.

### Summary
Present a summary table and confirm:
```
Task:           Summarize articles
Data:           articles.csv (47 rows, columns: title, author, content, date)
Output:         Per-item markdown → ~/claude/article-summaries_20260221/
Attachments:    None
QC:             @validate — min_words: 50, max_words: 300
Instructions:   Professional tone, include key takeaways
```
Ask user to confirm or adjust before proceeding.

---

## Phase 2: Build — Generate the .prompt File

### 2.1 Create Slug Directory

Generate a slug from the task description and today's date:
```bash
mkdir -p ~/claude/[slug]_[YYYYMMDD]/
```
Example: `~/claude/article-summaries_20260221/`

### 2.2 Read DSL Reference

Read the DSL reference: `~/.claude/skills/prompt-builder/references/dsl-reference.md`

Use this to ensure correct syntax for all directives.

### 2.3 Construct the .prompt File

Build the file with these conventions:

**Front-matter:**
- `output:` — use absolute path to ensure files land in the slug directory (e.g., `/Users/.../[slug]_[YYYYMMDD]/output/` for per_item). Relative paths resolve from the working directory, not the .prompt file.
- `collect:` — strategy from interview
- `vars:` — any user-defined variables (tone, constraints, etc.)
- Do NOT use `data:` in front-matter — prefer `@foreach <source>` inline syntax

**Body:**
- Use `@foreach <source>` with inline source path (preferred over `data:` front-matter)
- For data files not in the slug directory, use absolute paths (don't copy large files)
- Add `@attach` for static context files (use absolute paths)
- Add `@attach_from <column>` or `@attach {{column}}` for per-row dynamic files
- Use `@if`/`@else`/`@endif` for conditional logic when appropriate
- Add `@output` block if specific output structure is needed
- Add `@validate` block if validation rules were chosen
- Use `@step` blocks if pipeline QC was chosen

**Naming:** Save as `~/claude/[slug]_[YYYYMMDD]/[task-name].prompt`

### 2.4 Review

- Show the full .prompt file to the user
- Explain key parts briefly
- Ask if they want any changes before QC

---

## Phase 3: QC — Three-Part Quality Check

### 3a: Structural Validation

Run:
```bash
prompt-dsl validate ~/claude/[slug]/[file].prompt
```

Show results. If errors, fix and re-validate.

### 3b: Manual Review Checklist

Check these yourself (do not ask the user):
- All `@foreach`/`@step`/`@if`/`@output`/`@validate` blocks are properly closed with `@end` or `@endif`
- Front-matter keys are valid (`data`, `output`, `collect`, `vars`, `sheet`, `on_error`)
- All `{{variables}}` match data column names or built-in variables
- `@attach` paths exist (verify with ls/Read)
- `@attach_from` column names exist in the data file
- `collect` strategy matches the output path setup (directory for `per_item`, file for others)

If issues found, fix them and show the updated file.

### 3c: Dry Run

Run:
```bash
prompt-dsl run ~/claude/[slug]/[file].prompt --dry-run
```

Show the user:
- Number of items that will be processed
- Sample of the first prompt that would be sent
- Output path

Ask if changes are needed. If yes, iterate (edit file, re-validate, re-dry-run).

---

## Phase 4: Hand Off — Show Command & Offer Execution

### 4.1 Show Run Command

Display the exact command:
```
prompt-dsl run ~/claude/[slug]/[file].prompt [--backend X] [--model Y] [--docx]
```

Include relevant flags:
- `--backend` if user specified a non-default backend
- `--model` if user specified a model
- `--docx` if Word output was requested

### 4.2 Offer to Execute

Ask: "Want me to run this now?"
Options:
- **Yes** — Run it now
- **No** — I'll run it myself later

If yes:
- Execute the command
- Show progress as it runs
- When done, list the output files in the slug directory
- Preview one result (read the first output file)

### 4.3 Wrap Up

- Show the slug directory contents (`ls ~/claude/[slug]/`)
- Remind about reusability:
  ```
  Your .prompt file is saved at: ~/claude/[slug]/[file].prompt
  Re-run anytime: prompt-dsl run ~/claude/[slug]/[file].prompt
  Edit the .prompt file to adjust behavior without rebuilding from scratch.
  ```

---

## Error Recovery

### prompt-dsl not installed
```bash
pip install prompt-dsl[all]
```

### Missing data file
- Ask user for correct path
- Re-run from Phase 3

### Validation failures
- Fix the .prompt file
- Re-run `prompt-dsl validate`

### Execution failures (partial)
- The runner skips failed items by default (`on_error: skip`)
- Show which items failed
- Offer to re-run with `--debug` for details

### Empty output
- Check if prompt is too vague
- Suggest more specific instructions
- Try `--debug` to inspect what was sent

---

## Key Conventions

- All artifacts go in `~/claude/[slug]_[YYYYMMDD]/`
- Prefer `@foreach <source>` inline syntax over `data:` front-matter
- Use absolute paths for data files outside the slug directory
- Use `@validate` for automated QC (preferred over pipeline QC steps for simple checks)
- Use `@step` pipeline for complex QC that requires AI judgment
- The `prompt-dsl` CLI is the execution engine — never reference `run_claude.py`
