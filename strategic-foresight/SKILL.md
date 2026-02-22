---
name: strategic-foresight
description: >
  Strategic foresight and probabilistic forecasting with horizon scanning, scenario planning,
  and structured analytical frameworks. Produces citation-backed foresight reports with
  STPOT-compliant probabilistic forecasts.
  Triggers: "strategic foresight", "foresight", "forecast", "scenarios", "horizon scan",
  "futures analysis", "what could happen"
user_invocable: true
---

# Strategic Foresight Skill

## Three Review Roles

| Role | Focus | Asks |
|------|-------|------|
| **Scanner** | Signal coverage, STEEP breadth, evidence base | "Are we detecting enough signals across all STEEP dimensions? Is the evidence base diverse?" |
| **Red Team** | Cognitive biases, anchoring, overconfidence, missing hypotheses, Tetlock checklist | "Where are we anchored? What are we missing? Would this pass Tetlock's commandments?" |
| **Strategist** | Actionability, decision-relevance, "so what?" | "Can someone act on this? Are the forecasts decision-relevant? What's the 'so what?'" |

Design rationale: Strategist bookends the process (Gates 0 and 5) for decision-relevance. Red Team intensifies in the middle (Gates 2-4) where analytical rigor matters most. Scanner anchors evidence throughout (Gates 0-4).

---

## Setup: Parse Arguments

Parse `$ARGUMENTS` to determine the **mode** and **foresight query**:

1. Check if the first word of `$ARGUMENTS` is `scan`, `standard`, or `full`
   - If yes: use that as the mode, and the remainder is the foresight query
   - If no: default to `standard`, and the entire `$ARGUMENTS` is the foresight query
2. Set parameters based on mode:

| Parameter | scan | standard | full |
|-----------|------|----------|------|
| Search threads | 3 | 5 | 8 |
| Max search iterations | 1 | 2 | 3 |
| Min sources | 5 | 10 | 15 |
| Frameworks applied | STEEP scan + Three Horizons | + 2x2 Scenarios + CLA | + Backcasting + Wind Tunneling + GMA |
| Scenarios generated | 0 (signals only) | 4 | 4-6 |
| forecast.md word target | 2,000-4,000 | 5,000-9,000 | 9,000-15,000 |
| methodology.md word target | 500-1,000 | 1,000-2,000 | 2,000-3,500 |
| Key forecasts | 2-3 | 4-6 | 6-10 |
| Max QA remediation cycles | 1 | 2 | 3 |

3. Generate a topic slug from the query (lowercase, hyphens, max 50 chars)
4. Set the output directory: `~/Documents/foresight/[topic-slug]_[YYYYMMDD]/`
5. **Detect available search tools** — same logic as deep-research:
   a. Check if WebSearch and WebFetch tools are available. If yes → `web-native`
   b. If NOT available, test brave_search.py: `python3 ~/.claude/skills/strategic-foresight/brave_search.py search "test" 2>&1 | head -5`. If JSON results → `brave-api`
   c. If neither → tell user no search capability available and STOP
6. **Check for existing deep-research output**: Search for `~/Documents/research/*<topic-keywords>*/report.md` using Glob. If found, read it and mark it as H1 baseline input — this provides litany-level data and reduces scanning work.

Tell the user the mode, thread count, search mode, whether deep-research baseline was found, and that foresight analysis is beginning.

### Search Tool Reference (brave-api mode)

Same as deep-research:
- **Search**: `python3 ~/.claude/skills/strategic-foresight/brave_search.py search "query"`
- **Fetch**: `python3 ~/.claude/skills/strategic-foresight/brave_search.py fetch "url"`

---

## Phase 0: Frame

Analyze the foresight query and set up the analytical frame.

**Steps:**

