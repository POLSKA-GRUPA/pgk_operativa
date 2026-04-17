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
