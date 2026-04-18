"""Tests de la CLI Typer."""

from __future__ import annotations

from unittest.mock import patch

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


def _fake_run_graph(mensaje: str, **_kwargs: object) -> dict[str, object]:
    return {
        "modulo_tecnico": "fiscal" if "fiscal" in mensaje.lower() else "general",
        "clasificacion_razonamiento": "mock",
        "respuesta_final": f"Respuesta simulada para: {mensaje}",
    }


def test_ana_without_consenso() -> None:
    with patch("pgk_operativa.cli.main.run_graph", side_effect=_fake_run_graph):
        result = runner.invoke(app, ["ana", "hola"])
    assert result.exit_code == 0, result.stdout
    assert "Ana" in result.stdout


def test_ana_with_consenso_flag() -> None:
    with patch("pgk_operativa.cli.main.run_graph", side_effect=_fake_run_graph):
        result = runner.invoke(app, ["ana", "--consenso", "decision fiscal"])
    assert result.exit_code == 0, result.stdout
    assert "Ana" in result.stdout


def test_verificar_rejects_pr_zero() -> None:
    """--pr 0 y --pr negativo deben fallar con exit 2, no con FileNotFoundError."""
    result = runner.invoke(app, ["verificar", "--pr", "0"])
    assert result.exit_code == 2
    assert "positivo" in result.stdout or "positivo" in (result.stderr or "")


def test_verificar_rejects_pr_negative() -> None:
    result = runner.invoke(app, ["verificar", "--pr", "-5"])
    assert result.exit_code == 2
