"""Check: funciones/clases con cuerpo vacio (pass, ..., NotImplementedError).

Detecta "caparazones bonitos" aceptando que docstrings cuentan como cuerpo,
pero no funciones cuyo unico statement util es `pass` o `raise NotImplementedError`.
"""

from __future__ import annotations

import ast
from pathlib import Path

from pgk_operativa.verificador.manifest import Manifest, Relacion
from pgk_operativa.verificador.report import Finding, Severity


def _is_empty_body(node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> bool:
    """Devuelve True si el cuerpo es trivial (solo docstring/pass/Ellipsis/NotImplementedError)."""
    body = list(node.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
        body = body[1:]
    if not body:
        return True
    if len(body) == 1:
        stmt = body[0]
        if isinstance(stmt, ast.Pass):
            return True
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
            if stmt.value.value is Ellipsis or stmt.value.value is None:
                return True
        if isinstance(stmt, ast.Raise):
            exc = stmt.exc
            if isinstance(exc, ast.Name) and exc.id == "NotImplementedError":
                return True
            if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name):
                if exc.func.id == "NotImplementedError":
                    return True
    return False


def _iter_named(tree: ast.AST) -> list[tuple[str, ast.AST]]:
    items: list[tuple[str, ast.AST]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            items.append((node.name, node))
    return items


def run(manifest: Manifest, repo_root: Path, repos_root: Path) -> list[Finding]:
    """Flag funciones/clases con cuerpo trivial en archivos no-nuevos."""
    _ = repos_root
    findings: list[Finding] = []
    for archivo in manifest.archivos:
        target = archivo.target_path(repo_root)
        if not target.exists() or target.suffix != ".py":
            continue
        try:
            source = target.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(target))
        except (UnicodeDecodeError, SyntaxError) as exc:
            findings.append(
                Finding(
                    check="shell",
                    severity=Severity.CRITICAL,
                    target=archivo.target,
                    mensaje="Archivo Python no parseable",
                    detalle=str(exc),
                )
            )
            continue

        for name, node in _iter_named(tree):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                continue
            if _is_empty_body(node):
                is_protocol_like = (
                    name.startswith("_") or name.endswith("Protocol") or name.endswith("Base")
                )
                severity = Severity.MEDIUM if is_protocol_like else Severity.HIGH
                if archivo.relacion == Relacion.COPIA_LITERAL:
                    severity = Severity.HIGH
                findings.append(
                    Finding(
                        check="shell",
                        severity=severity,
                        target=archivo.target,
                        mensaje=f"'{name}' tiene cuerpo trivial (pass/NotImplementedError/...)",
                        detalle=(
                            f"Linea {getattr(node, 'lineno', '?')}. "
                            "Si es intencional (protocol/stub), documentalo en notas del manifest."
                        ),
                    )
                )
    return findings
