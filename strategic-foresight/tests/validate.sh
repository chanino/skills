#!/usr/bin/env bash
# Structural validation for strategic-foresight skill outputs
# Usage: bash validate.sh <output-directory> <mode>
# Example: bash validate.sh ~/Documents/foresight/remote-work-us-federal_20260221 scan

set -euo pipefail

DIR="${1:?Usage: validate.sh <output-directory> <mode>}"
MODE="${2:?Usage: validate.sh <output-directory> <mode>}"

FORECAST="$DIR/forecast.md"
METHODOLOGY="$DIR/methodology.md"

PASS=0
FAIL=0
WARN=0

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }
warn() { echo "  WARN: $1"; WARN=$((WARN + 1)); }

echo "=== Strategic Foresight Structural Validation ==="
echo "Directory: $DIR"
echo "Mode: $MODE"
echo ""

# --- File Existence ---
echo "--- File Existence ---"
if [[ -f "$FORECAST" ]]; then pass "forecast.md exists"; else fail "forecast.md missing"; fi
if [[ -f "$METHODOLOGY" ]]; then pass "methodology.md exists"; else fail "methodology.md missing"; fi

if [[ ! -f "$FORECAST" || ! -f "$METHODOLOGY" ]]; then
    echo ""
    echo "Cannot continue validation without both files."
    echo "Results: $PASS passed, $FAIL failed, $WARN warnings"
    exit 1
fi

# --- Word Counts ---
echo ""
echo "--- Word Counts ---"
FC_WORDS=$(wc -w < "$FORECAST" | tr -d ' ')
MC_WORDS=$(wc -w < "$METHODOLOGY" | tr -d ' ')

echo "  forecast.md: $FC_WORDS words"
echo "  methodology.md: $MC_WORDS words"

case "$MODE" in
    scan)
        [[ $FC_WORDS -ge 1500 && $FC_WORDS -le 5000 ]] && pass "forecast.md word count in range (1500-5000 for scan)" || warn "forecast.md word count $FC_WORDS outside target (2000-4000, allowing 1500-5000)"
        [[ $MC_WORDS -ge 300 && $MC_WORDS -le 1500 ]] && pass "methodology.md word count in range (300-1500 for scan)" || warn "methodology.md word count $MC_WORDS outside target (500-1000, allowing 300-1500)"
        ;;
    standard)
        [[ $FC_WORDS -ge 4000 && $FC_WORDS -le 11000 ]] && pass "forecast.md word count in range (4000-11000 for standard)" || warn "forecast.md word count $FC_WORDS outside target (5000-9000, allowing 4000-11000)"
        [[ $MC_WORDS -ge 750 && $MC_WORDS -le 2500 ]] && pass "methodology.md word count in range (750-2500 for standard)" || warn "methodology.md word count $MC_WORDS outside target (1000-2000, allowing 750-2500)"
        ;;
    full)
        [[ $FC_WORDS -ge 7000 && $FC_WORDS -le 18000 ]] && pass "forecast.md word count in range (7000-18000 for full)" || warn "forecast.md word count $FC_WORDS outside target (9000-15000, allowing 7000-18000)"
        [[ $MC_WORDS -ge 1500 && $MC_WORDS -le 4500 ]] && pass "methodology.md word count in range (1500-4500 for full)" || warn "methodology.md word count $MC_WORDS outside target (2000-3500, allowing 1500-4500)"
        ;;
    *)
        fail "Unknown mode: $MODE (expected scan, standard, or full)"
        ;;
esac

# --- Required Sections: forecast.md ---
echo ""
echo "--- forecast.md Required Sections ---"

check_section() {
    local file="$1" pattern="$2" label="$3"
    if grep -qiE "$pattern" "$file"; then
        pass "$label"
    else
        fail "$label"
    fi
}

check_section "$FORECAST" "^#+ .*Executive.*Foresight.*Summary|^#+ .*Executive Summary" "Executive Foresight Summary"
check_section "$FORECAST" "^#+ .*Signal Map" "Signal Map"
check_section "$FORECAST" "^#+ .*Three Horizons" "Three Horizons Analysis"
check_section "$FORECAST" "^#+ .*Critical Uncertainties" "Critical Uncertainties"
check_section "$FORECAST" "^#+ .*Key Forecasts|^#+ .*Forecast [0-9]" "Key Forecasts"
check_section "$FORECAST" "^#+ .*Indicators to Watch|^#+ .*Indicators" "Indicators to Watch"
check_section "$FORECAST" "^#+ .*Limitations|^#+ .*Caveats" "Limitations"

