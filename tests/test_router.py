"""Tests del router Ana (clasificacion por keywords + LLM fallback)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from pgk_operativa.core import router


@pytest.mark.parametrize(
    ("mensaje", "modulo_esperado"),
    [
        ("¿Cuando presento el modelo 210 IRNR?", "fiscal"),
        ("Necesito un asiento para una factura recibida de alquiler", "contable"),
        ("Dame la nomina de enero de Kowalski", "laboral"),
        ("Redacta alegaciones contra la sentencia del TSJ", "legal"),
        ("Preparame un borrador de email para el cliente polaco", "docs"),
        ("Plan SEO y buyer persona para captacion autonomos", "marketing"),
    ],
)
def test_classify_by_keywords_unambiguous(mensaje: str, modulo_esperado: str) -> None:
    """Mensajes claros deben clasificarse por keywords sin llamar a LLM."""
    modulo, razon = router.clasificar(mensaje)
    assert modulo == modulo_esperado
    assert "keywords" in razon


def test_classify_by_keywords_empty_falls_back_to_llm() -> None:
    """Mensaje sin keywords cae a LLM."""
    with patch.object(router, "_classify_by_llm", return_value=("general", "llm: saludo")) as mock:
        modulo, razon = router.clasificar("hola")
        assert modulo == "general"
        assert "llm" in razon
        mock.assert_called_once()


def test_nodo_ana_router_with_empty_message() -> None:
    """Mensaje vacio debe clasificarse como general sin llamar LLM."""
    state = {"mensaje_usuario": ""}
    result = router.nodo_ana_router(state)  # type: ignore[arg-type]
    assert result["modulo_tecnico"] == "general"
    assert result["clasificacion_razonamiento"] == "mensaje vacio"
    assert len(result["audit_trail"]) == 1
    assert result["audit_trail"][0]["nodo"] == "ana_router"


def test_nodo_ana_router_assigns_fiscal_for_aeat() -> None:
    state = {"mensaje_usuario": "Tengo que presentar el modelo 303 de IVA del tercer trimestre"}
    result = router.nodo_ana_router(state)  # type: ignore[arg-type]
    assert result["modulo_tecnico"] == "fiscal"


def test_nodo_ana_router_audit_trail_structure() -> None:
    state = {"mensaje_usuario": "Nomina de febrero para Anna Nowak"}
    result = router.nodo_ana_router(state)  # type: ignore[arg-type]
    trail = result["audit_trail"]
    assert len(trail) == 1
    entry = trail[0]
    assert entry["nodo"] == "ana_router"
    assert "modulo_elegido" in entry
    assert "razon" in entry


def test_classify_tie_breaks_to_llm() -> None:
    """Empate de keywords entre 2 modulos fuerza al LLM a desempatar."""
    with patch.object(router, "_classify_by_llm", return_value=("legal", "llm: contratos")) as mock:
        # "contrato" aparece en legal, "ads" en marketing. 1 vs 1 = empate.
        modulo, _ = router.clasificar("Contrato de colaboracion con agencia de ads")
        assert modulo == "legal"
        mock.assert_called_once()


def test_iva_no_matches_inside_motivacion() -> None:
    """'iva' (fiscal) NO debe matchear dentro de 'motivacion'. Word boundary."""
    with patch.object(router, "_classify_by_llm", return_value=("docs", "llm: carta")) as mock:
        # 'motivacion' contiene 'iva' como substring, pero no como palabra.
        # 'carta' (docs) sigue siendo keyword valida.
        modulo, razon = router.clasificar("Dame la carta de motivacion para el puesto")
        assert modulo == "docs"
        assert "carta" in razon
        mock.assert_not_called()


def test_contrato_laboral_resolves_to_laboral() -> None:
    """'contrato laboral' (laboral, frase) y 'contrato' (legal) empatan → LLM desempata."""
    with patch.object(
        router, "_classify_by_llm", return_value=("laboral", "llm: contrato de trabajo")
    ) as mock:
        modulo, razon = router.clasificar("Necesito preparar un contrato laboral para Kowalski")
        assert modulo == "laboral"
        assert razon
        mock.assert_called_once()


def test_word_boundary_respects_spanish_accents() -> None:
    """Palabras con acentos o flexiones no deben disparar falsos positivos."""
    # 'retencion' (fiscal) NO debe matchear dentro de 'retencionista' inventado.
    # 'iva' NO debe matchear en 'derivativa' ni 'primitiva'.
    with patch.object(router, "_classify_by_llm", return_value=("general", "llm: nada")) as mock:
        modulo, _ = router.clasificar("una derivativa primitiva cualquiera sin sentido fiscal")
        assert modulo == "general"
        mock.assert_called_once()


def test_ts_matches_tribunal_supremo_end_of_string() -> None:
    """'ts' (legal, Tribunal Supremo) debe matchear al final de frase."""
    modulo, razon = router.clasificar("Busca jurisprudencia del TS")
    assert modulo == "legal"
    assert "ts" in razon


def test_ts_no_matches_inside_bots_or_rats() -> None:
    """'ts' NO debe matchear dentro de 'bots', 'rats', etc."""
    with patch.object(router, "_classify_by_llm", return_value=("general", "llm: nada")) as mock:
        modulo, _ = router.clasificar("bots de automatizacion para rats de laboratorio")
        assert modulo == "general"
        mock.assert_called_once()


def test_llm_parser_accepts_module_with_trailing_text() -> None:
    """El parser del LLM debe extraer solo el primer token del modulo."""
    fake_resp = type(
        "Resp",
        (),
        {
            "choices": [
                type(
                    "C",
                    (),
                    {
                        "message": type(
                            "M",
                            (),
                            {"content": "MODULO: fiscal (impuestos AEAT)\nRAZON: es fiscal"},
                        )
                    },
                )
            ]
        },
    )()
    fake_client = type(
        "Client",
        (),
        {
            "chat": type(
                "Chat",
                (),
                {"completions": type("Comp", (), {"create": lambda *a, **k: fake_resp})()},
            )()
        },
    )()
    with patch.object(router, "build_openai_client", return_value=(fake_client, "glm-4.6")):
        modulo, razon = router._classify_by_llm("cualquier cosa")
        assert modulo == "fiscal"
        assert "es fiscal" in razon


def test_nodo_ana_router_survives_llm_exception() -> None:
    """Si el LLM revienta (timeout, 5xx), el nodo no tira, rutea a 'general'."""
    state = {"mensaje_usuario": "algo completamente ambiguo sin keywords claras"}
    with patch.object(router, "clasificar", side_effect=RuntimeError("boom: API 503")):
        resultado = router.nodo_ana_router(state)
    assert resultado["modulo_tecnico"] == "general"
    assert "error clasificacion" in resultado["clasificacion_razonamiento"]
    assert resultado["audit_trail"][0]["evento"] == "clasificacion_error"
    assert resultado["audit_trail"][0]["error_tipo"] == "RuntimeError"


def test_llm_parser_accepts_module_with_dash_suffix() -> None:
    """MODULO: fiscal - AEAT debe parsear fiscal."""
    fake_resp = type(
        "Resp",
        (),
        {
            "choices": [
                type(
                    "C",
                    (),
                    {
                        "message": type(
                            "M",
                            (),
                            {"content": "MODULO: legal - sentencia\nRAZON: ts"},
                        )
                    },
                )
            ]
        },
    )()
    fake_client = type(
        "Client",
        (),
        {
            "chat": type(
                "Chat",
                (),
                {"completions": type("Comp", (), {"create": lambda *a, **k: fake_resp})()},
            )()
        },
    )()
    with patch.object(router, "build_openai_client", return_value=(fake_client, "glm-4.6")):
        modulo, _ = router._classify_by_llm("jurisprudencia")
        assert modulo == "legal"
