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


def test_graph_preserves_enrichment_fields_fiscal() -> None:
    """Regresion PR#7 Devin Review: los helpers enriquecen el estado con
    `fuentes_citadas` y `recomendaciones`. Si `AnaState` no declara esas
    claves, LangGraph las descarta al hacer merge. Este test pasa por el
    grafo entero y comprueba que llegan al estado final.
    """
    respuesta_llm = (
        "Segun la Ley 35/2006 del IRPF y el Real Decreto 439/2007,\n"
        "el contribuyente debe presentar el modelo 210 antes del 31 de enero.\n"
        "Recomiendo revisar el Articulo 24 del Convenio de doble imposicion.\n"
        "Es importante conservar los justificantes al menos 4 anos."
    )

    class _MockChoice:
        def __init__(self, content: str) -> None:
            self.message = type("M", (), {"content": content})()

    class _MockResp:
        def __init__(self, content: str) -> None:
            self.choices = [_MockChoice(content)]

    class _MockCompletions:
        def create(self, **_kwargs: object) -> _MockResp:
            return _MockResp(respuesta_llm)

    class _MockChat:
        completions = _MockCompletions()

    class _MockClient:
        chat = _MockChat()

    with patch(
        "pgk_operativa.nodos._base.build_openai_client",
        return_value=(_MockClient(), "glm-4.6"),
    ):
        resultado = graph_module.run("modelo 210 IRNR alquiler polaco")

    assert resultado["modulo_tecnico"] == "fiscal"
    fuentes = resultado.get("fuentes_citadas", [])
    recomendaciones = resultado.get("recomendaciones", [])
    assert isinstance(fuentes, list), "fuentes_citadas debe sobrevivir al merge del grafo"
    assert isinstance(recomendaciones, list), "recomendaciones debe sobrevivir al merge del grafo"
    assert len(fuentes) > 0, "el helper extrae al menos una fuente del texto simulado"
    assert len(recomendaciones) > 0, (
        "el helper extrae al menos una recomendacion del texto simulado"
    )
    assert any("Ley 35/2006" in f or "Real Decreto" in f for f in fuentes)


def test_graph_preserves_enrichment_fields_contable() -> None:
    """Regresion PR#7: campos contables (asientos_detectados, modelos_detectados,
    pasos_aon) deben sobrevivir al merge del grafo.
    """
    respuesta_llm = (
        "Debe cargar la cuenta 572 Bancos a la cuenta 700 Ventas.\n"
        "Para la declaracion usar modelo 303 y modelo 390 anual.\n"
        "Paso AON: importar el fichero de asientos en el programa externo.\n"
    )

    class _MockChoice:
        def __init__(self, content: str) -> None:
            self.message = type("M", (), {"content": content})()

    class _MockResp:
        choices: list[_MockChoice]

        def __init__(self, content: str) -> None:
            self.choices = [_MockChoice(content)]

    class _MockCompletions:
        def create(self, **_kwargs: object) -> _MockResp:
            return _MockResp(respuesta_llm)

    class _MockChat:
        completions = _MockCompletions()

    class _MockClient:
        chat = _MockChat()

    with patch(
        "pgk_operativa.nodos._base.build_openai_client",
        return_value=(_MockClient(), "glm-4.6"),
    ):
        resultado = graph_module.run("asiento PGC cuenta 572 venta cliente")

    assert resultado["modulo_tecnico"] == "contable"
    assert isinstance(resultado.get("asientos_detectados", []), list)
    assert isinstance(resultado.get("modelos_detectados", []), list)
    assert isinstance(resultado.get("pasos_aon", []), list)
    modelos = resultado.get("modelos_detectados", [])
    assert "303" in modelos or "390" in modelos


@pytest.mark.parametrize(
    ("mensaje", "modulo_esperado"),
    [
        ("modelo 210 IRNR", "fiscal"),
        ("asiento PGC deudor", "contable"),
        ("alta empleado seguridad social", "laboral"),
        ("recurso alegaciones juzgado", "legal"),
        ("borrador email plantilla cliente", "docs"),
        ("campana SEO buyer persona landing", "marketing"),
        ("revision de calidad verificar fuentes", "calidad"),
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
