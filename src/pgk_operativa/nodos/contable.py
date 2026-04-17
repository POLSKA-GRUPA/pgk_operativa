"""Nodo tecnico: pgk.contable.

Contabilidad espanola (PGC 2008, asientos dobles, libros oficiales,
cuentas por grupo). El despacho trabaja con autonomos EDS y pymes.

Semana 2: ejecutor con prompt especializado. En fases posteriores se
anadiran tools deterministas (plan contable, motor de asientos),
adaptador CFO Agent, y conciliacion bancaria automatizada.
"""

from __future__ import annotations

from pgk_operativa.nodos._base import ejecutar_modulo


def nodo_contable(state: dict[str, object]) -> dict[str, object]:
    """Nodo LangGraph para consultas contables."""
    return ejecutar_modulo("contable", state)


__all__ = ["nodo_contable"]
