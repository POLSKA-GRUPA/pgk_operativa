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


def _collect_imports(tree: ast.AST) -> list[tuple[int, str]]:
    """Devuelve lista de (lineno, module_path) para imports absolutos de pgk_operativa."""
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("pgk_operativa"):
                    out.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("pgk_operativa") and node.level == 0:
                out.append((node.lineno, node.module))
    return out


def _resolve(module: str, src_root: Path) -> bool:
    """Verifica que `module` (punto-separado) existe como paquete o modulo en src_root."""
    parts = module.split(".")
    if parts[0] != "pgk_operativa":
        return True
    # `import pgk_operativa` sin submodulo: el paquete raiz.
    if len(parts) == 1:
        return (src_root / "pgk_operativa" / "__init__.py").exists()
    rel = Path(*parts[1:])
    as_package = src_root / "pgk_operativa" / rel / "__init__.py"
    as_module = src_root / "pgk_operativa" / rel.with_suffix(".py")
    if as_package.exists() or as_module.exists():
        return True
    # puede ser un simbolo importado from un modulo: probar con parent
    if len(parts) > 2:
        parent = ".".join(parts[:-1])
        return _resolve(parent, src_root)
    return False


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
        for lineno, module in _collect_imports(tree):
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
