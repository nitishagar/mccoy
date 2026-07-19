---
title: Install
description: Install McCoy from source on macOS or Linux.
---

McCoy requires Python ≥ 3.10 on macOS or Linux.

## From source (recommended)

```bash
git clone https://github.com/nitishagar/mccoy && cd mccoy
uv sync
```

## With pip

```bash
pip install git+https://github.com/nitishagar/mccoy.git
```

## Verify

```bash
uv run mccoy --help
```

You should see the `scan` and `fix` subcommands.
