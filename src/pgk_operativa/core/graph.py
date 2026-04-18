"""Grafo LangGraph principal de pgk_operativa.

Topologia Semana 2 (con routing por modulo):

    START -> ana_router -> {fiscal|contable|laboral|legal|docs|marketing|calidad|general} -> END

El router Ana clasifica el mensaje y escribe `modulo_tecnico`. Luego
el grafo enruta condicionalmente al nodo del modulo correspondiente.
Cada modulo tiene su propio prompt especializado y en fases posteriores
tendra logica propia (tools, RAG, motores deterministas, etc.).
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import cast
from uuid import uuid4

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from pgk_operativa.core.graph_state import AnaState
from pgk_operativa.core.router import nodo_ana_router
from pgk_operativa.nodos.calidad import nodo_calidad
from pgk_operativa.nodos.contable import nodo_contable
from pgk_operativa.nodos.docs import nodo_docs
from pgk_operativa.nodos.ejecutor import nodo_ejecutor
from pgk_operativa.nodos.fiscal import nodo_fiscal
from pgk_operativa.nodos.laboral import nodo_laboral
from pgk_operativa.nodos.legal import nodo_legal
from pgk_operativa.nodos.marketing import nodo_marketing

_ModuleNode = Callable[[dict[str, object]], dict[str, object]]

_MODULE_NODES: dict[str, _ModuleNode] = {
    "fiscal": nodo_fiscal,
    "contable": nodo_contable,
    "laboral": nodo_laboral,
    "legal": nodo_legal,
    "docs": nodo_docs,
    "marketing": nodo_marketing,
    "calidad": nodo_calidad,
}


def _route_to_module(state: AnaState) -> str:
    """Decide el nodo destino segun el modulo tecnico asignado por Ana."""
    modulo = state.get("modulo_tecnico", "general")
    if modulo in _MODULE_NODES:
        return modulo
    return "general"


def build_graph() -> CompiledStateGraph:
    """Construye y compila el grafo con routing condicional por modulo."""
    builder = StateGraph(AnaState)

    builder.add_node("ana_router", nodo_ana_router)
    for name, node_fn in _MODULE_NODES.items():
        builder.add_node(name, node_fn)
    builder.add_node("general", nodo_ejecutor)

    builder.add_edge(START, "ana_router")
    builder.add_conditional_edges(
        "ana_router",
        _route_to_module,
        {mod: mod for mod in [*_MODULE_NODES, "general"]},
    )
    for node in [*_MODULE_NODES, "general"]:
        builder.add_edge(node, END)

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
        "fuentes_citadas": [],
        "recomendaciones": [],
        "asientos_detectados": [],
        "modelos_detectados": [],
        "pasos_aon": [],
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
