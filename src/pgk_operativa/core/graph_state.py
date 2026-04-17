"""Estado tipado del grafo LangGraph.

Minimal para Semana 1. Campos adicionales se anaden segun crezcan los
casos de uso (verificacion Perplexity, protocolo metodologico, consejo
de direccion, etc). Heredado y simplificado de
`PGK_Empresa_Autonoma/src/core/state.py`.
"""

from __future__ import annotations

import operator
from typing import Annotated, Literal, TypedDict

from langgraph.graph.message import add_messages


def replace_or_set(_existing: object, new: object) -> object:
    """Reducer que reemplaza el valor anterior (no acumula)."""
    return new


ModuloTecnico = Literal[
    "fiscal",
    "contable",
    "laboral",
    "legal",
    "docs",
    "marketing",
    "general",
]


class AnaState(TypedDict, total=False):
    """Estado del grafo conducido por Ana.

    Ana es la unica cara visible al empleado. Los modulos tecnicos
    (fiscal, contable, laboral, legal, docs, marketing) son invisibles
    por contrato: nunca se exponen al usuario final.
    """

    messages: Annotated[list[dict[str, str]], add_messages]

    caso_id: Annotated[str, replace_or_set]
    cliente_nif: Annotated[str | None, replace_or_set]
    cliente_nombre: Annotated[str | None, replace_or_set]

    mensaje_usuario: Annotated[str, replace_or_set]
    consenso_activo: Annotated[bool, replace_or_set]

    modulo_tecnico: Annotated[ModuloTecnico, replace_or_set]
    tipo_caso: Annotated[str, replace_or_set]
    clasificacion_razonamiento: Annotated[str, replace_or_set]

    respuesta_tecnica: Annotated[str, replace_or_set]
    respuesta_final: Annotated[str, replace_or_set]

    audit_trail: Annotated[list[dict[str, object]], operator.add]
    timestamp_inicio: Annotated[str, replace_or_set]
    timestamp_fin: Annotated[str | None, replace_or_set]


__all__ = ["AnaState", "ModuloTecnico", "replace_or_set"]
