# McCoy

**Scan your MCP servers for deterministic security issues. Auto-fix what Codex can, and verify the
result with a fresh scan.**

McCoy connects to any MCP (Model Context Protocol) server over stdio or HTTP, enumerates its tool
surface, runs a deterministic ruleset over each tool definition, optionally annotates ambiguous
findings with a GPT-5.6 advisory pass, and drives Codex to patch the findings it can — re-scanning
after each round until the server is clean or the iteration cap is reached.

## Built with Codex and GPT-5.6

McCoy is an OpenAI Build Week 2026 project and both Codex and GPT-5.6 are first-class contributors:

- **GPT-5.6 (advisory pass).** Tool descriptions that match an injection marker (`ignore previous`,
  `system message`, …) are often benign documentation. For each MCC001 finding, McCoy asks GPT-5.6
  (via the Responses API with structured outputs) whether the description is genuine injection or
  benign docs, and annotates the finding with an advisory severity. The advisory never flips the
  pass/fail verdict — it only adds context. Set `OPENAI_API_KEY` to enable it; McCoy runs fully
  keyless without it.
- **Codex (fix-and-verify loop).** `mccoy fix` drives Codex against an isolated copy of your server
  source: it scans, asks Codex to patch each open finding, re-scans the patched copy, and repeats
  until the server is clean or the round cap is hit. The original files are never mutated in place.
  Each Codex run records its `thread_id` so you can resume the session that did the work.

## Install

Requires Python ≥ 3.10 on macOS or Linux.

```bash
git clone https://github.com/nitishagar/mccoy && cd mccoy
uv sync
```

You can also install from source with pip:

```bash
pip install git+https://github.com/nitishagar/mccoy.git
```

## Judge test path

Reproduce the demo without any entrant accounts:

```bash
# Scan the deliberately-vulnerable fixture. Expect ≥5 findings and exit code 2.
uv run mccoy scan fixtures/vuln_server/server.py

# Scan a clean fixture. Expect 0 findings and exit code 0.
uv run mccoy scan fixtures/vuln_server/clean_server.py
```

The fixture contains only misconfigurations and injection *text* — no harmful executable behavior —
so it is safe to ship and run anywhere.

## Advisory pass (BYO key)

`mccoy scan` is fully keyless by default: it runs the deterministic rules and exits. Set
`OPENAI_API_KEY` to enable the GPT-5.6 advisory pass, which annotates each injection-marker finding
with a benign/probably-malicious classification. The advisory never changes the exit code.

```bash
OPENAI_API_KEY=sk-... uv run mccoy scan fixtures/vuln_server/server.py
```

## Fix loop (BYO Codex)

`mccoy fix` requires the entrant's own `codex` CLI (it is never bundled). Install it from
<https://developers.openai.com/codex/>, then:

```bash
uv run mccoy fix fixtures/vuln_server/server.py --project fixtures/vuln_server
```

The loop operates on a copy of `--project`, so your original files are untouched. If Codex is not
installed and findings remain, McCoy prints an install hint and exits 3.

## Exit codes

| Code | Meaning                                                    |
|------|------------------------------------------------------------|
| `0`  | Clean — no deterministic findings (including a fix no-op). |
| `2`  | Unresolved deterministic findings remain.                  |
| `3`  | Infrastructure or tooling error (e.g. server won't start, Codex missing). |

## License

MIT. See [LICENSE](LICENSE).
