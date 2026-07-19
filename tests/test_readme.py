"""Sanity checks on the README — guards the judge-facing material (D2/B3)."""

from __future__ import annotations

from pathlib import Path

README = (Path(__file__).resolve().parent.parent / "README.md").read_text()


def test_readme_documents_install_command() -> None:
    assert "git clone https://github.com/nitishagar/mccoy" in README
    assert "uv sync" in README


def test_readme_documents_judge_test_path() -> None:
    # B3/B9: the judge must be able to reproduce the scan without rebuilding anything.
    assert "uv run mccoy scan fixtures/vuln_server/server.py" in README
    assert "uv run mccoy scan fixtures/vuln_server/clean_server.py" in README


def test_readme_documents_byo_key_and_codex() -> None:
    # B10: reproducibility without entrant accounts — never bundle a key, document the BYO path.
    assert "OPENAI_API_KEY" in README
    assert "codex" in README


def test_readme_states_license_and_exit_codes() -> None:
    assert "MIT" in README
    for code in ("0", "2", "3"):
        assert code in README


def test_readme_has_no_placeholder_text() -> None:
    lowered = README.lower()
    assert "todo" not in lowered
    assert "tbd" not in lowered
    assert "placeholder" not in lowered
