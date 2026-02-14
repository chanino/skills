#!/usr/bin/env bash
# validate.sh — Post-run validation for deep-research skill output
# Usage: ./validate.sh <output-dir> <mode>
# Example: ./validate.sh ~/Documents/research/fedramp-auth-2026_20260214 quick

set -euo pipefail

# --- Arguments ---
OUTPUT_DIR="${1:?Usage: validate.sh <output-dir> <mode>}"
MODE="${2:?Usage: validate.sh <output-dir> <mode>}"

REPORT="$OUTPUT_DIR/report.md"
SOURCES="$OUTPUT_DIR/sources.md"
SCORECARD_DIR="$(cd "$(dirname "$0")" && pwd)"
SCORECARD="$SCORECARD_DIR/scorecard.md"

# --- Mode parameters ---
case "$MODE" in
  quick)    MIN_SOURCES=5;  MIN_WORDS=1500; MAX_WORDS=3000; MIN_FINDINGS=4 ;;
  standard) MIN_SOURCES=10; MIN_WORDS=3000; MAX_WORDS=6000; MIN_FINDINGS=4 ;;
  deep)     MIN_SOURCES=15; MIN_WORDS=6000; MAX_WORDS=10000; MIN_FINDINGS=4 ;;
  *) echo "ERROR: Mode must be quick, standard, or deep"; exit 1 ;;
esac

PASS=0
FAIL=0
WARN=0
DETAILS=""

check() {
  local name="$1" result="$2" detail="$3"
  if [ "$result" = "PASS" ]; then
    PASS=$((PASS + 1))
    DETAILS+="  [PASS] $name: $detail"$'\n'
  elif [ "$result" = "WARN" ]; then
    WARN=$((WARN + 1))
    DETAILS+="  [WARN] $name: $detail"$'\n'
  else
    FAIL=$((FAIL + 1))
    DETAILS+="  [FAIL] $name: $detail"$'\n'
  fi
}

# ============================================================
# 1. File existence
# ============================================================
if [ -f "$REPORT" ]; then
  check "report.md exists" "PASS" "Found"
else
  check "report.md exists" "FAIL" "Not found at $REPORT"
  echo "FATAL: report.md not found. Cannot continue."
  exit 1
fi

if [ -f "$SOURCES" ]; then
  check "sources.md exists" "PASS" "Found"
else
  check "sources.md exists" "FAIL" "Not found at $SOURCES"
fi

# ============================================================
# 2. Required sections
# ============================================================
for section in "Executive Summary" "Introduction" "Findings" "Analysis" "Limitations" "References"; do
  if grep -qi "$section" "$REPORT"; then
    check "Section: $section" "PASS" "Present"
  else
    check "Section: $section" "FAIL" "Missing"
  fi
done

# ============================================================
# 3. Word count
# ============================================================
WORD_COUNT=$(wc -w < "$REPORT")
if [ "$WORD_COUNT" -ge "$MIN_WORDS" ] && [ "$WORD_COUNT" -le "$MAX_WORDS" ]; then
  check "Word count" "PASS" "$WORD_COUNT words (target: $MIN_WORDS–$MAX_WORDS)"
elif [ "$WORD_COUNT" -ge $((MIN_WORDS * 80 / 100)) ]; then
  check "Word count" "WARN" "$WORD_COUNT words (target: $MIN_WORDS–$MAX_WORDS, within 80%)"
else
  check "Word count" "FAIL" "$WORD_COUNT words (target: $MIN_WORDS–$MAX_WORDS)"
fi

# ============================================================
# 4. Source count
# ============================================================
if [ -f "$SOURCES" ]; then
  # Count citation entries like [1], [2], etc.
  SOURCE_COUNT=$(grep -cE '^\[[0-9]+\]' "$SOURCES" || true)
  if [ "$SOURCE_COUNT" -ge "$MIN_SOURCES" ]; then
    check "Source count" "PASS" "$SOURCE_COUNT sources (min: $MIN_SOURCES)"
  else
    check "Source count" "FAIL" "$SOURCE_COUNT sources (min: $MIN_SOURCES)"
  fi
else
  SOURCE_COUNT=0
  check "Source count" "FAIL" "sources.md missing"
fi

# ============================================================
# 5. Citation integrity
# ============================================================
# Extract all [N] citations from report
REPORT_CITATIONS=$(grep -oE '\[[0-9]+\]' "$REPORT" | sort -t'[' -k1 -n | uniq | tr -d '[]')
ORPHAN_COUNT=0
if [ -f "$SOURCES" ]; then
  for cnum in $REPORT_CITATIONS; do
    if ! grep -qE "^\[$cnum\]" "$SOURCES"; then
      ORPHAN_COUNT=$((ORPHAN_COUNT + 1))
    fi
  done