1. Classify the foresight question type:
   - **Disruption**: What could disrupt X? (e.g., "Future of higher education")
   - **Transition**: How will X transition to Y? (e.g., "Energy transition pathways")
   - **Emergence**: What new X is emerging? (e.g., "Emerging AI governance models")
   - **Geopolitical**: How will X relationship/conflict evolve? (e.g., "US-China semiconductor competition")
   - **Policy**: What are future implications of X policy? (e.g., "Impact of remote work mandates")
2. Identify relevant STEEP dimensions — select 3-5 dimensions most relevant to the query:
   - **S**ocial: Demographics, culture, public opinion, workforce, health, equity
   - **T**echnological: Innovation, R&D, digital transformation, infrastructure
   - **E**conomic: Markets, trade, labor, industry structure, investment
   - **E**nvironmental: Climate, resources, sustainability, biodiversity
   - **P**olitical: Governance, regulation, geopolitics, elections, institutions
3. Set time horizon based on query (default 5-10 years if unspecified)
4. If deep-research baseline was found in Setup, summarize the H1 baseline (current state from that report)
5. Formulate scanning threads — one per relevant STEEP dimension, each with 2-3 specific search queries focused on:
   - Trends and drivers in that dimension related to the topic
   - Weak signals and emerging developments
   - Wild cards and potential disruptions

Consult `references/foresight-frameworks.md` for STEEP definitions and signal taxonomy.

**Output to the user:** The foresight frame — question type, STEEP dimensions selected, time horizon, scanning threads, and whether a deep-research baseline was used.

### Gate 0 — Frame Review `[Strategist + Scanner]`

*As the Strategist* — is this frame decision-relevant?
- [ ] The question type is correctly classified
- [ ] The time horizon is appropriate for the query
- [ ] STEEP dimension selection covers the most important drivers of change
- [ ] The frame would produce actionable foresight (not just academic exercise)

*As the Scanner* — is the scanning plan comprehensive?
- [ ] At least 3 STEEP dimensions are covered
- [ ] Each thread has distinct, non-overlapping focus
- [ ] Search queries target signals (trends, weak signals, wild cards), not just current state
- [ ] If deep-research baseline exists, it is being used to avoid redundant scanning

**If any check fails**: Revise frame before proceeding.

---

## Phase 1: Scan

**Purpose**: Parallel horizon scanning — detect signals of change across STEEP dimensions.

Consult `references/foresight-frameworks.md` for signal taxonomy and `references/citation-guide.md` for credibility tiers.

Spawn **all scanning threads simultaneously** using the `Task` tool in a **single message** with multiple tool calls:

- `subagent_type`: `general-purpose`
- Each subagent receives a **scanning-focused prompt**:

```
You are a horizon scanning agent performing a FORESIGHT SCAN for one STEEP dimension of a larger strategic foresight analysis.

**Search mode**: [web-native OR brave-api]

If search mode is `web-native`:
  - Use WebSearch for queries and WebFetch for page content

If search mode is `brave-api`:
  - Use Bash to run: python3 ~/.claude/skills/strategic-foresight/brave_search.py search "query"
  - Use Bash to run: python3 ~/.claude/skills/strategic-foresight/brave_search.py fetch "url"
  - Parse the JSON output from search, text output from fetch

**Your STEEP dimension**: [Dimension name and focus area]

**Foresight question context**: [The user's original query and time horizon]

**Search queries to try**: [2-3 specific queries from Phase 0]

**Instructions**:
1. Execute the search queries (1-2 searches for breadth)
2. For the most promising results (up to 2-3), fetch fuller content
3. Classify every finding as one of:
   - **Trend**: Established pattern of change with directional momentum
   - **Weak signal**: Early, ambiguous indicator of potential change
   - **Wild card**: Low-probability, high-impact event or development
   - **Driver**: Force that shapes the direction and pace of change
   - **Uncertainty**: Key factor whose future direction is genuinely unknown
4. For each signal, assess: direction (growing/declining/stable), pace (fast/medium/slow), and confidence (high/medium/low)
5. Prioritize authoritative sources (T1/T2):
   - T1: .gov, .mil, peer-reviewed journals, official standards
   - T2: .edu, research orgs, professional associations
   - T3: Major journalism, established trade publications
   - T4: Vendor whitepapers, corporate blogs
   - T5: Personal blogs, forums, social media
6. Look specifically for: quantitative data on trends, expert forecasts, scenario analyses, policy signals, technology readiness indicators

**Return your findings in this exact format for EACH signal:**

### Signal: [Short descriptive title]
- **Type**: [Trend / Weak signal / Wild card / Driver / Uncertainty]
- **STEEP dimension**: [S / T / E / E / P]
- **Direction**: [Growing / Declining / Stable / Uncertain]
- **Pace**: [Fast / Medium / Slow]
- **Confidence**: [High / Medium / Low]
- **Source URL**: [exact URL]
- **Source credibility**: [T1 / T2 / T3 / T4 / T5]
- **Source date**: [date if available]
- **Evidence**: [Specific facts, data points, quotes supporting this signal]
- **Implications**: [1-2 sentences on what this signal means for the foresight question]

### Dimension Summary
[2-3 sentences: Overall assessment of this STEEP dimension. What's the dominant narrative? What surprises emerged? What critical uncertainties remain?]

### Leads for Deeper Investigation
[Specific reports, forecasts, data sources, or expert analyses worth pursuing]
```