# Mode-conditional sections
if [[ "$MODE" == "standard" || "$MODE" == "full" ]]; then
    check_section "$FORECAST" "^#+ .*Scenario" "Scenario Matrix (standard/full)"
    check_section "$FORECAST" "^#+ .*Causal Layered|^#+ .*CLA" "Causal Layered Analysis (standard/full)"
fi

if [[ "$MODE" == "full" ]]; then
    check_section "$FORECAST" "^#+ .*Backcast" "Backcasting (full)"
    check_section "$FORECAST" "^#+ .*Wind Tunnel" "Wind Tunneling (full)"
fi

# Scan mode should NOT have scenarios
if [[ "$MODE" == "scan" ]]; then
    if grep -qiE "^#+ .*Scenario Matrix|^#+ .*Scenario [0-9]" "$FORECAST"; then
        warn "Scenario section present in scan mode (should be absent)"
    else
        pass "No scenario section in scan mode (correct)"
    fi
fi

# --- Required Sections: methodology.md ---
echo ""
echo "--- methodology.md Required Sections ---"

check_section "$METHODOLOGY" "^#+ .*Frameworks Applied" "Frameworks Applied"
check_section "$METHODOLOGY" "^#+ .*Scanning Strategy" "Scanning Strategy"
check_section "$METHODOLOGY" "^#+ .*Assumptions" "Assumptions Log"
check_section "$METHODOLOGY" "^#+ .*Tetlock|^#+ .*10 Commandments" "Tetlock 10 Commandments"
check_section "$METHODOLOGY" "^#+ .*STPOT" "STPOT Compliance Matrix"
check_section "$METHODOLOGY" "^#+ .*Cognitive Bias|^#+ .*Bias" "Cognitive Bias Checklist"
check_section "$METHODOLOGY" "^#+ .*Sources|^#+ .*Source Distribution" "Source List"
check_section "$METHODOLOGY" "^#+ .*Glossary" "Glossary"

# --- Probability Statements ---
echo ""
echo "--- Forecast Quality Checks ---"

# Check for specific probability statements (XX%)
PROB_COUNT=$(grep -coE '[0-9]{1,3}%' "$FORECAST" || echo 0)
if [[ $PROB_COUNT -ge 2 ]]; then
    pass "Found $PROB_COUNT probability statements in forecast.md"
else
    fail "Only $PROB_COUNT probability statements found (expected ≥2)"
fi

# Check for vague probability language in forecast sections
VAGUE_COUNT=$(grep -ciE '\b(likely|unlikely|probably|possible|may happen|could occur)\b' "$FORECAST" || echo 0)
if [[ $VAGUE_COUNT -le 3 ]]; then
    pass "Low vague probability language ($VAGUE_COUNT instances)"
else
    warn "Found $VAGUE_COUNT instances of vague probability language — check forecasts use specific numbers"
fi

# Check for STPOT-formatted forecasts
FORECAST_COUNT=$(grep -cE '^\*\*Probability\*\*:|^- \*\*Probability\*\*:' "$FORECAST" || echo 0)
echo "  INFO: Found $FORECAST_COUNT formatted forecast entries"

case "$MODE" in
    scan)     [[ $FORECAST_COUNT -ge 2 ]] && pass "Forecast count ≥2 for scan" || warn "Expected ≥2 forecasts for scan, found $FORECAST_COUNT" ;;
    standard) [[ $FORECAST_COUNT -ge 4 ]] && pass "Forecast count ≥4 for standard" || warn "Expected ≥4 forecasts for standard, found $FORECAST_COUNT" ;;
    full)     [[ $FORECAST_COUNT -ge 6 ]] && pass "Forecast count ≥6 for full" || warn "Expected ≥6 forecasts for full, found $FORECAST_COUNT" ;;
esac

# --- Citation Integrity ---
echo ""
echo "--- Citation Integrity ---"

# Extract citation numbers from forecast.md
FC_CITATIONS=$(grep -oE '\[[0-9]+\]' "$FORECAST" | sort -t'[' -k1 -n | uniq)
FC_MAX_CITE=$(echo "$FC_CITATIONS" | grep -oE '[0-9]+' | sort -n | tail -1 || echo 0)

