# Implicit product specification — keep-list survivors only

Authority chain (highest first):

1. `docs/research/adversarial/01-need-verification.md` — keep / reject list (this spec may not
   re-litigate rejects into IMPLEMENT work).
2. Observable behavior already committed in `src/mccoy/` + `tests/`.
3. Public claims in `README.md`, `site/` — to be surgically narrowed where they overclaim.

This document specifies **only** keep-list survivors: **I5 IMPLEMENT**, **DOC-I1 / DOC-I2 /
DOC-I3**, and optional **FN (`fix_attempted`)**. It does not invent product surface the verifier
rejected.

---

## 1. Spec purpose & authority

**Purpose.** Make the next implementation / docs pass falsifiable: every requirement is an
observable acceptance criterion (CLI stdout, exit code, or exact claim text change), not a design
essay.

**In scope.**

| ID | Kind | Deliverable |
|----|------|-------------|
| I5 | IMPLEMENT | Terminal advisory visibility in `render_terminal` (and thus `mccoy scan` / `mccoy fix` stdout) |
| I1 | DOCUMENT-DOWN | Narrow “stdio or HTTP” claims to CLI stdio vs library HTTP |
| I2 | DOCUMENT-DOWN | Narrow “any MCP server” to Python-stdio CLI scope |
| I3 | DOCUMENT-DOWN | Remove / replace Codex resume promise |
| FN | OPTIONAL | `fix_attempted` terminal visibility **or** doc-down of that implication |

**Out of scope for this spec:** any item on the reject list in §2.

**ASSUMPTION (not in code/tests):** After claim surgery, no automated test currently fails on
README/landing marketing copy; docs consistency is enforced by human/agent review unless a new
test is added. Adding a README claim-guard test is **not** required by this spec.

---

## 2. Non-goals (explicit reject list)

Do **not** specify, implement, or “complete” as product work:

| Rejected ID | Forbidden work |
|-------------|----------------|
| I1 IMPLEMENT | CLI `--url` / HTTP scan target mode |
| I2 IMPLEMENT | Generic CLI spawn (`--command` / `--args` / env) for Node/Go/etc. |
| I3 IMPLEMENT | Codex thread resume (persist workspace, pass resume flags, user resume UX) |
| I4 IMPLEMENT | HTML CLI export (`--format html`, `--report`, wiring `render_html` into CLI) |
| I6 IMPLEMENT | `Finding.resolved` lifecycle / resolved-history report |
| I7 IMPLEMENT | Wire `infra_result` into CLI/report (keep exit-3 string path) |
| I8 IMPLEMENT | Invent a CRITICAL-emitting rule |

Also non-goals for keep-list items:

- Changing advisory semantics (A1): advisory must never flip pass/fail, score weights, or exit
  codes.
- Expanding fix loop to HTTP or non-Python targets.
- Shipping HTML as the advisory delivery channel (I4 reject; I5 fixes the default path).
- Turning collected `thread_ids` into a resume feature (I3 reject); DOCUMENT-DOWN only.

---

## 3. Current product invariants that must be preserved

These are already delivered and must remain true after I5 / doc surgery / optional FN work.

| Invariant | Observable contract |
|-----------|---------------------|
| **R4 exit codes** | `0` clean; `2` unresolved deterministic findings; `3` infrastructure/tooling (server won’t start, Codex missing when work remains). |
| **A1 advisory non-verdict** | With or without `OPENAI_API_KEY`, exit code and `Finding.severity` / `is_clean` / score are driven only by deterministic rules. Advisory attachment must not change those. |
| **Judge path (B3/B9/B10)** | `uv run mccoy scan fixtures/vuln_server/server.py` and `clean_server.py` work keyless; vuln → exit 2 with MCC* findings; clean → exit 0. |
| **CLI target shape** | `mccoy scan` / `mccoy fix` take a Python file path; spawn is `sys.executable [path]`. Docstrings already say “Python stdio MCP server.” |
| **F5 fix loop** | Copy-isolation, max rounds, re-scan via fresh connect, Codex missing → hint + exit 3 when findings remain, `outcome.cleanup()` after CLI diff. |
| **F6 CLI report** | Graded terminal report (`McCoy score:`, findings) + before/after unified diff on `mccoy fix`. |
| **R2** | Clean input skips Codex; cleared findings disappear on fresh re-scan (no `resolved=True` requirement). |
| **R3** | Codex failure marks attempt and continues; call budget / timeouts bound cost. |
| **Library transports (unshipped as CLI)** | `connect_http` and generic `connect_stdio(command, args, env=...)` may remain; they are not CLI product. Docs may mention them as library-only after DOC-I1/I2. |

