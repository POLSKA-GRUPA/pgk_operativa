"""Estado del subgraph de consenso (C.1).

TypedDict que viaja por el subgraph. Cada nodo lee y escribe campos
especificos. El grafo padre inyecta `query`, `context` y `providers`.
"""

from __future__ import annotations

from typing import Literal, TypedDict


class ProviderSpec(TypedDict):
    """Especificacion minima de un proveedor para consenso."""

    provider: str
    model: str
    api_key_env: str


class Response(TypedDict, total=False):
    """Respuesta de un proveedor durante una ronda."""

    text: str
    tokens: int
    cost_usd: float
    latency_ms: int


class Critique(TypedDict):
    """Critica estructurada entre perspectivas (C.6)."""

    acuerdos: list[str]
    desacuerdos: list[dict[str, str]]
    verificaciones_pendientes: list[dict[str, str]]


class Controversia(TypedDict):
    """Punto de desacuerdo persistente entre rondas."""

    punto: str
    posicion_a: str
    posicion_b: str


ConsensusType = Literal["single_model", "multi_provider", "degraded"]


class ConsensoState(TypedDict, total=False):
    """Estado completo del subgraph de consenso.

    Campos obligatorios inyectados por el grafo padre:
    - query: pregunta del empleado
    - context: contexto del modulo tecnico

    Campos gestionados por los nodos del subgraph:
    - providers, perspectivas, acuerdo, criticas, etc.
    """

    query: str
    context: str
    providers: list[ProviderSpec]
    perspectiva_a: Response
    perspectiva_b: Response
    round: int
    agreement_sintactico: float
    agreement_semantico: float
    critiques: list[Critique]
    controversias: list[Controversia]
    verifications_pending: list[dict[str, str]]
    consensus_type: ConsensusType
    aborted: bool
    abort_reason: str | None
    total_cost_usd: float
    total_tokens: int
    respuesta_sintetizada: str
    audit_trail: list[dict[str, object]]


__all__ = [
    "ConsensoState",
    "ConsensusType",
    "Controversia",
    "Critique",
    "ProviderSpec",
    "Response",
]
