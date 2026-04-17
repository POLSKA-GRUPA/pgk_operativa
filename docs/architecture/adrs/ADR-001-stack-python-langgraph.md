# ADR-001: Stack Python 3.12 + LangGraph + FastAPI

Fecha: 2026-04-17
Estado: Aceptado.

## Contexto

pgk_operativa consolida 7 sistemas previos. 6 de ellos son Python (FastAPI, LangGraph, SQLAlchemy). El séptimo (PGK-Despacho-Desktop) es TypeScript + Electron, y su frontend se archiva (ver ADR-003).

## Decisión

- Python 3.12 obligatorio.
- `uv` como gestor de paquetes (más rápido que pip/poetry, lockfile determinista).
- FastAPI para exponer APIs internas.
- LangGraph para el grafo de agentes.
- SQLAlchemy 2.0 + Alembic para persistencia y migraciones.
- Pydantic 2 para validación y settings.
- ChromaDB para embeddings locales.
- Typer para CLI.

## Consecuencias

- Todos los módulos que se migren a este repo deben adaptar su stack a Python 3.12.
- Código TypeScript/Electron no se integra (se archiva).
- Streamlit y otros prototipos de UI van a `archivo/`.
