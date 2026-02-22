# Forecast Quality Reference

## Tetlock's 10 Commandments for Aspiring Superforecasters

Use this as a self-assessment checklist. Every forecast should be evaluated against these commandments. Mark each as Pass / Partial / Fail.

### 1. Triage
**Principle**: Focus on questions where effort pays off — not too easy (already known), not too hard (impenetrable uncertainty).
- **Pass**: Question is in the "Goldilocks zone" — uncertain but researchable
- **Partial**: Question is very hard but some relevant evidence exists
- **Fail**: Question is either trivial (answer is obvious) or completely opaque (no useful information available)

### 2. Break Seemingly Intractable Problems into Tractable Sub-Problems (Fermi Estimation)
**Principle**: Decompose complex questions into components that can be individually estimated.
- **Pass**: Question broken into 2+ sub-problems with separate estimates that combine to the overall forecast
- **Partial**: Some decomposition attempted but not all components are independently estimable
- **Fail**: Holistic "gut feel" without decomposition

### 3. Strike the Right Balance Between Inside and Outside Views
**Principle**: Start with the base rate (outside view), then adjust for case-specific factors (inside view).
- **Pass**: Base rate explicitly identified and used as anchor, with documented adjustments
- **Partial**: Base rate mentioned but adjustments not systematic
- **Fail**: Pure inside view (no reference to similar past events) or pure outside view (no case-specific adjustment)

### 4. Strike the Right Balance Between Under- and Over-Reacting to Evidence
**Principle**: Update beliefs incrementally as new evidence arrives. Avoid both stubbornness and over-reaction.
- **Pass**: Evidence of incremental belief updating; new data shifts estimate but doesn't dominate
- **Partial**: Updates happen but may be too large or too small
- **Fail**: Either no updating (static forecast despite new information) or wild swings (anchoring to latest data point)

### 5. Look for the Clashing Causal Forces at Work in Each Problem
**Principle**: For every reason to expect an outcome, look for reasons to expect the opposite.
- **Pass**: Multiple competing hypotheses explicitly considered; both supporting and opposing evidence cited
- **Partial**: Counterarguments mentioned but not weighted
- **Fail**: Single narrative without consideration of opposing forces

### 6. Strive to Distinguish as Many Degrees of Doubt as the Problem Permits
**Principle**: Be as granular as the evidence supports — 72% is better than "likely."
- **Pass**: Probabilities are specific (not just multiples of 5 or 10); granularity matches evidence quality
- **Partial**: Specific probabilities given but may be false precision (e.g., 73.2% without supporting data)
- **Fail**: Vague language ("likely," "possible," "probably") or only round numbers (50%, 70%, 90%)

### 7. Strike the Right Balance Between Under- and Over-Confidence
**Principle**: Neither hide behind "maybe" nor claim certainty where none exists.
- **Pass**: Probabilities in the 20-80% range for genuinely uncertain questions; extremes (>90% or <10%) only with exceptional evidence
- **Partial**: Slight tendency toward overconfidence or underconfidence but generally reasonable
- **Fail**: Systematic overconfidence (many >90%) or systematic underconfidence (everything near 50%)

### 8. Look for the Errors Behind Your Mistakes
**Principle**: Conduct post-mortems on previous forecasts to improve.
- **Pass**: Previous related forecasts reviewed; lessons incorporated
- **Partial**: Acknowledged uncertainty about previous similar assessments
- **Fail**: No reference to past performance or lessons learned; N/A for first forecast in a domain

### 9. Bring Out the Best in Others and Let Others Bring Out the Best in You
**Principle**: Collaborative forecasting with constructive challenge.
- **Pass**: Multiple analytical perspectives considered; devil's advocate arguments made
- **Partial**: Some alternative viewpoints considered
- **Fail**: Single-perspective analysis without challenge; N/A for individual work (apply Red Team role instead)

### 10. Master the Error-Balancing Bicycle (Perpetual Beta)
**Principle**: Treat forecasting as a continuous learning process. Stay humble and self-critical.
- **Pass**: Assumptions clearly stated; limitations acknowledged; update triggers identified
- **Partial**: Some assumptions stated but not all; limitations section present but thin
- **Fail**: Overconfident presentation without acknowledgment of uncertainty or potential for error

