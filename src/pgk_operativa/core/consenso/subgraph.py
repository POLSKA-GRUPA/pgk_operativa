"""Subgraph LangGraph de consenso multi-proveedor (C.1).

Topologia:

    START -> verificar_providers -> llamar_perspectivas -> calcular_acuerdo
          -> decidir -> [sintesis | siguiente_ronda] -> END

Opt-in: solo se invoca cuando `consenso_activo=True` en el estado del
grafo padre. Si el circuit breaker esta abierto o no hay 2 proveedores,
degrada a single-model con aviso.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import cast

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from pgk_operativa.core.consenso.agreement import calcular_acuerdo, decidir_siguiente_paso
from pgk_operativa.core.consenso.circuit_breaker import get_breaker
from pgk_operativa.core.consenso.state import ConsensoState
from pgk_operativa.core.llm import build_openai_client, pick_consensus_pair

MAX_ROUNDS = 3


def _nodo_verificar_providers(state: ConsensoState) -> dict[str, object]:
    """C.2: Verifica que hay 2 proveedores distintos disponibles."""
    breaker = get_breaker()
    if breaker.abierto:
        return {
            "consensus_type": "degraded",
            "aborted": True,
            "abort_reason": "circuit_breaker_abierto",
            "audit_trail": [
                {
                    "nodo": "verificar_providers",
                    "evento": "circuit_breaker_abierto",
                    "estado_breaker": breaker.estado(),
                }
            ],
        }

    pair = pick_consensus_pair()
    if pair is None:
        return {
            "consensus_type": "single_model",
            "aborted": False,
            "abort_reason": "menos_de_2_proveedores",
            "providers": [],
            "audit_trail": [
                {
                    "nodo": "verificar_providers",
                    "evento": "single_model_fallback",
                    "razon": "No hay 2 proveedores con API key configurada.",
                }
            ],
        }

    cfg_a, cfg_b = pair
    providers = [
        {"provider": cfg_a.provider.value, "model": cfg_a.model, "api_key_env": cfg_a.api_key_env},
        {"provider": cfg_b.provider.value, "model": cfg_b.model, "api_key_env": cfg_b.api_key_env},
    ]
    return {
        "consensus_type": "multi_provider",
        "providers": providers,
        "round": 1,
        "aborted": False,
        "abort_reason": None,
        "total_cost_usd": 0.0,
        "total_tokens": 0,
        "audit_trail": [
            {
                "nodo": "verificar_providers",
                "evento": "multi_provider_ok",
                "providers": [p["provider"] for p in providers],
            }
        ],
    }


def _nodo_llamar_perspectivas(state: ConsensoState) -> dict[str, object]:
    """C.3: Llama a ambos proveedores (secuencial en Semana 2, async en Semana 3)."""
    consensus_type = state.get("consensus_type", "single_model")
    if consensus_type != "multi_provider":
        # Single-model fallback: usar solo Z.ai
        query = str(state.get("query", ""))
        context = str(state.get("context", ""))
        try:
            client, model = build_openai_client()
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": query},
                ],
                temperature=0.2,
                max_tokens=4096,
            )
            text = (resp.choices[0].message.content or "").strip()
        except Exception as exc:
            text = f"(error single-model: {type(exc).__name__})"
            get_breaker().registrar_fallo()

        return {
            "perspectiva_a": {"text": text, "tokens": 0, "cost_usd": 0.0, "latency_ms": 0},
            "perspectiva_b": {"text": "", "tokens": 0, "cost_usd": 0.0, "latency_ms": 0},
            "respuesta_sintetizada": text,
            "audit_trail": [
                {
                    "nodo": "llamar_perspectivas",
                    "evento": "single_model_call",
                    "consensus_type": consensus_type,
                }
            ],
        }

    # Multi-provider: llamar a ambos (secuencial en Semana 2).
    query = str(state.get("query", ""))
    context = str(state.get("context", ""))
    ronda = state.get("round", 1)
    providers = state.get("providers", [])

    resultados: list[dict[str, object]] = []
    for prov in providers[:2]:
        try:
            client, model = build_openai_client(prov.get("model"))
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": query},
                ],
                temperature=0.3,
                max_tokens=4096,
            )
            text = (resp.choices[0].message.content or "").strip()
            resultados.append({"text": text, "tokens": 0, "cost_usd": 0.0, "latency_ms": 0})
        except Exception as exc:
            resultados.append(
                {
                    "text": f"(error: {type(exc).__name__})",
                    "tokens": 0,
                    "cost_usd": 0.0,
                    "latency_ms": 0,
                }
            )
            get_breaker().registrar_fallo()

    persp_a = (
        resultados[0]
        if len(resultados) > 0
        else {"text": "", "tokens": 0, "cost_usd": 0.0, "latency_ms": 0}
    )
    persp_b = (
        resultados[1]
        if len(resultados) > 1
        else {"text": "", "tokens": 0, "cost_usd": 0.0, "latency_ms": 0}
    )

    return {
        "perspectiva_a": persp_a,
        "perspectiva_b": persp_b,
        "audit_trail": [
            {
                "nodo": "llamar_perspectivas",
                "evento": "multi_provider_call",
                "round": ronda,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ],
    }


def _nodo_calcular_acuerdo(state: ConsensoState) -> dict[str, object]:
    """C.4: Calcula acuerdo sintactico + semantico."""
    text_a = str((state.get("perspectiva_a") or {}).get("text", ""))
    text_b = str((state.get("perspectiva_b") or {}).get("text", ""))

    if not text_a or not text_b:
        return {
            "agreement_sintactico": 0.0,
            "agreement_semantico": 0.0,
            "audit_trail": [
                {
                    "nodo": "calcular_acuerdo",
                    "evento": "perspectiva_vacia",
                }
            ],
        }

    sint, sem = calcular_acuerdo(text_a, text_b)
    decision = decidir_siguiente_paso(sint, sem)

    return {
        "agreement_sintactico": sint,
        "agreement_semantico": sem,
        "audit_trail": [
            {
                "nodo": "calcular_acuerdo",
                "evento": "acuerdo_calculado",
                "agreement_sintactico": round(sint, 4),
                "agreement_semantico": round(sem, 4),
                "decision": decision,
                "round": state.get("round", 1),
            }
        ],
    }


def _route_after_acuerdo(state: ConsensoState) -> str:
    """Decide si sintetizar, continuar o forzar otra ronda."""
    consensus_type = state.get("consensus_type", "single_model")
    if consensus_type != "multi_provider":
        return "sintesis"

    sint = state.get("agreement_sintactico", 0.0)
    sem = state.get("agreement_semantico", 0.0)
    ronda = state.get("round", 1)

    decision = decidir_siguiente_paso(sint, sem)
    if decision == "early_exit" or ronda >= MAX_ROUNDS:
        return "sintesis"
    return "siguiente_ronda"


def _nodo_siguiente_ronda(state: ConsensoState) -> dict[str, object]:
    """Incrementa contador de ronda para la siguiente iteracion."""
    ronda_actual = state.get("round", 1)
    return {
        "round": ronda_actual + 1,
        "audit_trail": [
            {
                "nodo": "siguiente_ronda",
                "evento": "nueva_ronda",
                "round": ronda_actual + 1,
            }
        ],
    }


def _nodo_sintesis(state: ConsensoState) -> dict[str, object]:
    """Sintetiza la respuesta final del consenso.

    En Semana 2: concatena/selecciona la mejor perspectiva.
    En fases posteriores: arbitro LLM con criticas estructuradas (C.6).
    """
    consensus_type = state.get("consensus_type", "single_model")
    text_a = str((state.get("perspectiva_a") or {}).get("text", ""))
    text_b = str((state.get("perspectiva_b") or {}).get("text", ""))
    sint = state.get("agreement_sintactico", 0.0)
    sem = state.get("agreement_semantico", 0.0)

    breaker = get_breaker()

    if consensus_type != "multi_provider" or not text_b:
        respuesta = text_a or "(sin respuesta)"
        breaker.registrar_exito()
        return {
            "respuesta_sintetizada": respuesta,
            "audit_trail": [
                {
                    "nodo": "sintesis",
                    "evento": "single_model_passthrough",
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            ],
        }

    # Sintesis stub Semana 2: elegir mejor perspectiva o combinar.
    # En fases posteriores un arbitro LLM hara la sintesis real.
    if sint > 0.7 and sem > 0.8:
        # Alta concordancia: usar perspectiva A (suele ser Z.ai, mejor español)
        respuesta = text_a
        metodo = "high_agreement_select_a"
    elif len(text_a) >= len(text_b):
        respuesta = text_a
        metodo = "select_longer_a"
    else:
        respuesta = text_b
        metodo = "select_longer_b"

    breaker.registrar_exito()

    return {
        "respuesta_sintetizada": respuesta,
        "audit_trail": [
            {
                "nodo": "sintesis",
                "evento": "sintesis_completada",
                "metodo": metodo,
                "agreement_sintactico": round(sint, 4),
                "agreement_semantico": round(sem, 4),
                "consensus_type": consensus_type,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ],
    }


def build_consenso_subgraph() -> CompiledStateGraph:
    """Construye y compila el subgraph de consenso."""
    builder = StateGraph(ConsensoState)

    builder.add_node("verificar_providers", _nodo_verificar_providers)
    builder.add_node("llamar_perspectivas", _nodo_llamar_perspectivas)
    builder.add_node("calcular_acuerdo", _nodo_calcular_acuerdo)
    builder.add_node("siguiente_ronda", _nodo_siguiente_ronda)
    builder.add_node("sintesis", _nodo_sintesis)

    builder.add_edge(START, "verificar_providers")
    builder.add_edge("verificar_providers", "llamar_perspectivas")
    builder.add_edge("llamar_perspectivas", "calcular_acuerdo")
    builder.add_conditional_edges(
        "calcular_acuerdo",
        _route_after_acuerdo,
        {"sintesis": "sintesis", "siguiente_ronda": "siguiente_ronda"},
    )
    builder.add_edge("siguiente_ronda", "llamar_perspectivas")
    builder.add_edge("sintesis", END)

    return builder.compile()


def run_consenso(
    query: str,
    context: str = "",
) -> ConsensoState:
    """Ejecuta el subgraph de consenso. Devuelve el estado final."""
    graph = build_consenso_subgraph()
    initial: ConsensoState = {
        "query": query,
        "context": context,
        "providers": [],
        "perspectiva_a": {},
        "perspectiva_b": {},
        "round": 0,
        "agreement_sintactico": 0.0,
        "agreement_semantico": 0.0,
        "critiques": [],
        "controversias": [],
        "verifications_pending": [],
        "consensus_type": "single_model",
        "aborted": False,
        "abort_reason": None,
        "total_cost_usd": 0.0,
        "total_tokens": 0,
        "respuesta_sintetizada": "",
        "audit_trail": [],
    }
    result = graph.invoke(initial)
    return cast(ConsensoState, result)


__all__ = ["build_consenso_subgraph", "run_consenso"]
