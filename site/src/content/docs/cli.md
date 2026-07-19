---
title: CLI reference
description: McCoy command-line interface (generated from --help).
---

<!-- This file is regenerated from `uv run mccoy --help` on every build via scripts/gen-cli-ref.ts.
     Edit the CLI docstrings in src/mccoy/cli.py, not this file. -->

## `mccoy`

```text
Usage: mccoy [OPTIONS] COMMAND [ARGS]...                                       
                                                                                
 Scan MCP servers and help fix deterministic tool-surface findings.             
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.      │
│ --show-completion             Show completion for the current shell, to copy │
│                               it or customize the installation.              │
│ --help                        Show this message and exit.                    │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ scan  Scan a Python stdio MCP server and report deterministic findings.      │
│ fix   Scan, drive Codex to fix each open finding, and re-scan until green or │
│       capped.                                                                │
╰──────────────────────────────────────────────────────────────────────────────╯
                                                                                
 Exit codes: 0 clean, 2 unresolved findings, 3 infrastructure/tooling error.
```

## `mccoy scan`

```text
Usage: mccoy scan [OPTIONS] {server}                                           
                                                                                
 Scan a Python stdio MCP server and report deterministic findings.              
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    server      <path>  [required]                                          │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --timeout        <float>  [default: 30]                                      │
│ --help                    Show this message and exit.                        │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## `mccoy fix`

```text
Usage: mccoy fix [OPTIONS] {server}                                            
                                                                                
 Scan, drive Codex to fix each open finding, and re-scan until green or capped. 
                                                                                
 Operates on a copy of ``--project`` so the original files are never mutated.   
 Requires the                                                                   
 judge's own ``codex`` CLI (BYO install); exits 3 with an install hint when     
 Codex is missing.                                                              
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    server      <path>  [required]                                          │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --project              <path>   Project dir Codex edits; defaults to the     │
│                                 server's parent.                             │
│ --max-rounds           <int>    [default: 3]                                 │
│ --timeout              <float>  [default: 30.0]                              │
│ --codex-timeout        <float>  [default: 120.0]                             │
│ --help                          Show this message and exit.                  │
╰──────────────────────────────────────────────────────────────────────────────╯
```
