# Incomplete feature inventory (McCoy)

Source of truth for this inventory: public claims in `README.md` / docs site, scaffolded APIs in
`src/mccoy/`, and the feature IDs referenced in tests and comments (`F4`–`F6`, `R1`–`R4`, `A1`,
`B3`/`B9`/`B10`, `D1`/`D2`). `REASONING.md` / `IMPLICIT_SPEC` are referenced in code comments but
are not present in the repository (likely lived under the gitignored `thoughts/` tree).

## Status legend

| Status | Meaning |
|--------|---------|
| Done | Wired end-to-end and covered by tests |
| Partial | Library/API or tests exist; user-facing path incomplete |
| Gap | Claimed or scaffolded; no usable delivery path |
| Dead | Defined but unused / unreachable |

---

## Product surface claimed vs delivered

| Claim (README / docs / landing) | Reality today | Status |
|---------------------------------|---------------|--------|
| Scan over **stdio or HTTP** | `connect_http` + HTTP integration test exist; **CLI only accepts a Python file path and always uses stdio** via `sys.executable` | Partial |
| Connects to **any MCP server** | CLI hardcodes Python interpreter + `.py` path; no command/args/env URL mode | Gap |
| GPT-5.6 advisory annotates MCC001 | Works when `OPENAI_API_KEY` set; **terminal report never prints advisory notes** (HTML template does) | Partial |
| Codex fix-and-verify loop | Implemented with copy-isolation, caps, exit codes | Done |
| Record `thread_id` so you can **resume** the Codex session | IDs collected on `FixLoopResult.thread_ids`; **never passed back into `codex` and never printed/persisted for the user** | Gap |
| Static HTML report (F6) | `render_html` + Jinja2 template + tests exist; **CLI never writes/emits HTML** | Partial |
| Before/after diff after fix (F6) | `mccoy fix` prints unified diff | Done |
| Machine-checkable exit codes 0/2/3 (R4) | Implemented for scan + fix | Done |
| Judge-reproducible keyless scan (B3/B9/B10) | Documented + tested | Done |

---

## Feature-ID map (reconstructed from code/tests)

| ID | Intent (inferred) | Implementation status |
|----|-------------------|----------------------|
| F4 / A1 | GPT-5.6 advisory; never flips verdict | Done for scan path; terminal presentation incomplete |
| F5 | Codex fix-and-verify loop (product wedge) | Done |
| F6 | Graded report + static HTML + before/after diff | Terminal + diff Done; HTML CLI Gap |
| R1 | Degenerate empty tool list → clean, no crash | Done |
| R2 | Idempotent re-scan; clean input skips Codex | Done |
| R3 | Graceful Codex degradation + cost ceilings | Done |
| R4 | Exit codes 0/2/3 | Done |
| B3 / B9 / B10 | Judge path without entrant accounts; BYO key/Codex | Done |
| D1 | Docs site tokens mirror opencode.ai | Done |
| D2 | README / judge-facing docs | Done |

---

## Incomplete items that need a decision (candidates to implement)

### I1 — CLI HTTP scan target

**Evidence:** `connect_http` in `src/mccoy/connect.py`; `tests/test_integration.py` proves scan over streamable HTTP; README/landing claim “stdio or HTTP”; `mccoy scan` docstring says “Python stdio MCP server” only.

**Missing:** CLI flag (e.g. `--url`) or target mode that calls `connect_http`; docs/CLI help alignment; fix-loop HTTP story (harder — fix needs a source tree).

### I2 — Non-Python / generic stdio launch

**Evidence:** Marketing “any MCP server”; CLI always spawns `sys.executable [server.py]`.

**Missing:** Ability to pass `command` + `args` (+ optional `env`) for Node/Go/etc. stdio servers.

### I3 — Codex thread resume

**Evidence:** README: “records its `thread_id` so you can resume”; `run_codex_fix(..., thread_id=...)` accepts but does not pass a resume flag to `codex`; loop never reuses prior IDs; CLI does not print them.

**Missing:** Persist/print thread IDs; feed resume into subsequent Codex invocations (or drop the claim).

### I4 — HTML report CLI export (F6 completion)

**Evidence:** `render_html` + template tested; CLI only `render_terminal`.

**Missing:** `--format html` / `--report path.html` (or equivalent) on `scan`/`fix`.

### I5 — Advisory visibility in default output

**Evidence:** Advisory attached to findings; HTML shows it; terminal renderer ignores `finding.advisory`.

**Missing:** Terminal (and optionally score metadata) surface for advisory notes when present.

### I6 — `Finding.resolved` lifecycle

**Evidence:** Model field exists; loop tracks `fix_attempted` via `(rule_id, tool)` but never sets `resolved=True` on cleared findings (cleared findings simply disappear from the fresh scan).

**Missing:** Either use `resolved` in reports/history or remove the dead field.

### I7 — `infra_result` helper

**Evidence:** `scanner.infra_result` builds an MCC-INFRA finding; CLI instead catches exceptions and exits 3 with a string — helper unused.

**Missing:** Wire into CLI/report path or delete as dead code.

### I8 — Severity.CRITICAL unused

**Evidence:** Enum + score weight exist; no rule emits CRITICAL.

**Missing:** A rule that warrants CRITICAL, or document that CRITICAL is reserved.

---

## Explicitly out of scope for “incomplete” (already closed)

These appeared as phased/not-tested items in early commits and are now delivered:

- Deterministic rules MCC001–MCC008 + clean FastMCP MCC002 contract
- Live stdio scan foundation
- Advisory pass (library + `scan_with_advisory`)
- Fix loop with copy-isolation, max rounds, Codex missing → exit 3
- Docs site (D1) and full README (D2)
- Adversarial follow-ups in `1beb748` (python-free spawn, JSONL robustness, temp cleanup)

---

## Working hypothesis for follow-on adversarial review

The incomplete set that is **product-meaningful** (not mere dead-code hygiene) is:

1. **I1** HTTP via CLI (claim already public)
2. **I2** generic stdio targets (claim already public)
3. **I3** Codex resume (claim already public)
4. **I4** HTML report export (F6 half-shipped)
5. **I5** advisory in terminal output (advisory otherwise invisible to default UX)

I6–I8 are cleanup/consistency items and should be challenged hard before spending implementation budget.