### Gate 1 — Scan Coverage `[Scanner]`

After all scanning subagents return:

*As the Scanner* — do we have adequate signal coverage?
- [ ] Every STEEP dimension returned at least 2 signals
- [ ] Signal types are diverse (not all trends — look for weak signals and wild cards)
- [ ] Total unique sources ≥ 50% of mode minimum
- [ ] At least 1 uncertainty identified per dimension
- [ ] Signals span the full time horizon (near-term AND longer-term)

**If any check fails**: Re-run failed dimensions with adjusted queries.

**Output to the user:** Brief signal map — count of signals by type and STEEP dimension, notable findings, any gaps.

---

## Phase 2: Deepen

**Purpose**: Targeted deep dives on critical uncertainties — find base rates, historical analogies, existing forecasts, competing views.

From the scan results, identify the 3-5 most critical uncertainties and knowledge gaps. Spawn targeted subagents (2-4 per round) using `Task` + `general-purpose`:

```
You are a research assistant performing a TARGETED DEEP DIVE on a critical uncertainty for a strategic foresight analysis.

**Search mode**: [web-native OR brave-api]

[Same search mode instructions as Phase 1]

**Critical uncertainty to investigate**: [Specific description]

**What we already know from scanning**: [Key signals and findings relevant to this uncertainty]

**Leads to follow**: [Specific documents, forecasts, or sources to pursue]

**Foresight question context**: [Original query and time horizon]

**Instructions**:
1. Search for BASE RATES: How often have similar transitions/disruptions/events occurred historically? What is the reference class?
2. Search for HISTORICAL ANALOGIES: What past situations most closely resemble this uncertainty? What happened?
3. Search for EXISTING FORECASTS: Have prediction markets, expert panels, government agencies, or research institutions made forecasts on this or closely related questions?
4. Search for COMPETING VIEWS: What do different expert camps believe and why? Where is the genuine disagreement?
5. Search for LEADING INDICATORS: What observable metrics would signal which direction this uncertainty is resolving?
6. Extract specific quantitative data wherever possible

**Return findings in this format:**

### Base Rates
[What reference class applies? What are the historical frequencies?]

### Historical Analogies
[Most relevant precedents and their outcomes]

### Existing Forecasts
[Any formal forecasts found, with sources and methodologies]

### Competing Views
[Major schools of thought on this uncertainty]

### Leading Indicators
[Observable metrics to watch]

### Sources
[Standard source format with URL, tier, date, key evidence for each]
```

### Iteration and Stopping

Same as deep-research: iterate up to `max search iterations`. Stop on saturation, coverage, diminishing returns, or budget.

### Gate 2 — Analytical Depth `[Red Team]`

