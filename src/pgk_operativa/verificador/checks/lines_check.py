"""Check: archivos con muy pocas lineas no-blank (caparazon vacio)."""

from __future__ import annotations

from pathlib import Path

from pgk_operativa.verificador.manifest import Manifest, Relacion
from pgk_operativa.verificador.report import Finding, Severity

MIN_LINES_CODE = 5
MIN_LINES_LITERAL = 15


def _count_non_blank(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip())


def run(manifest: Manifest, repo_root: Path, repos_root: Path) -> list[Finding]:
    """Detecta archivos sospechosos de ser caparazones vacios."""
    _ = repos_root
    findings: list[Finding] = []
    for archivo in manifest.archivos:
        target = archivo.target_path(repo_root)
        if not target.exists() or not target.is_file():
            continue
        # Los __init__.py suelen ser marcadores de paquete y contienen
        # solo reexports; no procede la regla de minimo de lineas.
        if target.name == "__init__.py":
            continue
        try:
            content = target.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        non_blank = _count_non_blank(content)

        min_required = (
            MIN_LINES_LITERAL if archivo.relacion == Relacion.COPIA_LITERAL else MIN_LINES_CODE
        )

        if non_blank < min_required:
            findings.append(
                Finding(
                    check="lines",
                    severity=Severity.HIGH,
                    target=archivo.target,
                    mensaje=(
                        f"Archivo con solo {non_blank} lineas no-blank "
                        f"(minimo esperado: {min_required})"
                    ),
                    detalle=(f"Relacion: {archivo.relacion.value}. Puede ser un caparazon vacio."),
                )
            )
    return findings