**ASSUMPTION:** Historical changelog line “both supported transports” is git-derived narrative, not
a live product promise; it need not be rewritten unless a human-edited changelog is introduced.
Generated `site/.../changelog.md` is out of claim-surgery scope.

---

## 4. Spec I5 — Terminal advisory visibility

### 4.1 Problem (committed facts)

- `scan_with_advisory` attaches `finding.advisory: AdvisoryNote | None` for MCC001 findings when
  `OPENAI_API_KEY` is set (`src/mccoy/scanner.py`, `llm.py`).
- `ScanResult.metadata["advisory"]` records pass status: `"skipped (OPENAI_API_KEY unset)"`,
  `"completed"`, `"not applicable"`, or (pre-advisory) `"not run"`.
- `render_terminal` today prints only score, tools scanned, and
  `[SEVERITY] {rule_id} {tool}: {message}` — **ignores** `finding.advisory` and metadata.
- HTML template renders advisory message, but HTML is not on the CLI path (I4 rejected).
- Public quickstart claims each injection-marker finding gets a GPT-5.6 annotation when the key is
  set — operationally false for CLI users until I5 lands.

### 4.2 Requirements

**I5-R1 — Per-finding advisory lines (must).**  
When `finding.advisory is not None`, `render_terminal` MUST include that advisory in the returned
string such that a human reading CLI stdout can see it without a debugger. Minimum content:

- The advisory `message` text (exact string from `AdvisoryNote.message`).
- Association with the parent finding (same finding block / immediately following the finding
  line) so MCC001 lines are distinguishable from non-advised findings.

**I5-R2 — Benign / confidence signal (should).**  
When present, terminal output SHOULD surface enough to distinguish benign annotation from
“confirmed injection / no downgrade”:

- If `advisory.severity == Severity.INFO` (LLM said benign), indicate benign/docs context
  (label or severity token).
- Include `confidence` when it is a meaningful float (tests use values like `0.9` / `0.95`).

Exact formatting is implementation-defined; acceptance is content presence, not a fixed template.
A format aligned with the HTML precedent (`Advisory: {message}`) plus confidence is sufficient.

**I5-R3 — Pass-level status (should).**  
When `result.metadata.get("advisory")` is set, terminal output SHOULD include that status string
**once** (header or footer), so keyless vs keyed runs are distinguishable even when no finding
carries an advisory object (e.g. skipped, or no MCC001 findings → `"not applicable"`).

**I5-R4 — Absent advisory (must).**  
If `finding.advisory is None`, do **not** invent placeholder advisory text for that finding.
Keyless scan findings remain a single line each (plus optional pass-level “skipped …” from I5-R3).

**I5-R5 — Failed / skipped advisory attachment (must).**  
When the advisory pass ran but classification failed, code already sets
`AdvisoryNote(message="LLM unavailable — advisory pass skipped")`. Terminal MUST print that
message under the finding (same as any other advisory). Deterministic severity stays HIGH; exit
code unchanged (A1).

**I5-R6 — Exit codes unchanged (must, A1).**  
`render_terminal` is presentation-only. Enabling advisory display MUST NOT change:

- `ScanResult.is_clean`, `score`, or finding severities;
- CLI exit codes for the same inputs (keyless and keyed).

