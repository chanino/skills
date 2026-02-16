#!/usr/bin/env bash
# validate.sh — Smoke tests for gemini-image skill
# Usage: ./validate.sh
# Runs dependency checks, help output tests, and optional live API tests.
# Set GEMINI_API_KEY to enable live generation/analysis tests.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
GEN="$SKILL_DIR/scripts/generate_image.py"
A2T="$SKILL_DIR/scripts/image_to_text.py"
SCORECARD="$SCRIPT_DIR/scorecard.md"
TMP_DIR=$(mktemp -d)

trap 'rm -rf "$TMP_DIR"' EXIT

PASS=0
FAIL=0
WARN=0
SKIP=0
DETAILS=""

check() {
  local name="$1" result="$2" detail="$3"
  case "$result" in
    PASS) PASS=$((PASS + 1)); DETAILS+="  [PASS] $name: $detail"$'\n' ;;
    WARN) WARN=$((WARN + 1)); DETAILS+="  [WARN] $name: $detail"$'\n' ;;
    FAIL) FAIL=$((FAIL + 1)); DETAILS+="  [FAIL] $name: $detail"$'\n' ;;
    SKIP) SKIP=$((SKIP + 1)); DETAILS+="  [SKIP] $name: $detail"$'\n' ;;
  esac
}

# ============================================================
# 1. Dependency checks
# ============================================================
echo "--- Checking dependencies ---"

if command -v python3 &>/dev/null; then
  PY_VER=$(python3 --version 2>&1)
  check "Python 3" "PASS" "$PY_VER"
else
  check "Python 3" "FAIL" "python3 not found in PATH"
fi

if python3 -c "import google.genai" 2>/dev/null; then
  check "google-genai package" "PASS" "Importable"
else
  check "google-genai package" "FAIL" "Cannot import google.genai — run: pip install google-genai"
fi

if python3 -c "import dotenv" 2>/dev/null; then
  check "python-dotenv package" "PASS" "Importable"
else
  check "python-dotenv package" "WARN" "Cannot import dotenv — run: pip install python-dotenv"
fi

# ============================================================
# 2. API key check
# ============================================================
echo "--- Checking API key ---"

HAS_API_KEY=false
if [ -n "${GEMINI_API_KEY:-}" ]; then
  check "GEMINI_API_KEY" "PASS" "Set (${#GEMINI_API_KEY} chars)"
  HAS_API_KEY=true
else
  check "GEMINI_API_KEY" "WARN" "Not set — live tests will be skipped"
fi

# ============================================================
# 3. Script existence and help output
# ============================================================
echo "--- Checking scripts ---"

if [ -f "$GEN" ]; then
  check "generate_image.py exists" "PASS" "Found"
else
  check "generate_image.py exists" "FAIL" "Not found at $GEN"
fi

if [ -f "$A2T" ]; then
  check "image_to_text.py exists" "PASS" "Found"
else
  check "image_to_text.py exists" "FAIL" "Not found at $A2T"
fi

# --help tests
GEN_HELP=$(python3 "$GEN" --help 2>&1 || true)
if echo "$GEN_HELP" | grep -q "\-\-aspect"; then
  check "generate_image.py --help (--aspect)" "PASS" "Flag documented"
else
  check "generate_image.py --help (--aspect)" "FAIL" "--aspect flag not found in help output"
fi

if echo "$GEN_HELP" | grep -q "\-\-size"; then
  check "generate_image.py --help (--size)" "PASS" "Flag documented"
else
  check "generate_image.py --help (--size)" "FAIL" "--size flag not found in help output"
fi

A2T_HELP=$(python3 "$A2T" --help 2>&1 || true)
if echo "$A2T_HELP" | grep -q "\-\-input\|\\-i"; then
  check "image_to_text.py --help (-i)" "PASS" "Flag documented"
else
  check "image_to_text.py --help (-i)" "FAIL" "-i/--input flag not found in help output"
fi

# ============================================================
# 4. Error handling tests
# ============================================================
echo "--- Checking error handling ---"

# Missing prompt should exit non-zero
if python3 "$GEN" 2>/dev/null; then
  check "generate_image.py missing prompt" "FAIL" "Expected non-zero exit code"
else
  check "generate_image.py missing prompt" "PASS" "Exits with error as expected"
fi

# Missing input file should exit non-zero
if python3 "$A2T" -i "/nonexistent/file.png" 2>/dev/null; then
  check "image_to_text.py missing file" "FAIL" "Expected non-zero exit code"
else
  check "image_to_text.py missing file" "PASS" "Exits with error as expected"
