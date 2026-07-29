# Research: What McCoy still needs to implement

**Date:** 2026-07-29  
**Repo:** `nitishagar/mccoy`  
**Method:** Inventory → adversarial need verification → implicit spec → adversarial spec validation  
**Artifacts:**

| Step | Document |
|------|----------|
| 1. Inventory | [`00-incomplete-feature-inventory.md`](./00-incomplete-feature-inventory.md) |
| 2. Need verification (adversarial) | [`adversarial/01-need-verification.md`](./adversarial/01-need-verification.md) |
| 3. Implicit spec (adversarial) | [`adversarial/02-implicit-spec.md`](./adversarial/02-implicit-spec.md) |
| 4. Spec validation (adversarial) | [`adversarial/03-spec-validation.md`](./adversarial/03-spec-validation.md) |

**Spec baseline status:** APPROVED WITH FIXES (amendments applied in `02-implicit-spec.md`).

---

## 1. Executive summary

McCoy’s core product loop is **already shipped**: deterministic rules MCC001–MCC008, keyless
stdio scan with exit codes 0/2/3, optional GPT-5.6 advisory attachment, Codex fix-and-verify with
copy-isolation, graded terminal report + before/after diff, and the docs site.

What remains is **not** a transport/resume/HTML epic. Adversarial review collapsed the incomplete
inventory to:

1. **One code change:** make GPT-5.6 advisory notes visible in the default terminal report (I5).
2. **Claim surgery:** narrow README/overview/landing/fix-loop copy that overpromises HTTP CLI,
   “any MCP server,” and Codex session resume (I1–I3 DOCUMENT-DOWN).
3. **One xor closure:** either show `fix_attempted` in the terminal after `mccoy fix`, or stop
   implying the report surfaces it (FN A xor B).

Everything else proposed as “incomplete” (HTTP `--url`, generic CLI spawn, Codex resume, HTML
CLI export, `resolved` lifecycle, wiring `infra_result`, inventing a CRITICAL rule) was
**rejected as must-implement**.

---

## 2. How the incomplete set was found

There is no checked-in feature checklist (`REASONING.md` / `IMPLICIT_SPEC` are referenced in
comments but live outside the repo, likely under gitignored `thoughts/`). The inventory was
reconstructed from:

- Public claims (`README.md`, landing, overview, fix-loop docs)
- Scaffolded but unwired APIs (`connect_http`, `render_html`, unused `thread_id` resume param,
  dead `Finding.resolved` / `infra_result`)
- Feature IDs in tests/comments (`F4`–`F6`, `R1`–`R4`, `A1`, `B*`, `D*`)
- Commit narrative (phased “Not-tested” lines that later closed)

Initial inventory candidates: **I1–I8** (see `00-incomplete-feature-inventory.md`).

---

## 3. Adversarial filtering (what is actually needed)

Need verification attacked each I-item. The key insight: several gaps are **honesty problems**,
not **feature problems**.

| ID | Inventory framing | Verdict | Why |
|----|-------------------|---------|-----|
| I1 HTTP CLI | Product gap | DOCUMENT-DOWN | Library + integration test prove transport; judge/demo is stdio. `--url` creates a no-fix path. |
| I2 Any MCP / generic spawn | Product gap | DOCUMENT-DOWN | CLI is Python-path-only; “any MCP” is slogan debt. |
| I3 Codex resume | Incomplete feature | DOCUMENT-DOWN | Never worked; resume is incoherent with temp-copy + `cleanup()`. |
| I4 HTML CLI export | F6 half-shipped | REJECT IMPLEMENT | Never marketed; F6 CLI = terminal + diff (Done). |
| **I5 Advisory in terminal** | Partial UX | **IMPLEMENT** | Flagship GPT-5.6 pass is invisible on the only CLI path. |
| I6 `resolved` | Incomplete lifecycle | REJECT / optional DELETE | Fights fresh-scan model; field always false. |
| I7 `infra_result` | Unwired helper | REJECT / optional DELETE | Exit-3 string path is correct for R4. |
| I8 CRITICAL severity | Unused enum | REJECT | Leave reserved; no severity theater. |
| FN `fix_attempted` UX | (false negative) | A xor B | Docs imply user-visible mark; renderer never shows it. |

Full attack write-up: `adversarial/01-need-verification.md`.

---

## 4. What needs to be implemented (authoritative)

