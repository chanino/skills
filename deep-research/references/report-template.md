# Report Template & Writing Standards

## Report Structure

```markdown
# [Research Topic Title]

**Date**: [YYYY-MM-DD]
**Depth**: [quick | standard | deep]
**Sources consulted**: [N]

---

## Executive Summary

[3-5 paragraph summary of key findings. Should stand alone as a complete briefing.
Include the single most important finding, 2-3 supporting findings, and any critical
caveats or limitations. Target: 10-15% of total word count.]

---

## Introduction

[Context and scope of the research question. What was asked, why it matters, and
how the research was structured. Define key terms if needed. 1-2 paragraphs.]

---

## Findings

### [Finding 1 Title]

[Narrative prose with inline citations. Each finding section should have a clear
topic sentence, supporting evidence from 3+ sources, and a synthesis statement.
Present data, quotes, and specific evidence rather than vague assertions.]

### [Finding 2 Title]

[Continue for 4-8 findings depending on topic complexity and depth mode.]

...

---

## Analysis & Synthesis

[Cross-cutting analysis that connects findings. Identify patterns, contradictions,
and implications that emerge from the evidence as a whole. This is where analytical
inferences belong — clearly distinguished from source-grounded facts. 2-4 paragraphs.]

---

## Limitations & Gaps

[What the research could not determine. Sources that were unavailable, questions
that remain open, areas where evidence is thin or conflicting. Be specific. Bullet
list or short paragraphs.]

---

## Recommendations

[If applicable — actionable next steps based on the findings. Each recommendation
should trace back to specific findings. Skip this section if the research question
is purely informational and recommendations would be speculative.]

---

## References

See [sources.md](sources.md) for the complete source list with credibility assessments.

---

*Research conducted using Claude Code deep-research skill. All claims are sourced
from the referenced materials. Analytical inferences are clearly distinguished from
source-grounded facts.*
```

## Writing Standards

### Prose Quality
- **80%+ narrative prose**: Minimize bullet lists in the main body. Use paragraphs with clear topic sentences, supporting evidence, and transitions
- **Specificity over vagueness**: Write "increased 23% from 2023 to 2024 [3]" not "increased significantly"
- **Active voice preferred**: "NIST published the framework [1]" not "The framework was published by NIST"
- **No filler language**: Cut "It is important to note that" — just state the point

### Evidence Standards
- Every factual claim must have at least one inline citation
- Each finding section should draw from 3+ sources minimum
- Direct quotes should be used sparingly (2-4 per report) for maximum impact
- Quantitative data should always include the source and date of the measurement

### Analytical Transparency
- Clearly signal when you are synthesizing vs. reporting: "The evidence suggests..." or "Taken together, these findings indicate..."
- When sources conflict, present both positions with citations before offering analysis
- Never state an inference as if it were a sourced fact

### Section Balance
- No single finding section should exceed 30% of the total findings word count
- The executive summary must cover all major findings, not just the first few
- Limitations section should be substantive, not perfunctory

## Word Targets by Mode

| Mode     | Total Report | Executive Summary | Per Finding Section |
|----------|-------------|-------------------|---------------------|
| quick    | 1,500–3,000 | 200–400           | 200–400             |
| standard | 3,000–6,000 | 400–700           | 300–600             |
| deep     | 6,000–10,000| 700–1,000         | 500–1,000           |

## sources.md Format

The companion `sources.md` file lists all sources in citation order:

```markdown
# Sources

[1] **Title**
    URL: https://...
    Author/Organization: ...
    Date: ...
    Credibility: T1 — Government Primary Source
    Key contribution: What this source contributed to the report

[2] **Title**
    ...
```

Group sources by credibility tier at the end for a summary view:

```markdown
## Source Distribution

- Tier 1 (Authoritative): [N] sources
- Tier 2 (Institutional): [N] sources
- Tier 3 (Journalism/Analysis): [N] sources
- Tier 4 (Commercial): [N] sources
- Tier 5 (User-Generated): [N] sources
```
