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

You are executing a deep research workflow. Follow these six phases strictly and in order. Each phase ends with a **quality gate** — a role-based checklist that must pass before proceeding.

## Three Review Roles

Every quality gate evaluates from one or more of these perspective lenses. These are NOT separate agents or extra LLM calls — they are viewpoints you adopt when running each gate's checklist.

| Role | Focus | Asks |
|------|-------|------|
| **Researcher** | Methodology, coverage, source quality, rigor | "Is this thorough? Are sources credible? Is the methodology sound?" |
| **Critic** | Adversarial challenge — gaps, weak reasoning, unsupported claims, bias | "What's missing? What would an opponent attack? Where is the evidence thin?" |
| **Decision Maker** | Relevance, actionability, clarity, "so what?" | "Does this answer my question? Can I act on this? What should I do with this information?" |

**Design rationale**: Decision Maker bookends the process (Gates 1 and 5) to ensure relevance. Critic intensifies in the middle (Gates 3–5) where evidence quality matters most. Researcher anchors methodology throughout (Gates 1, 2, 4).

---

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
| Max QA remediation cycles | 1 | 2 | 3 |

3. Generate a topic slug from the query (lowercase, hyphens, max 50 chars) for the output directory.
4. Set the output directory: `~/Documents/research/[topic-slug]_[YYYYMMDD]/`
5. **Detect available search tools** — determine the search method for this session:
   a. Check if WebSearch and WebFetch tools are available to you. If yes → set search mode to `web-native`
   b. If NOT available, run this Bash command to check for Brave Search:
      `python3 ~/skills/deep-research/brave_search.py search "test" 2>&1 | head -5`
      If it returns JSON results → set search mode to `brave-api`
   c. If neither → tell the user no search capability is available and STOP.

Tell the user the depth mode, thread count, search mode, and that research is beginning.

### Search Tool Reference (brave-api mode)

When search mode is `brave-api`, subagents use these Bash commands instead of WebSearch/WebFetch:

**Search** (replaces WebSearch):
```
python3 ~/skills/deep-research/brave_search.py search "your query here"
```
Returns JSON array of results with title, url, description, age.

**Fetch** (replaces WebFetch):
```
python3 ~/skills/deep-research/brave_search.py fetch "https://example.com"
```
Returns cleaned text content from the URL (first ~15k chars).

---

## Phase 1: Scope

Analyze the research query and decompose it into research threads. Consult `references/research-methodology.md` for decomposition strategies matched to the question type.

**Steps:**

1. Identify the question type (factual, comparison, landscape, policy, technical, or hybrid)
2. Identify key entities, temporal scope, and domain
3. Decompose into N research threads (N = search threads for the depth mode), each targeting a **distinct facet** of the query — threads must not substantially overlap
4. For each thread, formulate 2–3 specific search queries following the query formulation tips in the methodology reference

**Output to the user:** A numbered research plan showing each thread with its focus area and planned search queries. Keep this concise — a few lines per thread.

### Gate 1 — Scope Review `[Decision Maker + Researcher]`

Before proceeding to Phase 2, evaluate the research plan:

*As the Decision Maker* — would this research plan actually answer my question?
- [ ] The threads, if fully researched, would give the requester what they need to make a decision or understand the topic
- [ ] No critical facet of the original query is missing from the plan
- [ ] The scope matches the depth mode (not overambitious for quick, not shallow for deep)

*As the Researcher* — is this plan methodologically sound?
- [ ] Threads are distinct (no substantial overlap)
- [ ] Question type correctly identified (factual, comparison, landscape, policy, technical, hybrid)
- [ ] Search queries are well-formulated (specific terminology, not vague)

**If any check fails**: Revise threads before proceeding. Do NOT start searching with a flawed plan.

---

## Phase 2: Survey

**Purpose**: Understand the territory before going deep. Broad landscape search to identify key sources, terminology, and promising leads.

Consult `references/citation-guide.md` for credibility tier definitions.

Spawn **all N threads simultaneously** using the `Task` tool in a **single message** with multiple tool calls:

- `subagent_type`: `general-purpose`
- Each subagent receives a **survey-focused prompt**:

