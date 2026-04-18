"""Check: el archivo origen declarado existe en el repo origen.

Si relacion es copia_literal o adaptado, adicionalmente verifica:
- Rango de lineas (si declarado) esta dentro del archivo origen.
- Simbolos declarados existen como def/class en el origen.
"""

from __future__ import annotations

import ast
from pathlib import Path

from pgk_operativa.verificador.manifest import Manifest, Relacion
from pgk_operativa.verificador.report import Finding, Severity


def _parse_lineas(rango: str) -> tuple[int, int] | None:
    if "-" not in rango:
        try:
            n = int(rango.strip())
        except ValueError:
            return None
        # Sin esta guarda, "0" o "-1" pasaban como (0,0)/(-1,-1) y la
        # comparacion `rango[1] > total_lines` nunca los flagea.
        if n < 1:
            return None
        return (n, n)
    parts = rango.split("-", 1)
    try:
        start = int(parts[0].strip())
        end = int(parts[1].strip())
    except ValueError:
        return None
    if start > end or start < 1:
        return None
    return (start, end)


def _extract_symbols(source: str) -> set[str] | None:
    """Extrae nombres de def/class del origen (solo top-level).

    Devuelve None si el archivo no parsea como Python (SyntaxError). El caller
    debe distinguir "no pude parsear" de "parse OK pero falta el simbolo"
    para no disparar falsos positivos HIGH.

    Solo se recolectan simbolos top-level del modulo. Con ast.walk recursivo
    se recogian tambien metodos dentro de clases y funciones anidadas, lo
    que disparaba falsos negativos: un manifest que declarase
    simbolos=["foo"] esperando una funcion top-level pasaba la verificacion
    aunque el origen real tuviese `class X: def foo(self)`.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    out: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            out.add(node.name)
    return out


def run(manifest: Manifest, repo_root: Path, repos_root: Path) -> list[Finding]:
    """Verifica origenes declarados contra los repos origen del filesystem."""
    _ = repo_root
    findings: list[Finding] = []
    for archivo in manifest.archivos:
        if archivo.relacion == Relacion.NUEVO or archivo.origen is None:
            continue
        origen = archivo.origen
        source_path = origen.absolute_path(repos_root)

        if not source_path.exists():
            findings.append(
                Finding(
                    check="fidelity",
                    severity=Severity.HIGH,
                    target=archivo.target,
                    mensaje=(f"Archivo origen no existe: {origen.repo}/{origen.path}"),
                    detalle=(
                        f"Ruta esperada: {source_path}. "
                        "Verifica que el repo origen esta clonado en repos_root."
                    ),
                )
            )
            continue

        try:
            source_content = source_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(
                Finding(
                    check="fidelity",
                    severity=Severity.MEDIUM,
                    target=archivo.target,
                    mensaje="No se pudo leer el archivo origen como UTF-8",
                    detalle=f"Ruta: {source_path}",
                )
            )
            continue

        if origen.lineas:
            rango = _parse_lineas(origen.lineas)
            if rango is None:
                findings.append(
                    Finding(
                        check="fidelity",
                        severity=Severity.LOW,
                        target=archivo.target,
                        mensaje=f"Campo origen.lineas con formato invalido: {origen.lineas!r}",
                        detalle="Formato esperado: 'N' o 'N-M'.",
                    )
                )
            else:
                total_lines = len(source_content.splitlines())
                if rango[1] > total_lines:
                    findings.append(
                        Finding(
                            check="fidelity",
                            severity=Severity.MEDIUM,
                            target=archivo.target,
                            mensaje=(
                                f"origen.lineas {origen.lineas!r} excede el archivo origen "
                                f"({total_lines} lineas totales)"
                            ),
                            detalle=f"Archivo: {source_path}",
                        )
                    )

        if origen.simbolos and source_path.suffix == ".py":
            present = _extract_symbols(source_content)
            if present is None:
                # SyntaxError en el origen: no podemos concluir nada sobre los
                # simbolos. Avisamos con MEDIUM en vez de disparar HIGH por
                # "missing" falso positivo.
                findings.append(
                    Finding(
                        check="fidelity",
                        severity=Severity.MEDIUM,
                        target=archivo.target,
                        mensaje="No se pudo parsear el archivo origen como Python",
                        detalle=(
                            f"Archivo: {source_path}. SyntaxError al analizar. "
                            "Verifica manualmente que los simbolos existen."
                        ),
                    )
                )
            else:
                missing = [s for s in origen.simbolos if s not in present]
                if missing:
                    findings.append(
                        Finding(
                            check="fidelity",
                            severity=Severity.HIGH,
                            target=archivo.target,
                            mensaje=(
                                f"Simbolos declarados no existen en origen: {', '.join(missing)}"
                            ),
                            detalle=(
                                f"Archivo origen: {source_path}. "
                                "Puede indicar copia obsoleta o renombrado."
                            ),
                        )
                    )
    return findings
