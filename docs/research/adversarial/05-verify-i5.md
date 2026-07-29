# Adversarial verify — I5 (terminal advisory visibility)

**Commit under review:** `38c79d7e8be6e2254db8843ce409fbb143c0facb`  
**Subject:** Show GPT-5.6 advisory notes in the terminal report  
**Branch:** `cursor/incomplete-feature-research-095e`  
**Authority:** `docs/research/adversarial/02-implicit-spec.md` §4 (I5) + §2 non-goals  

## 1. Overall verdict

**PASS**

No surgical code/test fixes required. Working tree left clean of product changes (this verify doc only).

## 2. Per-requirement table

| ID | Verdict | Evidence |
|----|---------|----------|
| **I5-R1** Per-finding advisory lines | **PASS** | `render_terminal` appends `_advisory_line` immediately after `_finding_line` when `item.advisory is not None`; message is exact `AdvisoryNote.message` (`  Advisory: {message}…`). |
| **I5-R2** Benign / confidence | **PASS** | INFO → `benign` token; `confidence > 0` → `confidence=0.90` style; default `0.0` omitted (failure-placeholder path). |
| **I5-R3** Pass-level status | **PASS** | Prints once for `skipped (OPENAI_API_KEY unset)` / `completed` / `not applicable` via `_ADVISORY_PASS_STATUSES`; `"not run"` excluded. |
| **I5-R4** Absent advisory | **PASS** | No advisory line when `advisory is None`; finding stays single `[SEVERITY] …` line (+ headers). |
| **I5-R5** Failed / skipped attachment | **PASS** | Attached `LLM unavailable — advisory pass skipped` prints under the finding; no score/severity mutation in renderer. |
| **I5-R6** Exit codes / A1 | **PASS** | Diff touches only `render_terminal` helpers + tests (+ research plan doc). No changes to `ScanResult.is_clean`, score, finding severities, or CLI exit paths. |
| **I5-R7** Call-site scope | **PASS** | Both `mccoy scan` and `mccoy fix` already call `render_terminal`. `fix_loop` still imports/`await scan(...)` only — **no** `scan_with_advisory` in the fix loop. `cli.py` scan uses advisory; fix does not rewire. |
| **I5-R8** No new flags/commands | **PASS** | No `--format`, advisory-only flag, HTML CLI export, or resume UX in this commit. |
| **AT-I5-1** | **PASS** | `test_terminal_renders_advisory_message_when_present` asserts `"benign docs"`. |
| **AT-I5-2** | **PASS** | `test_terminal_omits_advisory_when_absent` asserts no `Advisory:`, exactly 3 lines (score/tools/finding). |
| **AT-I5-3** | **PASS** | `test_terminal_renders_advisory_failure_message`. |
| **AT-I5-4** | **PASS** | `tests/test_cli.py` still covers vuln→2 + `MCC001`, clean→0, graded `McCoy score:`; suite green. |
| **AT-I5-5** | **PASS** | `test_terminal_prints_advisory_pass_status_but_not_not_run` covers skipped/completed and forbids printing `"not run"`. |
| Never print metadata `"not run"` | **PASS** | Allowlist + explicit test. |
| No fix-loop advisory wiring | **PASS** | `src/mccoy/fix_loop.py` → `scan` only; `cli.py` fix path unchanged. |
| No `--format` / HTML CLI / resume | **PASS** | Diff limited to `report.py`, `test_report.py`, research TDD plan. |
| **A1** presentation-only | **PASS** | Renderer-only; exit/score invariants untouched. |
| Commit message: no `Co-authored-by` | **PASS** | `git log -1` body has no trailer. |
| Pytest | **PASS** | `uv run pytest tests/test_report.py tests/test_cli.py -q` → **15 passed**. |

## 3. Required surgical fixes

None. **FAIL → fix** path not taken.

## 4. Scope creep check

| Check | Result |
|-------|--------|
| I4 HTML CLI (`--format html`, `--report`) | Not present |
| I3 resume IMPLEMENT | Not present |
| Fix-loop `scan_with_advisory` | Not present (correctly left out of scope) |
| Advisory semantics / score / exit changes (A1 violation) | Not present |
| Extra product surface beyond `render_terminal` | Not present |
| Extra file in commit | `docs/research/04-tdd-implementation-plan.md` (research sequencing for I5→DOC→FN). **Not product scope creep**; acceptable planning artifact. Does not implement rejects. |

**Verdict on creep:** Clean for I5 product surface. Mild research-doc bundling only.

## 5. Notes for parent

- Ready to proceed to DOC-I1/I2/I3 (and FN-A per plan) without amending I5 code.
- This verify file is uncommitted by design (adversarial deliverable for parent).
