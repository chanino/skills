# gemini-image Validation Scorecard

Results from `validate.sh` runs are appended below.

## Run: 2026-02-16 10:17

| Field | Value |
|-------|-------|
| Verdict | **PASS** |
| Pass/Warn/Fail/Skip | 10 / 1 / 0 / 3 |
| API Key | Not set |

<details><summary>Details</summary>

```
  [PASS] Python 3: Python 3.12.3
  [PASS] google-genai package: Importable
  [PASS] python-dotenv package: Importable
  [WARN] GEMINI_API_KEY: Not set — live tests will be skipped
  [PASS] generate_image.py exists: Found
  [PASS] image_to_text.py exists: Found
  [PASS] generate_image.py --help (--aspect): Flag documented
  [PASS] generate_image.py --help (--size): Flag documented
  [PASS] image_to_text.py --help (-i): Flag documented
  [PASS] generate_image.py missing prompt: Exits with error as expected
  [PASS] image_to_text.py missing file: Exits with error as expected
  [SKIP] Generate smoke test: GEMINI_API_KEY not set
  [SKIP] Analyze smoke test: GEMINI_API_KEY not set
  [SKIP] Stdin pipe test: GEMINI_API_KEY not set

```
</details>

## Run: 2026-02-16 10:21

| Field | Value |
|-------|-------|
| Verdict | **FAIL** |
| Pass/Warn/Fail/Skip | 11 / 0 / 1 / 2 |
| API Key | Set |

<details><summary>Details</summary>

```
  [PASS] Python 3: Python 3.12.3
  [PASS] google-genai package: Importable
  [PASS] python-dotenv package: Importable
  [PASS] GEMINI_API_KEY: Set (39 chars)
  [PASS] generate_image.py exists: Found
  [PASS] image_to_text.py exists: Found
  [PASS] generate_image.py --help (--aspect): Flag documented
  [PASS] generate_image.py --help (--size): Flag documented
  [PASS] image_to_text.py --help (-i): Flag documented
  [PASS] generate_image.py missing prompt: Exits with error as expected
  [PASS] image_to_text.py missing file: Exits with error as expected
  [FAIL] Generate smoke test: Script exited with error: Generating image for prompt: 'A solid red circle on a white background, simple flat icon' using model: 'gemini-2.0-flash-preview-image-generation'...
Transient error (attempt 1/3): 404 NOT_FOUND. {'error': {'code': 404, 'message': 'models/gemini-2.0-flash-preview-image-generation is not found for API version v1beta, or is not supported for generateContent. Call ListModels to see the list of available models and their supported methods.', 'status': 'NOT_FOUND'}}
Retrying in 2s...
Transient error (attempt 2/3): 404 NOT_FOUND. {'error': {'code': 404, 'message': 'models/gemini-2.0-flash-preview-image-generation is not found for API version v1beta, or is not supported for generateContent. Call ListModels to see the list of available models and their supported methods.', 'status': 'NOT_FOUND'}}
Retrying in 4s...
Error during image generation: 404 NOT_FOUND. {'error': {'code': 404, 'message': 'models/gemini-2.0-flash-preview-image-generation is not found for API version v1beta, or is not supported for generateContent. Call ListModels to see the list of available models and their supported methods.', 'status': 'NOT_FOUND'}}
  [SKIP] Analyze smoke test: No generated image to analyze
  [SKIP] Stdin pipe test: No generated image to pipe

```
</details>

## Run: 2026-02-16 10:23

| Field | Value |
|-------|-------|
| Verdict | **PASS** |
| Pass/Warn/Fail/Skip | 14 / 0 / 0 / 0 |
| API Key | Set |

<details><summary>Details</summary>

```
  [PASS] Python 3: Python 3.12.3
  [PASS] google-genai package: Importable
  [PASS] python-dotenv package: Importable
  [PASS] GEMINI_API_KEY: Set (39 chars)
  [PASS] generate_image.py exists: Found
  [PASS] image_to_text.py exists: Found
  [PASS] generate_image.py --help (--aspect): Flag documented
  [PASS] generate_image.py --help (--size): Flag documented
  [PASS] image_to_text.py --help (-i): Flag documented
  [PASS] generate_image.py missing prompt: Exits with error as expected
  [PASS] image_to_text.py missing file: Exits with error as expected
  [PASS] Generate smoke test: Output 258821 bytes (>10KB)
  [PASS] Analyze smoke test: Output 125 chars (>50)
  [PASS] Stdin pipe test: Got 26 chars via pipe

```
</details>
