# Adversarial need verification — incomplete inventory I1–I8

Auditor stance: attack the inventory's "product-meaningful" hypothesis. Prefer DOCUMENT-DOWN /
DELETE over IMPLEMENT wherever a public claim can be narrowed without breaking the judge path,
fix wedge, or exit-code contract.

Sources checked: `README.md`, `site/` (overview, cli, fix-loop, quickstart, landing),
`src/mccoy/{cli,connect,fix_loop,codex_runner,report,scanner,llm,models}.py`,
`tests/` (cli, integration, report, fix_loop, llm), inventory
`docs/research/00-incomplete-feature-inventory.md`.

---

## 1. Executive verdict

**Must-implement (code): I5 only.**

Everything else in I1–I8 is either marketing/doc overclaim debt (fix with DOCUMENT-DOWN, not
new surface area), internal scaffolding that was never sold to users (I4), or dead-model hygiene
(I6–I8). The inventory's working hypothesis that I1–I5 are all "product-meaningful" **overclaims
implementation need**. I1–I3 are real *honesty* problems; they are not real *feature* problems
for this Build-Week / judge-path product.

| ID | Survives as must-implement? | Correct resolution |
|----|-----------------------------|--------------------|
| I1 | No | DOCUMENT-DOWN |
| I2 | No | DOCUMENT-DOWN |
| I3 | No | DOCUMENT-DOWN (+ optional DELETE of unused resume plumbing) |
| I4 | No | DEFER / treat F6 as already delivered via terminal + diff |
| I5 | **Yes** | **IMPLEMENT** (terminal advisory lines) |
| I6 | No | DELETE field (optional hygiene) or leave unused |
| I7 | No | DELETE helper (do not wire) |
| I8 | No | Leave enum reserved; do not invent a CRITICAL rule |

---

## 2. Per-item attack (I1–I8)

### I1 — CLI HTTP scan target

- **Real need or overclaim?** Overclaim. README + overview say “stdio or HTTP.” The CLI help and
  docstring honestly say “Python stdio MCP server.” Library `connect_http` + integration test
  prove *transport*, not *product CLI*. Judge path is `mccoy scan fixtures/.../server.py` over
  stdio. Changelog line “both supported transports” describes library proof, not a shipped UX.
- **What breaks if NEVER implemented?** Nothing in the demo, fix loop, or exit-code contract.
  Only the README/overview sentence remains false relative to the CLI.
- **Cheapest valid resolution:** DOCUMENT-DOWN — narrow public copy to “stdio (CLI); HTTP via
  library/`connect_http` for programmatic use.” Do **not** add `--url` unless HTTP scan is sold
  as a separate scan-only mode with explicit “no fix” caveat.
- **Confidence:** high
- **Strongest counter-argument to implementing:** HTTP scan without a fix story creates a
  second-class path that cannot use the product wedge (Codex needs a source tree). Wiring `--url`
  “completes” a slogan while expanding support surface (auth, TLS, remote process lifecycle) for
  zero judge-path gain.

### I2 — Non-Python / generic stdio launch

- **Real need or overclaim?** Marketing overclaim. Landing/README: “any MCP server.” CLI always
  spawns `sys.executable [path.py]`. `connect_stdio(command, args, env=...)` already supports
  generic launch; only the CLI refuses to expose it. Fix path (`_fixture_path_under`, Python
  file as server arg) is Python-centric.
- **What breaks if NEVER implemented?** Users with Node/Go/etc. MCP servers cannot use the CLI
  as marketed. The actual shipped fixture/judge workflow is unaffected. CLI docs already
  under-promise relative to README.
- **Cheapest valid resolution:** DOCUMENT-DOWN — “Python stdio MCP servers via CLI; generic
  stdio available as a library.” Implementing `--command`/`--args` is scope expansion dressed as
  claim completion.
- **Confidence:** high
- **Strongest counter-argument to implementing:** Each new runtime brings spawn/env/path edge
  cases; the fix loop still assumes a Python module path under `--project`. “Any MCP” is a
  category claim this Build-Week scanner does not earn and should not try to earn mid-flight.

### I3 — Codex thread resume

- **Real need or overclaim?** Doc overclaim / false feature. README + `fix-loop.md`: records
  `thread_id` “so you can resume.” Reality: IDs are collected on `FixLoopResult.thread_ids`,
  never printed, never persisted, never passed into `codex` argv. `run_codex_fix(..., thread_id=)`
  accepts a parameter and ignores it for process construction. Tests only assert collection.
- **What breaks if NEVER implemented?** Resume never worked; users lose nothing functional. The
  false sentence remains if left in docs.
