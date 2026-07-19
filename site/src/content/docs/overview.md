---
title: Overview
description: McCoy scans live MCP tool surfaces for deterministic security issues and helps fix them.
---

McCoy connects to any MCP (Model Context Protocol) server over stdio or HTTP, enumerates its tool
surface, runs a deterministic ruleset over each tool definition, optionally annotates ambiguous
findings with a GPT-5.6 advisory pass, and drives Codex to patch the findings it can — re-scanning
after each round until the server is clean or the iteration cap is reached.

## Why

MCP servers expose tools to models. A tool description that contains `ignore previous
instructions`, a schema without `additionalProperties: false`, or a `0.0.0.0` bind is a real,
exploitable surface — but no rival scanner both detects these *and* fixes them. McCoy does.

## How it fits together

1. **Scan** — deterministic rules (8 of them) over the live tool surface.
2. **Advise** — GPT-5.6 sorts genuine injection from benign docs (advisory only, never the verdict).
3. **Fix** — Codex patches each open finding on an isolated copy, then re-scans.

Head to the [Quickstart](/quickstart/) to scan your first server.
