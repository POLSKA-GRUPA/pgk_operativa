"""Check: tests no-op (assert True, assert 1 == 1, pass)."""

from __future__ import annotations

import ast
from pathlib import Path

from pgk_operativa.verificador.manifest import Manifest
from pgk_operativa.verificador.report import Finding, Severity


def _is_noop_test(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    body = list(func.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
        body = body[1:]
    if not body:
        return True
    for stmt in body:
        if isinstance(stmt, ast.Pass):
            continue
        if isinstance(stmt, ast.Assert):
            test = stmt.test
            if isinstance(test, ast.Constant) and bool(test.value):
                continue
            if isinstance(test, ast.Compare):
                if all(isinstance(v, ast.Constant) for v in [test.left, *test.comparators]):
                    continue
            return False
        return False
    return True


def run(manifest: Manifest, repo_root: Path, repos_root: Path) -> list[Finding]:
    """Detecta tests cuya logica no aserta nada significativo."""
    _ = repos_root
    findings: list[Finding] = []
    for archivo in manifest.archivos:
        if not archivo.target.startswith("tests/"):
            continue
        target = archivo.target_path(repo_root)
        if not target.exists() or target.suffix != ".py":
            continue
        try:
            source = target.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(target))
        except (UnicodeDecodeError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            if not node.name.startswith("test_"):
                continue
            if _is_noop_test(node):
                findings.append(
                    Finding(
                        check="tests",
                        severity=Severity.HIGH,
                        target=archivo.target,
                        mensaje=f"Test '{node.name}' parece no-op (sin asserts reales)",
                        detalle=f"Linea {getattr(node, 'lineno', '?')}",
                    )
                )
    return findings