**I5-R7 — Scope of call sites (must).**  
Both `mccoy scan` and `mccoy fix` call `render_terminal`. I5 applies wherever that function is
used. Note: `mccoy fix` currently uses `scan()` (no advisory) inside the loop — so fix-path
findings typically have `advisory is None`. That is existing behavior; I5 does **not** require
wiring advisory into the fix loop. **ASSUMPTION:** wiring advisory into `mccoy fix` is out of
scope unless already present.

**I5-R8 — No new commands / flags (must).**  
No `--format`, no advisory-only flag. Visibility is default terminal output when data is present.

### 4.3 Acceptance tests (observable)

Add/extend tests under `tests/test_report.py` (and optionally CLI):

| # | Criterion |
|---|-----------|
| AT-I5-1 | `render_terminal` with `AdvisoryNote(message="benign docs", …)` includes `"benign docs"` in output. |
| AT-I5-2 | Same finding without advisory: output does **not** contain an `Advisory` label / invented advisory body. |
| AT-I5-3 | Advisory failure message `"LLM unavailable — advisory pass skipped"` appears when that note is attached. |
| AT-I5-4 | Existing CLI tests still pass: vuln scan exit 2, clean exit 0, graded report contains `McCoy score:` and `MCC001`. |
| AT-I5-5 | (Should) If metadata advisory status is rendered: keyless `scan_with_advisory` result’s metadata string starting with `skipped` appears in terminal when passed through `render_terminal`. |

**Manual / demo check (not necessarily automated):**  
`OPENAI_API_KEY=… uv run mccoy scan fixtures/vuln_server/server.py` shows advisory text under the
planted FP MCC001 finding; without the key, no per-finding advisory lines (optional single
“skipped” status line).

### 4.4 Edge cases

| Case | Expected terminal behavior |
|------|----------------------------|
| Key unset | `advisory is None` on findings; metadata skipped; no per-finding advisory lines; exit codes as today. |
| Key set, no MCC001 | metadata `"not applicable"` (or equivalent from `apply_advisories`); no per-finding advisories. |
| Key set, MCC001 present, LLM benign | advisory present, INFO severity on note; message visible; finding severity still HIGH. |
| Key set, LLM confirms injection | advisory present, `advisory.severity is None`; message visible; finding severity HIGH. |
| Key set, API error | skipped message on finding; severity HIGH. |
| `max_calls` budget | Only advised findings show advisory lines; later MCC001 may have `advisory is None`. |
| Non-MCC001 findings | No advisory object; unchanged single-line findings. |
| Empty findings / clean | Score 100; no advisory lines; exit 0. |
| Multi-line advisory message | Full message still present in stdout (wrapping OK). |

### 4.5 Non-goals for I5

- Do not require HTML CLI export to “see” advisories.
- Do not change Responses API / model id / schema.
- Do not use advisory to alter score or exit code.
- Do not require printing raw JSON of `AdvisoryNote`.

---

## 5. Spec DOC-I1 / DOC-I2 / DOC-I3 — Claim surgery

These are **wording constraints**. Implementation of rejected CLI features is forbidden. After
edits, public copy must not imply a shipped capability the CLI does not expose.

### 5.1 DOC-I1 — HTTP claim narrowing

**Truth constraint.** CLI scan/fix: Python file over **stdio** only. HTTP exists as library
`connect_http` + integration test proof — not a user CLI mode.

#### Exact claim surfaces

| File | Current false / over-broad claim | Replacement constraint |
|------|----------------------------------|------------------------|
| `README.md` (intro ¶) | “connects to any MCP … server over **stdio or HTTP**” | Must not claim CLI connects over HTTP. Allowed: CLI uses **stdio**; HTTP available via library / programmatic `connect_http` (optional one clause). |
| `site/src/content/docs/overview.md` (lede) | Same “stdio or HTTP” phrasing | Same constraint as README. |
| `site/src/pages/index.astro` (subhead) | Does not name HTTP today, but “any MCP server” overlaps I2; do not **add** HTTP to landing while fixing I2. | Landing must not newly claim HTTP CLI. |

**Surfaces that already match truth (leave or only tighten if contradictory):**

