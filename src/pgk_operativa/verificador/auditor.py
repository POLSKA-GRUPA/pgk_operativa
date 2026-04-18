"""Orquestador del verificador: ejecuta todos los checks y agrega findings."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from pgk_operativa.core.paths import REPO_ROOT
from pgk_operativa.verificador import checks, semantic
from pgk_operativa.verificador.manifest import Manifest
from pgk_operativa.verificador.report import Finding, Report, Severity

CheckRunner = Callable[[Manifest, Path, Path], list[Finding]]


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

    runners: list[tuple[str, CheckRunner]] = [
        ("targets", checks.targets_check),
        ("lines", checks.lines_check),
        ("shell", checks.shell_check),
        ("imports", checks.imports_check),
        ("todo", checks.todo_check),
        ("tests", checks.tests_check),
        ("fidelity", checks.fidelity_check),
    ]
    for name, runner in runners:
        _run_guarded(name, runner, manifest, rr, sr, report)

    if semantico:
        _run_guarded("semantic", semantic.run, manifest, rr, sr, report)

    return report


def _run_guarded(
    name: str,
    runner: CheckRunner,
    manifest: Manifest,
    rr: Path,
    sr: Path,
    report: Report,
) -> None:
    """Ejecuta un check aislando sus excepciones no previstas.

    Sin esta guarda, un bug en cualquier check (p.ej. OSError al leer un
    symlink roto, IndexError al parsear un AST exotico) aborta toda la
    auditoria y oculta los findings de los checks posteriores. Emitimos
    un finding HIGH explicito para que el crash sea visible en el informe
    sin bloquear el merge (CRITICAL lo hace, HIGH solo avisa).
    """
    try:
        for finding in runner(manifest, rr, sr):
            report.add(finding)
    except Exception as exc:
        report.add(
            Finding(
                check=name,
                severity=Severity.HIGH,
                target="(verificador)",
                mensaje=f"Check '{name}' crasheo: {type(exc).__name__}",
                detalle=(f"{exc!s}"[:300] + " [revisar manualmente; el check no pudo completar]"),
            )
        )


def informes_dir() -> Path:
    """Directorio canonico de informes de auditoria."""
    return REPO_ROOT / "informes" / "auditoria"
