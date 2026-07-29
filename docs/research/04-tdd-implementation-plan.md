# Surgical TDD plan — I5, DOC-I1–I3, FN-A

Authority: `docs/research/adversarial/02-implicit-spec.md` (post-validation).
One PR, three commits, adversarial verify after each. No co-author trailers.

## Commit 1 — I5 terminal advisory (code)

| Step | Action |
|------|--------|
| RED | Add AT-I5-1…5 in `tests/test_report.py` (must fail) |
| GREEN | Extend `render_terminal` only: advisory line + SHOULD status/confidence |
| VERIFY | `pytest tests/test_report.py tests/test_cli.py -q`; full suite |
| ADVERSARIAL | Agent checks I5-R* / A1 / no fix-loop advisory wiring / no `"not run"` print |

Format (locked by tests):
- Finding line unchanged: `[SEVERITY] RULE tool: message`
- Advisory line: `  Advisory: {message}` (+ ` (benign, confidence=0.90)` when INFO and confidence>0)
- Pass status once when metadata ∈ {skipped…, completed, not applicable}: `Advisory pass: {status}`
- Never print metadata `"not run"`

## Commit 2 — DOC claim surgery

| Step | Action |
|------|--------|
| RED | Add `tests/test_claim_honesty.py` forbidding `stdio or HTTP`, `any MCP server` / `any MCP (`, and `resume` near thread_id in README/overview/landing/fix-loop |
| GREEN | Edit those four surfaces only; optional one-clause library HTTP note |
| VERIFY | New tests + `test_readme.py` |
| ADVERSARIAL | Agent greps claims; confirms no `--url` / resume IMPLEMENT |

## Commit 3 — FN-A `fix_attempted` marker

| Step | Action |
|------|--------|
| RED | Tests: `fix_attempted=True` → marker; False → absent |
| GREEN | Append ` [fix attempted]` on finding line when True |
| VERIFY | report + fix_loop + cli tests |
| ADVERSARIAL | Agent confirms FN-A (not B), no resolved-history scope creep |

## Final

Full pytest + adversarial pass of whole diff vs `02-implicit-spec.md`. Update single PR body.
