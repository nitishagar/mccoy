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


def test_terminal_renders_advisory_message_when_present() -> None:
    # AT-I5-1: advisory message must appear in terminal output.
    advisory = AdvisoryNote(severity=Severity.INFO, confidence=0.9, message="benign docs")
    out = render_terminal(_result(advisory=advisory))

    assert "benign docs" in out
    assert "Advisory:" in out
    assert "confidence=0.90" in out
    assert "benign" in out.lower()


def test_terminal_omits_advisory_when_absent() -> None:
    # AT-I5-2: no Advisory: label and no invented advisory body line.
    out = render_terminal(_result())
    lines = out.splitlines()

    assert "Advisory:" not in out
    assert lines[0].startswith("McCoy score:")
    assert lines[1].startswith("Tools scanned:")
    assert lines[2].startswith("[HIGH] MCC001")
    assert len(lines) == 3


def test_terminal_renders_advisory_failure_message() -> None:
    # AT-I5-3: LLM-unavailable note must surface when attached.
    advisory = AdvisoryNote(message="LLM unavailable — advisory pass skipped")
    out = render_terminal(_result(advisory=advisory))

    assert "LLM unavailable — advisory pass skipped" in out
    assert "Advisory:" in out
    # Default confidence 0.0 on failure placeholders may be omitted (I5-R2).
    assert "confidence=0.00" not in out


def test_terminal_prints_advisory_pass_status_but_not_not_run() -> None:
    # AT-I5-5: print skipped/completed/not applicable once; never print "not run".
    skipped = _result()
    skipped.metadata["advisory"] = "skipped (OPENAI_API_KEY unset)"
    assert "skipped (OPENAI_API_KEY unset)" in render_terminal(skipped)

    completed = _result()
    completed.metadata["advisory"] = "completed"
    assert "Advisory pass: completed" in render_terminal(completed)

    not_run = _result()
    not_run.metadata["advisory"] = "not run"
    assert "not run" not in render_terminal(not_run)
    assert "Advisory pass:" not in render_terminal(not_run)


def test_terminal_marks_fix_attempted_findings() -> None:
    # FN-A-R1: attempted findings carry a clear adjacent marker.
    attempted = _result()
    attempted.findings[0].fix_attempted = True
    out = render_terminal(attempted)
    finding_line = next(line for line in out.splitlines() if line.startswith("[HIGH]"))
    assert "fix attempted" in finding_line


def test_terminal_omits_fix_attempted_marker_by_default() -> None:
    # FN-A-R2: default/False findings have no marker.
    out = render_terminal(_result())
    finding_line = next(line for line in out.splitlines() if line.startswith("[HIGH]"))
    assert "fix attempted" not in finding_line


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
