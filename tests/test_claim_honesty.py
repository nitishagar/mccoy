"""DOC-I1/I2/I3 claim-honesty guards — marketing must not over-promise the CLI."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text()
OVERVIEW = (ROOT / "site/src/content/docs/overview.md").read_text()
LANDING = (ROOT / "site/src/pages/index.astro").read_text()
FIX_LOOP = (ROOT / "site/src/content/docs/fix-loop.md").read_text()


def test_readme_and_overview_do_not_claim_stdio_or_http_cli() -> None:
    # DOC-I1: bare "stdio or HTTP" as product/CLI capability is forbidden.
    assert "stdio or HTTP" not in README
    assert "stdio or HTTP" not in OVERVIEW


def test_marketing_does_not_claim_any_mcp_server() -> None:
    # DOC-I2: unbounded "any MCP server" / "any MCP (" CLI claims are forbidden.
    for text, label in ((README, "README"), (OVERVIEW, "overview"), (LANDING, "landing")):
        assert "any MCP server" not in text, label
        assert "any MCP (" not in text, label


def test_readme_and_fix_loop_do_not_promise_codex_resume() -> None:
    # DOC-I3: no resume promise near thread_id / Codex session language.
    for text, label in ((README, "README"), (FIX_LOOP, "fix-loop")):
        lowered = text.lower()
        if "thread_id" in lowered or "thread id" in lowered:
            assert "resume" not in lowered, label
        assert "so you can resume" not in lowered, label
