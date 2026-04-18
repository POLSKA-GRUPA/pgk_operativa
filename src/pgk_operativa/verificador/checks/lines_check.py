"""Check: archivos con muy pocas lineas no-blank (caparazon vacio)."""

from __future__ import annotations

from pathlib import Path

from pgk_operativa.verificador.manifest import Manifest, Relacion
from pgk_operativa.verificador.report import Finding, Severity

MIN_LINES_CODE = 5
MIN_LINES_LITERAL = 15


def _count_non_blank(text: str, suffix: str) -> int:
    """Cuenta lineas con contenido real.

    Un archivo .py con 20 lineas de `# TODO: implementar` tecnicamente tiene
    20 lineas no-blank, pero es un caparazon: al ejecutarlo no pasa nada. Para
    el objetivo del check (detectar caparazones) excluimos comentarios puros
    de Python/shell/YAML. Para otros formatos (.md, .json, .txt) contamos
    todas las lineas con contenido: ahi un `#` puede ser markdown o dato.
    """
    skip_hash_comments = suffix in {".py", ".pyi", ".sh", ".yml", ".yaml", ".toml"}
    count = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if skip_hash_comments and stripped.startswith("#"):
            continue
        count += 1
    return count


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
        non_blank = _count_non_blank(content, target.suffix)

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
