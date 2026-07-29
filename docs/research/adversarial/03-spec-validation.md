# Spec validation — `02-implicit-spec.md`

Auditor stance: adversarially attack incompleteness, contradictions, untestable language, scope
creep, reject-list leakage, and claim-surgery accuracy against code +
`01-need-verification.md`. Prefer FAIL notes + minimal patches over a full rewrite.

**Documents under test:** `docs/research/adversarial/02-implicit-spec.md`  
**Authority:** `01-need-verification.md` keep/reject lists; `src/mccoy/` + `tests/`; public claims.  
**Amendments:** Surgical edits were applied to `02-implicit-spec.md` (marked
`<!-- amended: validation -->`). Pre-amendment FAILs are recorded below; post-amendment status
is used for the go/no-go.

---

## 1. Overall verdict

**APPROVE WITH FIXES** — fixes applied in-place to the implicit spec.

After amendments, the document is fit as the research baseline for I5 + DOC-I1/I2/I3 + FN (A xor B).
It does **not** require advisory wiring into the fix loop, does **not** smuggle I4 HTML export or
I3 resume IMPLEMENT, and claim quotes spot-checked against live files.

| Metric | Count |
|--------|------:|
| FAIL (pre-amendment) | 4 |
| WARN (pre-amendment) | 7 |
| FAIL remaining after amend | 0 |
| WARN remaining after amend | 2 (residual; non-blocking) |

---

## 2. Summary of findings (severity-ranked)

### Critical / FAIL (fixed by amendment)

1. **I5-R3 + `"not run"` (completeness / wrong UX)** — Pre-amendment: “when metadata advisory is
   set, print it.” `scan()` / `_scan_tools` always sets `metadata["advisory"] = "not run"`, and
   `mccoy fix` uses `scan()`. A faithful implementer would print `"not run"` on every fix report.
   **Amended:** I5-R3 only SHOULD-print `skipped…` / `completed` / `not applicable`; explicitly
   exclude `"not run"`; edge-case row + AT-I5-5 updated.

2. **FN marked skippable (keep-list mismatch)** — Pre-amendment: FN was “OPTIONAL” / sequencing
   “Optional,” allowing neither A nor B. Need-verification keep-list requires DOCUMENT-DOWN **or**
   small IMPLEMENT. **Amended:** FN is A xor B required; path choice optional, closure not.

3. **§1 I5 deliverable over-implied fix-path advisory** — “and thus `mccoy scan` / `mccoy fix`
   stdout” read as both commands showing advisories. Combined with soft I5-R7 (“out of scope
   unless already present”), risked scope creep toward wiring `scan_with_advisory` into the loop
   (contradicts need-verification: I5 is terminal display; fix uses `scan()`). **Amended:** §1
   table + I5-R7 state no wiring; fix path has `advisory is None` / `"not run"`.

4. **AT-I5-2 under-testable** — “no `Advisory` label / invented advisory body” allowed a silent
   second line without the word Advisory, or confused label absence with R1 (which does not
   mandate the HTML `Advisory:` label as MUST). **Amended:** assert no `Advisory:` and single
   severity line for non-advised findings.

### WARN (mostly fixed; two residual)

5. **I5-R2 “meaningful float”** — Under-specified vs default `confidence=0.0` on failure notes.
   **Amended:** `confidence > 0`; MAY omit `0.0` on failure placeholders.

6. **DOC-I1/I2 acceptance judgment language** — “HTTP as a CLI connection mode” / “no remaining
   marketing sentence…” hard to automate. **Amended:** concrete forbidden phrases (`stdio or
   HTTP`, `any MCP server` / `any MCP (`).

7. **DOC-I3 acceptance self-contradiction** — “fine if none today.” **Amended:** grep near
   thread_id/Codex; unrelated English out of scope.

8. **FN docstring claim surgery** — Spec paraphrased `_restore_attempt_state` as a generic
   “docstring claims.” **Amended:** accurate cites.

9. **Residual WARN — I5-R5 “severity stays HIGH”** — True for MCC001 (only advised rule) but
   worded as universal. Acceptable; do not invent non-MCC001 advisory paths.

