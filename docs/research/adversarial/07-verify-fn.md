# Adversarial verify — FN Option A (`fix_attempted` terminal marker)

**Commit under review:** `ab28f425480a8af92dbc45e1f8899c393c1ddb43`  
**Subject:** Mark fix-attempted findings in the terminal report  
**Branch:** `cursor/incomplete-feature-research-095e`  
**Authority:** `docs/research/adversarial/02-implicit-spec.md` §6 (FN A xor B) + §2 / §6.4 non-goals

## 1. Overall verdict

**PASS**

Uncommitted product fixes: **none**. This verify file only (adversarial deliverable; do not treat as a required product commit).

## 2. Per-check table

| Check | Verdict | Evidence |
|-------|---------|----------|
| FN-A-R1 marker when True | **PASS** | `_finding_line` appends ` [fix attempted]` when `item.fix_attempted`. `test_terminal_marks_fix_attempted_findings` asserts marker on the `[HIGH]` finding line. |
| FN-A-R2 absent when False/default | **PASS** | Marker gated on truthy `fix_attempted` only. `test_terminal_omits_fix_attempted_marker_by_default` asserts no `"fix attempted"` on the finding line (`Finding.fix_attempted` defaults `False`). |
| FN-A-R3 no exit/severity change | **PASS** | Change is presentation-only in `render_terminal` / `_finding_line`; does not touch `ScanResult` score, `Finding.severity`, `is_clean`, CLI exit mapping, or fix-loop attempt semantics. `tests/test_fix_loop.py` + `tests/test_cli.py` still pass (exit 2 / attempt flags unchanged). |
| Chose Option A (not B) | **PASS** | IMPLEMENT in `report.py` + FN-A unit tests. No Option B doc-down of “marked `fix_attempted`”. `fix-loop.md` still says marked `fix_attempted` — now true for terminal; allowed under §6.3 (“unless Option A ships”). |
| No I6 resolved-history creep | **PASS** | Commit does not read/set `Finding.resolved`, add resolved UI, or change loop history model. HTML / models / fix_loop untouched for resolved. |
| No HTML `fix_attempted` requirement | **PASS** | `report.html.j2` unchanged; no HTML tests for the marker. Terminal-only closure matches §6.4. |
| No loop attempt-keying change | **PASS** | `fix_loop.py` not in commit diff. |
| No `Co-authored-by` | **PASS** | `git log -1` body has no trailer. |
| Pytest (required suite) | **PASS** | `uv run pytest tests/test_report.py tests/test_fix_loop.py tests/test_cli.py -q` → **26 passed**. |

## 3. Diff scope (adversarial)

| Path | Role | Scope OK? |
|------|------|-----------|
| `src/mccoy/report.py` | Option A: terminal marker | Yes |
| `tests/test_report.py` | FN-A-R1 / R2 acceptance | Yes |
| `docs/research/adversarial/06-verify-doc.md` | Prior DOC verify artifact bundled | Research-only; not I6/HTML/reject IMPLEMENT |

Rejected §2 surfaces absent from this commit: I1/I2/I3 IMPLEMENT, I4 HTML CLI, I6 resolved lifecycle, I7 `infra_result`, I8 CRITICAL rule.

## 4. Option A xor B

Closure path: **Option A**. Option B not required and not performed. Docs that still say “marked `fix_attempted`” are consistent with A, not a dual-path failure.

## 5. Required surgical fixes

None. **FAIL → fix** path not taken.

## 6. Notes for parent

- FN keep-list item is closed via terminal marker; prefer leaving Option B docs as-is.
- Marker string is `[fix attempted]` on the finding line (spec allows implementation-defined form; adjacent / clear).
- This verify file is uncommitted by design (adversarial deliverable for parent).