```
You are a research assistant performing a SURVEY pass for one thread of a larger research project. Your goal is breadth, not depth — map the landscape.

**Search mode**: [web-native OR brave-api]

If search mode is `web-native`:
  - Use WebSearch for queries and WebFetch for page content

If search mode is `brave-api`:
  - Use Bash to run: python3 ~/skills/deep-research/brave_search.py search "query"
  - Use Bash to run: python3 ~/skills/deep-research/brave_search.py fetch "url"
  - Parse the JSON output from search, text output from fetch

**Your research thread**: [Thread title and focus area]

**Research question context**: [The user's original query for context]

**Search queries to try**: [2-3 specific queries from Phase 1]

**Instructions**:
1. Use WebSearch (web-native) or the brave_search.py script (brave-api) to execute the provided search queries (1-2 searches — don't go exhaustive)
2. For the most promising results (up to 2-3), use WebFetch (web-native) or brave_search.py fetch (brave-api) to get fuller content
3. Prioritize breadth: identify key players, main sources, terminology, and landscape
4. Identify the most authoritative sources (especially T1/T2):
   - T1: .gov, .mil, peer-reviewed journals, official standards
   - T2: .edu, research orgs (RAND, MITRE, Brookings), professional associations
   - T3: Major journalism (Reuters, AP, NYT), established trade publications (FedScoop, Nextgov)
   - T4: Vendor whitepapers, corporate blogs, consulting firms
   - T5: Personal blogs, forums, social media, Wikipedia
5. Note promising leads for deeper investigation (specific reports, datasets, cited documents)
6. Flag areas where evidence seems thin or conflicting

**Return your findings in this exact format for EACH source:**

### Source: [Title of page/document]
- **URL**: [exact URL]
- **Domain type**: [government / academic / journalism / commercial / user-generated]
- **Credibility tier**: [T1 / T2 / T3 / T4 / T5]
- **Date**: [publication date if found, otherwise "not available"]
- **Author/Org**: [author or organization if found, otherwise "not listed"]
- **Key evidence**: [Bullet list of specific facts, data points, and quotes extracted from this source. Be specific and include numbers, dates, and direct quotes where available.]

### Leads for Deeper Investigation
[List specific reports, datasets, documents, or citation chains worth following up in a deeper pass]

### Thread Summary
[2-3 sentence summary of what you found across all sources for this thread. Note any gaps, conflicts, or areas where evidence was thin.]
```

### Gate 2 — Coverage Check `[Researcher]`

After all survey subagents return, collect and assess results:

*As the Researcher* — do we have adequate landscape coverage to guide deeper investigation?
- [ ] Every thread returned at least 1 source
- [ ] No thread came back completely empty
- [ ] Total unique sources ≥ 50% of mode minimum (on track)
- [ ] Key terminology and major sources identified for each thread
- [ ] Promising leads noted for Phase 3 (citation chains, primary documents, specific reports)

**If any check fails**: Re-run failed threads with adjusted queries before deepening.

**Output to the user:** Brief progress update — how many sources collected per thread, total unique count, any notable gaps or leads being tracked.

---

## Phase 3: Deepen

**Purpose**: Progressive refinement based on Survey findings. Targeted deep dives to fill gaps, resolve conflicts, and build a robust evidence base.

Spawn targeted subagents (2–4 per round, or more for deep mode) using `Task` + `general-purpose`, with prompts that:

- **Fill gaps**: Threads with thin coverage get focused follow-up searches
- **Resolve conflicts**: Where Survey found disagreement, find primary/authoritative sources
- **Chase leads**: Follow citation chains — find primary documents referenced in survey results
- **Pursue depth**: For the most promising threads, go deeper with more specific queries
- **Recency check**: For claims >6 months old, search for updates

Each subagent receives a prompt structured as:

