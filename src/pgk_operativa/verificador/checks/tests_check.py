"""Check: tests no-op (assert True, assert 1 == 1, pass)."""

from __future__ import annotations

import ast
from pathlib import Path

from pgk_operativa.verificador.manifest import Manifest
from pgk_operativa.verificador.report import Finding, Severity

_CMP_OPS: dict[type[ast.cmpop], object] = {
    ast.Eq: lambda a, b: a == b,
    ast.NotEq: lambda a, b: a != b,
    ast.Lt: lambda a, b: a < b,
    ast.LtE: lambda a, b: a <= b,
    ast.Gt: lambda a, b: a > b,
    ast.GtE: lambda a, b: a >= b,
    ast.Is: lambda a, b: a is b,
    ast.IsNot: lambda a, b: a is not b,
    ast.In: lambda a, b: a in b,
    ast.NotIn: lambda a, b: a not in b,
}


def _constant_compare_is_true(node: ast.Compare) -> bool | None:
    """Evalua un Compare con operandos ast.Constant sin usar eval.

    Devuelve True/False si se puede evaluar, None si algun operando no es
    constante o el operador no esta soportado.
    """
    if not all(isinstance(v, ast.Constant) for v in [node.left, *node.comparators]):
        return None
    values = [v.value for v in [node.left, *node.comparators]]  # type: ignore[attr-defined]
    for i, op in enumerate(node.ops):
        fn = _CMP_OPS.get(type(op))
        if fn is None:
            return None
        try:
            if not fn(values[i], values[i + 1]):  # type: ignore[operator]
                return False
        except TypeError:
            return None
    return True


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
                # Solo es "no-op" si la comparacion de constantes evalua a True
                # (p.ej. `assert 1 == 1`). `assert 1 == 2` siempre falla, no
                # es un no-op y el test merece respeto del auditor.
                result = _constant_compare_is_true(test)
                if result is True:
                    continue
            return False
        return False
    return True


def _iter_test_functions(
    tree: ast.Module,
) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    """Devuelve SOLO tests top-level o metodos directos de clases.

    `ast.walk` recorria todos los FunctionDef del arbol, lo que flagaba
    como no-op a helpers anidados dentro de un test real:

        def test_real():
            def test_helper():  # <- anidada, NO es un test pytest
                pass
            assert condicion_real()

    Pytest solo recoge tests de nivel modulo o metodos de clases `Test*`,
    nunca funciones anidadas. Iteramos solo esos dos niveles para eliminar
    el falso positivo.
    """
    out: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            if node.name.startswith("test_"):
                out.append(node)
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                    if item.name.startswith("test_"):
                        out.append(item)
    return out


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
        for node in _iter_test_functions(tree):
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
