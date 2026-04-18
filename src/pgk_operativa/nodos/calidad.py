"""Nodo tecnico: pgk.calidad.

Control de calidad de respuestas generadas por otros modulos. Verifica
citas normativas, detecta hedging excesivo, valida fuentes y cifras,
evalua coherencia pregunta/respuesta.

Alcance actual (Paso 5, Semana 3):
- Ejecutor con prompt especializado (Ana en modo Jennifer).
- Sin helpers portables en esta fase: el `nodo_jennifer` original es
  principalmente mantenimiento de filesystem (limpieza, rollback
  snapshots, metrics), no post-procesado de texto. Se deja como thin
  wrapper hasta que se definan checks de calidad explicitos.

Origen (auditoria hacia atras):
PGK_Empresa_Autonoma/src/agents/nodos.py, `nodo_jennifer` (linea 1858).
Relacion: inspirado (solo prompt + shell, no filesystem maintenance).

En fases posteriores se anadira quality gate con evaluador fiscal,
deteccion de alucinaciones, y sugerencia automatica de modo consenso
cuando confianza < umbral.
"""

from __future__ import annotations

from pgk_operativa.nodos._base import ejecutar_modulo


def nodo_calidad(state: dict[str, object]) -> dict[str, object]:
    """Nodo LangGraph para control de calidad.

    Thin wrapper sobre el ejecutor generico. En fases posteriores se
    enriquecera con checks deterministas (cobertura de fuentes,
    deteccion de hedging, deteccion de cifras sin fuente).
    """
    return ejecutar_modulo("calidad", state)


__all__ = ["nodo_calidad"]
