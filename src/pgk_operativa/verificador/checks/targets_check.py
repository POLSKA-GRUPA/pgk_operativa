"""Check: archivos target declarados en el manifest existen."""

from __future__ import annotations

from pathlib import Path

from pgk_operativa.verificador.manifest import Manifest
from pgk_operativa.verificador.report import Finding, Severity


def run(manifest: Manifest, repo_root: Path, repos_root: Path) -> list[Finding]:
    """Verifica que cada archivo target del manifest existe en el repo."""
    _ = repos_root
    findings: list[Finding] = []
    for archivo in manifest.archivos:
        target = archivo.target_path(repo_root)
        if not target.exists():
            findings.append(
                Finding(
                    check="targets",
                    severity=Severity.CRITICAL,
                    target=archivo.target,
                    mensaje="Archivo target declarado en manifest no existe",
                    detalle=f"Ruta esperada: {target}",
                )
            )
        elif not target.is_file():
            findings.append(
                Finding(
                    check="targets",
                    severity=Severity.CRITICAL,
                    target=archivo.target,
                    mensaje="Target existe pero no es un archivo regular",
                    detalle=f"Ruta: {target}",
                )
            )
    return findings