- **Cheapest valid resolution:** DOCUMENT-DOWN — delete “so you can resume.” Optionally stop
  collecting/printing IDs entirely, or print them as opaque debug metadata without promising
  resume. Do **not** implement resume.
- **Confidence:** high
- **Strongest counter-argument to implementing:** Resume is **architecturally incoherent** with
  the shipped fix UX: the CLI operates on a temp copy and calls `outcome.cleanup()` after the
  diff, destroying the workspace the thread would resume against. Full resume implies persisting
  `work_dir`, teaching Codex resume flags, and a second user workflow — a new product, not a
  gap-fill.

### I4 — HTML report CLI export (F6 “completion”)

- **Real need or overclaim?** Inventory overclaim. `render_html` + Jinja2 + tests exist; CLI never
  calls them. **No README, quickstart, CLI ref, or landing page promises HTML export.** F6 as
  exercised by CLI tests is “graded terminal report + before/after diff” — both Done. HTML is
  internal scaffolding / optional library API, not a public incomplete feature.
- **What breaks if NEVER implemented?** Nothing user-facing. Maintainers keep a tested dead path
  (cost is small).
- **Cheapest valid resolution:** DEFER — leave `render_html` as a library helper; treat F6 as
  delivered. Do not spend CLI flag budget. Alternative: DELETE template if maintenance annoyance
  outweighs option value (not required).
- **Confidence:** high
- **Strongest counter-argument to implementing:** Wiring `--format html` “finishes” an unshipped
  claim the inventory invented from code comments. It also becomes the wrong place to “fix”
  advisory visibility (see I5) — shipping HTML instead of fixing terminal would hide GPT-5.6
  behind a format flag nobody is told to use.

### I5 — Advisory visibility in default output

- **Real need or overclaim?** **Real product need.** GPT-5.6 advisory is a flagship README /
  landing / quickstart feature. `scan_with_advisory` attaches `finding.advisory` when
  `OPENAI_API_KEY` is set. `render_terminal` ignores it. HTML template shows it, but HTML is not
  on the CLI path (I4). Net: paying for the advisory pass yields **zero visible change** vs
  keyless scan in the only UX users have.
- **What breaks if NEVER implemented?** The advisory pass is a silent no-op for humans. Quickstart
  (“each injection-marker finding gets a GPT-5.6 advisory annotation”) is operationally false for
  CLI users. Planted FP demo cannot be observed without reading objects in a debugger/tests.
- **Cheapest valid resolution:** IMPLEMENT — print advisory message (and maybe confidence /
  benign hint) under MCC001 lines in `render_terminal` when present; optionally echo
  `metadata["advisory"]` status once. Tiny diff; no new commands.
- **Confidence:** high
- **Strongest counter-argument to implementing:** One could DOCUMENT-DOWN advisory as
  “programmatic / library-only annotation.” That gutting would contradict the “Built with Codex
  and GPT-5.6” positioning harder than a five-line renderer fix. Not a serious alternative.

### I6 — `Finding.resolved` lifecycle

- **Real need or overclaim?** Neither — dead model field. Loop design: cleared findings disappear
  on re-scan; attempt history uses `fix_attempted` + `(rule_id, tool)`. Tests assert
  `not any(f.resolved ...)`. No report reads `resolved`.
- **What breaks if NEVER implemented?** Nothing. Field stays always-false forever.
- **Cheapest valid resolution:** DELETE the field (hygiene) or leave it. Do not build a
  resolved-history report just to justify the field.
- **Confidence:** high
- **Strongest counter-argument to implementing:** “Using” `resolved` requires keeping cleared
  findings in the result set, which fights R2’s fresh-scan idempotency model and complicates
  `is_clean` / scoring.

### I7 — `infra_result` helper

- **Real need or overclaim?** Dead code. CLI catches exceptions, prints a string, exits 3. That
  matches R4. `infra_result` would invent MCC-INFRA findings and could pollute score / `is_clean`
  semantics if naively wired.
- **What breaks if NEVER implemented?** Nothing.
- **Cheapest valid resolution:** DELETE. Do not wire into CLI.
- **Confidence:** high
- **Strongest counter-argument to implementing:** Wiring infrastructure failures as findings
  risks exit-code / score confusion (findings ⇒ exit 2 vs infra ⇒ exit 3). The current string +
  exit 3 path is the correct product contract.

### I8 — `Severity.CRITICAL` unused

- **Real need or overclaim?** Speculative enum slot. Weight exists in `score`; no rule emits
  CRITICAL (rules use HIGH/MEDIUM/LOW). Not claimed publicly as a shipped severity.
