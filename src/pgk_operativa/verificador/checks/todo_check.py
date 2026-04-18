"""Check: TODOs/FIXMEs sin issue asociado."""

from __future__ import annotations

import re
from pathlib import Path

from pgk_operativa.verificador.manifest import Manifest
from pgk_operativa.verificador.report import Finding, Severity

_PATTERN = re.compile(r"\b(TODO|FIXME|XXX|HACK)\b(.*)$")
_ISSUE = re.compile(r"#\d+|issue[-_ ]?\d+|PR-\d+", re.IGNORECASE)


def _is_in_comment(line: str, match_start: int) -> bool:
    """Heuristica: el match esta dentro de un comentario `#` o docstring.

    Sin esta comprobacion el patron matcheaba TODOs dentro de cadenas tipo
    msg = "TODO: fix", generando falsos positivos. Para Python basta con
    exigir que aparezca `#` antes del match en la misma linea, o que la
    linea empiece con triple-comillas (docstring abierto).

    Respeta escapes `\\"` y `\\'`: sin esto una cadena con un escape
    impar como `"a \\" # TODO"` cerraria prematuramente el string y el
    `#` interno se interpretaria como inicio de comentario, emitiendo un
    falso positivo LOW.
    """
    prefix = line[:match_start]
    stripped = prefix.lstrip()
    if stripped.startswith(("#", '"""', "'''")):
        return True
    # Buscar '#' fuera de cadenas simples a la izquierda del match.
    in_single = False
    in_double = False
    i = 0
    while i < len(prefix):
        ch = prefix[i]
        if ch == "\\" and i + 1 < len(prefix) and (in_single or in_double):
            # Escape dentro de string: saltar el caracter escapado. Solo
            # aplica dentro de strings; fuera de strings `\` no es escape.
            i += 2
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            return True
        i += 1
    return False


def run(manifest: Manifest, repo_root: Path, repos_root: Path) -> list[Finding]:
    """Lista TODOs sin referencia a issue o PR. Severidad LOW."""
    _ = repos_root
    findings: list[Finding] = []
    for archivo in manifest.archivos:
        target = archivo.target_path(repo_root)
        if not target.exists() or not target.is_file():
            continue
        try:
            lines = target.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        is_python = target.suffix == ".py"
        for lineno, line in enumerate(lines, start=1):
            match = _PATTERN.search(line)
            if not match:
                continue
            # Para .py filtramos matches que caen dentro de cadenas para no
            # disparar LOW sobre strings como `msg = "TODO: algo"`. Otros
            # formatos (Markdown, YAML) no tienen esa distincion clara.
            if is_python and not _is_in_comment(line, match.start()):
                continue
            tail = match.group(2) or ""
            if _ISSUE.search(tail):
                continue
            findings.append(
                Finding(
                    check="todo",
                    severity=Severity.LOW,
                    target=archivo.target,
                    mensaje=f"{match.group(1).upper()} sin issue/PR asociado",
                    detalle=f"Linea {lineno}: {line.strip()[:120]}",
                )
            )
    return findings
