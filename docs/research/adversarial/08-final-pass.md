# Final adversarial pass — keep-list product commits

**Branch:** `cursor/incomplete-feature-research-095e`  
**Scope:** Three product commits vs `origin/main` (ignore research-only commits before them)  
**Authority:** `01-need-verification.md` keep/reject + `02-implicit-spec.md` (post-amendment)  
**Prior verifies:** `05-verify-i5.md`, `06-verify-doc.md`, `07-verify-fn.md`  

**Product commits audited:**

| SHA | Subject |
|-----|---------|
| `38c79d7` | Show GPT-5.6 advisory notes in the terminal report (I5) |
| `7bdc3c7` | Narrow marketing claims to match the Python stdio CLI (DOC-I1/I2/I3) |
| `ab28f42` | Mark fix-attempted findings in the terminal report (FN-A) |

**Cumulative product surface vs main:** `src/mccoy/report.py`, `tests/test_report.py`, `tests/test_claim_honesty.py`, `README.md`, `site/.../overview.md`, `site/.../fix-loop.md`, `site/src/pages/index.astro` (+ research verify/plan docs bundled in those commits).

---

## 1. Overall verdict

# GO

All three keep-list items are closed correctly. No reject-list IMPLEMENT leakage. A1 / R4 / R2 / R3 invariants preserved. Full suite green. Product commit messages have no `Co-authored-by`. **No must-fix product bugs; no uncommitted product fixes.**

---

## 2. Per keep-list item status

| ID | Status | Closure evidence |
|----|--------|------------------|
| **I5** | **CLOSED** | `render_terminal` prints per-finding `Advisory: {message}` (+ benign / confidence when present), allowlisted pass status once, never `"not run"`. Fix loop still uses `scan()` only — no advisory wiring (I5-R7). Tests AT-I5-1..5 in `tests/test_report.py`. |
| **DOC-I1** | **CLOSED** | README + overview drop `stdio or HTTP`; HTTP scoped to library `connect_http` / CLI stdio-only. Landing does not newly claim HTTP. Guarded by `test_claim_honesty.py`. |
| **DOC-I2** | **CLOSED** | README / overview / landing replace unbounded “any MCP…” with Python stdio scope. Guarded. |
| **DOC-I3** | **CLOSED** | Resume promise removed from README Codex bullet and `fix-loop.md` (“After the loop”; ephemeral sessions). Guarded (`so you can resume` + resume-near-thread_id). |
| **FN** | **CLOSED via Option A** | `[fix attempted]` on finding line when `fix_attempted=True`; absent by default. A xor B satisfied via A; Option B not required. `fix-loop.md` “marked `fix_attempted`” is now accurate for terminal. |

---

## 3. Reject-list leakage check

| Rejected work | Present in product diff / CLI? | Verdict |
|---------------|--------------------------------|---------|
| I1 IMPLEMENT `--url` / HTTP scan CLI | No — `cli.py` unchanged; no `--url` | **CLEAN** |
| I2 IMPLEMENT generic `--command` / `--args` | No | **CLEAN** |
| I3 IMPLEMENT Codex resume UX / argv | No — docs only removed resume promise; no resume wiring | **CLEAN** |
| I4 IMPLEMENT HTML CLI (`--format html`, `--report`) | No — `render_html` remains library-only | **CLEAN** |
| I6 IMPLEMENT `resolved` lifecycle / report | No — field unused; not read by renderer | **CLEAN** |
| I7 IMPLEMENT wire `infra_result` | No — helper still unwired; CLI exit-3 string path unchanged | **CLEAN** |
| I8 IMPLEMENT CRITICAL-emitting rule | No | **CLEAN** |

**I5 / FN non-goals:** `"not run"` not printed; no `scan_with_advisory` in `fix_loop.py`; no new flags; no HTML requirement for FN marker.

**Invariants (spot-check):**

| Invariant | Result |
|-----------|--------|
| **A1** advisory non-verdict | Presentation-only in `report.py`; no score/severity/exit mutation |
| **R4** exit codes | Untouched in product commits; CLI tests still pass |
| **R2** clean skip / fresh re-scan | `fix_loop.py` not product-changed |
| **R3** Codex failure → mark + continue | Attempt semantics unchanged; FN only surfaces existing flag |

---

## 4. Test results

```
uv run pytest -q
→ 53 passed, 1 warning (pre-existing HTTP client deprecation in integration)

uv run ruff check src tests
→ All checks passed!

uv run mypy src/mccoy
→ Success: no issues found in 11 source files
```

Acceptance coverage vs implicit spec: AT-I5-1..5, FN-A True/False marker tests, DOC forbidden-phrase guards — all present and green. CLI graded-report / exit-code tests still pass (AT-I5-4).

---

## 5. Commit message co-author check

Checked: `git log origin/main..HEAD --format='%h %s%n%b%n---'` focusing on the three **product** commits.

| Commit | `Co-authored-by`? |
|--------|-------------------|
| `38c79d7` I5 | **None** |
| `7bdc3c7` DOC | **None** |
| `ab28f42` FN-A | **None** |

(Research commits before the product trio still carry `Co-authored-by`; out of scope for this checklist item.)

---

## 6. Remaining issues

### Must-fix

**None.** No product code/doc fixes applied; working tree product paths clean of auditor edits.

### Accept (non-blocking)

1. **AT-I5-5 partial:** unit test asserts skipped + completed + forbids `"not run"`; `"not applicable"` is in the allowlist but not separately asserted. Implementation correct; optional test completeness only.
2. **Mild research bundling:** I5 commit includes `04-tdd-implementation-plan.md`; DOC commit includes `05-verify-i5.md`; FN commit includes `06-verify-doc.md`. Not reject leakage / not drive-by refactors of product logic.
3. **Pre-existing dead scaffolding** (`infra_result`, `Finding.resolved`, unused `thread_id` param, library `render_html` / `connect_http`) remains — correctly left alone per reject/hygiene policy.

### Surgical assessment

Product diffs are narrowly scoped to renderer + claim surfaces + matching tests. No drive-by refactors in `cli.py`, `scanner.py`, `fix_loop.py`, or models.

---

## Bottom line for parent

**GO.** Keep-list complete. Uncommitted product fixes: **none**.
