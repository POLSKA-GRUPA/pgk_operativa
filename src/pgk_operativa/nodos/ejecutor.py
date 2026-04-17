"""Ejecutor generico de nodos tecnicos.

Semana 1: todos los modulos (fiscal, contable, laboral, legal, docs,
marketing, general) comparten la misma logica de ejecucion: llaman a
Z.ai GLM-4.6 con un system prompt especifico del modulo. En fases
posteriores cada modulo crecera con su propia logica (tools, RAG,
motor determinista laboral, consejos de direccion, etc.).
"""

from __future__ import annotations

from datetime import UTC, datetime

from pgk_operativa.core.graph_state import AnaState
from pgk_operativa.core.llm import build_openai_client
from pgk_operativa.nodos.prompts import build_system_prompt


def _invocar_llm(system_prompt: str, mensaje_usuario: str) -> str:
    """Llamada unica a Z.ai GLM-4.6 via OpenAI SDK."""
    client, model = build_openai_client()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": mensaje_usuario},
        ],
        temperature=0.2,
        max_tokens=1024,
    )
    return (resp.choices[0].message.content or "").strip()


def nodo_ejecutor(state: AnaState) -> dict[str, object]:
    """Ejecuta la consulta usando el prompt del modulo tecnico asignado."""
    modulo = state.get("modulo_tecnico", "general")
    mensaje = state.get("mensaje_usuario", "")
    system_prompt = build_system_prompt(modulo)

    try:
        respuesta = _invocar_llm(system_prompt, mensaje)
        evento = {
            "nodo": f"ejecutor_{modulo}",
            "evento": "llm_respuesta_ok",
            "longitud_respuesta": len(respuesta),
        }
    except Exception as exc:
        respuesta = (
            "No he podido generar una respuesta ahora mismo. "
            "Intentalo en unos segundos o contacta con soporte. "
            f"(Error tecnico: {type(exc).__name__})"
        )
        evento = {
            "nodo": f"ejecutor_{modulo}",
            "evento": "llm_error",
            "error_tipo": type(exc).__name__,
            "error_msg": str(exc)[:200],
        }

    return {
        "respuesta_tecnica": respuesta,
        "respuesta_final": respuesta,
        "timestamp_fin": datetime.now(UTC).isoformat(),
        "audit_trail": [evento],
    }


__all__ = ["nodo_ejecutor"]
