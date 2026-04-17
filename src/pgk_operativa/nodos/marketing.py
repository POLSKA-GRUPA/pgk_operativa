"""Nodo tecnico: pgk.marketing.

Marketing B2B para despacho fiscal (SEO, contenido, captacion,
LinkedIn, casos de exito, buyer personas).

Semana 2: ejecutor con prompt especializado. En fases posteriores se
anadiran Fase 11 (Marketing del empleado), perfiles web, blog firmado,
y LinkedIn asistido.
"""

from __future__ import annotations

from pgk_operativa.nodos._base import ejecutar_modulo


def nodo_marketing(state: dict[str, object]) -> dict[str, object]:
    """Nodo LangGraph para consultas de marketing."""
    return ejecutar_modulo("marketing", state)


__all__ = ["nodo_marketing"]
