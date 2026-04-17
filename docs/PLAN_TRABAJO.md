# Plan de trabajo pgk_operativa

Ruta crítica 25 a 33 días útiles + 10 buffer. Detalle completo en `docs/plan_devin.md` (pendiente de migrar).

## Resumen por semana

### Semana 0: Scaffolding (Día 0 a Día 5)

- [x] Crear repo privado `POLSKA-GRUPA/pgk_operativa`.
- [x] `pyproject.toml` con Python 3.12, `uv`, FastAPI, LangGraph, SQLAlchemy, Alembic, Pydantic, ChromaDB.
- [x] `.gitignore`, `.env.example`, `.pre-commit-config.yaml`, CI GitHub Actions.
- [x] Estructura `src/pgk_operativa/` con `core/` (paths, config, llm) y `cli/` (Typer con `ana`, `doctor`, `version`).
- [x] Tests smoke (rutas absolutas, LLM factory, CLI).
- [x] ADRs 001 a 006 publicados.
- [ ] Commit inicial + CI verde.
- [ ] Smoke test Z.ai GLM-4.6 (pendiente de key en entorno).
- [ ] Smoke test túnel SSH a Postgres 209.74.72.83 (pendiente de credenciales).

### Semana 1: Core y fichaje y Ana mínima (Día 6 a Día 10)

- Módulo `pgk.identidad`: tabla `users` con email lógico más `emp_<slug>_<uuid4>`, grupo `pgk_empleado`, capacidades JSONB.
- Módulo `pgk.fichajes`: `fichajes` con RLS y append-only trigger. CLI `pgk ana "entrada"` / `"salida"`.
- Router Ana mínimo (LangGraph): clasifica intención, delega a módulos.
- Migraciones Alembic 001 y 002.

### Semana 2: 8 módulos base más consenso más goldens (Día 11 a Día 15)

- Módulos: `pgk.fiscal`, `pgk.contable`, `pgk.laboral`, `pgk.legal`, `pgk.docs`, `pgk.calidad`, `pgk.marketing`, `pgk.workflows`.
- Subgraph `/consenso` con assert runtime.
- 18 a 20 golden tests multi-proveedor.

### Semana 3: Integraciones conta/laboral/legal/consejo/forja más H1.1 a H1.3 (Día 16 a Día 20)

- Traer motor laboral determinista (7 109 LoC) desde pgk-laboral-desk.
- Traer CFO Agent con 8 sub-agentes desde conta-pgk-hispania.
- Traer 17 skills legales de `junior`.
- Traer consejo de 7 consejeros desde PGK-direccion-general.
- Traer REVISOR_UNIFICADO desde PROGRAMADOR_FRIKI_PGK.
- H1.1 testing base, H1.2 security baseline, H1.3 RGPD.

### Semana 4: H1.4 a H1.7 más 5 workflows Copilot más memoria operativa (Día 21 a Día 25)

- H1.4 calidad IA, H1.5 actualización conocimiento, H1.6 continuidad, H1.7 staging.
- 5 workflows Copilot (modelo_210, contestacion_hacienda, alta_autonomo, revision_trimestral, preparar_contrato).
- `memoria_operativa.db` con FTS5 y Bayesian updating.

### Semana 5: Distribución y piloto (Día 26 a Día 30)

- Distribución `uv sync && git pull` (tufup diferido a Semana 7).
- Onboarding one-liner documentado.
- Piloto con Kenyi más 1 empleado.

### Semana 6 en adelante: Fase 12 AOD más Guardias v1.8

- 17 workflows Fase 12.
- Guardia Integridad y Guardia Plazos.

## Reglas por semana

- Viernes EOD: `HANDOFF_ADVISOR_semana_N.md`.
- CI verde antes de merge.
- Tests con coverage > 80% en Semana 4.
- Sin em-dash, sin rutas hardcoded (CI lo bloquea).
