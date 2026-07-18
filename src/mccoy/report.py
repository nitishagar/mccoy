"""Human-readable terminal and static report rendering."""

from __future__ import annotations

from html import escape

from mccoy.models import ScanResult


def render_terminal(result: ScanResult) -> str:
    rows = [f"McCoy score: {result.score}/100", f"Tools scanned: {result.tools_scanned}"]
    rows.extend(
        f"[{item.severity.upper()}] {item.rule_id} {item.tool}: {item.message}"
        for item in result.findings
    )
    return "\n".join(rows)


def render_html(result: ScanResult, diff: str = "") -> str:
    findings = "".join(
        "<li>"
        f"<strong>{escape(item.severity)}</strong> {escape(item.rule_id)} — "
        f"{escape(item.message)}<br><code>{escape(item.fix_hint)}</code></li>"
        for item in result.findings
    )
    return (
        "<!doctype html><html><body><h1>McCoy report</h1>"
        f"<p>Score: {result.score}/100</p><ul>{findings}</ul>"
        f"<h2>Before/after diff</h2><pre>{escape(diff)}</pre></body></html>"
    )
