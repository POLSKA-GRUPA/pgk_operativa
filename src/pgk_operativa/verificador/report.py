"""Modelo de findings y generador de informes Markdown."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path


class Severity(IntEnum):
    """Severidad de un finding. Orden: LOW < MEDIUM < HIGH < CRITICAL."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

    @property
    def label(self) -> str:
        return {
            Severity.LOW: "LOW",
            Severity.MEDIUM: "MEDIUM",
            Severity.HIGH: "HIGH",
            Severity.CRITICAL: "CRITICAL",
        }[self]


@dataclass(frozen=True)
class Finding:
    """Hallazgo individual de una check."""

    check: str
    severity: Severity
    target: str
    mensaje: str
    detalle: str = ""


@dataclass
class Report:
    """Informe de auditoría de un PR."""

    pr: int
    titulo: str
    fecha_auditoria: str
    findings: list[Finding] = field(default_factory=list)

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)

    def by_severity(self, sev: Severity) -> list[Finding]:
        return [f for f in self.findings if f.severity == sev]

    @property
    def has_critical(self) -> bool:
        return any(f.severity == Severity.CRITICAL for f in self.findings)

    @property
    def has_high(self) -> bool:
        return any(f.severity == Severity.HIGH for f in self.findings)

    @property
    def exit_code(self) -> int:
        """0 si todo OK, 2 si hay CRITICAL (bloqueante)."""
        return 2 if self.has_critical else 0

    def to_markdown(self) -> str:
        lines: list[str] = [
            f"# Auditoría PR #{self.pr:04d}",
            "",
            f"**Título**: {self.titulo}",
            "",
            f"**Fecha auditoría**: {self.fecha_auditoria}",
            "",
            "## Resumen",
            "",
            "| Severidad | N |",
            "|-----------|---|",
        ]
        for sev in (Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW):
            lines.append(f"| {sev.label} | {len(self.by_severity(sev))} |")

        total = len(self.findings)
        lines.extend(
            [
                f"| **TOTAL** | **{total}** |",
                "",
                f"**Estado**: {'BLOQUEANTE' if self.has_critical else 'APTO'}",
                "",
            ]
        )

        if total == 0:
            lines.append("Sin hallazgos. PR fiel al manifest.")
            return "\n".join(lines) + "\n"

        lines.extend(["## Hallazgos", ""])
        for sev in (Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW):
            subset = self.by_severity(sev)
            if not subset:
                continue
            lines.extend([f"### {sev.label} ({len(subset)})", ""])
            for f in subset:
                lines.extend(
                    [
                        f"- **[{f.check}]** `{f.target}`",
                        f"  - {f.mensaje}",
                    ]
                )
                if f.detalle:
                    for line in f.detalle.splitlines():
                        lines.append(f"  - {line}")
                lines.append("")
        return "\n".join(lines) + "\n"

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_markdown(), encoding="utf-8")
