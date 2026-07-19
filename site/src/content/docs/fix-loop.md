---
title: Fix loop
description: How McCoy drives Codex to patch findings and re-scan until clean.
---

`mccoy fix` is McCoy's wedge: it is the only MCP scanner that detects a finding, patches it, and
re-scans to verify — automatically.

## How it works

1. **Copy** the `--project` directory into a temp workspace (the original is never mutated).
2. **Scan** the workspace copy.
3. If clean, exit `0` immediately (no Codex call — idempotent on green).
4. For each open finding, **ask Codex** (`codex exec --sandbox workspace-write --json`) to patch it.
5. **Re-scan** the workspace copy.
6. Repeat up to `--max-rounds` (default 3) or until clean.

## Invariants

- **Copy-isolation:** your fixture source is never edited in place.
- **Idempotency:** a finding Codex cleared does not reappear, so it is never re-patched.
- **Graceful degradation:** if a Codex call fails, the finding is marked `fix_attempted` and the
  loop continues with the rest.
- **Cost ceiling:** hard `--max-rounds` cap and a per-call `--codex-timeout` (default 120s).

## Exit codes

| Code | Meaning |
|------|---------|
| `0`  | Clean (including a no-op on already-clean input) |
| `2`  | Unresolved findings remain |
| `3`  | Infrastructure error (e.g. Codex CLI missing, server won't start) |

## The thread id

Each Codex run records a `thread_id` in its JSONL stream. McCoy captures these so you can resume
the session that did the work.
