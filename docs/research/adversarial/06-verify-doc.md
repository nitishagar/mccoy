# Adversarial verify — DOC-I1 / DOC-I2 / DOC-I3 (claim surgery)

**Commit under review:** `7bdc3c72e54f88c44ccf1e2f5dd5f2a2779dd165`  
**Subject:** Narrow marketing claims to match the Python stdio CLI  
**Branch:** `cursor/incomplete-feature-research-095e`  
**Authority:** `docs/research/adversarial/02-implicit-spec.md` §5 (DOC-I1/I2/I3) + §2 non-goals

## 1. Overall verdict

**PASS**

No product/doc/test fixes required. Uncommitted fixes: **none** (this verify file only).

## 2. Per-check table

| Check | Verdict | Evidence |
|-------|---------|----------|
| Forbidden `stdio or HTTP` gone | **PASS** | Absent from `README.md` and `overview.md`. Remaining HTTP mentions are scoped: “Streamable HTTP … via the library `connect_http` … CLI itself speaks stdio only.” |
| Forbidden `any MCP server` / `any MCP (` gone | **PASS** | Absent from README, overview, and `index.astro`. Replaced with “Python stdio MCP server” / “your Python stdio MCP server.” |
| Resume near `thread_id` / Codex session gone | **PASS** | README Codex bullet no longer mentions `thread_id` or resume; states graded report + before/after diff. `fix-loop.md` section retitled “After the loop”; ephemeral sessions + report/diff/cleanup; no resume workflow. |
| Replacement still accurate | **PASS** | CLI scoped to `.py` path / Python stdio; optional library `connect_http` clause matches §5.1 and §3 library-transport invariant. `connect_http` / `connect_stdio` remain in `src/mccoy/connect.py`. |
| Landing did **not** newly claim HTTP CLI | **PASS** | `index.astro` subhead has no HTTP; only Python-stdio narrowing. |
| No IMPLEMENT `--url` / `--command` / resume | **PASS** | Commit touches no `src/`. `cli.py` has no `--url` / `--command` / `--args`. No resume UX or argv wiring in this commit. |
| Tests cover acceptance | **PASS** | `tests/test_claim_honesty.py` guards all three forbidden families + “so you can resume”. |
| Pytest | **PASS** | `uv run pytest tests/test_claim_honesty.py tests/test_readme.py -q` → **8 passed**. |
| No `Co-authored-by` | **PASS** | `git log -1` body has no trailer. |
| Judge path docs intact | **PASS** | README still documents both scan commands under “Judge test path”; `test_readme.py` asserts them. |

## 3. Surface-by-surface (DOC triad consistency)

| Surface | After surgery | §5 fit |
|---------|---------------|--------|
| `README.md` intro | Python stdio + library `connect_http` clause | DOC-I1 + I2 |
| `README.md` Codex bullet | Report + diff of temp copy; no resume | DOC-I3 (replacement b) |
| `overview.md` lede | Same as README intro | DOC-I1 + I2 |
| `index.astro` subhead | “your Python stdio MCP server”; no HTTP added | DOC-I2; I1 landing constraint |
| `fix-loop.md` | “After the loop” — ephemeral + report/diff/cleanup | DOC-I3 |

## 4. Non-goals / scope creep

| Reject (§2) | Present in commit? |
|-------------|-------------------|
| I1 IMPLEMENT `--url` | No |
| I2 IMPLEMENT `--command` / `--args` | No |
| I3 IMPLEMENT resume | No |
| I4 / I6 / I7 / I8 | No |

Extra file in commit: `docs/research/adversarial/05-verify-i5.md` (prior I5 verify artifact). Research bundling only; does not implement rejects or re-broaden claims.

## 5. Required surgical fixes

None. **FAIL → fix** path not taken.

## 6. Notes for parent

- DOC-I1/I2/I3 claim surgery is closed for the triad surfaces; ready for FN (A xor B) if not already done.
- `fix-loop.md` still says findings are “marked `fix_attempted`” — that is FN §6 debt, **out of scope** for this DOC verify.
- This verify file is uncommitted by design (adversarial deliverable for parent).
