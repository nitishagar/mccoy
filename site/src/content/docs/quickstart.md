---
title: Quickstart
description: Scan your first MCP server in under a minute.
---

## Scan the vulnerable fixture

```bash
uv run mccoy scan fixtures/vuln_server/server.py
```

McCoy connects over stdio, enumerates the tools, and runs the deterministic ruleset. The fixture
ships ≥5 findings across multiple rule types, so you will see output like:

```
HIGH MCC001 unsafe_lookup: Description contains an instruction-injection marker.
MEDIUM MCC002 unsafe_lookup: Input schema does not forbid unknown properties.
...
12 finding(s) across 4 tool(s)
```

The exit code is `2` (unresolved findings).

## Scan a clean target

```bash
uv run mccoy scan fixtures/vuln_server/clean_server.py
```

This exits `0` — clean.

## Enable the advisory pass

```bash
OPENAI_API_KEY=sk-... uv run mccoy scan fixtures/vuln_server/server.py
```

Each injection-marker finding gets a GPT-5.6 advisory annotation. The verdict (exit code) does
not change.

## Fix with Codex

```bash
uv run mccoy fix fixtures/vuln_server/server.py --project fixtures/vuln_server
```

Requires your own `codex` CLI. McCoy patches a copy, re-scans, and repeats until clean.
