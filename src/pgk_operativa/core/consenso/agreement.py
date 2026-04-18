"""Calculo de acuerdo sintactico + semantico (C.4).

Dos capas:
- Sintactico: Jaccard sobre cifras y citas normativas extraidas.
- Semantico: coseno entre embeddings de conclusiones (stub en Semana 2,
  sustituido por OpenAI text-embedding-3-small en Semana 3).

Thresholds iniciales (calibrables tras 50 casos reales):
- Sintactico > 0.7 AND semantico > 0.8 -> early-exit a sintesis
- Sintactico < 0.3 OR semantico < 0.4 -> forzar R3
"""

from __future__ import annotations

import re
from typing import Literal


def extract_cifras(texto: str) -> set[str]:
    """Extrae cifras numericas significativas (porcentajes, importes, articulos)."""
    patrones = [
        r"\d+(?:[.,]\d+)?%",
        r"\d+(?:[.,]\d+)?\s*(?:EUR|USD|eur|usd)",
        r"(?:art(?:iculo)?\.?\s*)\d+(?:\.\d+)*",
        r"\b\d{2,}\b",
    ]
    cifras: set[str] = set()
    for patron in patrones:
        cifras.update(re.findall(patron, texto, re.IGNORECASE))
    return cifras


def extract_citas_normativas(texto: str) -> set[str]:
    """Extrae citas normativas (ECLI, BOE, leyes, modelos AEAT).

    Usa `re.IGNORECASE` para aceptar variantes como 'ley 35/2006' o
    'modelo 210': sin el flag, Jaccard fallaba entre proveedores que
    escribieran las normas con distinta capitalizacion.
    """
    patrones = [
        r"ECLI:ES:\w+:\d{4}:\d+",
        r"BOE-\w+-\d+(?:-\d+)*",
        r"(?:Ley|RD|RDL|Orden)\s+\d+/\d{4}",
        r"(?:modelo|Modelo)\s+\d{3}",
        r"LIRNR|LIRPF|LIVA|LGT|LIS|TRLGSS",
    ]
    citas: set[str] = set()
    for patron in patrones:
        citas.update(re.findall(patron, texto, re.IGNORECASE))
    return citas


def jaccard(a: set[str], b: set[str]) -> float:
    """Indice de Jaccard entre dos conjuntos."""
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 1.0
    return len(a & b) / len(union)


def _norm(items: set[str]) -> set[str]:
    """Normaliza tokens para comparacion Jaccard: lower() + strip + colapsa espacios.

    Sin esta normalizacion, "Modelo 210" y "modelo 210" cuentan como
    distintos en el set: dos proveedores que citan la misma norma con
    capitalizacion diferente obtenian Jaccard 0 cuando deberia ser 1.
    Igual para "1500 EUR" vs "1500 eur" y "Ley 35/2006" vs "ley 35/2006".
    """
    out: set[str] = set()
    for tok in items:
        norm = " ".join(tok.lower().split())
        if norm:
            out.add(norm)
    return out


def calcular_acuerdo(respuesta_a: str, respuesta_b: str) -> tuple[float, float]:
    """Calcula acuerdo sintactico y semantico entre dos respuestas.

    Returns:
        (acuerdo_sintactico, acuerdo_semantico).

    El acuerdo semantico en Semana 2 usa Jaccard sobre palabras clave
    como stub. En Semana 3 se sustituira por coseno de embeddings
    (OpenAI text-embedding-3-small).
    """
    cifras_a = _norm(extract_cifras(respuesta_a))
    cifras_b = _norm(extract_cifras(respuesta_b))
    citas_a = _norm(extract_citas_normativas(respuesta_a))
    citas_b = _norm(extract_citas_normativas(respuesta_b))

    cifras_overlap = jaccard(cifras_a, cifras_b)
    citas_overlap = jaccard(citas_a, citas_b)
    acuerdo_sintactico = 0.5 * cifras_overlap + 0.5 * citas_overlap

    # Stub semantico: Jaccard sobre tokens significativos (> 4 chars).
    # Sustituido por embedding cosine en fases posteriores.
    tokens_a = {w.lower() for w in respuesta_a.split() if len(w) > 4}
    tokens_b = {w.lower() for w in respuesta_b.split() if len(w) > 4}
    acuerdo_semantico = jaccard(tokens_a, tokens_b)

    return acuerdo_sintactico, acuerdo_semantico


# Thresholds calibrables (seccion 36.6 C.4).
EARLY_EXIT_SINTACTICO = 0.7
EARLY_EXIT_SEMANTICO = 0.8
FORCE_R3_SINTACTICO = 0.3
FORCE_R3_SEMANTICO = 0.4


AgreementDecision = Literal["early_exit", "force_r3", "continue"]


def decidir_siguiente_paso(
    acuerdo_sint: float,
    acuerdo_sem: float,
) -> AgreementDecision:
    """Gate de decision entre rondas (C.4)."""
    if acuerdo_sint > EARLY_EXIT_SINTACTICO and acuerdo_sem > EARLY_EXIT_SEMANTICO:
        return "early_exit"
    if acuerdo_sint < FORCE_R3_SINTACTICO or acuerdo_sem < FORCE_R3_SEMANTICO:
        return "force_r3"
    return "continue"


__all__ = [
    "AgreementDecision",
    "calcular_acuerdo",
    "decidir_siguiente_paso",
    "extract_cifras",
    "extract_citas_normativas",
    "jaccard",
]