---

## STPOT Criteria for Forecast Quality

Every individual forecast MUST satisfy all five STPOT criteria:

### S — Specific
- **Good**: "The European Union will adopt a comprehensive AI regulation framework that includes mandatory algorithmic impact assessments for high-risk AI systems"
- **Bad**: "AI regulation will increase in Europe"
- **Checklist**: Is the outcome precisely defined? Could two reasonable people disagree about whether it happened?

### T — Time-bound
- **Good**: "By December 31, 2028"
- **Bad**: "In the coming years" / "eventually" / "in the near future"
- **Checklist**: Is there a specific date or date range? Could you set a calendar reminder to check?

### P — Probabilistic
- **Good**: "65% probability"
- **Bad**: "Likely" / "probable" / "there's a good chance"
- **Checklist**: Is a specific number given? Does it reflect genuine uncertainty rather than false precision?

### O — Operationalizable
- **Good**: "Resolution: The European Commission publishes a regulation in the Official Journal of the EU that includes 'algorithmic impact assessment' requirements for AI systems classified as high-risk"
- **Bad**: "We'll know it when we see it"
- **Checklist**: Is there a clear data source or observable event that determines resolution? Would a neutral third party be able to judge?

### T — Trackable
- **Good**: "This forecast could be submitted to Metaculus/Good Judgment Open for scoring"
- **Bad**: Vague enough that resolution could be disputed
- **Checklist**: Is the forecast specific enough to be scored? Could it receive a Brier score?

---

## Cognitive Bias Checklist

Review each forecast and the overall analysis for these biases. For each, note: Present / Mitigated / Not Applicable.

### Anchoring
**What it is**: Over-weighting the first piece of information encountered.
**Red flags**:
- First data point found dominates the estimate
- Adjustment from initial estimate is suspiciously small
- Base rate was found after the initial estimate was formed
**Mitigation**: Start with the base rate before reading case-specific evidence. Explicitly check: "If I had encountered the evidence in a different order, would my estimate be different?"

### Availability Bias
**What it is**: Over-weighting easily recalled or vivid examples.
**Red flags**:
- Recent dramatic events dominate the analysis (e.g., over-weighting pandemic risk because of COVID-19)
- Highly publicized cases treated as representative
- Absence of evidence treated as evidence of absence
**Mitigation**: Seek systematic data over anecdotes. Ask: "Is this example representative, or just memorable?"

### Overconfidence
**What it is**: Assigning probabilities that are too extreme (too close to 0% or 100%).
**Red flags**:
- Multiple forecasts at >90% or <10% for genuinely uncertain questions
- No probability in the 30-70% range
- "Definitely" or "impossible" language
- Calibration history not considered
**Mitigation**: Default toward the center for uncertain questions. Ask: "Would I bet my own money at these odds?" Check: "If I made 100 predictions at this probability, would the right fraction come true?"

### Motivated Reasoning
**What it is**: Conclusions driven by desired outcomes rather than evidence.
**Red flags**:
- Forecasts consistently favor a preferred outcome or ideology
- Counterevidence is dismissed or explained away
- Asymmetric evidence standards (strict for unwanted conclusions, lenient for wanted ones)
**Mitigation**: Explicitly state preferred outcomes and check if forecasts lean toward them. Apply equal scrutiny to evidence supporting and opposing the preferred view.

### Dunning-Kruger Effect
**What it is**: Those with less expertise in a domain overestimate their forecasting ability in that domain.
**Red flags**:
- High confidence in domains where the forecaster has limited expertise
- Failure to consult domain experts or existing forecasts
- Dismissal of domain complexity
**Mitigation**: Explicitly rate domain expertise (low/medium/high). For low-expertise domains, weight existing expert forecasts and prediction markets more heavily. Widen uncertainty bands.

### Groupthink / Herding
**What it is**: Conforming to consensus views without independent analysis.
**Red flags**:
- All forecasts align with the current consensus
- No contrarian scenarios considered
- "Everyone says" used as evidence
**Mitigation**: Actively seek dissenting views. For each consensus view, ask: "What would make this wrong?" Ensure at least one scenario challenges the conventional wisdom.

