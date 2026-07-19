from __future__ import annotations

from pathlib import Path

from mccoy.models import AdvisoryNote, Finding, ScanResult, Severity
from mccoy.report import render_diff, render_html, render_terminal


def _result(message: str = "Problem", advisory: AdvisoryNote | None = None) -> ScanResult:
    return ScanResult(
        findings=[
            Finding(
                rule_id="MCC001",
                tool="demo",
                severity=Severity.HIGH,
                message=message,
                fix_hint="Fix it",
                advisory=advisory,
            )
        ],
        tools_scanned=1,
    )


def test_terminal_report_includes_score_and_finding() -> None:
    out = render_terminal(_result())

    assert "MCC001" in out
    assert "McCoy score:" in out


def test_html_report_contains_score_finding_hint_and_diff_block() -> None:
    html = render_html(_result(), "- unsafe\n+ safe")

    assert "Score:" in html
    assert "MCC001" in html
    assert "Problem" in html
    assert "Fix it" in html
    assert "Before/after diff" in html
    assert "- unsafe" in html
    assert "+ safe" in html


def test_html_report_escapes_finding_text() -> None:
    # F6/robustness: finding messages are untrusted tool output; autoescape must neutralize markup.
    html = render_html(_result(message="<script>alert(1)</script>"))

    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_html_report_renders_advisory_when_present() -> None:
    advisory = AdvisoryNote(severity=Severity.INFO, confidence=0.9, message="benign docs")
    html = render_html(_result(advisory=advisory))

    assert "benign docs" in html
    assert "Advisory" in html


def test_render_diff_returns_unified_diff_for_differing_files(tmp_path: Path) -> None:
    before = tmp_path / "before.py"
    after = tmp_path / "after.py"
    before.write_text("unsafe = 1\n")
    after.write_text("safe = 1\n")

    diff = render_diff(before, after)

    assert "-unsafe = 1" in diff
    assert "+safe = 1" in diff


def test_render_diff_is_empty_for_identical_files(tmp_path: Path) -> None:
    same = tmp_path / "same.py"
    same.write_text("x = 1\n")

    assert render_diff(same, same) == ""
