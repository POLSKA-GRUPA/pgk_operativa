"""Nodo tecnico: pgk.docs.

Redaccion de borradores de comunicacion profesional (emails, cartas,
informes, plantillas, traducciones ES/PL). Los emails se entregan
SIEMPRE como borrador, nunca enviados directamente.

Alcance actual (Paso 5, Semana 3):
- Ejecutor con prompt especializado (Ana en modo Paloma).
- Sin helpers portables en esta fase: el `nodo_paloma` original depende
  de integraciones no migrables ahora mismo (PalomaEmailSystem,
  PgkDatabase, Drive, StateManager, rollback). Se deja como thin
  wrapper hasta Fase 4 (Paso 11) donde se portan las integraciones.

Origen (auditoria hacia atras):
PGK_Empresa_Autonoma/src/agents/nodos.py, `nodo_paloma` (linea 1304).
Relacion: inspirado (no copia literal, solo prompt + shell).

En fases posteriores se anadira generacion de borradores de email
(cuentas info/admin/klient/biznes), generacion de PDF via formateador
oficial, organizacion de expedientes en Drive.
"""

from __future__ import annotations

from pgk_operativa.nodos._base import ejecutar_modulo


def nodo_docs(state: dict[str, object]) -> dict[str, object]:
    """Nodo LangGraph para redaccion documental.

    Thin wrapper sobre el ejecutor generico. En Fase 4 se enriquecera
    con integraciones de email, Drive y plantillas.
    """
    return ejecutar_modulo("docs", state)


__all__ = ["nodo_docs"]