- **What breaks if NEVER implemented?** Nothing. Score table already handles missing severities
  via `.get(..., 0)`.
- **Cheapest valid resolution:** Leave reserved. Do not invent a CRITICAL rule to “use” the
  enum. Optional one-line doc in models/rules index: “CRITICAL reserved.”
- **Confidence:** high
- **Strongest counter-argument to implementing:** Severity inflation without a distinct
  exploitability story weakens the ruleset. Unused enum members are normal.

---

## 3. False positives / false negatives

### False positives (inventory overstates need)

1. **I4 as “F6 half-shipped / product-meaningful”** — F6’s user-visible CLI contract is already
   met (terminal grade + diff). HTML was never marketed.
2. **I1 / I2 as implement candidates** — they are claim-alignment problems. The inventory
   correctly spots the gap; the wrong default action is “build CLI generality.”
3. **I3 as resume feature gap** — framed as incomplete resume; correctly it is a **false claim
   incompatible with copy-isolation + cleanup**. Implementing resume is the wrong repair.
4. **I6–I8 as “incomplete items that need a decision” toward product work** — only DELETE/ignore
   decisions; the inventory’s own footnote already suspected this.

### False negatives (missed or under-weighted)

1. **`fix_attempted` invisible in terminal after `mccoy fix`** — loop docs/docstrings say the
   report can tell the user which findings Codex tried; `render_terminal` never shows
   `fix_attempted` (HTML doesn’t either). Medium product debt; cheapest fix is a terminal marker
   alongside I5, or DOCUMENT-DOWN the “marked” language to “internal state.” Not as severe as I5
   (no BYO-key silent spend), but real.
2. **Advisory is double-invisible** — inventory splits I4/I5; the sharper statement is: advisory
   only renders in an unreachable HTML path. Fixing I5 without I4 is sufficient; fixing I4
   without I5 is not.
3. **Claim surface inconsistency is the primary I1/I2 deliverable** — README/overview/landing vs
  CLI help already disagree. The missed “item” is a docs consistency pass, not a transport epic.
4. **No missed must-implement features found** beyond I5 (+ optional `fix_attempted` display).
   Judge path, rules, fix loop, exit codes, keyless scan are closed as the inventory states.

### Already-done items wrongly lingering (none as IDs)

I1–I8 are all still incomplete or unused as described. No inventory ID is a pure false positive
of “already shipped” — I4 is a false positive of *need*, not of *gap existence*.

---

## 4. Final keep-list (survivors) + resolution

These are the only items that deserve intentional follow-up. “Keep” ≠ “implement.”

| ID | Resolution | Action |
|----|------------|--------|
| **I5** | **IMPLEMENT** | Show `finding.advisory` (and ideally advisory metadata status) in `render_terminal`. Primary keep. |
| **I1** | **DOCUMENT-DOWN** | Align README/overview/landing with CLI: stdio Python targets; HTTP = library/tested transport only. |
| **I2** | **DOCUMENT-DOWN** | Replace “any MCP server” with Python-stdio (CLI) scope; mention library generality if desired. |
| **I3** | **DOCUMENT-DOWN** | Remove resume promise. Optionally print thread IDs as non-actionable metadata or drop collection. Do not build resume. |
| **FN: fix_attempted UX** | DOCUMENT-DOWN or small IMPLEMENT | Either show attempted flag in terminal after fix, or stop implying the report surfaces it. |

---

## 5. Explicit reject-list

Do **not** treat these as must-implement product work:

| ID | Reject reason |
|----|----------------|
| **I1 IMPLEMENT (`--url`)** | Slogan debt ≠ transport product; breaks fix story symmetry. |
| **I2 IMPLEMENT (generic CLI spawn)** | Scope expansion; judge/demo is Python. |
| **I3 IMPLEMENT (Codex resume)** | Incoherent with temp copy + cleanup; false feature. |
| **I4 IMPLEMENT (HTML CLI export)** | Never publicly claimed; F6 CLI already Done; wrong advisory fix. |
| **I6 IMPLEMENT (resolved lifecycle)** | Fights fresh-scan model; field is dead — DELETE optional only. |
| **I7 IMPLEMENT (wire infra_result)** | Threatens R4 clarity; DELETE optional only. |
| **I8 IMPLEMENT (CRITICAL rule)** | Severity theater; leave enum reserved. |

---

## Bottom line for planning

Spend implementation budget on **I5** (and optionally `fix_attempted` terminal visibility). Spend
editing budget on **I1–I3 claim surgery**. Refuse transport/resume/HTML/CRITICAL/infra_result
“completion” work framed as unfinished inventory.