*As the Red Team* — are we prepared to analyze rigorously?
- [ ] Critical uncertainties have base rates or reference classes identified
- [ ] At least 1 historical analogy per major uncertainty
- [ ] Competing views are represented (not just the consensus)
- [ ] Total unique sources ≥ mode minimum
- [ ] Evidence base supports probabilistic reasoning (not just narrative)

**If fails and iterations remain**: Run another round targeting Red Team's specific gaps.
**If fails and no iterations remain**: Note gaps as limitations to carry forward.

**Output to the user:** Brief update — uncertainties investigated, base rates found, remaining gaps.

---

## Phase 3: Analyze

**Purpose**: Apply foresight frameworks to transform raw signals and evidence into structured analytical products. This is the core intellectual work — NO subagents. You do this analysis directly.

Consult `references/foresight-frameworks.md` for framework instructions and `references/forecast-quality.md` for Tetlock's commandments and STPOT criteria.

**Steps by mode:**

### All modes (scan, standard, full):

**1. STEEP Signal Map**
Organize all signals from Phase 1 into a structured map by dimension. For each dimension:
- List signals with type, direction, pace
- Identify cross-dimensional interactions (e.g., a technological trend that amplifies a social driver)
- Flag the strongest signals and most critical uncertainties

**2. Three Horizons Analysis**
Present in H1-H3-H2 order (per best practice — you need H3 vision before you can evaluate H2):
- **H1 (Current system)**: What is the dominant paradigm? What are its strengths and weaknesses? What signs show it is losing fitness?
- **H3 (Future vision)**: Based on weak signals and emerging patterns, what could the future system look like? What new paradigm is emerging?
- **H2 (Transition space)**: What innovations and experiments bridge H1 and H3? Distinguish:
  - **H2+**: Innovations that advance toward H3 (transformative)
  - **H2-**: Innovations that merely extend H1 (sustaining)

### Standard and full modes additionally:

**3. 2x2 Scenario Matrix** (standard: 4 scenarios, full: 4-6)
- Select the two critical uncertainties with highest impact and greatest uncertainty
- Define extreme poles for each (clearly label each pole)
- Construct narrative scenarios for each quadrant:
  - Give each scenario a memorable name
  - Describe the scenario in 2-3 paragraphs
  - Assign a probability estimate (all scenarios must sum to ~100%)
  - Identify key indicators that would signal this scenario is emerging
  - Note: probabilities must use specific numbers (e.g., "30%"), not vague language

**4. Causal Layered Analysis (CLA)**
Analyze the foresight question at four levels:
- **Litany**: Surface-level data and current trends (draw from Phase 1 scan results and any deep-research baseline)
- **Systemic causes**: Underlying structural forces — economic incentives, institutional arrangements, market structures
- **Worldview**: Cultural assumptions, ideological frames, mental models that shape how stakeholders see this issue
- **Myth/Metaphor**: Deep narratives and archetypal stories that unconsciously drive behavior and expectations
For each level: what is the dominant narrative? What alternative narratives exist?

### Full mode additionally:

**5. Backcasting**
For the most desirable scenario (or a stakeholder-specified goal):
- Define the desired future state clearly
- Work backward: what milestones must be achieved, and by when?
- Identify critical path decisions and dependencies
- Flag potential obstacles and enablers at each stage

**6. Wind Tunneling**
If the user's query implies a strategy or decision:
- State the strategy/decision being tested
- Evaluate it against each scenario from the 2x2 matrix:
  - How does the strategy perform in this scenario? (Strong / Adequate / Weak / Fails)
  - What adaptations would be needed?
  - What are the key vulnerabilities?
- Identify "no-regret" moves that work across all scenarios
- Identify "big bets" that pay off in some scenarios but fail in others

**7. General Morphological Analysis (GMA)** (full mode only)
For complex multi-dimensional problems:
- Define 3-5 key dimensions of the problem space
- For each dimension, define 2-4 possible states
- Construct a Zwicky box (combination matrix)
- Identify the most contrasting viable combinations as alternative futures
- Cross-check against scenario matrix for consistency

