"""Ejecutor generico de nodos tecnicos.

Mantiene compatibilidad con Semana 1: se usa como nodo "general" para
mensajes que no encajan en ningun modulo tecnico especializado.

La logica compartida de ejecucion LLM esta en `_base.py`. Los modulos
especializados (fiscal, contable, laboral, legal, docs, marketing,
calidad) importan desde ahi.
"""

from __future__ import annotations

from pgk_operativa.nodos._base import ejecutar_modulo


def nodo_ejecutor(state: dict[str, object]) -> dict[str, object]:
    """Ejecuta la consulta como modulo general (fallback)."""
    modulo = str(state.get("modulo_tecnico", "general"))
    return ejecutar_modulo(modulo, state)


__all__ = ["nodo_ejecutor"]
