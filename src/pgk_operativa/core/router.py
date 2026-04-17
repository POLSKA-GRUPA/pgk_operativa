"""Router Ana: clasifica la intencion del mensaje y asigna modulo tecnico.

Ana es la unica cara visible. El empleado nunca sabe si detras responde
fiscal, contable, laboral, legal, docs o marketing. El router decide en
silencio y el nodo correspondiente ejecuta.

Clasificacion primaria por keywords deterministas (rapido, gratis,
trazable). Si el mensaje es ambiguo, se delega a Z.ai para desempate.
"""

from __future__ import annotations

import re
import unicodedata
from typing import get_args

from pgk_operativa.core.graph_state import AnaState, ModuloTecnico
from pgk_operativa.core.llm import build_openai_client

_VALID_MODULES: tuple[str, ...] = get_args(ModuloTecnico)

_KEYWORDS: dict[str, list[str]] = {
    "fiscal": [
        "irnr",
        "modelo 210",
        "modelo 100",
        "modelo 303",
        "modelo 130",
        "modelo 111",
        "modelo 115",
        "modelo 390",
        "modelo 347",
        "hacienda",
        "aeat",
        "irpf",
        "iva",
        "declaracion",
        "trimestre",
        "autoliquidacion",
        "retencion",
        "no residente",
        "convenio doble",
        "dividendo",
        "plusvalia",
        "ganancia patrimonial",
    ],
    "contable": [
        "asiento",
        "libro diario",
        "contabilidad",
        "pgc",
        "balance",
        "cuenta de resultados",
        "amortizacion",
        "factura emitida",
        "factura recibida",
        "conciliacion bancaria",
        "mayor",
        "acreedor",
        "deudor",
        "cierre contable",
    ],
    "laboral": [
        "nomina",
        "seguridad social",
        "iberley",
        "contrato laboral",
        "alta empleado",
        "baja empleado",
        "finiquito",
        "despido",
        "cotizacion",
        "irpf laboral",
        "convenio colectivo",
        "reta",
        "autonomo cuota",
        "siltra",
    ],
    "legal": [
        "sentencia",
        "recurso",
        "alegaciones",
        "procedimiento",
        "demanda",
        "contrato",
        "escritura",
        "poder notarial",
        "juzgado",
        "lo 1/2025",
        "masc",
        "jurisprudencia",
        "ts",
        "audiencia nacional",
        "tsj",
    ],
    "docs": [
        "borrador",
        "email",
        "plantilla",
        "redacta",
        "traduce",
        "traduccion",
        "comunicacion cliente",
        "carta",
        "informe cliente",
    ],
    "marketing": [
        "seo",
        "campana",
        "contenido",
        "linkedin",
        "instagram",
        "tiktok",
        "ads",
        "google ads",
        "keyword",
        "buyer persona",
        "landing",
        "copywriting",
    ],
}


def _normalize(texto: str) -> str:
    """Normaliza a minusculas y elimina diacriticos.

    El texto del empleado llega con tildes ("declaracion", "nomina",
    "cotizacion"). Los keywords estan sin tildes. Sin normalizar,
    re.search no matchea porque lower() preserva acentos. Normalizamos
    ambos lados para que el matching sea robusto.
    """
    nfkd = unicodedata.normalize("NFKD", texto.lower())
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def _keyword_matches(texto: str, kw: str) -> bool:
    """Coincidencia segura de keyword.

    - Keywords de una sola palabra: word boundaries (evita falsos positivos
      como "iva" dentro de "motivacion" o "contrato" dentro de "contrato
      laboral").
    - Keywords multipalabra: substring directo (ya son especificos de por si).
    """
    if " " in kw or "/" in kw:
        return kw in texto
    return re.search(rf"\b{re.escape(kw)}\b", texto) is not None


def _classify_by_keywords(mensaje: str) -> tuple[str, str] | None:
    """Clasifica por keywords. Devuelve (modulo, razon) o None si ambiguo."""
    texto = _normalize(mensaje)
    matches: dict[str, list[str]] = {}
    for modulo, kws in _KEYWORDS.items():
        hit = [kw for kw in kws if _keyword_matches(texto, kw)]
        if hit:
            matches[modulo] = hit

    if not matches:
        return None
    if len(matches) == 1:
        modulo = next(iter(matches))
        return modulo, f"keywords: {matches[modulo]}"

    ranked = sorted(matches.items(), key=lambda x: -len(x[1]))
    top, second = ranked[0], ranked[1]
    if len(top[1]) > len(second[1]):
        return top[0], f"keywords (top {len(top[1])} vs {len(second[1])}): {top[1]}"
    return None


