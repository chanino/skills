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

### [prompt-runner](./prompt-runner/)

Interactive workflow for building, validating, and running prompt-dsl `.prompt` files that process data through Claude. Guides users from requirements gathering through `.prompt` file generation, validation, dry-run preview, execution, and result delivery.

**Usage:** `/prompt-runner`

**Triggers:** "prompt runner", "batch process", "process spreadsheet", "process CSV", "process data with Claude", "generate from template", "batch Claude", "prompt pipeline"

**Phases:**
1. **Interview** — Gather requirements via progressive questions
2. **Validate** — Pre-flight checks on data files, attachments, dependencies
3. **Generate** — Build a `.prompt` file from interview answers
4. **Preview** — Dry-run to verify prompt structure
5. **Execute** — Run the prompt file through Claude
6. **Deliver** — Present results and remind about reuse

**Features:** CSV/XLSX/JSON data iteration, per-item output files, static and dynamic attachments, QC validation pipelines, Word `.docx` generation

**Dependencies:** `run_claude.py` (prompt-dsl runner), optionally `openpyxl` (XLSX), `python-docx` (Word output), `pdftotext` (PDF attachments)

## Installation

Copy (or symlink) a skill directory into `~/.claude/skills/`:

```bash
# Example: install skills
cp -r deep-research ~/.claude/skills/deep-research
cp -r powerpoint-diagrams ~/.claude/skills/powerpoint-diagrams
cp -r prompt-runner ~/.claude/skills/prompt-runner
```

For powerpoint-diagrams, install the Python dependencies:

```bash
pip install python-pptx lxml
```

## License

MIT