fi

if [ "$ORPHAN_COUNT" -eq 0 ]; then
  check "Citation integrity" "PASS" "All citations map to sources"
else
  check "Citation integrity" "FAIL" "$ORPHAN_COUNT orphan citation(s) with no source entry"
fi

# Check for sequence gaps
if [ -n "$REPORT_CITATIONS" ]; then
  MAX_CITE=$(echo "$REPORT_CITATIONS" | tail -1)
  EXPECTED_COUNT=$MAX_CITE
  ACTUAL_COUNT=$(echo "$REPORT_CITATIONS" | wc -l)
  if [ "$ACTUAL_COUNT" -eq "$EXPECTED_COUNT" ]; then
    check "Citation sequence" "PASS" "No gaps in [1]–[$MAX_CITE]"
  else
    check "Citation sequence" "WARN" "Expected $EXPECTED_COUNT citations, found $ACTUAL_COUNT unique (possible gaps)"
  fi
fi

# ============================================================
# 6. Tier distribution
# ============================================================
if [ -f "$SOURCES" ]; then
  T1=$(grep -c "T1" "$SOURCES" || true)
  T2=$(grep -c "T2" "$SOURCES" || true)
  T3=$(grep -c "T3" "$SOURCES" || true)
  T4=$(grep -c "T4" "$SOURCES" || true)
  T5=$(grep -c "T5" "$SOURCES" || true)
  TIER_DIST="T1:$T1 T2:$T2 T3:$T3 T4:$T4 T5:$T5"

  # Warn if all sources are T4/T5
  HIGH_TIER=$((T1 + T2 + T3))
  if [ "$HIGH_TIER" -gt 0 ]; then
    check "Tier distribution" "PASS" "$TIER_DIST"
  else
    check "Tier distribution" "FAIL" "No T1–T3 sources ($TIER_DIST)"
  fi
else
  TIER_DIST="N/A"
fi

# ============================================================
# 7. Findings count and per-finding citations
# ============================================================
FINDINGS_COUNT=$(grep -cE '^###' "$REPORT" || true)
# Rough estimate — count ### headings within Findings section
if [ "$FINDINGS_COUNT" -ge "$MIN_FINDINGS" ]; then
  check "Findings sections" "PASS" "$FINDINGS_COUNT subsections found (min: $MIN_FINDINGS)"
else
  check "Findings sections" "WARN" "$FINDINGS_COUNT subsections found (min: $MIN_FINDINGS)"
fi

# ============================================================
# 8. QA summary present
# ============================================================
if grep -qi "QA summary\|quality gate\|gate.*remediation\|gates triggered" "$REPORT"; then
  check "QA summary" "PASS" "QA/gate information found in report"
else
  check "QA summary" "WARN" "No QA summary detected in report"
fi

# ============================================================
# Print scorecard
# ============================================================
TOTAL=$((PASS + FAIL + WARN))
echo ""
echo "============================================"
echo "  DEEP RESEARCH VALIDATION SCORECARD"
echo "============================================"
echo "  Output: $OUTPUT_DIR"
echo "  Mode:   $MODE"
echo "  Date:   $(date +%Y-%m-%d)"
echo "--------------------------------------------"
echo "$DETAILS"
echo "--------------------------------------------"
echo "  PASS: $PASS / $TOTAL"
echo "  WARN: $WARN / $TOTAL"
echo "  FAIL: $FAIL / $TOTAL"
echo "  Words: $WORD_COUNT | Sources: $SOURCE_COUNT | Tiers: $TIER_DIST"
echo "============================================"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "RESULT: ALL CHECKS PASSED"
  VERDICT="PASS"
else
  echo "RESULT: $FAIL CHECK(S) FAILED"
  VERDICT="FAIL"
fi

# ============================================================
# Append to scorecard.md
# ============================================================
{
  echo ""
  echo "## Run: $(date +%Y-%m-%d\ %H:%M)"
  echo ""
  echo "| Field | Value |"
  echo "|-------|-------|"
  echo "| Output | \`$OUTPUT_DIR\` |"
  echo "| Mode | $MODE |"
  echo "| Verdict | **$VERDICT** |"
  echo "| Pass/Warn/Fail | $PASS / $WARN / $FAIL |"
  echo "| Words | $WORD_COUNT |"
  echo "| Sources | $SOURCE_COUNT |"
  echo "| Tiers | $TIER_DIST |"
  echo ""
  echo "<details><summary>Details</summary>"
  echo ""
  echo '```'
  echo "$DETAILS"
  echo '```'
  echo "</details>"
} >> "$SCORECARD"

echo "Scorecard appended to $SCORECARD"