_LLM_CLASSIFIER_PROMPT = """Eres el router de un despacho fiscal espanol. Clasifica el siguiente mensaje en UNO de estos modulos tecnicos:

- fiscal: impuestos, declaraciones, Hacienda, IRNR, IRPF, IVA, modelos AEAT
- contable: asientos, PGC, libros contables, balances, facturas en contabilidad
- laboral: nominas, Seguridad Social, contratos de trabajo, despidos, cotizaciones
- legal: derecho, sentencias, procedimientos judiciales, contratos civiles/mercantiles, escrituras
- docs: redaccion de borradores, emails, plantillas, traducciones para cliente
- marketing: SEO, campanas, contenido, redes sociales, captacion
- general: cualquier otra cosa (saludos, preguntas fuera de dominio)

Responde UNICAMENTE con una linea en formato:
MODULO: <uno de los 7>
RAZON: <10 palabras max>

Mensaje del empleado:
---
{mensaje}
---"""


def _classify_by_llm(mensaje: str) -> tuple[str, str]:
    """Usa Z.ai para clasificar mensajes ambiguos."""
    client, model = build_openai_client()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Eres un clasificador determinista."},
            {"role": "user", "content": _LLM_CLASSIFIER_PROMPT.format(mensaje=mensaje)},
        ],
        temperature=0.0,
        max_tokens=80,
    )
    content = (resp.choices[0].message.content or "").strip()

    modulo = "general"
    razon = "llm sin razon explicita"
    for line in content.splitlines():
        if line.lower().startswith("modulo:"):
            raw = line.split(":", 1)[1].strip().lower()
            tokens = raw.split()
            primero = tokens[0] if tokens else ""
            candidato = re.sub(r"[^a-z]", "", primero)
            if candidato in _VALID_MODULES:
                modulo = candidato
        elif line.lower().startswith("razon:"):
            razon = line.split(":", 1)[1].strip()[:120]

    return modulo, f"llm: {razon}"


def clasificar(mensaje: str) -> tuple[str, str]:
    """Clasifica un mensaje en un modulo tecnico.

    Primero intenta keywords (barato, determinista). Si no desempata,
    pregunta a Z.ai. Devuelve (modulo, razonamiento_corto).
    """
    por_kw = _classify_by_keywords(mensaje)
    if por_kw is not None:
        return por_kw
    return _classify_by_llm(mensaje)


def nodo_ana_router(state: AnaState) -> dict[str, object]:
    """Nodo LangGraph: Ana clasifica el mensaje y decide modulo.

    Nunca exponer el nombre del modulo al empleado. Solo ruteo interno.
    """
    mensaje = state.get("mensaje_usuario", "")
    if not mensaje:
        return {
            "modulo_tecnico": "general",
            "clasificacion_razonamiento": "mensaje vacio",
            "audit_trail": [
                {"nodo": "ana_router", "evento": "mensaje_vacio", "decision": "general"}
            ],
        }

    try:
        modulo, razon = clasificar(mensaje)
    except Exception as exc:
        # Si el LLM falla (timeout, 5xx, rate limit, red), no tiramos el grafo.
        # Ruteamos a 'general' y el ejecutor respondera de forma generica.
        return {
            "modulo_tecnico": "general",
            "clasificacion_razonamiento": (
                f"error clasificacion ({type(exc).__name__}): fallback a general"
            ),
            "audit_trail": [
                {
                    "nodo": "ana_router",
                    "evento": "clasificacion_error",
                    "error_tipo": type(exc).__name__,
                    "error_msg": str(exc)[:200],
                    "decision": "general",
                }
            ],
        }
    return {
        "modulo_tecnico": modulo,
        "clasificacion_razonamiento": razon,
        "audit_trail": [{"nodo": "ana_router", "modulo_elegido": modulo, "razon": razon}],
    }


__all__ = ["clasificar", "nodo_ana_router"]
