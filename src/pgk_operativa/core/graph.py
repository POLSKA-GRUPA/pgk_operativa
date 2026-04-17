"""Grafo LangGraph principal de pgk_operativa.

Topologia Semana 1 (minimal):

    START -> ana_router -> ejecutor -> END

El router Ana clasifica el mensaje y escribe `modulo_tecnico`. El
ejecutor ramifica internamente via prompt especifico del modulo. En
fases posteriores el grafo crecera con nodos dedicados por modulo,
subgrafo de consenso opt-in, verificacion Perplexity, protocolo
metodologico, consejo de direccion, memoria operativa, etc.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import cast
from uuid import uuid4

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from pgk_operativa.core.graph_state import AnaState
from pgk_operativa.core.router import nodo_ana_router
from pgk_operativa.nodos.ejecutor import nodo_ejecutor


def build_graph() -> CompiledStateGraph:
    """Construye y compila el grafo minimo de Semana 1."""
    builder = StateGraph(AnaState)
    builder.add_node("ana_router", nodo_ana_router)
    builder.add_node("ejecutor", nodo_ejecutor)
    builder.add_edge(START, "ana_router")
    builder.add_edge("ana_router", "ejecutor")
    builder.add_edge("ejecutor", END)
    return builder.compile()


def initial_state(
    mensaje: str,
    *,
    nif: str | None = None,
    nombre: str | None = None,
    consenso: bool = False,
) -> AnaState:
    """Crea el estado inicial para una invocacion del grafo."""
    ahora = datetime.now(UTC).isoformat()
    caso_id = f"caso-{uuid4().hex[:10]}"
    return {
        "messages": [{"role": "user", "content": mensaje}],
        "caso_id": caso_id,
        "cliente_nif": nif,
        "cliente_nombre": nombre,
        "mensaje_usuario": mensaje,
        "consenso_activo": consenso,
        "modulo_tecnico": "general",
        "tipo_caso": "conversacion",
        "clasificacion_razonamiento": "",
        "respuesta_tecnica": "",
        "respuesta_final": "",
        "audit_trail": [{"nodo": "init", "evento": "caso_creado", "caso_id": caso_id}],
        "timestamp_inicio": ahora,
        "timestamp_fin": None,
    }


def run(
    mensaje: str,
    *,
    nif: str | None = None,
    nombre: str | None = None,
    consenso: bool = False,
) -> AnaState:
    """Ejecucion sincrona del grafo. Devuelve el estado final."""
    graph = build_graph()
    state = initial_state(mensaje, nif=nif, nombre=nombre, consenso=consenso)
    result = graph.invoke(state)
    return cast(AnaState, result)


__all__ = ["build_graph", "initial_state", "run"]
