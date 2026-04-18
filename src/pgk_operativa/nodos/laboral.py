"""Nodo tecnico: pgk.laboral.

Derecho laboral y Seguridad Social en Espana (cotizaciones 2026,
convenios colectivos, nominas, contratos, altas/bajas, IRPF
autonomico). Motor determinista previsto via pgk-laboral-desk en
Fase 4.

Alcance actual (Paso 5, Semana 3):
- Ejecutor con prompt especializado.
- Sin helpers portables en esta fase: el nodo laboral en origen
  PGK_Empresa_Autonoma no existia (laboral se resolvia via chat
  conversacional o fiscal). Aqui se trata como modulo tecnico
  independiente preparado para integrar pgk-laboral-desk.

Origen (auditoria hacia atras):
Modulo nuevo. No hay funcion `nodo_laboral` en origen. Relacion:
nuevo (prompt inspirado en el scope de pgk-laboral-desk).

En fases posteriores se anadira adapter HTTP al motor laboral
(calculadora SS 2026, IRPF por CCAA, convenios BOE), y helpers
deterministas de nominas.
"""

from __future__ import annotations

from pgk_operativa.nodos._base import ejecutar_modulo


def nodo_laboral(state: dict[str, object]) -> dict[str, object]:
    """Nodo LangGraph para consultas laborales y de Seguridad Social.

    Thin wrapper sobre el ejecutor generico. En fases posteriores se
    enriquecera con el motor determinista pgk-laboral-desk via HTTP.
    """
    return ejecutar_modulo("laboral", state)


__all__ = ["nodo_laboral"]
