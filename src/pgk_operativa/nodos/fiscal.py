"""Nodo tecnico: pgk.fiscal.

Materia fiscal espanola (AEAT, modelos 210/303/130/111/390, IRPF, IVA,
IRNR, retenciones, convenios de doble imposicion). Clientes
predominantemente no residentes polacos en Espana.

Semana 2: ejecutor con prompt especializado. En fases posteriores se
anadiran tools deterministas (calendario AEAT, calculadora IRNR),
RAG sobre KB normativa, y verificacion Perplexity.
"""

from __future__ import annotations

from pgk_operativa.nodos._base import ejecutar_modulo


def nodo_fiscal(state: dict[str, object]) -> dict[str, object]:
    """Nodo LangGraph para consultas fiscales."""
    return ejecutar_modulo("fiscal", state)


__all__ = ["nodo_fiscal"]