---

## Calibration Guidance

### What Good Calibration Looks Like
A well-calibrated forecaster's probabilities match observed frequencies:
- Their 30% predictions come true ~30% of the time
- Their 70% predictions come true ~70% of the time
- Their 90% predictions come true ~90% of the time
- On a calibration curve (predicted probability vs. observed frequency), they track close to the diagonal

### Red Flags for Poor Calibration
- **Round numbers only**: Using only 50%, 70%, 90% suggests the forecaster isn't thinking carefully about fine distinctions
- **No updates**: Maintaining the same forecast despite new information
- **Clustering at extremes**: Many predictions near 0% or 100% for questions with genuine uncertainty
- **Clustering at center**: Everything near 50% — this may indicate uncertainty aversion rather than genuine assessment
- **Narrative over analysis**: Compelling stories without quantitative reasoning

### Self-Calibration Check
For the set of forecasts in this report:
- Are probabilities spread across the range (not all near 50%, not all near extremes)?
- Do the forecasts use the full granularity appropriate to the evidence?
- For each forecast: "If I made 100 similar predictions at this probability, would roughly this fraction come true?"
- Is there a mix of higher-confidence (>70%) and lower-confidence (<50%) forecasts?

---

## Base Rate / Reference Class Forecasting

### The Principle
Daniel Kahneman and Amos Tversky showed that "the prevalent tendency to underweigh or ignore distributional information is perhaps the major source of error in forecasting." Starting with base rates is the single most impactful improvement to forecasting accuracy.

### Steps
1. **Identify the reference class**: What category of events is this an instance of?
   - Be specific: "government technology modernization programs" is better than "government programs"
   - Consider multiple reference classes and note how estimates differ
2. **Find the base rate**: How often do events in this reference class occur?
   - Historical frequency data
   - Prediction market prices for similar past questions
   - Expert surveys on similar past questions
3. **Adjust for case-specific factors** (inside view):
   - What makes this case different from the reference class average?
   - Document each adjustment and its direction/magnitude
4. **Document the reasoning**: Show the base rate, adjustments, and final estimate

### Common Reference Classes for Foresight
- Technology adoption curves (S-curves): How long do similar technologies take to reach mainstream adoption?
- Regulatory timelines: How long does similar legislation take from proposal to implementation?
- Geopolitical transitions: How often do similar power shifts occur, and what is the typical timeline?
- Market disruptions: What fraction of "disruptive" technologies actually displace incumbents within 10 years?
- International agreements: What fraction of announced agreements are actually implemented on schedule?

### When Base Rates Are Unavailable
- Use the broadest applicable reference class
- Consult prediction markets for related resolved questions
- Note the absence explicitly: "No suitable reference class identified; this forecast relies primarily on inside-view analysis"
- Widen the probability range to reflect greater uncertainty

---

## Brier Score (Post-Hoc Evaluation)

The Brier score measures the accuracy of probabilistic predictions after resolution. Not used during forecasting, but important for evaluating forecast quality retrospectively.

### Formula
BS = (probability - outcome)² where outcome = 1 (occurred) or 0 (did not occur)

### Interpretation
- **0.0**: Perfect prediction (100% probability assigned to what actually happened)
- **0.25**: Equivalent to always predicting 50% (uninformative)
- **0.5**: Worst possible — 100% confidence in the wrong outcome
- **Superforecaster benchmark**: ~0.25 average across diverse geopolitical questions (IARPA ACE tournament)
- **Elite superforecasters**: ~0.15 on questions where they have adequate information

### Decomposition
- **Calibration (reliability)**: How well predicted probabilities match observed frequencies
- **Resolution**: How well the forecaster distinguishes outcomes that occur from those that don't
- **Uncertainty**: The base rate of the event (not under the forecaster's control)

### For This Skill
Include in methodology.md:
- Note that Brier scores can be computed after forecasts resolve
- Provide resolution dates for all forecasts
- Recommend revisiting forecasts at resolution for scoring