10. **Residual WARN — DOC acceptance still needs human grep judgment** for near-miss rewrites
    (“HTTP transport supported” without saying library). Acceptable for DOCUMENT-DOWN; no claim-
    guard test required (spec ASSUMPTION matches `tests/test_readme.py`).

### Pass highlights (no amend needed)

- Reject list §2 complete; no I4/I6–I8 IMPLEMENT leakage; HTML mentioned only as non-CLI path.
- I5-R1/R4/R6/R8 testable MUSTs; A1/R4 invariants preserved.
- Claim quotes for README / overview / landing / fix-loop / quickstart / HTML `Advisory:` /
  metadata strings / LLM failure message — all present as cited (spot-check §3.5).
- Sequencing matches need-verification budget (I5 code first; docs surgery; FN piggyback).

---

## 3. Per-section validation

### 3.1 I5 (terminal advisory)

| Check | Result |
|-------|--------|
| Traceability to keep-list I5 IMPLEMENT | PASS |
| Reject leakage (I4 HTML as delivery channel) | PASS — explicitly non-goal |
| Fix-loop advisory wiring | PASS (post-amend) — I5-R7 forbids |
| Testability of MUSTs | PASS (post-amend AT-I5-2) |
| Consistency with A1 / R4 / scan vs scan_with_advisory | PASS |
| Completeness (`not run`, max_calls, failure note) | PASS (post-amend) |
| Over-spec | PASS — R2/R3 correctly SHOULD |
| Under-spec / silent no-op | PASS — R1 exact message string blocks no-op |
| Claim / code accuracy §4.1 | PASS — verified in `scanner.py`, `llm.py`, `report.py`, template |

### 3.2 DOC-I1 / DOC-I2 / DOC-I3

| Check | Result |
|-------|--------|
| Traceability to DOCUMENT-DOWN keep-list | PASS |
| Surfaces listed match live overclaims | PASS (see §3.5) |
| No IMPLEMENT of `--url` / `--command` / resume | PASS |
| Acceptance testability | PASS (post-amend forbidden phrases) |
| Changelog correctly out of scope | PASS |
| Quickstart honesty on stdio | PASS — correctly “leave” |

### 3.3 FN (`fix_attempted`)

| Check | Result |
|-------|--------|
| Traceability to keep-list FN | PASS (post-amend A xor B) |
| Option A testable | PASS |
| Option B surfaces accurate | PASS (post-amend) |
| No I6 resolved-history creep | PASS |
| No HTML requirement | PASS |

### 3.4 Non-goals & sequencing

| Check | Result |
|-------|--------|
| Reject list matches need-verification §5 | PASS |
| A1 / no HTTP-fix expansion / no HTML advisory channel | PASS |
| Priority order sensible | PASS |
| FN sequencing strength | PASS (post-amend required closure) |

### 3.5 Claim-surgery accuracy (spot-check)

| Cited claim | File evidence | Accurate? |
|-------------|---------------|-----------|
| “stdio or HTTP” | `README.md` L6; `overview.md` L6 | Yes |
| “any MCP … server” | README L6; overview L6 | Yes |
| Landing “any MCP server” (no HTTP) | `index.astro` L31–33 | Yes |
| “so you can resume” + thread_id | README L24; `fix-loop.md` L36–37 | Yes |
| Quickstart “connects over stdio” | `quickstart.md` L12 | Yes |
| CLI “Python stdio MCP server” | `cli.py` L34; `cli.md` | Yes |
| `render_terminal` ignores advisory | `report.py` L27–33 | Yes |
| HTML `Advisory:` + message | `report.html.j2` L30–32 | Yes |
| metadata skipped / completed / not applicable / not run | `scanner.py` L27–28, L33, L41; `llm.py` L66 | Yes |
| `LLM unavailable — advisory pass skipped` | `llm.py` L63 | Yes |
| fix uses `scan()` not `scan_with_advisory` | `fix_loop.py` L21, L137; `cli.py` uses advisory only in `scan` | Yes |
| `thread_id` param unused in argv | `codex_runner.py` L22–45 | Yes |

---

## 4. Table: Requirement ID → PASS/FAIL/WARN

Statuses are **post-amendment**. Pre-amend FAILs noted in “Notes.”

