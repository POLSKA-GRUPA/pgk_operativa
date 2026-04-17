"""Nodo tecnico: pgk.docs.

Redaccion de borradores de comunicacion profesional para cliente
(emails, cartas, informes, plantillas, traducciones ES/PL).

Semana 2: ejecutor con prompt especializado. En fases posteriores se
anadiran plantillas corporativas, motor de traducciones, y generador
de firmas con Paloma.
"""

from __future__ import annotations

from pgk_operativa.nodos._base import ejecutar_modulo


def nodo_docs(state: dict[str, object]) -> dict[str, object]:
    """Nodo LangGraph para redaccion de documentos."""
    return ejecutar_modulo("docs", state)


__all__ = ["nodo_docs"]