fi

# ============================================================
# 5. Live generation test (requires API key)
# ============================================================
echo "--- Live tests ---"

if $HAS_API_KEY; then
  echo "Running live generation test..."
  GEN_OUT="$TMP_DIR/test_gen.png"
  if python3 "$GEN" "A solid red circle on a white background, simple flat icon" -o "$GEN_OUT" --size 512 2>"$TMP_DIR/gen_stderr.txt"; then
    if [ -f "$GEN_OUT" ]; then
      FILE_SIZE=$(stat -c%s "$GEN_OUT" 2>/dev/null || stat -f%z "$GEN_OUT" 2>/dev/null || echo "0")
      if [ "$FILE_SIZE" -gt 10240 ]; then
        check "Generate smoke test" "PASS" "Output ${FILE_SIZE} bytes (>10KB)"
      else
        check "Generate smoke test" "FAIL" "Output only ${FILE_SIZE} bytes (<10KB)"
      fi
    else
      check "Generate smoke test" "FAIL" "Output file not created"
    fi
  else
    STDERR=$(cat "$TMP_DIR/gen_stderr.txt" 2>/dev/null || echo "unknown error")
    check "Generate smoke test" "FAIL" "Script exited with error: $STDERR"
  fi

  # ============================================================
  # 6. Live analysis test (requires generated image)
  # ============================================================
  if [ -f "$GEN_OUT" ]; then
    echo "Running live analysis test..."
    A2T_OUT="$TMP_DIR/test_analysis.txt"
    if python3 "$A2T" -i "$GEN_OUT" "Describe this image in one sentence" -o "$A2T_OUT" 2>"$TMP_DIR/a2t_stderr.txt"; then
      if [ -f "$A2T_OUT" ]; then
        CHAR_COUNT=$(wc -c < "$A2T_OUT")
        if [ "$CHAR_COUNT" -gt 50 ]; then
          check "Analyze smoke test" "PASS" "Output ${CHAR_COUNT} chars (>50)"
        else
          check "Analyze smoke test" "FAIL" "Output only ${CHAR_COUNT} chars (<50)"
        fi
      else
        check "Analyze smoke test" "FAIL" "Output file not created"
      fi
    else
      STDERR=$(cat "$TMP_DIR/a2t_stderr.txt" 2>/dev/null || echo "unknown error")
      check "Analyze smoke test" "FAIL" "Script exited with error: $STDERR"
    fi

    # ============================================================
    # 7. Stdin pipe test
    # ============================================================
    echo "Running stdin pipe test..."
    PIPE_OUT=$(cat "$GEN_OUT" | python3 "$A2T" "What color is the main shape?" 2>/dev/null || echo "")
    if [ ${#PIPE_OUT} -gt 10 ]; then
      check "Stdin pipe test" "PASS" "Got ${#PIPE_OUT} chars via pipe"
    else
      check "Stdin pipe test" "FAIL" "Pipe output too short (${#PIPE_OUT} chars)"
    fi
  else
    check "Analyze smoke test" "SKIP" "No generated image to analyze"
    check "Stdin pipe test" "SKIP" "No generated image to pipe"
  fi
else
  check "Generate smoke test" "SKIP" "GEMINI_API_KEY not set"
  check "Analyze smoke test" "SKIP" "GEMINI_API_KEY not set"
  check "Stdin pipe test" "SKIP" "GEMINI_API_KEY not set"
fi

# ============================================================
# Print scorecard
# ============================================================
TOTAL=$((PASS + FAIL + WARN + SKIP))
echo ""
echo "============================================"
echo "  GEMINI-IMAGE VALIDATION SCORECARD"
echo "============================================"
echo "  Date:   $(date +%Y-%m-%d)"
echo "--------------------------------------------"
echo "$DETAILS"
echo "--------------------------------------------"
echo "  PASS: $PASS / $TOTAL"
echo "  WARN: $WARN / $TOTAL"
echo "  FAIL: $FAIL / $TOTAL"
echo "  SKIP: $SKIP / $TOTAL"
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
  echo "| Verdict | **$VERDICT** |"
  echo "| Pass/Warn/Fail/Skip | $PASS / $WARN / $FAIL / $SKIP |"
  echo "| API Key | $(if $HAS_API_KEY; then echo "Set"; else echo "Not set"; fi) |"
  echo ""
  echo "<details><summary>Details</summary>"
  echo ""
  echo '```'
  echo "$DETAILS"
  echo '```'
  echo "</details>"
} >> "$SCORECARD"

echo "Scorecard appended to $SCORECARD"