| Requirement ID | Status | Notes |
|----------------|--------|-------|
| I5-R1 | PASS | Exact `message` + association; testable via AT-I5-1 |
| I5-R2 | PASS | Was WARN (“meaningful float”); now `confidence > 0` |
| I5-R3 | PASS | Was FAIL (`not run`); scoped status whitelist |
| I5-R4 | PASS | No invented per-finding text |
| I5-R5 | WARN | Failure message MUST — good; “stays HIGH” is MCC001-true residual |
| I5-R6 | PASS | A1 / presentation-only |
| I5-R7 | PASS | Was FAIL/WARN (wiring weasel); now explicit out of scope |
| I5-R8 | PASS | No new flags |
| AT-I5-1 | PASS | |
| AT-I5-2 | PASS | Was FAIL under-testable |
| AT-I5-3 | PASS | |
| AT-I5-4 | PASS | Regression; aligns with `test_cli.py` |
| AT-I5-5 | PASS | Tied to I5-R3; excludes `not run` |
| DOC-I1 | PASS | Was WARN acceptance; concrete phrase ban |
| DOC-I2 | PASS | Was WARN acceptance; concrete phrase ban |
| DOC-I3 | PASS | Was WARN “if none today” |
| DOC cross-cut §5.4 | PASS | |
| FN-A-R1..R3 | PASS | |
| FN-B | PASS | Cite accuracy amended |
| FN closure (A xor B) | PASS | Was FAIL as skippable OPTIONAL |
| Non-goals §2 | PASS | No reject leakage |
| Invariants §3 | PASS | Matches shipped R4/A1/F5/F6/R2/R3 |
| Sequencing §7 | PASS | |
| Open questions §8 | PASS | Real unknowns only |

---

## 5. Required amendments (applied)

Numbered patches already incorporated into `02-implicit-spec.md`:

1. **§1 / intro — I5 + FN scope wording** — Clarify scan vs fix advisory data; FN = A xor B required.
2. **I5-R2** — Define confidence as `> 0`; MAY omit default `0.0` on failure notes.
3. **I5-R3 + edge case + AT-I5-5** — Whitelist print statuses; forbid treating `"not run"` as SHOULD-print.
4. **I5-R7** — Delete “unless already present”; forbid wiring `scan_with_advisory` into fix.
5. **AT-I5-2** — Concrete absence criteria (`Advisory:`, single severity line).
6. **DOC-I1 / DOC-I2 / DOC-I3 acceptance** — Concrete forbidden phrases / cleaner resume grep.
7. **§6 FN + sequencing + appendix** — Required closure; accurate docstring cites.

No further mandatory patches. Optional polish (not applied): demote I5-R5 “HIGH” to “unchanged
deterministic severity (MCC001 remains HIGH).”

---

## 6. Residual risks after amendments

1. **SHOULD vs MUST on I5-R3** — Implementer may ship only per-finding lines; keyless vs keyed still
   differs when MCC001+key produces advisories, but keyless-with-no-visible-delta on servers
   without MCC001 remains possible if R3 skipped. Acceptable per open question #1 / need-verification
   “optionally echo metadata.”
2. **DOC near-miss rewrites** — Authors could invent new overclaims not matching the forbidden
   phrases (`HTTP mode`, `language-agnostic CLI`). Human review of the triad (§5.4) still needed.
3. **FN-A marker string unconstrained** — `fix attempted` vs `attempted` vs symbol — fine; tests
   must lock the chosen token.
4. **I5 + FN-A on same finding line** — Layout interaction unspecified; low risk if both adjacent
   to the severity line.

---

## 7. Final go / no-go

**GO** — Use the **amended** `02-implicit-spec.md` as the research baseline for the next
implementation / docs pass.

Do **not** use a pre-amendment copy: the `"not run"` I5-R3 hole and skippable-FN wording would
cause wrong or incomplete keep-list closure.

---

## Appendix — Reject-leakage & special checks

| Check | Result |
|-------|--------|
| Spec does not require advisory in fix loop | PASS (I5-R7 amended) |
| Spec does not smuggle I4 HTML CLI export | PASS |
| Spec does not smuggle I3 resume IMPLEMENT | PASS (DOCUMENT-DOWN only) |
| Inventory I6–I8 not reintroduced as IMPLEMENT | PASS |
