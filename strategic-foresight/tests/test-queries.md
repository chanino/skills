# Test Queries for Strategic Foresight Skill

## Test 1: Remote Work — Scan Mode
```
/strategic-foresight scan Future of remote work in US federal government over next 5 years
```
**Expected behavior**:
- Mode: scan (3 threads, 1 iteration, 2-3 forecasts)
- STEEP dimensions: Social, Technological, Political (minimum)
- Frameworks: STEEP scan + Three Horizons only
- No scenarios (scan mode)
- Output: forecast.md (2,000-4,000 words) + methodology.md (500-1,000 words)
- Should detect deep-research baseline if `~/Documents/research/*remote-work*` exists

**Key signals to look for**:
- OPM telework policies and recent mandates
- Agency-level return-to-office trends
- Federal workforce demographics and attrition data
- Technology infrastructure (VPN, collaboration tools)
- Congressional/political pressure on federal telework

---

## Test 2: LLMs + Legal — Standard Mode
```
/strategic-foresight standard Impact of large language models on the US legal profession through 2030
```
**Expected behavior**:
- Mode: standard (5 threads, 2 iterations, 4-6 forecasts)
- STEEP dimensions: Technological, Economic, Political, Social
- Frameworks: STEEP + Three Horizons + 2x2 Scenarios + CLA
- 4 scenarios with probability assignments
- Output: forecast.md (5,000-9,000 words) + methodology.md (1,000-2,000 words)

**Key signals to look for**:
- LLM adoption rates in law firms (BigLaw vs. small practice)
- Bar association positions on AI-assisted legal work
- Court rulings on AI-generated filings
- Legal tech investment trends
- Law school enrollment and curriculum changes
- State-level AI regulation affecting legal practice

---

## Test 3: US-China Semiconductors — Standard Mode
```
/strategic-foresight standard US-China semiconductor competition and global supply chain restructuring through 2032
```
**Expected behavior**:
- Mode: standard (5 threads, 2 iterations, 4-6 forecasts)
- STEEP dimensions: Technological, Economic, Political, (Environmental optional)
- Frameworks: STEEP + Three Horizons + 2x2 Scenarios + CLA
- 4 scenarios with probability assignments
- Should leverage geopolitical reference classes from Phase 2

**Key signals to look for**:
- CHIPS Act implementation progress
- China's domestic semiconductor capabilities (SMIC, Huawei)
- Export control effectiveness and workarounds
- Allied coordination (Japan, Netherlands, South Korea, Taiwan)
- TSMC Arizona/Japan fab progress
- AI chip demand trajectories

---

## Test 4: Energy Transition — Full Mode
```
/strategic-foresight full Global energy transition pathways and implications for US energy security 2025-2050
```
**Expected behavior**:
- Mode: full (8 threads, 3 iterations, 6-10 forecasts)
- STEEP dimensions: All five (S, T, E, E, P)
- Frameworks: All — STEEP + Three Horizons + 2x2 Scenarios + CLA + Backcasting + Wind Tunneling + GMA
- 4-6 scenarios with probability assignments
- Backcasting from net-zero target
- Wind tunneling of energy security strategies
- Output: forecast.md (9,000-15,000 words) + methodology.md (2,000-3,500 words)

**Key signals to look for**:
- Renewable energy cost curves and deployment rates
- Grid modernization and storage breakthroughs
- Fossil fuel demand projections (IEA, EIA, OPEC)
- Critical mineral supply chains (lithium, cobalt, rare earths)
- Carbon pricing and climate policy trends
- Nuclear renaissance indicators
- Hydrogen economy development
- Geopolitical energy dependencies

---

## Test 5: Higher Education — Scan Mode
```
/strategic-foresight scan Future of US higher education business model over next decade
```
**Expected behavior**:
- Mode: scan (3 threads, 1 iteration, 2-3 forecasts)
- STEEP dimensions: Social, Economic, Technological
- Frameworks: STEEP scan + Three Horizons only
- No scenarios (scan mode)
- Output: forecast.md (2,000-4,000 words) + methodology.md (500-1,000 words)

**Key signals to look for**:
- Enrollment trends (demographic cliff, online vs. in-person)
- Tuition and student debt dynamics
- Alternative credentialing (micro-credentials, bootcamps, employer-led)
- AI impact on teaching and assessment
- Institutional financial stress indicators
- State funding trends
- International student enrollment shifts

---

## Validation Criteria (All Tests)

### Structural
- [ ] Output directory created at `~/Documents/foresight/[slug]_[YYYYMMDD]/`
- [ ] Both forecast.md and methodology.md present
- [ ] Word counts within target range for mode
- [ ] All mode-required sections present
- [ ] No mode-inappropriate sections (e.g., no scenarios in scan mode)

### Forecast Quality
- [ ] All forecasts STPOT-compliant
- [ ] Probabilities are specific numbers (not vague language)
- [ ] Base rates referenced where available
- [ ] Resolution criteria are clear and operationalizable
- [ ] Scenario probabilities sum to ~100%

### Analytical Quality
- [ ] Three Horizons presented in H1-H3-H2 order
- [ ] H2+ and H2- distinguished
- [ ] CLA reaches myth/metaphor level (not just litany + systemic)
- [ ] Signals classified by type (trend, weak signal, wild card, driver, uncertainty)
- [ ] Cross-dimensional interactions identified

### Methodology
- [ ] Tetlock 10 Commandments self-assessment complete
- [ ] STPOT compliance matrix present
- [ ] Cognitive bias checklist present
- [ ] Assumptions log populated
- [ ] Source tier distribution included
