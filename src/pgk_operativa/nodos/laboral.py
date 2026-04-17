"""Nodo tecnico: pgk.laboral.

Derecho laboral y Seguridad Social en Espana (cotizaciones, convenios
colectivos, nominas, contratos, altas/bajas, IRPF autonomico).

Semana 2: ejecutor con prompt especializado. En fases posteriores se
anadira el motor laboral determinista (pgk-laboral-engine como paquete
Python), SILTRA integration, y calculadora de cotizaciones.
"""

from __future__ import annotations

from pgk_operativa.nodos._base import ejecutar_modulo


def nodo_laboral(state: dict[str, object]) -> dict[str, object]:
    """Nodo LangGraph para consultas laborales."""
    return ejecutar_modulo("laboral", state)


__all__ = ["nodo_laboral"]
