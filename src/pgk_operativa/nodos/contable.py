"""Nodo tecnico: pgk.contable.

Contabilidad espanola (PGC 2008, asientos dobles, modelos 303/130/111/390,
libros oficiales). Clientes principales: autonomos EDS y pymes.

Alcance actual (Paso 5, Semana 3):
- Ejecutor con prompt especializado.
- Helpers deterministas de post-procesado:
  - `analisis_contable_basico`: dict de fallback si el LLM falla.
  - `extraer_fuentes`: referencias PGC, ICAC, NRV, Ley.
  - `extraer_asientos`: lineas con cuenta/importe (debe/haber).
  - `extraer_modelos`: modelos AEAT mencionados (303, 130, 111, etc.).
  - `extraer_pasos_aon`: pasos de navegacion en AON Solutions.
- `nodo_contable` enriquece la salida con estos campos.

Origen (auditoria hacia atras):
PGK_Empresa_Autonoma/src/agents/nodos.py, funciones:
- `_analisis_contable_basico` (linea 2748)
- `_extraer_fuentes_edu` (linea 2770)
- `_extraer_asientos` (linea 2797)
- `_extraer_modelos` (linea 2810)
- `_extraer_pasos_aon` (linea 2825)

En fases posteriores se anadira adapter HTTP a conta-pgk-hispania
(Paso 12), integracion con AON Solutions, y RAG sobre el PGC.
"""

from __future__ import annotations

from pgk_operativa.nodos._base import ejecutar_modulo

_PATRONES_FUENTES_CONTABLE: tuple[str, ...] = (
    "Ley",
    "BOE",
    "Real Decreto",
    "RD ",
    "Articulo",
    "Artículo",
    "Art.",
    "PGC",
    "ICAC",
    "AEAT",
    "Modelo",
    "NRV",
    "Resolucion",
    "Resolución",
)

_KEYWORDS_ASIENTOS: tuple[str, ...] = ("debe", "haber", "cuenta", "asiento")

_MODELOS_AEAT: tuple[str, ...] = (
    "303",
    "130",
    "131",
    "210",
    "200",
    "202",
    "349",
    "390",
    "100",
    "111",
    "115",
    "347",
)

_KEYWORDS_AON: tuple[str, ...] = (
    "aon",
    "menu",
    "menú",
    "contabilidad",
    "fiscal",
    "paso",
)


def analisis_contable_basico(cliente_nif: str, tipo_caso: str, mensaje: str) -> dict[str, object]:
    """Analisis contable basico sin LLM (fallback).

    Devuelve estructura canonica con fuentes PGC/IVA/IRPF y placeholders
    de asientos y modelos. `mensaje` se conserva en la firma para poder
    enriquecer el fallback con contexto del usuario en fases posteriores.
    """
    _ = mensaje  # reservado para enriquecimiento futuro
    return {
        "cliente_identificado": cliente_nif,
        "tipo_caso": tipo_caso,
        "analisis_contable": "Análisis contable pendiente de revisión por experto.",
        "fuentes_citadas": [
            "RD 1514/2007 (Plan General Contable)",
            "Ley 37/1992 (IVA)",
            "Ley 35/2006 (IRPF)",
        ],
        "asientos_generados": [],
        "modelos_calculados": [],
        "confianza": 0.5,
        "had_consensus": False,
        "recomendaciones_aon": [
            "Verificar datos en AON Solutions",
            "Consultar con experto contable",
        ],
    }


def extraer_fuentes(respuesta: str) -> list[str]:
    """Extrae referencias PGC, ICAC, NRV, Ley, RD de la respuesta contable."""
    fuentes: list[str] = []
    for linea in respuesta.split("\n"):
        for patron in _PATRONES_FUENTES_CONTABLE:
            if patron in linea:
                fuentes.append(linea.strip()[:100])
                break
    return list(dict.fromkeys(fuentes))[:5]


def extraer_asientos(respuesta: str) -> list[str]:
    """Extrae lineas que parecen asientos contables (debe/haber con digitos).

    Filtro conservador: la linea debe contener keyword de asiento y al
    menos un digito. Limitado a 10 para no saturar el estado.
    """
    asientos: list[str] = []
    for linea in respuesta.split("\n"):
        linea_lower = linea.lower()
        if any(kw in linea_lower for kw in _KEYWORDS_ASIENTOS) and any(
            ch.isdigit() for ch in linea
        ):
            asientos.append(linea.strip()[:150])
    return asientos[:10]


def extraer_modelos(respuesta: str) -> list[str]:
    """Extrae modelos AEAT mencionados (303, 130, 111, etc.).

    Busca patrones `modelo NNN` y `mod. NNN` en minusculas. Devuelve
    lista unica en el orden original de aparicion.
    """
    lower = respuesta.lower()
    encontrados: list[str] = []
    for modelo in _MODELOS_AEAT:
        if f"modelo {modelo}" in lower or f"mod. {modelo}" in lower:
            encontrados.append(modelo)
    return list(dict.fromkeys(encontrados))


def extraer_pasos_aon(respuesta: str) -> list[str]:
    """Extrae pasos de navegacion en AON Solutions.

    Busca keywords tipicas (AON, menu, paso, contabilidad, fiscal).
    Si no encuentra nada, devuelve un placeholder seguro.
    """
    pasos: list[str] = []
    for linea in respuesta.split("\n"):
        linea_lower = linea.lower()
        if any(kw in linea_lower for kw in _KEYWORDS_AON):
            pasos.append(linea.strip()[:200])
    if not pasos:
        return ["Consultar manual AON Solutions"]
    return pasos[:5]


def nodo_contable(state: dict[str, object]) -> dict[str, object]:
    """Nodo LangGraph para consultas contables.

    Invoca el ejecutor generico y enriquece la salida con fuentes,
    asientos, modelos AEAT y pasos AON detectados en la respuesta.
    """
    resultado = ejecutar_modulo("contable", state)
    respuesta = str(resultado.get("respuesta_tecnica", ""))
    resultado["fuentes_citadas"] = extraer_fuentes(respuesta)
    resultado["asientos_detectados"] = extraer_asientos(respuesta)
    resultado["modelos_detectados"] = extraer_modelos(respuesta)
    resultado["pasos_aon"] = extraer_pasos_aon(respuesta)
    return resultado


__all__ = [
    "analisis_contable_basico",
    "extraer_asientos",
    "extraer_fuentes",
    "extraer_modelos",
    "extraer_pasos_aon",
    "nodo_contable",
]
