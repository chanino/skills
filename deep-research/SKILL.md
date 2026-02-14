---
name: deep-research
description: >
  Multi-step iterative deep research with query decomposition, parallel web search
  via subagents, source verification, and citation-backed report generation.
  Triggers: "deep research", "research this", "investigate", "research report",
  "comprehensive research"
user_invocable: true
---

# Deep Research Skill

You are executing a deep research workflow. Follow these four phases strictly and in order.

## Setup: Parse Arguments

Parse `$ARGUMENTS` to determine the **depth mode** and **research query**:

1. Check if the first word of `$ARGUMENTS` is `quick`, `standard`, or `deep`
   - If yes: use that as the depth mode, and the remainder is the research query
   - If no: default to `standard`, and the entire `$ARGUMENTS` is the research query
2. Set parameters based on depth mode:

| Parameter        | quick | standard | deep |
|------------------|-------|----------|------|
| Search threads   | 3     | 5        | 8    |
| Max iterations   | 1     | 2        | 3    |
| Min sources      | 5     | 10       | 15   |
| Word target      | 1,500–3,000 | 3,000–6,000 | 6,000–10,000 |

3. Generate a topic slug from the query (lowercase, hyphens, max 50 chars) for the output directory.
4. Set the output directory: `~/Documents/research/[topic-slug]_[YYYYMMDD]/`

Tell the user the depth mode, thread count, and that research is beginning.

---

## Phase 1: Scope

Analyze the research query and decompose it into research threads. Consult `references/research-methodology.md` for decomposition strategies matched to the question type.

**Steps:**

1. Identify the question type (factual, comparison, landscape, policy, technical, or hybrid)
2. Identify key entities, temporal scope, and domain
3. Decompose into N research threads (N = search threads for the depth mode), each targeting a **distinct facet** of the query — threads must not substantially overlap
4. For each thread, formulate 2–3 specific search queries following the query formulation tips in the methodology reference

**Output to the user:** A numbered research plan showing each thread with its focus area and planned search queries. Keep this concise — a few lines per thread.

---

## Phase 2: Search

Execute the research plan using parallel subagents. Consult `references/citation-guide.md` for credibility tier definitions.

### Round 1: Primary Search

Spawn **all N threads simultaneously** using the `Task` tool in a **single message** with multiple tool calls:

- `subagent_type`: `general-purpose`
- Each subagent receives a prompt structured as follows:

```
You are a research assistant performing one thread of a larger research project.

**Your research thread**: [Thread title and focus area]

**Research question context**: [The user's original query for context]

**Search queries to try**: [2-3 specific queries from Phase 1]

**Instructions**:
1. Use WebSearch to execute the provided search queries (and variations if initial results are thin)
2. For the most promising results (up to 3-4), use WebFetch to get fuller content
3. Evaluate each source's credibility tier:
   - T1: .gov, .mil, peer-reviewed journals, official standards
   - T2: .edu, research orgs (RAND, MITRE, Brookings), professional associations
   - T3: Major journalism (Reuters, AP, NYT), established trade publications (FedScoop, Nextgov)
   - T4: Vendor whitepapers, corporate blogs, consulting firms
   - T5: Personal blogs, forums, social media, Wikipedia
4. Extract specific facts, data points, quotes, and evidence — not vague summaries

**Return your findings in this exact format for EACH source:**

### Source: [Title of page/document]
- **URL**: [exact URL]
- **Domain type**: [government / academic / journalism / commercial / user-generated]
- **Credibility tier**: [T1 / T2 / T3 / T4 / T5]
- **Date**: [publication date if found, otherwise "not available"]
- **Author/Org**: [author or organization if found, otherwise "not listed"]
- **Key evidence**: [Bullet list of specific facts, data points, and quotes extracted from this source. Be specific and include numbers, dates, and direct quotes where available.]

### Thread Summary
[2-3 sentence summary of what you found across all sources for this thread. Note any gaps or areas where evidence was thin.]
```

### Assessing Round 1 Results

After all subagents return:

1. Collect all sources and deduplicate by URL
2. Count unique sources — compare against the minimum for the depth mode
3. Assess coverage: Does every thread have at least 2 credible sources?
4. Identify gaps: Which threads came back thin? Are there obvious follow-up questions raised by the results?
5. Identify conflicts: Do sources contradict each other on key points?

### Round 2+ (if mode allows and gaps/conflicts exist)

