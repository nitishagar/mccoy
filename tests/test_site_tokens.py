"""D1 drift guard — asserts the docs site ships the verified opencode.ai color tokens.

Asserts against the SOURCE file (site/src/styles/tokens.css) rather than built CSS: the source is
stable across CI environments, always present, and a drift here propagates to the build. The
values were re-verified from opencode.ai's compiled CSS on 2026-07-19 (see REASONING.md) — they
are HSL, not hex, and dark mode switches via prefers-color-scheme (system-only).
"""

from __future__ import annotations

import re
from pathlib import Path

TOKENS = (
    Path(__file__).resolve().parent.parent / "site" / "src" / "styles" / "tokens.css"
).read_text()


def _value(token: str, section: str = TOKENS) -> str:
    match = re.search(rf"--{re.escape(token)}:\s*([^;]+);", section)
    assert match is not None, f"--{token} not defined in tokens.css"
    return match.group(1).strip()


_DARK_BLOCK = re.compile(
    r"@media\s*\(\s*prefers-color-scheme:\s*dark\s*\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}"
)


def _dark_section() -> str:
    match = _DARK_BLOCK.search(TOKENS)
    assert match is not None, "no prefers-color-scheme: dark block in tokens.css"
    return match.group(1)


def test_light_mode_tokens_match_opencode_palette() -> None:
    assert _value("color-background") == "hsl(0, 20%, 99%)"
    assert _value("color-background-weak") == "hsl(0, 8%, 97%)"
    assert _value("color-background-strong") == "hsl(0, 5%, 12%)"
    assert _value("color-text") == "hsl(0, 1%, 39%)"
    assert _value("color-text-strong") == "hsl(0, 5%, 12%)"
    assert _value("color-border") == "hsl(30, 2%, 81%)"


def test_dark_mode_tokens_match_opencode_palette() -> None:
    dark = _dark_section()
    assert _value("color-background", dark) == "hsl(0, 9%, 7%)"
    assert _value("color-background-weak", dark) == "hsl(0, 6%, 10%)"
    assert _value("color-background-strong", dark) == "hsl(0, 15%, 94%)"
    assert _value("color-text", dark) == "hsl(0, 4%, 71%)"
    assert _value("color-text-strong", dark) == "hsl(0, 15%, 94%)"
    assert _value("color-border", dark) == "hsl(0, 3%, 28%)"


def test_plan_alias_tokens_resolve_to_opencode_names() -> None:
    # The plan/IMPLICIT_SPEC reference --color-bg/--color-surface/--color-strong; they must alias
    # the real opencode names so both naming conventions stay in sync.
    assert _value("color-bg") == "var(--color-background)"
    assert _value("color-surface") == "var(--color-background-weak)"
    assert _value("color-strong") == "var(--color-background-strong)"


def test_ibm_plex_mono_is_the_primary_typeface() -> None:
    font = _value("sl-font")
    assert "IBM Plex Mono" in font
    # D1: dark mode is system-only — the toggle must not appear as a data-theme attribute scheme.
    assert "prefers-color-scheme" in TOKENS
