"""Nodo tecnico: pgk.marketing.

Marketing B2B para despacho fiscal (SEO, contenido, captacion,
LinkedIn, casos de exito, buyer personas). Adaptado al publico
polaco-espanol cuando procede.

Alcance actual (Paso 5, Semana 3):
- Ejecutor con prompt especializado (Ana en modo Mark).
- Sin helpers portables en esta fase: el `nodo_mark` original delega
  a `.mark_agent.consultar_mark` con PersonaBlend, que no esta portado
  a pgk_operativa. Se deja como thin wrapper hasta Fase 4 (migrar el
  mark_agent o su equivalente ligero).

Origen (auditoria hacia atras):
PGK_Empresa_Autonoma/src/agents/nodos.py, `nodo_mark` (linea 2220).
Relacion: inspirado (solo prompt + shell).

En fases posteriores se anadira generacion de casos de exito,
analisis de buyer personas, y auditoria SEO on-page.
"""

from __future__ import annotations

from pgk_operativa.nodos._base import ejecutar_modulo


def nodo_marketing(state: dict[str, object]) -> dict[str, object]:
    """Nodo LangGraph para consultas de marketing y SEO.

    Thin wrapper sobre el ejecutor generico. En fases posteriores se
    enriquecera con PersonaBlend, analisis SEO, y banco de plantillas
    de contenido.
    """
    return ejecutar_modulo("marketing", state)


__all__ = ["nodo_marketing"]
