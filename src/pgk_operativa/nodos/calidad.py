"""Nodo tecnico: pgk.calidad.

Control de calidad de respuestas generadas por otros modulos.
Verificacion cruzada, deteccion de hedging excesivo, validacion
de citas y fuentes.

Semana 2: ejecutor con prompt especializado. En fases posteriores se
anadira integracion con el subgraph de consenso, red_team, y
verificacion Perplexity.
"""

from __future__ import annotations

from pgk_operativa.nodos._base import ejecutar_modulo


def nodo_calidad(state: dict[str, object]) -> dict[str, object]:
    """Nodo LangGraph para control de calidad."""
    return ejecutar_modulo("calidad", state)


__all__ = ["nodo_calidad"]
