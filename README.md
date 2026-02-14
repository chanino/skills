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

## Installation

Copy (or symlink) a skill directory into `~/.claude/skills/`:

```bash
# Example: install deep-research
cp -r deep-research ~/.claude/skills/deep-research
```

## License

MIT