```
You are a research assistant performing a TARGETED DEEP DIVE for a specific research gap.

**Search mode**: [web-native OR brave-api]

If search mode is `web-native`:
  - Use WebSearch for queries and WebFetch for page content

If search mode is `brave-api`:
  - Use Bash to run: python3 ~/skills/deep-research/brave_search.py search "query"
  - Use Bash to run: python3 ~/skills/deep-research/brave_search.py fetch "url"
  - Parse the JSON output from search, text output from fetch

**Gap to fill**: [Specific description of what's missing or needs resolution]

**What we already know**: [Key findings from Survey relevant to this gap]

**Leads to follow**: [Specific documents, citation chains, or sources to pursue]

**Research question context**: [The user's original query]

**Instructions**:
1. Use WebSearch (web-native) or the brave_search.py script (brave-api) with specific, targeted queries to fill the identified gap
2. Use WebFetch (web-native) or brave_search.py fetch (brave-api) on promising results and any specific URLs from leads
3. Prioritize primary/authoritative sources over secondary reporting
4. If resolving a conflict, find the most authoritative source that others cite
5. Extract specific facts, data points, quotes, and evidence

**Return your findings in this exact format for EACH source:**

### Source: [Title of page/document]
- **URL**: [exact URL]
- **Domain type**: [government / academic / journalism / commercial / user-generated]
- **Credibility tier**: [T1 / T2 / T3 / T4 / T5]
- **Date**: [publication date if found, otherwise "not available"]
- **Author/Org**: [author or organization if found, otherwise "not listed"]
- **Key evidence**: [Bullet list of specific facts, data points, and quotes extracted from this source.]

### Gap Resolution Summary
[Did this deep dive fill the gap? What was found? Any remaining uncertainties?]
```

### Iteration and Stopping Conditions

Iterate up to `max iterations` for the depth mode. After each round, assess and stop if ANY condition is met:

1. **Saturation** — new searches return already-collected sources
2. **Coverage** — all threads have 2+ credible sources
3. **Diminishing returns** — fewer than 2 new unique sources in the latest round
4. **Budget** — max iterations reached

### Gate 3 — Source Sufficiency `[Critic]`

*As the Critic* — where are the weak points in our evidence base?
- [ ] Total unique sources ≥ mode minimum
- [ ] Every thread has 2+ credible sources
- [ ] T3–T5 claims have 2+ independent sources (corroboration rule)
- [ ] Source tier distribution is reasonable (not all T4/T5)
- [ ] Where sources conflict, both sides are represented
- [ ] No single-source dependencies for major claims (what breaks if one source is wrong?)

**If fails and iterations remain**: Run another Deepen round targeting the specific gaps the Critic identified.
**If fails and no iterations remain**: Note gaps explicitly as limitations to carry forward. Proceed.

**Output to the user:** Brief progress update — total sources collected, tier distribution, any gaps noted as limitations.

---

## Phase 4: Synthesize

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

### Gate 4 — Evidence Integrity `[Critic + Researcher]`

*As the Critic* — can I poke holes in the argument?
- [ ] No unsupported claims (every key claim maps to 1+ sources)
- [ ] Conflicting evidence is surfaced, not silently resolved
- [ ] Analytical inferences are clearly separated from sourced facts
- [ ] No logical leaps — conclusions follow from the evidence presented

*As the Researcher* — is the synthesis methodologically sound?
- [ ] Corroboration rules satisfied (T1 standalone OK; T3–T5 need 2+ sources)
- [ ] Narrative outline has 4–8 distinct sections with minimal overlap
- [ ] Each section draws from 3+ sources minimum
- [ ] Source-to-claim mapping is complete and traceable

**If any check fails**: Revise outline — drop unsupported claims, flag gaps, restructure sections.

Do NOT output the synthesis to the user — proceed directly to Phase 5.

---

## Phase 5: Draft & Refine

Write the report draft and run iterative quality checks. This phase loops up to `Max QA remediation cycles` times.

### Step 1: Draft

Write `report.md` and `sources.md` content in-memory following `references/report-template.md` and `references/citation-guide.md`:

- **report.md**: Title, metadata, executive summary, introduction, findings (4–8 sections), analysis & synthesis, limitations & gaps, recommendations (if applicable), references
- **sources.md**: All sources in citation order with tier tags, plus tier distribution summary

### Step 2: Quality Checklist

Run all checks against the draft:

*Structural:*
- [ ] Citation integrity — every `[N]` maps to a source in sources.md, no orphans, no sequence gaps
- [ ] Section completeness — all required sections present (exec summary, intro, findings, analysis, limitations, references)
- [ ] Word count within target range for the depth mode

*Content quality:*
- [ ] Section balance — no single finding >30% of findings word count
- [ ] Prose quality — ≥80% narrative prose in findings and analysis (minimize bullet lists)
- [ ] Inference labeling — hedging language for analytical claims ("evidence suggests...", "taken together...")
- [ ] Exec summary covers all major findings, not just the first few
- [ ] Conflicting evidence presented where sources disagreed

*Source quality:*
- [ ] Per-finding coverage — each finding section cites 3+ sources
- [ ] No fabricated URLs — every URL came from an actual search result or page fetch

