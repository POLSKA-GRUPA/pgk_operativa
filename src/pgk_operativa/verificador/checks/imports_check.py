"""Check: imports del modulo se pueden resolver (modulos internos o en dependencies).

No ejecutamos importlib.import_module (costoso y side-effect). Solo validamos:
- Imports relativos dentro de `src/pgk_operativa/` apuntan a archivos o paquetes existentes.
- Imports absolutos con prefijo `pgk_operativa.` resuelven a un archivo .py o directorio con __init__.py.
"""

from __future__ import annotations

import ast
from pathlib import Path

from pgk_operativa.verificador.manifest import Manifest
from pgk_operativa.verificador.report import Finding, Severity


def _is_pgk_module(name: str) -> bool:
    """True solo si `name` es el paquete pgk_operativa o un submodulo suyo.

    `startswith("pgk_operativa")` matchearia por error paquetes colindantes
    como `pgk_operativa_extra`. Comparamos nombre exacto o prefijo con punto.
    """
    return name == "pgk_operativa" or name.startswith("pgk_operativa.")


def _file_package(target: Path, src_root: Path) -> list[str] | None:
    """Paquete (partes dotted) al que pertenece `target` dentro de `src_root`.

    Para `src/pgk_operativa/core/router.py` devuelve `['pgk_operativa', 'core']`.
    Para `src/pgk_operativa/core/__init__.py` tambien `['pgk_operativa', 'core']`
    (el propio paquete). None si target no cuelga de `src_root/pgk_operativa/`.
    """
    try:
        rel = target.resolve().relative_to(src_root.resolve())
    except ValueError:
        return None
    parts = list(rel.parts)
    if len(parts) < 2 or parts[0] != "pgk_operativa":
        return None
    return parts[:-1]


def _resolve_relative(module: str | None, level: int, file_pkg: list[str]) -> str | None:
    """Convierte un `from .X import Y` en ruta absoluta `pgk_operativa.core.X`.

    level=1 significa el mismo paquete; level=2 sube un padre; etc. Devuelve
    None si el ascenso escapa del paquete raiz `pgk_operativa`, lo cual es
    siempre un bug (Python lanzaria ImportError en runtime).
    """
    climb = level - 1
    base_len = len(file_pkg) - climb
    # base_len < 1 equivale a subir por encima del paquete raiz. La comparacion
    # con 1 incluye el caso climb == len(file_pkg) - 1 porque entonces base_len
    # seria 1 pero al estar debajo de 'pgk_operativa' exacto esto es valido.
    if base_len < 1:
        return None
    base = file_pkg[:base_len]
    if module:
        base = base + module.split(".")
    return ".".join(base)


def _collect_imports(tree: ast.AST, file_pkg: list[str] | None) -> list[tuple[int, str]]:
    """Devuelve lista de (lineno, module_path) para imports que deben resolver.

    Incluye:
    - `import pgk_operativa.X` y `from pgk_operativa.X import Y` (absolutos).
    - `from .X import Y` (relativos), resueltos al paquete destino. Un
      manifest que declara `from ..foo import X` donde `..foo` no existe es
      un caparazon roto: antes este check no lo veia porque filtraba por
      `node.level == 0`, dejando pasar silenciosamente los relativos rotos.
    """
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _is_pgk_module(alias.name):
                    out.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                if node.module and _is_pgk_module(node.module):
                    out.append((node.lineno, node.module))
            else:
                # Import relativo. Sin file_pkg no podemos resolver, lo
                # tratamos como no-pgk (otro paquete instalable que casualmente
                # usa relativos). Con file_pkg resolvemos a dotted absoluto.
                if file_pkg is None:
                    continue
                resolved = _resolve_relative(node.module, node.level, file_pkg)
                if resolved is None:
                    # Escapa por encima de pgk_operativa: siempre roto.
                    out.append(
                        (
                            node.lineno,
                            f"<relativo invalido: level={node.level} "
                            f"module={node.module!r} desde pgk "
                            f"{'.'.join(file_pkg)}>",
                        )
                    )
                elif _is_pgk_module(resolved):
                    out.append((node.lineno, resolved))
    return out


def _resolve(module: str, src_root: Path) -> bool:
    """Verifica que `module` (punto-separado) existe como paquete o modulo en src_root.

    Para `ast.Import` y `ast.ImportFrom`, `node.module` / `alias.name` contienen
    SIEMPRE una ruta de modulo completa, nunca un simbolo. El fallback a parent
    que existia aqui enmascaraba imports rotos: ante
    `from pgk_operativa.core.nonexistent import X`, el modulo `pgk_operativa.core`
    si existe y devolvia True, ocultando que `nonexistent` no existe.
    """
    # Tokens inyectados por _collect_imports para relativos invalidos. No
    # intentamos resolverlos: siempre son findings.
    if module.startswith("<"):
        return False
    parts = module.split(".")
    if parts[0] != "pgk_operativa":
        return True
    if len(parts) == 1:
        return (src_root / "pgk_operativa" / "__init__.py").exists()
    rel = Path(*parts[1:])
    as_package = src_root / "pgk_operativa" / rel / "__init__.py"
    as_module = src_root / "pgk_operativa" / rel.with_suffix(".py")
    return as_package.exists() or as_module.exists()


def run(manifest: Manifest, repo_root: Path, repos_root: Path) -> list[Finding]:
    """Detecta imports absolutos de pgk_operativa que no resuelven."""
    _ = repos_root
    findings: list[Finding] = []
    src_root = repo_root / "src"
    for archivo in manifest.archivos:
        target = archivo.target_path(repo_root)
        if not target.exists() or target.suffix != ".py":
            continue
        try:
            source = target.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(target))
        except (UnicodeDecodeError, SyntaxError):
            continue
        file_pkg = _file_package(target, src_root)
        for lineno, module in _collect_imports(tree, file_pkg):
            if not _resolve(module, src_root):
                findings.append(
                    Finding(
                        check="imports",
                        severity=Severity.CRITICAL,
                        target=archivo.target,
                        mensaje=f"Import interno no resuelve: '{module}'",
                        detalle=f"Linea {lineno}. Verificar path o renombrar.",
                    )
                )
    return findings
