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


# Decoradores que HACEN que un cuerpo trivial sea correcto por diseno.
# Sin esta whitelist, metodos abstractos (`@abstractmethod`), overloads
# de tipos (`@overload`, `@typing.overload`) y property stubs legitimos
# disparaban un falso positivo HIGH en el check.
_ALLOWED_EMPTY_DECORATORS: frozenset[str] = frozenset(
    {
        "abstractmethod",
        "abstractproperty",
        "abstractclassmethod",
        "abstractstaticmethod",
        "overload",
    }
)


def _decorator_name(dec: ast.expr) -> str | None:
    """Extrae el nombre base de un decorator, ignorando el modulo.

    Cubre los tres patrones habituales:
        @abstractmethod           -> Name("abstractmethod")
        @abc.abstractmethod       -> Attribute(value=Name("abc"), attr="abstractmethod")
        @typing.overload          -> Attribute(value=Name("typing"), attr="overload")
    """
    if isinstance(dec, ast.Name):
        return dec.id
    if isinstance(dec, ast.Attribute):
        return dec.attr
    if isinstance(dec, ast.Call):
        return _decorator_name(dec.func)
    return None


def _has_allowed_empty_decorator(
    node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
) -> bool:
    """True si el nodo tiene un decorador que justifica cuerpo vacio."""
    for dec in getattr(node, "decorator_list", []):
        name = _decorator_name(dec)
        if name is not None and name in _ALLOWED_EMPTY_DECORATORS:
            return True
    return False


_Named = ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef


def _iter_named(tree: ast.AST) -> list[tuple[str, _Named]]:
    """Recorre el arbol y devuelve (name, node) para funciones y clases.

    El tipo de retorno estrecha `_Named` para que el caller no necesite
    re-chequear con isinstance, evitando codigo muerto inducido por el
    tipo laxo `ast.AST` anterior.
    """
    items: list[tuple[str, _Named]] = []
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
            if not _is_empty_body(node):
                continue
            # Skip decoradores que hacen que el cuerpo vacio sea correcto
            # (abstractmethod, overload, etc.). Solo aplica a funciones.
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                if _has_allowed_empty_decorator(node):
                    continue
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
