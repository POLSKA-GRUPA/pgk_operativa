"""Orquestador del verificador: ejecuta todos los checks y agrega findings."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from pgk_operativa.core.paths import REPO_ROOT
from pgk_operativa.verificador import checks, semantic
from pgk_operativa.verificador.manifest import Manifest
from pgk_operativa.verificador.report import Report


def default_repos_root() -> Path:
    """Directorio donde viven los repos origen. Convencion: `~/repos/`."""
    return Path.home() / "repos"


def audit(
    manifest: Manifest,
    repo_root: Path | None = None,
    repos_root: Path | None = None,
    semantico: bool = False,
) -> Report:
    """Ejecuta todos los checks sobre el manifest y devuelve el informe.

    Args:
        manifest: Manifest cargado del PR.
        repo_root: Raiz del repo destino. Default: REPO_ROOT.
        repos_root: Raiz donde viven los repos origen. Default: ~/repos/.
        semantico: Si True, corre tambien el check LLM (coste + latencia).
    """
    rr = repo_root or REPO_ROOT
    sr = repos_root or default_repos_root()

    report = Report(
        pr=manifest.pr,
        titulo=manifest.titulo,
        fecha_auditoria=datetime.now(UTC).isoformat(timespec="seconds"),
    )

    runners = [
        checks.targets_check,
        checks.lines_check,
        checks.shell_check,
        checks.imports_check,
        checks.todo_check,
        checks.tests_check,
        checks.fidelity_check,
    ]
    for runner in runners:
        for finding in runner(manifest, rr, sr):
            report.add(finding)

    if semantico:
        for finding in semantic.run(manifest, rr, sr):
            report.add(finding)

    return report


def informes_dir() -> Path:
    """Directorio canonico de informes de auditoria."""
    return REPO_ROOT / "informes" / "auditoria"
