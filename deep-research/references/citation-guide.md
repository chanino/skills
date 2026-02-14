# Citation & Source Credibility Guide

## 5-Tier Source Credibility System

### Tier 1 — Authoritative Primary Sources
- Government domains: `.gov`, `.mil`
- Peer-reviewed journals and academic publications
- Official standards bodies: NIST, ISO, IEEE, W3C
- Primary legislation, executive orders, federal register notices
- **Corroboration**: Can stand alone as a source for factual claims

### Tier 2 — Institutional & Academic
- Educational institutions: `.edu`
- Established research organizations: RAND, Brookings, MITRE, GAO reports
- Professional associations: ACM, ISACA, (ISC)²
- Federally funded research centers (FFRDCs)
- **Corroboration**: Can stand alone for domain-specific claims; cross-reference with T1 when available

### Tier 3 — Major Journalism & Industry Analysis
- Major news outlets with editorial oversight (Reuters, AP, NYT, WSJ, WaPo)
- Established trade publications (FedScoop, Nextgov, FCW, GovExec, Defense One)
- Major analyst firms (Gartner, Forrester) — note potential conflicts of interest
- Well-established tech journalism (Ars Technica, Wired, The Register)
- **Corroboration**: Prefer 2+ independent T3 sources for key claims; 1 is acceptable if corroborated by T1/T2

### Tier 4 — Commercial & Advocacy
- Vendor whitepapers and product documentation
- Industry group publications and advocacy organizations
- Corporate blogs from major technology companies
- Consulting firm publications
- **Corroboration**: Require 2+ independent sources; always note potential bias; never use as sole source for contested claims

### Tier 5 — User-Generated & Unverified
- Personal blogs, Medium posts, Substack
- Forum posts (Reddit, Stack Overflow, HN)
- Social media posts
- Wikipedia (use as a pointer to primary sources, not as a source itself)
- **Corroboration**: Require independent verification from T1-T3 sources; use only for context, sentiment, or to identify leads

## Inline Citation Formatting

### Basic Citation
Place citation numbers immediately after the claim they support, before punctuation:
```
The framework requires continuous monitoring of all authorized systems [1].
```

### Multiple Sources for One Claim
Use adjacent brackets when multiple sources support the same claim:
```
Federal agencies must achieve FedRAMP authorization before deploying cloud services [1][3].
```

### Direct Quotes
Use quotation marks with citation:
```
The memorandum states that agencies should "prioritize zero trust implementations" [4].
```

### Citing Specific Data
When citing a specific statistic or data point, cite immediately after the number:
```
As of 2024, over 300 cloud services hold FedRAMP authorization [2], representing a 40% increase from 2021 [5].
```

### Conflicting Sources
When sources disagree, present both with citations:
```
Some analysts estimate the market at $50B [3], while government figures suggest $38B [1]. The discrepancy likely reflects different scope definitions.
```

## References Section Format

Each entry in `sources.md` follows this format:

```
[N] **Title of Source**
    URL: https://example.gov/path
    Author/Organization: Name or Org
    Date: YYYY-MM-DD (or "accessed YYYY-MM-DD" if no publication date)
    Credibility: T1 — Government Primary Source
    Key contribution: Brief description of what this source contributed to the report
```

### Credibility Tier Tags
- `T1 — Government Primary Source` / `T1 — Peer-Reviewed Research`
- `T2 — Academic/Research Institution`
- `T3 — Major Journalism` / `T3 — Industry Analysis`
- `T4 — Commercial/Vendor` / `T4 — Advocacy Organization`
- `T5 — User-Generated Content`

## Anti-Hallucination Rules

1. **Never fabricate URLs**: Every URL in the references must come from an actual WebSearch or WebFetch result
2. **Never invent source titles**: Use the actual title returned by the search/fetch
3. **Never guess publication dates**: If the date is not clear from the source, use "accessed [today's date]"
4. **Never attribute quotes to sources that didn't contain them**: Only use direct quotes from fetched content
5. **Flag gaps honestly**: If a claim lacks a source, mark it as `[citation needed]` or qualify it as analytical inference
6. **Distinguish fact from inference**: Use language like "Based on [1] and [3], this suggests..." for analytical conclusions
7. **Note missing metadata**: If author or date is unknown, write "Author not listed" or "Date not available" rather than guessing
