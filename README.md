# Claude Code Skills

A collection of personal skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Skills

### [deep-research](./deep-research/)

Multi-step iterative deep research with query decomposition, parallel web search via subagents, source verification, and citation-backed report generation.

**Usage:** `/deep-research [quick|standard|deep] <your research question>`

| Mode     | Search Threads | Iterations | Min Sources | Word Target    |
|----------|---------------|------------|-------------|----------------|
| quick    | 3             | 1          | 5           | 1,500–3,000    |
| standard | 5             | 2          | 10          | 3,000–6,000    |
| deep     | 8             | 3          | 15          | 6,000–10,000   |

**Output:** Research report saved to `~/Documents/research/[topic-slug]_[YYYYMMDD]/report.md` with companion `sources.md`.

### [powerpoint-diagrams](./powerpoint-diagrams/)

Generative-first technical diagrams via python-pptx. Produces standalone Python scripts that generate native, editable PowerPoint diagrams with orthogonal routed connectors, gradient-filled shapes, and region-based layouts.

**Usage:** `/powerpoint-diagrams`

**Triggers:** "create a PowerPoint diagram", "make a flowchart in PowerPoint", "create an org chart", "make an architecture diagram", "generate a PPTX diagram", "draw a diagram in PowerPoint"

**Supported diagram types:** Architecture (hub-and-spoke, layered, L→R flow), Flowchart (linear, branching, decision), Org Chart, Process Flow

**Output:** `{name}.py` (standalone generator script) + `{name}.pptx` (diagram)

**Dependencies:** `python-pptx`, `lxml`

### [prompt-builder](./prompt-builder/)

Build high-quality prompt-dsl `.prompt` files through an interview, construction, QC, and hand-off workflow. Helps users create batch processing workflows without writing Python. All artifacts are saved to organized slug directories (`~/claude/[slug]_[YYYYMMDD]/`).

**Usage:** `/prompt-builder`

**Triggers:** "prompt builder", "build prompt", "create prompt file", "batch process", "process spreadsheet", "process CSV", "process data with Claude", "generate from template", "batch Claude", "prompt pipeline"

**Phases:**
1. **Understand** — Smart-gated interview (skipped if request is already clear)
2. **Build** — Generate the `.prompt` file with correct DSL syntax
3. **QC** — Structural validation, manual review checklist, dry-run preview
4. **Hand Off** — Show run command, offer to execute, remind about reusability

**Features:** CSV/XLSX/JSON/directory/glob iteration, `@validate` auto-retry, `@step` pipelines, `@attach` static and dynamic files, `@if`/`@else` conditionals, `@include` shared fragments, Word `.docx` output

**Dependencies:** `prompt-dsl` (pip package: `pip install prompt-dsl[all]`)

## Installation

Copy (or symlink) a skill directory into `~/.claude/skills/`:

```bash
# Example: install skills
cp -r deep-research ~/.claude/skills/deep-research
cp -r powerpoint-diagrams ~/.claude/skills/powerpoint-diagrams
cp -r prompt-builder ~/.claude/skills/prompt-builder
```

For powerpoint-diagrams, install the Python dependencies:

```bash
pip install python-pptx lxml
```

## License

MIT