### Step 3: Remediate

Fix all checklist failures found in Step 2. If source gaps need new research AND remediation cycles remain, spawn 1–3 targeted subagents using the same `Task` + `general-purpose` pattern to fill specific gaps. Integrate results into the draft and re-run the checklist.

### Step 4: Progress Note

Tell user: "Draft QA: fixed X issues, Y remain." (Keep this brief.)

### Gate 5 — Report Quality `[Decision Maker + Critic]`

*As the Decision Maker* — "so what?" test:
- [ ] The report actually answers the original research question
- [ ] The executive summary is self-contained — a busy person reading only this section gets the key takeaways
- [ ] Findings lead to clear implications or actionable insights (not just a data dump)
- [ ] Limitations are honest — the reader knows what they can and can't rely on

*As the Critic* — final adversarial check:
- [ ] All structural checks pass (citations, sections, word count)
- [ ] No source fabrication
- [ ] ≤2 minor content issues remaining
- [ ] Nothing that would embarrass the researcher if fact-checked

**If fails and QA cycles remain**: Loop back to Step 2 with remaining issues.
**If fails and no cycles remain**: Note remaining issues in the Limitations section and proceed.

---

## Phase 6: Publish

1. Generate the topic slug from the research query:
   - Lowercase, replace spaces and special chars with hyphens, max 50 chars
   - Examples:
     "FedRAMP authorization process 2025" → fedramp-authorization-process-2025
     "AI regulation across US EU China" → ai-regulation-us-eu-china
     "Kubernetes vs serverless for enterprise" → kubernetes-vs-serverless-enterprise

2. Create the output directory using the slug and today's date (YYYYMMDD):
   ```
   mkdir -p ~/Documents/research/[topic-slug]_[YYYYMMDD]/
   ```
   CRITICAL: Do NOT use generic names like "research-report" or "output".
   The directory MUST reflect the specific research topic.

3. Write `report.md` and `sources.md` to disk using the Write tool

4. **Display to the user:**
   - The full executive summary
   - Source count and tier distribution (e.g., "15 sources: 4 T1, 3 T2, 5 T3, 2 T4, 1 T5")
   - File paths to both report.md and sources.md
   - Any notable limitations or caveats
   - **QA summary**: Which gates triggered remediation, what was fixed, and final gate status

---

## Quality Gate Summary

| Gate | After Phase | Role Lens | Key Question | Remediation |
|------|-------------|-----------|--------------|-------------|
| 1 | Scope | Decision Maker + Researcher | Will this plan answer the question? | Revise threads |
| 2 | Survey | Researcher | Do we have broad landscape coverage? | Re-search failed threads |
| 3 | Deepen | Critic | Where are the weak points in evidence? | Additional targeted search |
| 4 | Synthesize | Critic + Researcher | Can I poke holes? Is it methodologically sound? | Revise outline, drop weak claims |
| 5 | Draft & Refine | Decision Maker + Critic | Does this answer the question? Would it survive fact-checking? | Fix in-place or re-search |

---

## Constraints

- **Never fabricate URLs or citations.** Every URL must come from an actual search result (WebSearch, Brave Search API, or page fetch). If you cannot find a source for a claim, mark it `[citation needed]` or remove the claim.
- **Never invent source metadata.** Titles, authors, dates must come from actual source content. Use "not listed" / "not available" / "accessed [date]" when metadata is missing.
- **Domain-neutral source selection.** Do not prefer .gov or .edu sources by default — let the topic determine which sources are relevant. Rank by credibility tier, not domain type. A T3 journalism source with direct reporting may be more valuable than a T1 government page with generic information.
- **Present conflicting evidence.** When sources disagree, show both positions with citations. Offer analysis of why they might differ, but do not silently pick a side.
- **Distinguish fact from inference.** Use clear language: "According to [1]..." for sourced facts vs. "The evidence suggests..." or "Taken together, these findings indicate..." for your analytical conclusions.
- **Respect the depth mode.** Do not exceed the iteration count or significantly overshoot word targets. The user chose the depth for a reason.
- **Be transparent about limitations.** A short, honest report is better than a long one that papers over gaps. The Limitations section is mandatory and must be substantive.
- **Gate discipline.** Never skip a quality gate. If a gate fails and remediation is available, remediate before proceeding. If no remediation cycles remain, document the failure in Limitations.
