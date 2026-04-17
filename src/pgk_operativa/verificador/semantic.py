"""Check semantico opt-in con LLM (Z.ai GLM-4.6 por defecto).

Para cada archivo con relacion `adaptado` o `copia_literal`, pregunta al
modelo si el destino preserva la intencion del origen y lista diferencias
materiales. El resultado se emite como Finding con severidad proporcional.

Este check NO corre por defecto (requiere API key + coste). Se activa con
`pgk verificar --semantico`.
"""

from __future__ import annotations

import json
from pathlib import Path

from pgk_operativa.core.llm import build_openai_client
from pgk_operativa.verificador.manifest import Manifest, Relacion
from pgk_operativa.verificador.report import Finding, Severity

MAX_CHARS = 6000


_PROMPT = """Eres un auditor de codigo senior. Recibes dos archivos:

- ORIGEN: archivo fuente en un repo anterior.
- DESTINO: archivo derivado copiado/adaptado en un nuevo repo.

Relacion declarada: {relacion}
- copia_literal: debe preservar la semantica al 100%.
- adaptado: cambios menores (renames, tipos, imports); intencion preservada.

Tu tarea: detectar si el DESTINO preserva la intencion del ORIGEN.

Responde en JSON estricto con este schema:
{{
  "preserva_intencion": true|false,
  "severidad": "CRITICAL"|"HIGH"|"MEDIUM"|"LOW",
  "resumen": "una frase concisa en castellano",
  "diferencias_materiales": ["lista breve de diferencias relevantes"]
}}

Criterios severidad:
- CRITICAL: funcionalidad clave eliminada, logica invertida, seguridad comprometida.
- HIGH: comportamiento distinto en casos comunes, API incompatible.
- MEDIUM: diferencias relevantes pero justificables (documentar en notas).
- LOW: refactor cosmetico, sin impacto.

No devuelvas NADA fuera del JSON. Sin markdown, sin backticks.

---ORIGEN ({origen_path})---
{origen_text}

---DESTINO ({destino_path})---
{destino_text}
"""


def _truncate(text: str, limit: int = MAX_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n... [truncado, {len(text) - limit} chars mas]"


def _parse_severity(raw: str) -> Severity:
    mapping = {
        "CRITICAL": Severity.CRITICAL,
        "HIGH": Severity.HIGH,
        "MEDIUM": Severity.MEDIUM,
        "LOW": Severity.LOW,
    }
    return mapping.get(raw.upper(), Severity.MEDIUM)


def _extract_json(text: str) -> dict[str, object]:
    """Extrae el primer bloque JSON valido de la respuesta del LLM."""
    text = text.strip()
    # Algunos modelos envuelven en ```json ... ```
    if text.startswith("```"):
        lines = text.splitlines()
        inner = [ln for ln in lines if not ln.strip().startswith("```")]
        text = "\n".join(inner)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"No se encontro JSON valido en respuesta LLM: {text[:200]!r}")
    blob = text[start : end + 1]
    data = json.loads(blob)
    if not isinstance(data, dict):
        raise ValueError("JSON devuelto no es un objeto")
    return data


def run(manifest: Manifest, repo_root: Path, repos_root: Path) -> list[Finding]:
    """Ejecuta el check semantico LLM sobre archivos copia_literal/adaptado."""
    findings: list[Finding] = []
    eligibles = [
        a
        for a in manifest.archivos
        if a.relacion in (Relacion.COPIA_LITERAL, Relacion.ADAPTADO) and a.origen is not None
    ]
    if not eligibles:
        return findings

    try:
        client, model = build_openai_client()
    except RuntimeError as exc:
        findings.append(
            Finding(
                check="semantic",
                severity=Severity.LOW,
                target="(verificador)",
                mensaje="Check semantico deshabilitado",
                detalle=f"No se pudo instanciar cliente LLM: {exc}",
            )
        )
        return findings

    for archivo in eligibles:
        assert archivo.origen is not None
        target = archivo.target_path(repo_root)
        origen = archivo.origen.absolute_path(repos_root)
        if not target.exists() or not origen.exists():
            continue
        try:
            destino_text = _truncate(target.read_text(encoding="utf-8"))
            origen_text = _truncate(origen.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError) as exc:
            findings.append(
                Finding(
                    check="semantic",
                    severity=Severity.LOW,
                    target=archivo.target,
                    mensaje="No se pudo leer origen o destino",
                    detalle=str(exc),
                )
            )
            continue

        prompt = _PROMPT.format(
            relacion=archivo.relacion.value,
            origen_path=f"{archivo.origen.repo}/{archivo.origen.path}",
            origen_text=origen_text,
            destino_path=archivo.target,
            destino_text=destino_text,
        )

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=512,
            )
            content = response.choices[0].message.content or ""
            data = _extract_json(content)
        except Exception as exc:  # pragma: no cover - red del LLM, auth, rate limit, etc.
            # Capturamos Exception porque el SDK de OpenAI/Z.ai lanza subclases
            # de openai.OpenAIError (APIError, RateLimitError, AuthenticationError,
            # APITimeoutError) que no heredan de ValueError/OSError/RuntimeError.
            # El verificador nunca debe crashear por un fallo de red del LLM.
            findings.append(
                Finding(
                    check="semantic",
                    severity=Severity.LOW,
                    target=archivo.target,
                    mensaje="Check semantico fallo",
                    detalle=str(exc)[:300],
                )
            )
            continue

        preserva = bool(data.get("preserva_intencion", True))
        if preserva:
            continue

        severidad_raw = str(data.get("severidad", "MEDIUM"))
        resumen = str(data.get("resumen", "Diferencia semantica detectada"))
        diffs_raw = data.get("diferencias_materiales", [])
        diffs_list = diffs_raw if isinstance(diffs_raw, list) else []
        diffs = "; ".join(str(d) for d in diffs_list[:5])

        findings.append(
            Finding(
                check="semantic",
                severity=_parse_severity(severidad_raw),
                target=archivo.target,
                mensaje=resumen,
                detalle=f"Origen: {archivo.origen.repo}/{archivo.origen.path}. {diffs}",
            )
        )

    return findings