Use `adversarial/02-implicit-spec.md` (post-validation) as the implementer’s contract. Condensed:

### 4.1 Must implement — I5 terminal advisory visibility

**Problem.** `scan_with_advisory` attaches `AdvisoryNote` when `OPENAI_API_KEY` is set, but
`render_terminal` ignores it. HTML shows advisories, but HTML is not on the CLI path. Keyed scans
look identical to keyless ones.

**Required behavior (MUSTs):**

- When `finding.advisory is not None`, print the advisory `message` associated with that finding.
- When advisory is absent, invent no placeholder text.
- Print the existing LLM-failure note (`LLM unavailable — advisory pass skipped`) when attached.
- Do **not** change exit codes, score, or severities (A1).
- No new flags/commands.
- Do **not** wire `scan_with_advisory` into the fix loop (`mccoy fix` continues to use `scan()`).

**Shoulds:** confidence / benign hint when `confidence > 0`; one-shot pass status for
`skipped…` / `completed` / `not applicable` — **never** print `"not run"` (fix path uses
`scan()`, which always sets that metadata).

**Acceptance:** extend `tests/test_report.py` (AT-I5-1…5 in the spec); keep existing CLI exit
tests green.

### 4.2 Must edit docs — DOC-I1 / I2 / I3 claim surgery

| Claim | Files | Replacement constraint |
|-------|-------|------------------------|
| “stdio or HTTP” as CLI capability | `README.md`, `overview.md` | CLI = stdio; HTTP only if scoped as library/`connect_http` |
| “any MCP server” | `README.md`, `overview.md`, `index.astro` | Python stdio MCP servers via CLI |
| “thread_id so you can resume” | `README.md`, `fix-loop.md` | Delete resume promise; no resume UX |

Forbidden phrases for acceptance greps include `stdio or HTTP` and unbounded `any MCP server` /
`any MCP (` in those marketing surfaces. Do not add `--url`, generic spawn, or resume.

### 4.3 Must close — FN `fix_attempted` (A xor B)

- **A (preferred if touching renderer for I5):** mark attempted findings in terminal output.
- **B:** document that `fix_attempted` is internal loop state, not a user-visible report field.

Leaving neither A nor B open is not allowed (validation amendment).

### 4.4 Explicitly do not implement

HTTP CLI, generic CLI spawn, Codex resume, HTML CLI export, `resolved` lifecycle,
`infra_result` wiring, CRITICAL-emitting rule. See spec §2.

---

## 5. Sequencing recommendation

| Order | Work | Size / risk |
|-------|------|-------------|
| 1 | I5 in `render_terminal` + unit tests (+ FN-A piggyback) | Small; presentation-only; preserves A1/R4 |
| 2 | DOC-I1 + DOC-I2 (same intro paragraphs) | Docs-only |
| 3 | DOC-I3 (resume sentence/section) | Docs-only |
| 4 | FN-B only if FN-A skipped | Docs-only |

Optional PR split: (1) renderer + tests, (2) claim surgery.

---

## 6. What this research deliberately does not authorize

- Expanding McCoy into a multi-runtime / multi-transport CLI product in this pass.
- Building resume around ephemeral workspaces.
- Using HTML export as a substitute for fixing default terminal output.
- Changing deterministic verdict semantics to surface advisory or infra failures as findings.

Those may be future product choices; they are **out of scope** for closing the current incomplete
set honestly.

---

## 7. Residual risks

1. **Doc near-misses** — rewrites like “HTTP transport supported” without “library” can still
   overclaim; acceptance greps help but need human review (no claim-guard test required).
2. **Fix path stays advisory-dark** — intentional; users who only run `mccoy fix` still won’t see
   GPT-5.6 notes unless they also `scan` with a key. Spec forbids wiring advisory into the loop
   in this pass.
3. **Dead scaffolding remains** (`render_html`, unused `thread_id` param, `resolved`,
   `infra_result`) — hygiene optional; not product work.
4. **I5-R5 wording** — “severity stays HIGH” is true for MCC001 (only advised rule); do not
   generalize into non-MCC001 advisory paths.

---

## 8. Bottom line

**Implement I5. Fix the marketing lies (I1–I3). Close `fix_attempted` visibility xor docs (FN).
Refuse the rest.**

That is the complete, adversarially validated implementation agenda for McCoy’s current incomplete
feature set.
