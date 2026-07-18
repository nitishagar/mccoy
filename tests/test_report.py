from mccoy.models import Finding, ScanResult, Severity
from mccoy.report import render_html, render_terminal


def test_reports_include_score_finding_and_diff() -> None:
    result = ScanResult(
        findings=[
            Finding(
                rule_id="MCC001",
                tool="demo",
                severity=Severity.HIGH,
                message="Problem",
                fix_hint="Fix it",
            )
        ],
        tools_scanned=1,
    )

    assert "MCC001" in render_terminal(result)
    html = render_html(result, "- unsafe\n+ safe")
    assert "Score:" in html
    assert "MCC001" in html
    assert "Before/after diff" in html
