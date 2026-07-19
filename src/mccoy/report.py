"""Human-readable terminal and static report rendering.

``render_html`` renders a static, severity-graded HTML report (Jinja2 with autoescape on) that
includes the top-level score badge, each finding with its rationale and fix hint, and a
before/after diff block. Static HTML only — no server (F6). ``render_diff`` produces a unified
diff via ``git diff --no-index`` for use after a Codex fix round.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from mccoy.models import ScanResult

_TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    autoescape=select_autoescape(["html", "htm", "xml", "j2"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_terminal(result: ScanResult) -> str:
    rows = [f"McCoy score: {result.score}/100", f"Tools scanned: {result.tools_scanned}"]
    rows.extend(
        f"[{item.severity.upper()}] {item.rule_id} {item.tool}: {item.message}"
        for item in result.findings
    )
    return "\n".join(rows)


def render_html(result: ScanResult, diff: str = "") -> str:
    """Render a static HTML report. Autoescape is on, so finding text is XSS-safe."""
    template = _env.get_template("report.html.j2")
    return template.render(result=result, diff=diff)


def render_diff(before_path: Path, after_path: Path) -> str:
    """Return a unified diff of two files via ``git diff --no-index``.

    Returns an empty string when the files are identical. Raises RuntimeError if git is unavailable
    or fails unexpectedly (the two-path diff itself returns a non-zero exit on differences, which
    is expected and suppressed).
    """
    try:
        completed = subprocess.run(  # noqa: S603 - argv is constructed from trusted Path args
            ["git", "diff", "--no-index", "--", str(before_path), str(after_path)],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as error:  # pragma: no cover - git is assumed present in CI/dev
        raise RuntimeError("git is required to render diffs") from error
    # git diff --no-index exits 1 when files differ (the normal case) and 0 when identical.
    if completed.returncode not in (0, 1):
        raise RuntimeError(f"git diff failed: {completed.stderr.strip()}")
    return completed.stdout


__all__ = ["render_diff", "render_html", "render_terminal"]
