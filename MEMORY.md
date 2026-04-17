# MEMORY.md

Resumen ejecutivo para arranque rápido de agentes IA en este repo.

## Qué es esto

Super-agente unificado de Polska Grupa Konsultingowa S.L.. Consolida 7 sistemas previos en un solo repositorio. Cara visible única: Ana. Módulos técnicos detrás.

## Estado actual

Semana 0 Día 0. Scaffolding inicial. Ver `docs/PLAN_TRABAJO.md`.

## Reglas que no se negocian

1. Ana única cara visible. Módulos conservan nombre técnico.
2. Rutas absolutas runtime (`Path(__file__).resolve()`).
3. Consenso opt-in (`/consenso`), no default.
4. Default LLM: Z.ai GLM-4.6 vía OpenAI SDK.
5. Tres BDs inviolables: `pgk_database` remoto, `memoria_operativa.db` local, `engram.db` local.
6. Estilo PGK: sin em-dash, sin líneas decorativas.
7. Nada se borra: lo antiguo a `archivo/` con README y fecha.
8. Emails: siempre borrador, nunca envío directo.

## Ubicaciones clave

- Código: `src/pgk_operativa/`.
- Tests: `tests/`.
- Documentación: `docs/`.
- ADRs: `docs/architecture/adrs/`.
- Archivo: `archivo/` (creada al iniciar migraciones).
- Plantilla entorno: `.env.example`.

## Decisiones clave

Ver `docs/architecture/adrs/`:

- ADR-001: stack Python 3.12 + LangGraph + FastAPI.
- ADR-002: Ana única sin rebranding.
- ADR-003: `archivo/`, nada se borra.
- ADR-004: rutas absolutas runtime.
- ADR-005: consenso opt-in, default single-model.
- ADR-006: tres BDs inviolables.

## Comandos útiles

```bash
# Setup
uv sync --all-extras --dev
uv run pre-commit install

# Desarrollo
uv run pytest
uv run ruff check .
uv run ruff format .
uv run mypy src/pgk_operativa

# CLI
uv run pgk doctor
uv run pgk version
uv run pgk ana "hola"
uv run pgk ana --consenso "decision fiscal"
```

## Próximos pasos (Día 0 pendiente)

- Smoke test Z.ai GLM-4.6 con key real.
- Smoke test túnel SSH a Postgres remoto con credenciales.
- Commit inicial y validar CI verde.
- Message a Kenyi: "Scaffolding completo, listo para Semana 1".

## Advisor

Claude Opus 4.7. Ver `docs/ADVISOR.md`. Handoff semanal cada viernes.