### All modes — Key Forecasts:

**8. Probabilistic Forecasts**
Generate the required number of key forecasts (scan: 2-3, standard: 4-6, full: 6-10). Each forecast MUST be STPOT-compliant:

- **S**pecific: Precisely defined outcome with clear resolution criteria
- **T**ime-bound: Explicit time horizon (by when?)
- **P**robabilistic: Expressed as a specific probability (e.g., "65%"), not vague language
- **O**perationalizable: Clear data source or method for determining resolution
- **T**rackable: Could be submitted to a prediction platform for scoring

Format each forecast as:
```
**Forecast [N]**: [Clear statement of the predicted outcome]
- **Probability**: [X]%
- **Time horizon**: By [specific date or timeframe]
- **Resolution criteria**: [How we would determine if this came true]
- **Base rate**: [Reference class and historical frequency, if available]
- **Key assumptions**: [What must hold for this forecast to be valid]
- **Confidence drivers**: [What pushes the probability up vs. down]
```

Run each forecast through Tetlock's 10 Commandments checklist (from `references/forecast-quality.md`). Note any commandments that are not fully satisfied.

### Gate 3 — Analytical Rigor `[Red Team + Scanner]`

*As the Red Team*:
- [ ] Forecasts use specific probabilities, not vague language
- [ ] Probabilities are calibrated (not all clustered at 50% or at extremes)
- [ ] Base rates are referenced where available
- [ ] At least 2 competing hypotheses considered for each major uncertainty
- [ ] Anchoring check: Are initial estimates over-influenced by the first data point found?
- [ ] Overconfidence check: Are any forecasts above 90% or below 10%? If so, is the evidence truly that strong?
- [ ] Missing hypotheses: What scenarios or possibilities are NOT represented?

*As the Scanner*:
- [ ] All STEEP dimensions are reflected in the analysis (not just the most data-rich)
- [ ] Cross-dimensional interactions are identified
- [ ] Weak signals are given appropriate weight (not dismissed as noise)
- [ ] Signal-to-framework mapping is traceable (can trace each analytical conclusion back to specific signals)

**If any check fails**: Revise analysis. This is the most important gate — do not proceed with flawed analysis.

---

## Phase 4: Synthesize

**Purpose**: Build document outlines, assign citations, map claims to sources, build assumptions log.

**Steps:**

1. **Assign citation numbers**: Number all unique sources sequentially [1], [2], [3]... in order of first appearance
2. **Cross-reference claims**: Map each signal, analytical claim, and forecast to its supporting source(s)
3. **Build forecast.md outline**: Organize into sections per `references/output-templates.md`
4. **Build methodology.md outline**: Document frameworks used, scanning strategy, assumptions
5. **Build assumptions log**: List all key assumptions underlying the analysis, noting which are evidence-based vs. analytical judgments
6. **Apply corroboration rules** from `references/citation-guide.md`:
   - T1 sources can stand alone
   - T3-T5 claims need 2+ independent sources
   - Flag any claims that don't meet thresholds

### Gate 4 — Synthesis Integrity `[Red Team + Scanner]`

*As the Red Team*:
- [ ] No unsupported claims
- [ ] Forecasts map to specific evidence (not generated from narrative alone)
- [ ] Assumptions log is complete and honest
- [ ] Conflicting evidence is surfaced, not buried

*As the Scanner*:
- [ ] Every signal from Phase 1 is accounted for (used in analysis, or explicitly noted as not significant)
- [ ] Citation coverage is adequate (no large sections without sources)
- [ ] Source-to-claim mapping is complete

**If any check fails**: Revise before proceeding.

---

## Phase 5: Draft & Refine

Write the two output files and run iterative quality checks. This phase loops up to `Max QA remediation cycles` times.

### Step 1: Draft

Write `forecast.md` and `methodology.md` content following `references/output-templates.md`:

