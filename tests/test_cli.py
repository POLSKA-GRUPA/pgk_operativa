"""Tests de la CLI Typer."""

from __future__ import annotations

from typer.testing import CliRunner

from pgk_operativa import __version__
from pgk_operativa.cli.main import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_doctor_runs() -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "pgk_operativa doctor" in result.stdout


def test_ana_without_consenso() -> None:
    result = runner.invoke(app, ["ana", "hola"])
    assert result.exit_code == 0
    assert "Ana" in result.stdout


def test_ana_with_consenso_flag() -> None:
    result = runner.invoke(app, ["ana", "--consenso", "decision fiscal"])
    assert result.exit_code == 0
    assert "Ana" in result.stdout
