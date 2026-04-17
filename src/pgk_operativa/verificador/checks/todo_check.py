"""Check: TODOs/FIXMEs sin issue asociado."""

from __future__ import annotations

import re
from pathlib import Path

from pgk_operativa.verificador.manifest import Manifest
from pgk_operativa.verificador.report import Finding, Severity

_PATTERN = re.compile(r"\b(TODO|FIXME|XXX|HACK)\b[:\s](.*)$")
_ISSUE = re.compile(r"#\d+|issue[-_ ]?\d+|PR-\d+", re.IGNORECASE)


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
        for lineno, line in enumerate(lines, start=1):
            match = _PATTERN.search(line)
            if not match:
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