**forecast.md** structure:
- Title, metadata (mode, date, sources consulted, time horizon)
- Executive foresight summary (standalone briefing)
- Signal map (by STEEP dimension, with signal types)
- Three Horizons analysis (H1-H3-H2)
- Critical uncertainties
- [standard/full] Scenario matrix with probabilities
- [standard/full] Causal Layered Analysis
- [full] Backcasting pathway
- [full] Wind tunneling results
- [full] GMA / morphological analysis
- Key probabilistic forecasts (STPOT-compliant)
- Indicators to watch
- Implications and strategic options
- Limitations and caveats
- References (link to methodology.md for full source list)

**methodology.md** structure:
- Frameworks applied (list with brief rationale for each)
- Scanning strategy (STEEP dimensions, search queries, iterations)
- Assumptions log (all key assumptions with evidence basis)
- Tetlock 10 Commandments self-assessment (pass/partial/fail for each)
- STPOT compliance matrix (each forecast assessed against each criterion)
- Cognitive bias self-check (anchoring, availability, overconfidence, motivated reasoning, Dunning-Kruger)
- Full source list with tiers (same format as deep-research sources.md)
- Source distribution summary
- Glossary of foresight terms used

### Step 2: Quality Checklist

*Structural:*
- [ ] Citation integrity — every [N] maps to a source in methodology.md
- [ ] Section completeness — all required sections for the mode are present
- [ ] Word count within target range for the mode (both files)
- [ ] Mode-conditional sections present only when appropriate

*Content quality — forecast.md:*
- [ ] Section balance — no single section >30% of total word count
- [ ] ≥80% narrative prose in analytical sections
- [ ] Hedging language for analytical inferences
- [ ] Executive summary covers all major findings
- [ ] Conflicting evidence presented where sources disagreed
- [ ] All forecasts are STPOT-compliant

*Content quality — methodology.md:*
- [ ] Tetlock 10 Commandments self-assessment is complete
- [ ] STPOT compliance matrix covers all forecasts
- [ ] Assumptions log is populated
- [ ] Source list includes tier distribution

*Forecast-specific:*
- [ ] Probability language: all probabilities use specific numbers, not "likely" or "unlikely"
- [ ] Calibration check: probabilities are spread across the range (not all near 50%)
- [ ] Resolution criteria: every forecast has clear resolution criteria
- [ ] Time bounds: every forecast has a specific time horizon
- [ ] Base rates: referenced where available

### Step 3: Remediate

Fix all checklist failures. If source gaps need new research AND cycles remain, spawn 1-3 targeted subagents. Re-run checklist after fixes.

### Step 4: Progress Note

Tell user: "Draft QA: fixed X issues, Y remain."

### Gate 5 — Report Quality `[Strategist + Red Team]`

*As the Strategist* — "so what?" test:
- [ ] The foresight report answers the original question with actionable insights
- [ ] The executive summary is self-contained
- [ ] Forecasts are decision-relevant (a decision-maker could use them)
- [ ] Indicators to watch are specific and observable
- [ ] Limitations are honest

*As the Red Team* — final adversarial check:
- [ ] All structural checks pass
- [ ] No source fabrication
- [ ] Forecasts pass Tetlock's commandments
- [ ] No systematic overconfidence or anchoring
- [ ] ≤2 minor content issues remaining

**If fails and QA cycles remain**: Loop back to Step 2.
**If fails and no cycles remain**: Note remaining issues in Limitations and proceed.

---

## Phase 6: Publish

1. Generate the topic slug from the foresight query:
   - Lowercase, replace spaces and special chars with hyphens, max 50 chars
   - Examples:
     "Future of remote work in US federal government" → future-remote-work-us-federal-government
     "Energy transition pathways 2030-2050" → energy-transition-pathways-2030-2050
     "US-China semiconductor competition" → us-china-semiconductor-competition

