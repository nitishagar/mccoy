from typer.testing import CliRunner

from mccoy.cli import app


def test_help_lists_commands_and_exit_contract() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "scan" in result.output
    assert "fix" in result.output
    assert "Exit codes" in result.output
