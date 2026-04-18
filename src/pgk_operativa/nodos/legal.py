"""Nodo tecnico: pgk.legal.

Derecho civil, mercantil y procesal espanol (LEC, LO 1/2025, MASC, LGT,
jurisprudencia TS, SAN, TSJ). Preparacion de escritos, analisis de
expedientes sancionadores, asesoramiento juridico para el despacho.

Alcance actual (Paso 5, Semana 3):
- Ejecutor con prompt especializado.
- Helpers deterministas de post-procesado:
  - `analisis_legal_basico`: dict de fallback si el LLM falla.
  - `extraer_fuentes_legales`: referencias a Ley, BOE, RD, Codigo Civil,
    LEC, LGT, STS, STSJ, STC, etc.
- `nodo_legal` enriquece la salida con `fuentes_citadas` (clave uniforme
    entre modulos fiscal/contable/legal).

Origen (auditoria hacia atras):
PGK_Empresa_Autonoma/src/agents/nodos.py, funciones:
- `_analisis_legal_basico` (linea 3534)
- `_extraer_fuentes_legales` (linea 3550)

En fases posteriores se anadira verificacion ECLI (CENDOJ, EUR-Lex),
integracion con la skill de verificacion juridica documental, y
plantillas de escritos procesales.
"""

from __future__ import annotations

from pgk_operativa.nodos._base import ejecutar_modulo

_PATRONES_FUENTES_LEGAL: tuple[str, ...] = (
    "Ley",
    "BOE",
    "Real Decreto",
    "RD ",
    "Articulo",
    "Artículo",
    "Art.",
    "STS",
    "STSJ",
    "STC",
    "Sentencia",
    "Codigo Civil",
    "Código Civil",
    "LEC",
    "LJCA",
    "LPAC",
    "CC",
    "CCom",
)


def analisis_legal_basico(cliente_nif: str, tipo_caso: str, mensaje: str) -> dict[str, object]:
    """Analisis legal basico sin LLM (fallback).

    `mensaje` se conserva en la firma para poder enriquecer el fallback
    con contexto del expediente en fases posteriores.
    """
    _ = mensaje
    return {
        "cliente_identificado": cliente_nif,
        "tipo_caso": tipo_caso,
        "analisis_legal": "Análisis legal pendiente de revisión por abogado colegiado.",
        "fuentes_citadas": [
            "Código Civil (RD 24 julio 1889)",
            "Ley 1/2000 (LEC)",
            "Ley 39/2015 (LPAC)",
        ],
        "confianza": 0.5,
        "had_consensus": False,
    }


def extraer_fuentes_legales(respuesta: str) -> list[str]:
    """Extrae referencias normativas y jurisprudenciales.

    Cubre patrones tipicos: Ley, BOE, articulos, sentencias (STS, STSJ,
    STC), codigos sustantivos (CC, CCom) y procesales (LEC, LJCA, LPAC).
    """
    fuentes: list[str] = []
    for linea in respuesta.split("\n"):
        for patron in _PATRONES_FUENTES_LEGAL:
            if patron in linea:
                fuentes.append(linea.strip()[:100])
                break
    return list(dict.fromkeys(fuentes))[:5]


def nodo_legal(state: dict[str, object]) -> dict[str, object]:
    """Nodo LangGraph para consultas legales.

    Invoca el ejecutor generico y enriquece la salida con referencias
    normativas y jurisprudenciales detectadas en la respuesta.
    """
    resultado = ejecutar_modulo("legal", state)
    respuesta = str(resultado.get("respuesta_tecnica", ""))
    resultado["fuentes_citadas"] = extraer_fuentes_legales(respuesta)
    return resultado


__all__ = [
    "analisis_legal_basico",
    "extraer_fuentes_legales",
    "nodo_legal",
]
