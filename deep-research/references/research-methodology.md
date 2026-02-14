# Research Methodology Reference

## Query Decomposition Strategies

Decompose the user's research question into distinct, non-overlapping threads based on question type:

### Factual Questions
("What is X?", "How does X work?")
- Thread 1: Official definitions and specifications
- Thread 2: Current status and recent developments
- Thread 3: Implementation details and technical mechanics
- Thread 4: Stakeholder perspectives and impact
- Thread 5: Historical context and evolution

### Comparison Questions
("How does X compare to Y?", "What are the differences between X and Y?")
- Thread per entity: Individual deep-dive on each entity
- Thread: Head-to-head comparison from third-party analyses
- Thread: Use-case or context-specific performance
- Thread: Expert or practitioner assessments

### State-of-the-Art / Landscape Questions
("What is the current state of X?", "Overview of X")
- Thread 1: Regulatory and policy landscape
- Thread 2: Major players and market dynamics
- Thread 3: Recent developments (last 6-12 months)
- Thread 4: Technical trends and capabilities
- Thread 5: Challenges and open problems
- Thread 6: Future outlook and projections

### Policy and Regulatory Questions
("What are the requirements for X?", "How is X regulated?")
- Thread 1: Primary authoritative sources (legislation, executive orders, agency guidance)
- Thread 2: Implementation guidance and compliance frameworks
- Thread 3: Enforcement actions and case studies
- Thread 4: Industry response and compliance strategies
- Thread 5: Pending changes and proposed rules

### Technical / How-To Questions
("How do you implement X?", "Best practices for X")
- Thread 1: Official documentation and standards
- Thread 2: Reference architectures and design patterns
- Thread 3: Implementation case studies
- Thread 4: Common pitfalls and troubleshooting
- Thread 5: Performance benchmarks and optimization

## Search Query Formulation

### General Tips
- Use specific terminology from the domain rather than layperson terms
- Include year qualifiers for time-sensitive topics: `"FedRAMP 2024 2025"`
- Use quotes for exact phrases: `"zero trust architecture"`
- Combine entity + action + context: `NIST AI RMF implementation guidance federal agencies`

### Federal/Government Domain
- Use agency acronyms alongside full names: `CISA (Cybersecurity and Infrastructure Security Agency)`
- Reference specific document numbers: `OMB M-24-10`, `EO 14110`
- Search .gov domains explicitly when needed: `site:fedramp.gov authorization process`
- Include `federal register` for proposed and final rules

### Date Qualifiers
- For current state: include current and previous year
- For historical context: include the relevant date range
- For recent developments: `after:YYYY-01-01` style qualifiers where supported

## Iterative Refinement Patterns

### Gap-Filling (Round 2+)
After Round 1, identify:
- Sub-questions that got zero or low-quality results
- Facets mentioned in results but not yet explored
- Spawn targeted follow-up threads for these gaps

### Conflict Resolution (Round 2+)
When sources disagree:
- Search for the primary/authoritative source that others cite
- Search for more recent information that may supersede older claims
- Search for meta-analyses or systematic reviews that reconcile differences

### Lead-Following (Round 2+)
When Round 1 results reference important documents, reports, or data:
- Fetch the primary source directly via WebFetch
- Search for analyses or summaries of that primary source
- Follow citation chains to foundational sources

### Recency Check (Round 2+)
For any claim older than 6 months:
- Search for updates or superseding information
- Check if referenced programs, policies, or technologies have changed status

## Stopping Conditions

Stop iterating when ANY of these conditions are met:

1. **Saturation**: New searches return sources already collected — no new information
2. **Coverage**: All decomposed threads have at least 2 credible sources each
3. **Budget**: Maximum iterations for the depth mode reached
4. **Diminishing returns**: Latest iteration added fewer than 2 new unique sources
5. **Authoritative sufficiency**: A T1 source directly and comprehensively answers the question

## Source Selection Priority

When multiple sources cover the same ground, prefer:
1. Most recent over older (unless the older source is the canonical reference)
2. Primary over secondary (original research over reporting on research)
3. Higher credibility tier over lower (see citation-guide.md)
4. More specific over more general (directly on-topic over tangentially related)
5. Quantitative over qualitative (data-backed claims over opinion)