- `src/mccoy/cli.py` docstring: “Scan a Python stdio MCP server” — keep.
- `site/src/content/docs/cli.md` (generated from help) — keep; do not edit by hand to invent `--url`.
- `site/src/content/docs/quickstart.md`: “connects over stdio” — already honest.

**Acceptance.** Grep of README + overview + landing for user-facing “HTTP” as a **CLI** connection
mode returns no hit that asserts `mccoy scan` speaks HTTP. Mentions of library HTTP are OK if
explicitly scoped (“library”, “programmatic”, `connect_http`).

**Non-goal:** Do not add `--url`. Do not remove `connect_http` from the codebase.

---

### 5.2 DOC-I2 — “Any MCP server” claim narrowing

**Truth constraint.** CLI always spawns `sys.executable` + `.py` path. “Any MCP” (Node/Go/etc.)
is not a shipped CLI capability. Library `connect_stdio(command, args, env=...)` can launch
generic stdio processes but is not exposed by the CLI.

#### Exact claim surfaces

| File | Current false claim | Replacement constraint |
|------|---------------------|------------------------|
| `README.md` (intro ¶) | “connects to **any MCP** (Model Context Protocol) server …” | Replace with scope that matches CLI: **Python stdio MCP servers** (file path). Optional: note library can take a generic stdio command. |
| `site/src/content/docs/overview.md` (lede) | “connects to **any MCP** … server …” | Same as README. |
| `site/src/pages/index.astro` (subhead) | “McCoy connects to **any MCP server** …” | Replace “any MCP server” with Python-stdio / CLI-accurate scope (e.g. “your Python MCP server” / “Python stdio MCP servers”). Must not retain unbounded “any”. |

**Surfaces already narrower:** CLI help / `cli.md` — preserve.

**Acceptance.** No remaining user-facing marketing sentence that promises CLI support for
arbitrary-language / arbitrary-command MCP servers without a library qualifier.

**Non-goal:** Do not implement `--command` / `--args`.

---

### 5.3 DOC-I3 — Remove / replace Codex resume claim

**Truth constraint.** `thread_id` values may be collected on `FixLoopResult.thread_ids` and
parsed from Codex JSONL, but they are **never** printed by the CLI, never persisted for the user,
never passed into a subsequent `codex` argv as resume, and the CLI deletes the temp work copy via
`cleanup()` after the diff. Resume is a false feature and architecturally incoherent with
copy-isolation.

#### Exact claim surfaces

| File | Current false claim | Replacement constraint |
|------|---------------------|------------------------|
| `README.md` (Codex bullet) | “Each Codex run records its `thread_id` **so you can resume** the session that did the work.” | **Must remove** the resume promise. Allowed replacements: (a) delete the sentence entirely; or (b) state that Codex runs are ephemeral on a temp copy and the CLI prints a graded report + diff only; or (c) if mentioning `thread_id` at all, label it **internal / non-actionable** and **must not** say users can resume. |
| `site/src/content/docs/fix-loop.md` (“The thread id” section) | “McCoy captures these **so you can resume** the session that did the work.” | Same: delete section, or rewrite without resume. Must not teach a resume workflow. |

**Code/docstrings:** `run_codex_fix(..., thread_id=)` accepting an unused parameter may remain
(hygiene optional; not required). Tests may keep asserting ID collection. **Do not** implement
resume to make the old sentence true.

**Acceptance.** Grep of `README.md` + `site/src/content/docs/fix-loop.md` for `resume` in the
Codex / thread_id sense returns zero hits. (Unrelated English “resume” elsewhere is fine if none
today.)

**Non-goal:** Persist `work_dir`, print actionable resume instructions, or pass resume flags to
Codex.

---

### 5.4 Cross-cutting doc acceptance for I1–I3

After claim surgery, the following triad must be mutually consistent:

1. README intro + Codex bullet  
2. Docs overview lede + fix-loop page  
3. Landing subhead  

CLI help remains the narrowest honest surface; marketing must not over-promise relative to it.

---

## 6. Spec FN-optional — `fix_attempted` visibility or doc fix

### 6.1 Problem

