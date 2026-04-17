# Arquitectura

## Visión en 10 líneas

Un grafo LangGraph es el cerebro. Ana es la cara. Los módulos técnicos son los especialistas: fiscal, contable, laboral, legal, docs, calidad, marketing, consejo, forja, workflows. El empleado nunca los llama por su nombre: habla con Ana. Tres bases de datos son inviolables: Postgres remoto para lo administrativo, SQLite local para la memoria de negocio, SQLite local para la memoria de desarrollo. No hay front-end: CLI, bot Mattermost, email borrador. Todas las rutas se calculan en runtime con `Path(__file__).resolve()`, nunca hardcoded. Consenso es un comando opt-in, no un default. Emails nunca se envían, solo se guardan como borrador. Nada se borra: lo antiguo va a `archivo/`.

## Capa de presentación

Única entrada del empleado: `pgk ana "<mensaje>"`.

Implementaciones:

- CLI Typer (`pgk ...`): consultas, fichajes, admin.
- Bot Mattermost: fichaje móvil, consultas cortas.
- Email borrador: Ana redacta en `INBOX.Drafts`, humano revisa y envía.

Prohibido: dashboards, paneles web, paneles Streamlit en producción.

## Capa de cerebro

Grafo LangGraph con nodos:

- **Ana** (router): clasifica intención y enruta al módulo técnico.
- **Módulos técnicos**: lógica de negocio por dominio.
- **Quality gate**: valida respuestas antes de devolverlas al empleado.
- **Red team**: contraargumenta en decisiones de alto impacto (dispara solo con `/consenso` o umbrales específicos).
- **HITL**: escalación humana en decisiones críticas (montos, legales).
- **Checkpointer**: Postgres para persistencia de estado entre pasos.

## Módulos técnicos

- `pgk.fiscal`: IRNR, modelo 210, modelo 100, convenios internacionales. Fuente: PGK_Empresa_Autonoma/src/agents/nodos.py (Gran Dragón).
- `pgk.contable`: PGC 2008, modelos 303/130/111/115/390/347, conciliación bancaria, amortización. Fuente: conta-pgk-hispania.
- `pgk.laboral`: nóminas, cotizaciones SS, IRPF autonómico, convenios colectivos BOE. Fuente: pgk-laboral-desk (motor determinista).
- `pgk.legal`: 17 skills de `junior` (LO 1/2025, MASC, procedimientos).
- `pgk.docs`: generación PDF/DOCX/PPTX con estilo PGK. Fuente: PGK_Empresa_Autonoma/src/documentos (Paloma).
- `pgk.calidad`: limpieza de código, reportes internos. Fuente: PGK_Empresa_Autonoma (Jennifer).
- `pgk.marketing`: SEO, contenido, case study, email marketing. Fuente: PGK-Marketing-Autonomo (14 subagentes).
- `pgk.consejo`: consejo de dirección (7 consejeros), DeLLMa, Monte Carlo. Fuente: PGK-direccion-general.
- `pgk.forja`: seguridad, code review, CI, despliegue. Fuente: PROGRAMADOR_FRIKI_PGK (REVISOR_UNIFICADO).
- `pgk.workflows`: los 5 workflows Copilot validados (modelo_210, contestacion_hacienda, alta_autonomo, revision_trimestral, preparar_contrato) más motor declarativo.

## Capa de persistencia

Ver `docs/BDS.md`. Tres BDs inviolables:

1. `pgk_database` (Postgres remoto 209.74.72.83, schema `pgk_admin`, vía túnel SSH).
2. `memoria_operativa.db` (SQLite local FTS5, memoria de negocio del agente).
3. `engram.db` (SQLite local, memoria de desarrollo entre sesiones de IA).

## Portabilidad

- Todas las rutas `Path(__file__).resolve()`.
- Variables de entorno para rutas específicas del usuario (`PGK_USER_HOME`, `PGK_LOCAL_DOCUMENTS_PATH`).
- Distribución por `uv sync && git pull` hasta Semana 5. Firma con `tufup` diferida a Semana 7.

## LLM stack

- Default: OpenAI SDK con `base_url=https://api.z.ai/api/coding/paas/v4`, modelo `glm-4.6`. 1 modelo por defecto.
- Consenso opt-in `/consenso`: 2 proveedores distintos, assert en runtime, degrada si faltan keys.
- Fallback: Anthropic Sonnet 4.5 vía Z.ai proxy, Gemini 2.5 Pro, Grok-3, DeepSeek, GPT-4o.
- Perplexity para verificación normativa fiscal/legal.
- Embeddings: text-embedding-3-small.

Presupuesto objetivo: 80 a 250 USD/mes.
