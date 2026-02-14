# Test Queries for Deep Research Skill

Five curated queries spanning different question types and depth modes. Use these to validate the skill after changes.

---

## Test 1: Policy (quick)

**Command**: `/deep-research quick What is FedRAMP and what does the authorization process look like in 2025-2026?`

**Type**: Policy / Regulatory
**Why this query**: Clear scope, abundant T1 sources (.gov), well-defined domain. Quick mode should produce a focused report with strong citations. Good smoke test — if this fails, something fundamental is broken.

**Expected signals**:
- T1 sources from fedramp.gov, gsa.gov
- Clear description of authorization levels (Low, Moderate, High)
- Mentions of FedRAMP 20x or Rev 5 updates if applicable
- 5+ sources, 1,500–3,000 words

---

## Test 2: Landscape (standard)

**Command**: `/deep-research standard Current state of AI regulation across the US, EU, and China as of 2025-2026`

**Type**: State-of-the-art / Landscape
**Why this query**: Forces multi-jurisdictional coverage, tests thread decomposition across geographies. Requires recency. Broad enough to test whether Survey→Deepen progression works — Survey should map the landscape, Deepen should fill jurisdictional gaps.

**Expected signals**:
- EU AI Act details (T1 from EUR-Lex or ec.europa.eu)
- US executive orders and NIST AI RMF references
- China's regulatory approach (Generative AI regulations)
- Comparison/contrast across jurisdictions
- 10+ sources, 3,000–6,000 words

---

## Test 3: Comparison (standard)

**Command**: `/deep-research standard Compare Kubernetes vs serverless (AWS Lambda / Azure Functions / GCP Cloud Functions) for microservices architecture in enterprise environments`

**Type**: Comparison / Technical
**Why this query**: Tests balanced comparison structure. Risk of vendor-biased sources (T4). The Critic gate should catch one-sided analysis. Good test for whether section balance checks work.

**Expected signals**:
- Balanced treatment of both approaches
- Specific technical tradeoffs (cold starts, scaling, cost, operational overhead)
- Enterprise case studies or benchmarks
- Source diversity (not all vendor blogs)
- 10+ sources, 3,000–6,000 words

---

## Test 4: Technical (deep)

**Command**: `/deep-research deep Zero trust architecture implementation for federal agencies: NIST 800-207 framework, CISA maturity model, and real-world adoption patterns`

**Type**: Technical / Policy hybrid
**Why this query**: Deep mode stress test. Multiple authoritative frameworks to cross-reference. Should trigger multiple Deepen rounds. Tests whether citation chains are followed (NIST → CISA → OMB memos → agency implementations).

**Expected signals**:
- NIST SP 800-207 details (T1)
- CISA Zero Trust Maturity Model (T1)
- OMB M-22-09 requirements (T1)
- Agency implementation case studies
- 15+ sources, 6,000–10,000 words

---

## Test 5: Current Events (quick)

**Command**: `/deep-research quick Latest developments in quantum computing error correction, last 6 months`

**Type**: Factual / Current events
**Why this query**: Tests recency handling. Sources will skew T3 (journalism) and T2 (academic). Good test for whether the skill handles topics where T1 government sources are scarce. Quick mode — should be concise and focused.

**Expected signals**:
- Recent papers or announcements (Google, IBM, Microsoft, academic groups)
- Specific error correction milestones or techniques
- Appropriate hedging on unverified claims
- 5+ sources, 1,500–3,000 words

---

## Running Tests

1. Run the command in Claude Code
2. After completion, run validation:
   ```bash
   ./validate.sh ~/Documents/research/<output-dir> <mode>
   ```
3. Score with `rubric.md` for qualitative assessment
4. Log results in `scorecard.md`

**Target**: All tests should achieve ≥3.5 on the rubric weighted score and pass all structural checks in `validate.sh`.