2. Create the output directory:
   ```
   mkdir -p ~/Documents/foresight/[topic-slug]_[YYYYMMDD]/
   ```
   CRITICAL: Do NOT use generic names. The directory MUST reflect the specific topic.

3. Write `forecast.md` and `methodology.md` to disk using the Write tool.

4. **Display to the user:**
   - The full executive foresight summary
   - Signal count by STEEP dimension
   - Number of scenarios (if applicable) with names and probability ranges
   - Number of key forecasts with probability range
   - Source count and tier distribution
   - File paths to both forecast.md and methodology.md
   - Any notable limitations
   - **QA summary**: Which gates triggered remediation, what was fixed, final gate status

---

## Quality Gate Summary

| Gate | After Phase | Role Lens | Key Question | Remediation |
|------|-------------|-----------|--------------|-------------|
| 0 | Frame | Strategist + Scanner | Is the frame decision-relevant and comprehensive? | Revise frame |
| 1 | Scan | Scanner | Do we have adequate signal coverage? | Re-scan weak dimensions |
| 2 | Deepen | Red Team | Are we prepared to analyze rigorously? | Additional deep dives |
| 3 | Analyze | Red Team + Scanner | Is the analysis rigorous and unbiased? | Revise analysis |
| 4 | Synthesize | Red Team + Scanner | Is the synthesis traceable and complete? | Revise outline |
| 5 | Draft & Refine | Strategist + Red Team | Is this actionable and would it survive scrutiny? | Fix in-place or re-search |

---

## Constraints

### Anti-Hallucination Rules (from deep-research)
- **Never fabricate URLs or citations.** Every URL must come from an actual search result. If no source, use `[citation needed]` or remove the claim.
- **Never invent source metadata.** Use "not listed" / "not available" / "accessed [date]" when metadata is missing.
- **Present conflicting evidence.** Show both positions with citations. Do not silently pick a side.
- **Distinguish fact from inference.** "According to [1]..." for sourced facts vs. "The evidence suggests..." for analytical conclusions.

### Forecast-Specific Rules
- **Never present a probability without a base rate or explicit reasoning.** Every probability must be traceable to evidence, reference classes, or analytical logic — not just intuition.
- **Avoid anchoring.** When multiple sources provide different estimates, present the range rather than averaging.
- **Avoid overconfidence.** Probabilities above 90% or below 10% require exceptional evidence. Default toward the 20-80% range for genuinely uncertain outcomes.
- **Calibration discipline.** Forecasts should use the full probability range appropriate to the uncertainty, not cluster at round numbers (50%, 70%, 90%).
- **Distinguish forecasting from foresight.** Forecasts are specific, time-bound, probabilistic predictions about observable outcomes. Foresight is the broader analytical process of understanding possible futures. Both are outputs; do not conflate them.
- **Respect the time horizon.** Short-range forecasts (1-2 years) should be more specific and confident. Long-range forecasts (5-10+ years) should acknowledge greater uncertainty and use wider probability ranges.
- **Scenario probabilities must sum to approximately 100%.** If presenting mutually exclusive scenarios, their probabilities should sum to 95-105% (allowing for rounding).
- **Be transparent about limitations.** A short, honest report is better than one that papers over gaps.
- **Gate discipline.** Never skip a quality gate.

---

## Mode Parameters Quick Reference

| Parameter | scan | standard | full |
|-----------|------|----------|------|
| Search threads | 3 | 5 | 8 |
| Max search iterations | 1 | 2 | 3 |
| Min sources | 5 | 10 | 15 |
| Frameworks | STEEP + Three Horizons | + 2x2 Scenarios + CLA | + Backcasting + Wind Tunneling + GMA |
| Scenarios | 0 | 4 | 4-6 |
| forecast.md words | 2,000-4,000 | 5,000-9,000 | 9,000-15,000 |
| methodology.md words | 500-1,000 | 1,000-2,000 | 2,000-3,500 |
| Key forecasts | 2-3 | 4-6 | 6-10 |
| Max QA cycles | 1 | 2 | 3 |