If the depth mode allows more iterations AND (source count is below minimum OR coverage gaps exist OR conflicts need resolution):

Spawn targeted follow-up subagents (2-4 per round) using the same `Task` + `general-purpose` pattern, but with refined prompts that:
- Target specific gaps identified in assessment
- Seek primary sources behind secondary reporting
- Resolve conflicts with more authoritative or recent sources
- Follow leads mentioned in Round 1 results (specific reports, datasets, documents)

Apply the stopping conditions from `references/research-methodology.md`.

**Output to the user:** Brief progress update after each round — how many sources collected, any notable gaps being pursued.

---

## Phase 3: Synthesize

Build the report structure from the collected evidence.

**Steps:**

1. **Assign citation numbers**: Number all unique sources sequentially [1], [2], [3]... in the order they will first appear in the report
2. **Cross-reference claims**: Map each key claim to its supporting source(s). Note where sources agree, where they conflict, and where a claim has only one source
3. **Build narrative outline**: Organize findings into 4–8 thematic sections. Each section should:
   - Have a clear thesis supported by evidence from multiple sources
   - Draw from 3+ sources minimum
   - Be distinct from other sections (minimal overlap)
4. **Identify analytical inferences**: Separate what the sources directly state from what you are inferring by connecting evidence across sources. Mark inferences clearly in your outline
5. **Apply corroboration rules** from `references/citation-guide.md`:
   - T1 sources can stand alone
   - T3-T5 claims need 2+ independent sources
   - Flag any claims that don't meet corroboration thresholds

Do NOT output the synthesis to the user — proceed directly to Phase 4.

---

## Phase 4: Report

Generate the final report following `references/report-template.md` and `references/citation-guide.md`.

**Steps:**

1. Create the output directory:
   ```
   mkdir -p ~/Documents/research/[topic-slug]_[YYYYMMDD]/
   ```

2. Write `report.md` following the template structure:
   - **Title, metadata, date**
   - **Executive summary**: 3-5 paragraphs covering all major findings — must stand alone as a complete briefing
   - **Introduction**: Context, scope, key terms
   - **Findings**: 4-8 sections, each with narrative prose, inline citations `[N]`, specific evidence
   - **Analysis & Synthesis**: Cross-cutting patterns, implications, inferences (clearly marked)
   - **Limitations & Gaps**: What couldn't be determined, thin evidence areas, open questions
   - **Recommendations**: If applicable — traceable to findings. Skip if purely informational
   - **References**: Link to sources.md

3. Write `sources.md` with all sources in citation order:
   - Each entry: number, title, URL, author/org, date, credibility tier, key contribution
   - End with a source distribution summary by tier

4. **Quality checks before writing files:**
   - Every `[N]` citation in the report maps to a real entry in sources.md
   - No fabricated URLs — every URL came from a WebSearch/WebFetch result
   - Word count is within the target range for the depth mode
   - Every finding section draws from 3+ sources
   - Conflicting evidence is presented, not silently resolved
   - Analytical inferences are clearly distinguished from sourced facts

5. Write both files using the Write tool

6. **Display to the user:**
   - The full executive summary
   - Source count and tier distribution (e.g., "15 sources: 4 T1, 3 T2, 5 T3, 2 T4, 1 T5")
   - File paths to both report.md and sources.md
   - Any notable limitations or caveats

---

## Constraints

- **Never fabricate URLs or citations.** Every URL must come from an actual WebSearch or WebFetch result. If you cannot find a source for a claim, mark it `[citation needed]` or remove the claim.
- **Never invent source metadata.** Titles, authors, dates must come from actual source content. Use "not listed" / "not available" / "accessed [date]" when metadata is missing.
- **Domain-neutral source selection.** Do not prefer .gov or .edu sources by default — let the topic determine which sources are relevant. Rank by credibility tier, not domain type. A T3 journalism source with direct reporting may be more valuable than a T1 government page with generic information.
- **Present conflicting evidence.** When sources disagree, show both positions with citations. Offer analysis of why they might differ, but do not silently pick a side.
- **Distinguish fact from inference.** Use clear language: "According to [1]..." for sourced facts vs. "The evidence suggests..." or "Taken together, these findings indicate..." for your analytical conclusions.
- **Respect the depth mode.** Do not exceed the iteration count or significantly overshoot word targets. The user chose the depth for a reason.
- **Be transparent about limitations.** A short, honest report is better than a long one that papers over gaps. The Limitations section is mandatory and must be substantive.
