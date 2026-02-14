# Deep Research Scoring Rubric

DRACO-inspired 4-dimension manual scoring rubric for evaluating deep research output quality.

## Dimensions and Weights

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| Factual Accuracy | 40% | Correctness, source backing, no fabrication |
| Breadth & Depth | 25% | Coverage completeness, progressive refinement |
| Citation Quality | 20% | Source credibility, corroboration, traceability |
| Presentation | 15% | Clarity, structure, actionability |

---

## Dimension 1: Factual Accuracy (40%)

| Score | Criteria |
|-------|----------|
| **5** | All claims are source-backed. No fabricated URLs or citations. Conflicting evidence presented with both sides. Zero factual errors detectable. |
| **4** | All major claims source-backed. 1–2 minor unsourced claims (non-critical). No fabrication. Conflicts mostly surfaced. |
| **3** | Most claims source-backed but some key claims lack citations. No fabrication. Some conflicts silently resolved. |
| **2** | Multiple unsourced or weakly-sourced claims. Possible fabricated URL or citation. Conflicts ignored. |
| **1** | Widespread unsourced claims, fabricated citations, or demonstrably false statements. |

**Key checks**:
- Spot-check 3–5 specific claims by visiting the cited URL
- Verify that direct quotes actually appear in the cited source
- Look for claims that feel too precise or convenient (hallucination signal)

---

## Dimension 2: Breadth & Depth (25%)

| Score | Criteria |
|-------|----------|
| **5** | All facets of the query covered. Progressive deepening visible (survey → targeted dives). No obvious gaps. Appropriate depth for the mode. |
| **4** | Most facets covered well. 1 minor facet underexplored. Depth appropriate for mode. Evidence of iterative refinement. |
| **3** | Core question answered but 1–2 significant facets missing or shallow. Depth adequate but not thorough. |
| **2** | Narrow coverage — only addresses the most obvious aspects. Feels like a single search pass. |
| **1** | Barely addresses the query. Major facets missing. Reads like a summary of 1–2 sources. |

**Key checks**:
- Does the thread decomposition from Phase 1 map to the final findings?
- Are there facets a domain expert would expect that are missing?
- Does the report go beyond what a simple web search would yield?

---

## Dimension 3: Citation Quality (20%)

| Score | Criteria |
|-------|----------|
| **5** | Strong tier distribution (multiple T1/T2). Corroboration rules followed. Every finding cites 3+ sources. Citation chains followed to primary documents. Source metadata complete. |
| **4** | Good tier distribution. Most corroboration rules followed. 1–2 findings have <3 sources. Source metadata mostly complete. |
| **3** | Acceptable distribution but leans T3–T4. Some corroboration gaps. Source metadata has some "not available" entries. |
| **2** | Mostly T4–T5 sources. Corroboration rules frequently violated. Many metadata gaps. |
| **1** | Few sources, mostly low-tier. No corroboration. Sources feel cherry-picked or irrelevant. |

**Key checks**:
- Count sources by tier — is the distribution reasonable for the topic?
- Are T3–T5 claims corroborated by 2+ independent sources?
- Were primary documents cited (not just journalism about those documents)?

---

## Dimension 4: Presentation (15%)

| Score | Criteria |
|-------|----------|
| **5** | Clear structure. Executive summary is self-contained and actionable. Findings flow logically. Prose quality high (≥80% narrative). Limitations honest and specific. **"So what?" is clear** — reader knows what to do with this information. |
| **4** | Good structure. Exec summary covers key points. Mostly narrative prose. Limitations present. Actionable takeaways mostly clear. |
| **3** | Adequate structure but exec summary incomplete or findings poorly organized. Mix of prose and bullet lists. Limitations perfunctory. Reader has to work to extract actionable insights. |
| **2** | Disorganized. Exec summary missing key findings. Heavy bullet lists. Limitations section missing or trivial. No clear "so what?". |
| **1** | Unstructured data dump. No exec summary or useless one. No limitations. Reader cannot extract value without significant effort. |

**Key checks**:
- Read ONLY the executive summary — could you brief someone from this alone?
- Is there a clear answer to "so what should I do with this information?"
- Are analytical inferences clearly distinguished from sourced facts?

---

## Scoring Template

```
Query: [test query]
Mode: [quick / standard / deep]
Date: [YYYY-MM-DD]

| Dimension | Score (1-5) | Weight | Weighted |
|-----------|-------------|--------|----------|
| Factual Accuracy | _ | 0.40 | _ |
| Breadth & Depth | _ | 0.25 | _ |
| Citation Quality | _ | 0.20 | _ |
| Presentation | _ | 0.15 | _ |
| **TOTAL** | | | **_._ / 5.0** |

Notes:
- [Strengths]
- [Weaknesses]
- [Gate observations: which gates triggered remediation?]
```

**Target score**: ≥ 3.5 / 5.0 for all test queries.

**Scoring guidance**:
- Score each dimension independently — a report can have great sources (Citation Quality 5) but poor organization (Presentation 2)
- Be strict on Factual Accuracy — this is the most important dimension and has the highest weight for good reason
- Consider the depth mode when scoring Breadth & Depth — a quick mode report should not be penalized for less depth than a deep mode report
