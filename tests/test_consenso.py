"""Tests del subgraph de consenso multi-proveedor (C.1-C.10).

Fixtures stub para CI rapido. No hacen llamadas reales a proveedores.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from pgk_operativa.core.consenso.agreement import (
    calcular_acuerdo,
    decidir_siguiente_paso,
    extract_cifras,
    extract_citas_normativas,
    jaccard,
)
from pgk_operativa.core.consenso.circuit_breaker import CircuitBreaker
from pgk_operativa.core.consenso.subgraph import build_consenso_subgraph, run_consenso
from pgk_operativa.core.llm import Provider, pick_consensus_pair

# ---------------------------------------------------------------------------
# C.4 Agreement tests
# ---------------------------------------------------------------------------


class TestJaccard:
    def test_empty_sets(self) -> None:
        assert jaccard(set(), set()) == 1.0

    def test_identical_sets(self) -> None:
        assert jaccard({"a", "b"}, {"a", "b"}) == 1.0

    def test_disjoint_sets(self) -> None:
        assert jaccard({"a"}, {"b"}) == 0.0

    def test_partial_overlap(self) -> None:
        assert jaccard({"a", "b", "c"}, {"b", "c", "d"}) == pytest.approx(0.5)


class TestExtractCifras:
    def test_porcentajes(self) -> None:
        result = extract_cifras("El tipo es 24% para no residentes y 19% con CDI.")
        assert "24%" in result
        assert "19%" in result

    def test_importes(self) -> None:
        result = extract_cifras("Cuota de 1500 EUR mas 200 EUR de recargo.")
        assert "1500 EUR" in result
        assert "200 EUR" in result

    def test_articulos(self) -> None:
        result = extract_cifras("Segun art. 24 y articulo 85.3 de la LIRNR.")
        assert any("24" in c for c in result)


class TestExtractCitasNormativas:
    def test_ecli(self) -> None:
        result = extract_citas_normativas("Ver ECLI:ES:TS:2024:1234")
        assert "ECLI:ES:TS:2024:1234" in result

    def test_boe(self) -> None:
        result = extract_citas_normativas("Publicado en BOE-A-2024-12345")
        assert "BOE-A-2024-12345" in result

    def test_leyes(self) -> None:
        result = extract_citas_normativas("Ley 35/2006 del IRPF y RD 439/2007.")
        assert "Ley 35/2006" in result
        assert "RD 439/2007" in result

    def test_modelos_aeat(self) -> None:
        result = extract_citas_normativas("Presenta el modelo 210 y el Modelo 303.")
        assert "modelo 210" in result
        assert "Modelo 303" in result

    def test_siglas_normativas(self) -> None:
        result = extract_citas_normativas("La LIRNR y la LGT regulan esto.")
        assert "LIRNR" in result
        assert "LGT" in result


class TestCalcularAcuerdo:
    def test_identical_responses(self) -> None:
        text = "El modelo 210 aplica segun art. 24 LIRNR. Tipo 24%."
        sint, sem = calcular_acuerdo(text, text)
        assert sint == 1.0
        assert sem == 1.0

    def test_disjoint_responses(self) -> None:
        a = "Modelo 210 tipo 24% segun LIRNR."
        b = "Impuesto sobre Sociedades, Ley 27/2014."
        sint, _sem = calcular_acuerdo(a, b)
        assert sint < 0.5

    def test_empty_responses(self) -> None:
        sint, _sem = calcular_acuerdo("", "")
        # Jaccard(empty, empty) = 1.0
        assert sint == 1.0


class TestDecidirSiguientePaso:
    def test_early_exit(self) -> None:
        assert decidir_siguiente_paso(0.8, 0.9) == "early_exit"

    def test_force_r3_low_sintactico(self) -> None:
        assert decidir_siguiente_paso(0.2, 0.5) == "force_r3"

    def test_force_r3_low_semantico(self) -> None:
        assert decidir_siguiente_paso(0.5, 0.3) == "force_r3"

    def test_continue(self) -> None:
        assert decidir_siguiente_paso(0.5, 0.6) == "continue"


# ---------------------------------------------------------------------------
# C.8 Circuit breaker tests
# ---------------------------------------------------------------------------


class TestCircuitBreaker:
    def test_starts_closed(self) -> None:
        cb = CircuitBreaker(max_fallos=3)
        assert not cb.abierto

    def test_opens_after_threshold(self) -> None:
        cb = CircuitBreaker(max_fallos=3)
        cb.registrar_fallo()
        cb.registrar_fallo()
        opened = cb.registrar_fallo()
        assert opened is True
        assert cb.abierto

    def test_success_resets(self) -> None:
        cb = CircuitBreaker(max_fallos=3)
        cb.registrar_fallo()
        cb.registrar_fallo()
        cb.registrar_exito()
        cb.registrar_fallo()
        assert not cb.abierto

    def test_estado_snapshot(self) -> None:
        cb = CircuitBreaker(max_fallos=5)
        cb.registrar_fallo()
        estado = cb.estado()
        assert estado["abierto"] is False
        assert estado["fallos_recientes"] == 1
        assert estado["max_fallos"] == 5


# ---------------------------------------------------------------------------
# C.1 Subgraph structure tests
# ---------------------------------------------------------------------------


class TestSubgraphStructure:
    def test_compiles(self) -> None:
        g = build_consenso_subgraph()
        assert g is not None

    def test_run_consenso_single_model_mocked(self) -> None:
        """Consenso sin 2 proveedores: degrada a single-model."""

        class _MockChoice:
            def __init__(self, content: str) -> None:
                self.message = type("M", (), {"content": content})()

        class _MockResp:
            def __init__(self, content: str) -> None:
                self.choices = [_MockChoice(content)]

        class _MockCompletions:
            def create(self, **_kwargs: object) -> _MockResp:
                return _MockResp("Respuesta single-model simulada")

        class _MockChat:
            completions = _MockCompletions()

        class _MockClient:
            chat = _MockChat()

        with (
            patch(
                "pgk_operativa.core.consenso.subgraph.pick_consensus_pair",
                return_value=None,
            ),
            patch(
                "pgk_operativa.core.consenso.subgraph.build_openai_client",
                return_value=(_MockClient(), "glm-4.6"),
            ),
        ):
            result = run_consenso("Pregunta fiscal de prueba", context="Eres asesor fiscal.")

        assert result["consensus_type"] == "single_model"
        assert result["respuesta_sintetizada"] == "Respuesta single-model simulada"

    def test_run_consenso_circuit_breaker_open(self) -> None:
        """Si el circuit breaker esta abierto, se aborta."""
        cb = CircuitBreaker(max_fallos=1)
        cb.registrar_fallo()
        assert cb.abierto

        with patch(
            "pgk_operativa.core.consenso.subgraph.get_breaker",
            return_value=cb,
        ):
            result = run_consenso("Pregunta de prueba")

        assert result["consensus_type"] == "degraded"
        assert result["aborted"] is True


# ---------------------------------------------------------------------------
# C.10 Golden test stubs (simple category)
# ---------------------------------------------------------------------------


class TestGoldenStubs:
    """Stubs para los golden tests C.10. Verifican estructura, no contenido LLM."""

    def test_simple_definition_routes_single_model(self) -> None:
        """Pregunta simple: no necesita consenso, single-model."""

        class _StubClient:
            class chat:  # noqa: N801
                class completions:  # noqa: N801
                    @staticmethod
                    def create(**_kw: object) -> object:
                        return type(
                            "R",
                            (),
                            {
                                "choices": [
                                    type(
                                        "C",
                                        (),
                                        {"message": type("M", (), {"content": "Definicion ok"})()},
                                    )()
                                ]
                            },
                        )()

        with (
            patch(
                "pgk_operativa.core.consenso.subgraph.pick_consensus_pair",
                return_value=None,
            ),
            patch(
                "pgk_operativa.core.consenso.subgraph.build_openai_client",
                return_value=(_StubClient(), "glm-4.6"),
            ),
        ):
            result = run_consenso("Que es el IRNR?")

        assert result["consensus_type"] == "single_model"
        assert "Definicion ok" in result["respuesta_sintetizada"]

    def test_empty_query_handled(self) -> None:
        """Edge case: query vacia no rompe el subgraph."""

        class _StubClient:
            class chat:  # noqa: N801
                class completions:  # noqa: N801
                    @staticmethod
                    def create(**_kw: object) -> object:
                        return type(
                            "R",
                            (),
                            {
                                "choices": [
                                    type("C", (), {"message": type("M", (), {"content": ""})()})()
                                ]
                            },
                        )()

        with (
            patch(
                "pgk_operativa.core.consenso.subgraph.pick_consensus_pair",
                return_value=None,
            ),
            patch(
                "pgk_operativa.core.consenso.subgraph.build_openai_client",
                return_value=(_StubClient(), "glm-4.6"),
            ),
        ):
            result = run_consenso("")

        assert result["consensus_type"] == "single_model"
        # No crash


# ---------------------------------------------------------------------------
# Bug #31: pick_consensus_pair debe cubrir TODAS las combinaciones
# ---------------------------------------------------------------------------


class TestAgreementCaseInsensitive:
    """Regresion Bug #32: calcular_acuerdo no normalizaba case, asi que
    'Modelo 210' y 'modelo 210' contaban como distintos en Jaccard.
    """

    def test_modelo_case_different_gives_high_agreement(self) -> None:
        a = "Presenta el Modelo 210 segun la Ley 35/2006."
        b = "presenta el modelo 210 segun la ley 35/2006."
        sint, _sem = calcular_acuerdo(a, b)
        assert sint >= 0.9, f"sintactico deberia ser ~1.0 con solo case diff: {sint}"

    def test_eur_case_different_gives_high_agreement(self) -> None:
        a = "La cuota es 1500 EUR al trimestre."
        b = "la cuota es 1500 eur al trimestre."
        sint, _sem = calcular_acuerdo(a, b)
        assert sint >= 0.5, f"sintactico deberia ser alto pese a case diff: {sint}"


class TestPickConsensusPairCoverage:
    """Regresion Bug #31: la lista hardcoded de pares no cubria OPENAI ni
    todas las combinaciones con DEEPSEEK. Usuarios con solo ZAI+OPENAI
    o OPENAI+DEEPSEEK recibian None pese a tener 2 proveedores validos
    y degradaban silenciosamente a single_model sin diagnostico.
    """

    def test_zai_plus_openai_returns_pair(self) -> None:
        with patch(
            "pgk_operativa.core.llm.available_providers",
            return_value=[Provider.ZAI, Provider.OPENAI],
        ):
            pair = pick_consensus_pair()
        assert pair is not None
        a, b = pair
        assert {a.provider, b.provider} == {Provider.ZAI, Provider.OPENAI}
        assert a.model != b.model

    def test_openai_plus_deepseek_returns_pair(self) -> None:
        with patch(
            "pgk_operativa.core.llm.available_providers",
            return_value=[Provider.OPENAI, Provider.DEEPSEEK],
        ):
            pair = pick_consensus_pair()
        assert pair is not None
        a, b = pair
        assert {a.provider, b.provider} == {Provider.OPENAI, Provider.DEEPSEEK}

    def test_anthropic_plus_deepseek_returns_pair(self) -> None:
        with patch(
            "pgk_operativa.core.llm.available_providers",
            return_value=[Provider.ANTHROPIC, Provider.DEEPSEEK],
        ):
            pair = pick_consensus_pair()
        assert pair is not None

    def test_single_provider_returns_none(self) -> None:
        with patch(
            "pgk_operativa.core.llm.available_providers",
            return_value=[Provider.ZAI],
        ):
            assert pick_consensus_pair() is None

    def test_prefers_zai_first(self) -> None:
        """Con multiples disponibles, ZAI aparece como A por preferencia."""
        with patch(
            "pgk_operativa.core.llm.available_providers",
            return_value=[Provider.DEEPSEEK, Provider.ZAI, Provider.OPENAI],
        ):
            pair = pick_consensus_pair()
        assert pair is not None
        assert pair[0].provider == Provider.ZAI