# Extract source numbers from methodology.md
MC_SOURCES=$(grep -oE '^\[[0-9]+\]' "$METHODOLOGY" | sort -t'[' -k1 -n | uniq)
MC_MAX_SOURCE=$(echo "$MC_SOURCES" | grep -oE '[0-9]+' | sort -n | tail -1 || echo 0)

echo "  INFO: Highest citation in forecast.md: [$FC_MAX_CITE]"
echo "  INFO: Highest source in methodology.md: [$MC_MAX_SOURCE]"

if [[ $FC_MAX_CITE -le $MC_MAX_SOURCE && $MC_MAX_SOURCE -gt 0 ]]; then
    pass "All citations in forecast.md have corresponding sources in methodology.md"
else
    if [[ $MC_MAX_SOURCE -eq 0 ]]; then
        warn "No numbered sources found in methodology.md — check format"
    else
        warn "Citation [$FC_MAX_CITE] in forecast.md may exceed source count [$MC_MAX_SOURCE] in methodology.md"
    fi
fi

# Check for citation gaps in methodology.md
if [[ $MC_MAX_SOURCE -gt 0 ]]; then
    GAPS=0
    for i in $(seq 1 "$MC_MAX_SOURCE"); do
        if ! grep -q "^\[$i\]" "$METHODOLOGY"; then
            ((GAPS++))
        fi
    done
    if [[ $GAPS -eq 0 ]]; then
        pass "No citation gaps in methodology.md source numbering"
    else
        warn "$GAPS gaps in methodology.md source numbering"
    fi
fi

# --- Three Horizons Order ---
echo ""
echo "--- Framework-Specific Checks ---"

# Check H1-H3-H2 presentation order
H1_LINE=$(grep -nE '^#+ .*H1|^#+ .*Current System|^#+ .*Business as Usual' "$FORECAST" | head -1 | cut -d: -f1 || echo 0)
H3_LINE=$(grep -nE '^#+ .*H3|^#+ .*Seeds.*Future|^#+ .*New Paradigm' "$FORECAST" | head -1 | cut -d: -f1 || echo 0)
H2_LINE=$(grep -nE '^#+ .*H2 |^#+ .*H2—|^#+ .*Transition' "$FORECAST" | head -1 | cut -d: -f1 || echo 0)

if [[ $H1_LINE -gt 0 && $H3_LINE -gt 0 && $H2_LINE -gt 0 ]]; then
    if [[ $H1_LINE -lt $H3_LINE && $H3_LINE -lt $H2_LINE ]]; then
        pass "Three Horizons in correct H1-H3-H2 order"
    else
        warn "Three Horizons may not be in H1-H3-H2 order (H1:$H1_LINE, H3:$H3_LINE, H2:$H2_LINE)"
    fi
else
    warn "Could not detect Three Horizons section ordering"
fi

# Check for H2+/H2- distinction
if grep -qE 'H2\+|H2-|transformative|sustaining' "$FORECAST"; then
    pass "H2+/H2- distinction present"
else
    warn "H2+/H2- distinction not detected"
fi

# Scenario probability sum check (standard/full only)
if [[ "$MODE" == "standard" || "$MODE" == "full" ]]; then
    SCENARIO_PROBS=$(grep -oE 'p\s*=\s*[0-9]+%|probability.*[0-9]+%' "$FORECAST" | grep -oE '[0-9]+' || true)
    if [[ -n "$SCENARIO_PROBS" ]]; then
        SUM=0
        while read -r p; do ((SUM += p)); done <<< "$SCENARIO_PROBS"
        if [[ $SUM -ge 90 && $SUM -le 110 ]]; then
            pass "Scenario probabilities sum to $SUM% (acceptable range 90-110%)"
        else
            warn "Scenario probabilities sum to $SUM% (expected ~100%)"
        fi
    else
        warn "Could not extract scenario probabilities for sum check"
    fi
fi

# --- Summary ---
echo ""
echo "=== Validation Summary ==="
echo "  PASS: $PASS"
echo "  FAIL: $FAIL"
echo "  WARN: $WARN"
echo ""

if [[ $FAIL -eq 0 ]]; then
    echo "  RESULT: ALL STRUCTURAL CHECKS PASSED"
    exit 0
elif [[ $FAIL -le 2 ]]; then
    echo "  RESULT: MINOR ISSUES ($FAIL failures)"
    exit 0
else
    echo "  RESULT: SIGNIFICANT ISSUES ($FAIL failures)"
    exit 1
fi
