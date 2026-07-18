"""Print the JSONL emitted by a minimal Codex execution."""

from __future__ import annotations

import subprocess

if __name__ == "__main__":
    subprocess.run(["codex", "exec", "--json", "echo ok"], check=False)
