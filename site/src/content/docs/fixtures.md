---
title: Fixtures
description: The deliberately-vulnerable and clean MCP fixtures shipped with McCoy.
---

McCoy ships two MCP fixtures so judges and users can reproduce the scan without any setup.

## Vulnerable fixture

`fixtures/vuln_server/server.py` exposes four tools that trip ≥5 findings across multiple rule
types (injection, open schema, secret reference, broad scope, public bind, hidden Unicode,
mutable description, unpinned dependency, plus a planted false positive for the advisory demo).

It contains **no executable harmful behavior** — only misconfigurations and injection *text* — so
it is safe to ship and run anywhere.

```bash
uv run mccoy scan fixtures/vuln_server/server.py   # expect ≥5 findings, exit 2
```

## Clean fixture

`fixtures/vuln_server/clean_server.py` exposes a single tool with a frozen Pydantic input model.
It is the canonical green target.

```bash
uv run mccoy scan fixtures/vuln_server/clean_server.py   # expect 0 findings, exit 0
```
