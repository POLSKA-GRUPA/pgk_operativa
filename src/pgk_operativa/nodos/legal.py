"""Nodo tecnico: pgk.legal.

Derecho civil, mercantil y procesal espanol (LEC, LO 1/2025, MASC,
LGT, jurisprudencia TS, SAN, TSJ).

Semana 2: ejecutor con prompt especializado. En fases posteriores se
anadiran 17 skills de Junior + 8 de PGK_Empresa_Autonoma, KB legal
con ECLI verificable, y motor de alegaciones.
"""

from __future__ import annotations

from pgk_operativa.nodos._base import ejecutar_modulo


def nodo_legal(state: dict[str, object]) -> dict[str, object]:
    """Nodo LangGraph para consultas legales."""
    return ejecutar_modulo("legal", state)


__all__ = ["nodo_legal"]
