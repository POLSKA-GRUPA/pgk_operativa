"""Nodo tecnico: pgk.fiscal.

Materia fiscal espanola (AEAT, modelos 210/303/130/111/390, IRPF, IVA,
IRNR, retenciones, convenios de doble imposicion). Clientes
predominantemente no residentes polacos en Espana.

Alcance actual (Paso 5, Semana 3):
- Ejecutor con prompt especializado (Z.ai GLM-4.6 via OpenAI SDK).
- Helpers deterministas de post-procesado de la respuesta LLM:
  - `analisis_fiscal_basico`: dict de fallback si el LLM falla.
  - `extraer_fuentes`: extrae referencias normativas (BOE, Ley, RD, etc.).
  - `extraer_recomendaciones`: extrae recomendaciones accionables.
- `nodo_fiscal` enriquece la salida con `fuentes_citadas` y `recomendaciones`.

Origen (para auditoria hacia atras):
PGK_Empresa_Autonoma/src/agents/nodos.py, funciones:
- `_analisis_fiscal_basico` (linea 1240)
- `_extraer_fuentes_de_respuesta` (linea 1260)
- `_extraer_recomendaciones` (linea 1283)

En fases posteriores se anadiran tools deterministas (calendario AEAT,
calculadora IRNR, adapter conta-pgk-hispania), RAG sobre KB normativa,
y verificacion Perplexity.
"""

from __future__ import annotations

from pgk_operativa.nodos._base import ejecutar_modulo

_PATRONES_FUENTES_FISCAL: tuple[str, ...] = (
    "Ley",
    "BOE",
    "Real Decreto",
    "RD ",
    "Articulo",
    "Artículo",
    "Art.",
    "Convenio",
    "Modelo 210",
    "IRNR",
)

_KEYWORDS_RECOMENDACIONES: tuple[str, ...] = (
    "recomend",
    "suger",
    "aconsej",
    "debe",
    "importante",
)


def analisis_fiscal_basico(cliente_nif: str, tipo_caso: str) -> dict[str, object]:
    """Analisis fiscal basico sin LLM (fallback).

    Se usa cuando el LLM falla o el caso entra en modo degradado. Devuelve
    una estructura canonica que otros nodos pueden consumir sin tener que
    comprobar si la respuesta vino del modelo o del fallback.
    """
    return {
        "cliente_identificado": cliente_nif,
        "tipo_caso": tipo_caso,
        "analisis_fiscal": "Análisis fiscal pendiente de revisión por experto.",
        "fuentes_citadas": [
            "BOE-A-2023-1234",
            "Guía IRNR 2024 (Hacienda)",
        ],
        "confianza": 0.5,
        "routing_decision": "fallback",
        "had_consensus": False,
        "recomendaciones": [
            "Revisar documentación del cliente",
            "Consultar normativa aplicable",
        ],
    }


def extraer_fuentes(respuesta: str) -> list[str]:
    """Extrae referencias normativas (BOE, Ley, RD, articulos) de la respuesta LLM.

    Barre linea a linea y guarda la primera linea que contenga uno de los
    patrones. Deduplica y limita a 5 fuentes para no saturar el estado.
    """
    fuentes: list[str] = []
    for linea in respuesta.split("\n"):
        for patron in _PATRONES_FUENTES_FISCAL:
            if patron in linea:
                fuentes.append(linea.strip()[:100])
                break
    return list(dict.fromkeys(fuentes))[:5]


def extraer_recomendaciones(respuesta: str) -> list[str]:
    """Extrae frases que parezcan recomendaciones accionables.

    Busca keywords tipicas (recomiendo, debe, importante, aconsejo) y
    devuelve hasta 5 frases. Si no encuentra nada, devuelve un placeholder
    seguro pidiendo revision humana.
    """
    recomendaciones: list[str] = []
    for linea in respuesta.split("\n"):
        linea_lower = linea.lower()
        if any(kw in linea_lower for kw in _KEYWORDS_RECOMENDACIONES):
            recomendaciones.append(linea.strip()[:200])
    if not recomendaciones:
        return ["Consultar con experto fiscal"]
    return recomendaciones[:5]


def nodo_fiscal(state: dict[str, object]) -> dict[str, object]:
    """Nodo LangGraph para consultas fiscales.

    Invoca el ejecutor generico y enriquece la salida con parsing
    determinista de la respuesta: fuentes citadas y recomendaciones.
    """
    resultado = ejecutar_modulo("fiscal", state)
    respuesta = str(resultado.get("respuesta_tecnica", ""))
    resultado["fuentes_citadas"] = extraer_fuentes(respuesta)
    resultado["recomendaciones"] = extraer_recomendaciones(respuesta)
    return resultado


__all__ = [
    "analisis_fiscal_basico",
    "extraer_fuentes",
    "extraer_recomendaciones",
    "nodo_fiscal",
]