- Loop restores `fix_attempted=True` on remaining findings after re-scan
  (`fix_loop._restore_attempt_state`).
- Docstring claims the final report can tell the user which findings Codex tried.
- `fix-loop.md`: “the finding is marked `fix_attempted`”.
- `render_terminal` (and HTML) never show `fix_attempted`.

Medium debt; cheaper than I5; either path satisfies the keep-list.

### 6.2 Option A — Small IMPLEMENT (preferred if editing `render_terminal` for I5 anyway)

**FN-A-R1.** When `finding.fix_attempted` is True, terminal output for that finding MUST include a
clear marker (e.g. `fix attempted` / `attempted`) adjacent to the finding line.

**FN-A-R2.** When False / default, no marker.

**FN-A-R3.** Does not change exit codes or severities.

**Acceptance:** unit test on `render_terminal` with `fix_attempted=True` asserts marker present;
False asserts absent.

### 6.3 Option B — DOCUMENT-DOWN

If Option A is not done:

| File | Current implication | Replacement constraint |
|------|---------------------|------------------------|
| `site/src/content/docs/fix-loop.md` (Graceful degradation) | “marked `fix_attempted`” reads as user-visible report state | Clarify that `fix_attempted` is **internal loop state** (or omit the field name); do not imply the terminal report displays it. |
| `src/mccoy/fix_loop.py` docstring | “final report could not tell the user…” / attempt history for the report | Soften to internal tracking for loop idempotency / tests, unless Option A ships. |

**Acceptance:** Docs no longer imply CLI users see `fix_attempted` in the report unless Option A
is implemented.

### 6.4 Non-goals for FN

- Do not build a resolved-history UI (I6 reject).
- Do not require HTML to show `fix_attempted`.
- Do not change loop attempt-keying semantics.

---

## 7. Priority / sequencing

| Order | Work | Rationale |
|-------|------|-----------|
| 1 | **I5** IMPLEMENT in `render_terminal` + tests | Only must-implement code item; unblocks honest advisory demo. |
| 2 | **DOC-I1 + DOC-I2** together | Same intro paragraphs in README/overview/landing; one editing pass. |
| 3 | **DOC-I3** | Independent sentence/section delete; do with or right after 2. |
| 4 | **FN** Option A piggyback on I5 renderer change, **or** Option B with DOC-I3 fix-loop edit | Optional; prefer A if touching the renderer. |

Suggested PR split (optional): (1) I5 + tests (+ FN-A), (2) claim surgery I1–I3 (+ FN-B if A skipped).

---

## 8. Open questions (real unknowns only)

1. **I5 metadata line:** Is a one-line `metadata["advisory"]` status required for judge demos, or
   is per-finding advisory text alone enough? Spec marks it SHOULD (I5-R3); product owner may
   demote to MAY without violating A1.
2. **I5 confidence formatting:** Exact string form (`confidence=0.90` vs `90%`) is unspecified;
   pick one in implementation and lock with a test if desired.
3. **FN default:** Prefer Option A vs B if schedule is tight after I5? Verifier allows either;
   this spec prefers A when the renderer is already open.
4. **Library callouts in docs:** How prominently to mention `connect_http` / generic
   `connect_stdio` after narrowing CLI claims — one clause vs a dedicated “Library API” note.
   Either satisfies DOCUMENT-DOWN if CLI overclaims are gone.
5. **Unused `thread_id` parameter / collection:** DELETE vs leave as dead plumbing is hygiene,
   not product; not decided here (I3 DOCUMENT-DOWN does not require DELETE).

---

## Appendix — Keep-list map (traceability)

| Keep-list ID | Spec section |
|--------------|--------------|
| I5 IMPLEMENT | §4 |
| I1 DOCUMENT-DOWN | §5.1 |
| I2 DOCUMENT-DOWN | §5.2 |
| I3 DOCUMENT-DOWN | §5.3 |
| FN optional | §6 |
| Explicit rejects | §2 |

No other inventory IDs (I4, I6–I8 IMPLEMENT) appear as requirements in this document.
