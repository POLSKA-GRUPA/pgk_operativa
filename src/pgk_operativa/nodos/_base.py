"""Base comun para nodos tecnicos.

Extrae la logica compartida del ejecutor generico para que cada modulo
tecnico (fiscal, contable, laboral, legal, docs, marketing, calidad,
general) pueda reutilizarla. En fases posteriores cada modulo sobreescribira
o extendera esta logica con tools, RAG, motores deterministas, etc.
"""

from __future__ import annotations

from datetime import UTC, datetime

from pgk_operativa.core.llm import build_openai_client
from pgk_operativa.nodos.prompts import build_system_prompt


def _invocar_llm(system_prompt: str, mensaje_usuario: str) -> str:
    """Llamada unica a Z.ai GLM-4.6 via OpenAI SDK.

    GLM-4.6 es un modelo de razonamiento: consume tokens en
    `reasoning_content` antes de emitir `content`. Si `max_tokens` es
    bajo, el razonamiento ocupa todo el presupuesto y `content` queda
    vacio. Usamos un techo amplio para dejar espacio al razonamiento y
    a la respuesta final.
    """
    client, model = build_openai_client()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": mensaje_usuario},
        ],
        temperature=0.2,
        max_tokens=4096,
    )
    content = (resp.choices[0].message.content or "").strip()
    if content:
        return content
    reasoning = getattr(resp.choices[0].message, "reasoning_content", None) or ""
    reasoning = reasoning.strip()
    if reasoning:
        return (
            "No he podido redactar una respuesta final dentro del limite de tokens. "
            "Reintenta el mensaje o pide que lo resuma."
        )
    return "(respuesta vacia)"


def ejecutar_modulo(modulo: str, state: dict[str, object]) -> dict[str, object]:
    """Ejecuta la consulta usando el prompt del modulo tecnico indicado.

    Logica comun a todos los nodos. Cada modulo la invoca con su nombre.
    En fases posteriores los modulos podran sobreescribir esta funcion
    para anadir logica propia (tools, RAG, motores deterministas).
    """
    mensaje = str(state.get("mensaje_usuario", ""))
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


__all__ = ["ejecutar_modulo"]
