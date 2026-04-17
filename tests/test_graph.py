"""Tests del grafo LangGraph: Semana 1 regresion + Semana 2 routing condicional."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from pgk_operativa.core import graph as graph_module


def test_build_graph_compiles() -> None:
    """El grafo debe compilar sin errores."""
    g = graph_module.build_graph()
    assert g is not None


def test_initial_state_has_required_keys() -> None:
    state = graph_module.initial_state("Hola Ana", nif="X1234567P", nombre="Jan Kowalski")
    assert state["caso_id"].startswith("caso-")
    assert state["cliente_nif"] == "X1234567P"
    assert state["cliente_nombre"] == "Jan Kowalski"
    assert state["mensaje_usuario"] == "Hola Ana"
    assert state["consenso_activo"] is False
    assert state["timestamp_inicio"]
    assert state["timestamp_fin"] is None
    assert state["audit_trail"][0]["nodo"] == "init"


def test_initial_state_without_cliente_data() -> None:
    state = graph_module.initial_state("consulta anonima")
    assert state["cliente_nif"] is None
    assert state["cliente_nombre"] is None


def test_initial_state_consenso_flag() -> None:
    state = graph_module.initial_state("caso con consenso", consenso=True)
    assert state["consenso_activo"] is True


def test_graph_run_end_to_end_mocked() -> None:
    """End-to-end con LLM mockeado: clasifica + responde."""
    respuestas_simuladas = iter(["Respuesta fiscal simulada"])

    class _MockChoice:
        def __init__(self, content: str) -> None:
            self.message = type("M", (), {"content": content})()

    class _MockResp:
        def __init__(self, content: str) -> None:
            self.choices = [_MockChoice(content)]

    class _MockCompletions:
        def create(self, **_kwargs: object) -> _MockResp:
            return _MockResp(next(respuestas_simuladas))

    class _MockChat:
        completions = _MockCompletions()

    class _MockClient:
        chat = _MockChat()

    with patch(
        "pgk_operativa.nodos._base.build_openai_client",
        return_value=(_MockClient(), "glm-4.6"),
    ):
        resultado = graph_module.run(
            "¿Cuando vence el modelo 210 IRNR del ejercicio 2024?",
            nif="X9876543L",
            nombre="Anna Nowak",
        )

    assert resultado["modulo_tecnico"] == "fiscal"
    assert resultado["respuesta_final"] == "Respuesta fiscal simulada"
    assert resultado["timestamp_fin"] is not None
    trail = resultado["audit_trail"]
    assert any(e.get("nodo") == "init" for e in trail)
    assert any(e.get("nodo") == "ana_router" for e in trail)
    assert any(e.get("nodo", "").startswith("ejecutor_") for e in trail)


def test_graph_run_llm_failure_returns_graceful_message() -> None:
    """Si el LLM falla el grafo no debe petar: responde mensaje de error amable."""

    class _ExplodingCompletions:
        def create(self, **_kwargs: object) -> object:
            raise RuntimeError("boom red")

    class _ExplodingChat:
        completions = _ExplodingCompletions()

    class _ExplodingClient:
        chat = _ExplodingChat()

    with patch(
        "pgk_operativa.nodos._base.build_openai_client",
        return_value=(_ExplodingClient(), "glm-4.6"),
    ):
        resultado = graph_module.run("declaracion trimestral 303")

    assert "No he podido generar" in resultado["respuesta_final"]
    assert any(e.get("evento") == "llm_error" for e in resultado["audit_trail"])


@pytest.mark.parametrize(
    ("mensaje", "modulo_esperado"),
    [
        ("modelo 210 IRNR", "fiscal"),
        ("asiento PGC deudor", "contable"),
        ("alta empleado seguridad social", "laboral"),
    ],
)
def test_graph_routes_to_correct_module(mensaje: str, modulo_esperado: str) -> None:
    """El ruteo debe asignar el modulo correcto antes de ejecutar."""

    class _StubClient:
        class chat:  # noqa: N801
            class completions:  # noqa: N801
                @staticmethod
                def create(**_kwargs: object) -> object:
                    return type(
                        "R",
                        (),
                        {
                            "choices": [
                                type(
                                    "C",
                                    (),
                                    {"message": type("M", (), {"content": "ok"})()},
                                )()
                            ]
                        },
                    )()

    with patch(
        "pgk_operativa.nodos._base.build_openai_client",
        return_value=(_StubClient(), "glm-4.6"),
    ):
        resultado = graph_module.run(mensaje)

    assert resultado["modulo_tecnico"] == modulo_esperado
