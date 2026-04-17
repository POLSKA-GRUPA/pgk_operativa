# HANDOFF pgk_operativa

Manual de traspaso para la socia de Kenyi. Documento autocontenido. Leer de principio a fin no es obligatorio, pero la primera vez conviene. El índice permite volver a cualquier sección sin depender de notas previas.

Versión del documento: 2026-04-16.
Estado del repo al generar el handoff: Semana 1 cerrada, PR #2 mergeado a main, 47 de 47 tests verdes, CI verde.

## Índice

0. [Qué es pgk_operativa en una página](#0-qué-es-pgk_operativa-en-una-página)
1. [ULTRAPLAN v1.8, los tres principios y los ocho principios rectores](#1-ultraplan-v18-los-tres-principios-y-los-ocho-principios-rectores)
2. [Arquitectura del repo](#2-arquitectura-del-repo)
3. [Las tres bases de datos inviolables](#3-las-tres-bases-de-datos-inviolables)
4. [Forma de trabajar: reglas que no se negocian](#4-forma-de-trabajar-reglas-que-no-se-negocian)
5. [Rutas absolutas en profundidad](#5-rutas-absolutas-en-profundidad)
6. [Estilo PGK para todo documento](#6-estilo-pgk-para-todo-documento)
7. [Consenso opt-in y el default Z.ai](#7-consenso-opt-in-y-el-default-zai)
8. [Ana única cara visible](#8-ana-única-cara-visible)
9. [Archivo en lugar de legacy](#9-archivo-en-lugar-de-legacy)
10. [Emails siempre borrador](#10-emails-siempre-borrador)
11. [Requisitos mínimos de la máquina](#11-requisitos-mínimos-de-la-máquina)
12. [Onboarding paso a paso (de cero a primer pgk ana)](#12-onboarding-paso-a-paso-de-cero-a-primer-pgk-ana)
13. [Flujo Git y política de PRs](#13-flujo-git-y-política-de-prs)
14. [Estado actual: Semana 1 cerrada](#14-estado-actual-semana-1-cerrada)
15. [Hoja de ruta Semana 2 a Semana 6](#15-hoja-de-ruta-semana-2-a-semana-6)
16. [H1 Fundaciones Enterprise en detalle](#16-h1-fundaciones-enterprise-en-detalle)
17. [Fase 12 AOD: 15 workflows de operativa diaria](#17-fase-12-aod-15-workflows-de-operativa-diaria)
18. [Adenda v1.7: distribución a empleados](#18-adenda-v17-distribución-a-empleados)
19. [Adenda v1.8: Guardia Integridad y Guardia Plazos](#19-adenda-v18-guardia-integridad-y-guardia-plazos)
20. [Qué hace y qué NO hace pgk_operativa](#20-qué-hace-y-qué-no-hace-pgk_operativa)
21. [Decisiones tomadas (ADRs) y decisiones pendientes](#21-decisiones-tomadas-adrs-y-decisiones-pendientes)
22. [Glosario](#22-glosario)
23. [Troubleshooting frecuente](#23-troubleshooting-frecuente)
24. [Contactos y canales](#24-contactos-y-canales)
25. [Anexo: comandos útiles del día a día](#25-anexo-comandos-útiles-del-día-a-día)

## 0. Qué es pgk_operativa en una página

pgk_operativa es el repositorio único y nuevo de Polska Grupa Konsultingowa S.L. Sustituye (consolidándolos, no borrándolos) a siete repos previos: PGK_Empresa_Autonoma, conta-pgk-hispania, pgk-laboral-desk, junior, PGK-direccion-general, PGK-Marketing-Autonomo y PROGRAMADOR_FRIKI_PGK, más el portal que vivía dentro de PGK_Empresa_Autonoma.

El negocio es un despacho fiscal-contable-laboral-legal remoto enfocado a no residentes en España, principalmente polacos. pgk_operativa es el cerebro unificado que permite que:

- Empleados y Kenyi trabajen con una sola interfaz conversacional llamada Ana.
- Ana enrute la consulta por debajo al módulo técnico adecuado (fiscal, contable, laboral, legal, docs, calidad, marketing, consejo, forja, workflows).
- Las respuestas lleguen por Mattermost, email, CLI o chat, nunca por dashboards.
- El grafo LangGraph sea la autoridad de negocio (Cecilia, Gran Dragón, Edu, German, Paloma como prompts de personalidad, no como agentes visibles).
- Todo conocimiento (skills, plantillas, BOE, dictámenes previos) quede consolidado en un solo sitio con ADRs que expliquen cada decisión.

El objetivo operativo es eliminar el 60% del trabajo repetitivo del despacho via workflows adaptativos, conservando fiabilidad enterprise (auditoría, backups, RGPD).

Estado actual: infraestructura montada y grafo mínimo operativo. Quedan por integrar los módulos reales (fiscal, contable, laboral, legal, etc.), migrar los cinco workflows Copilot validados y aplicar las guardias de integridad y plazos.

Si solo puedes leer 5 minutos, lee las secciones 1, 4 y 14.

## 1. ULTRAPLAN v1.8, los tres principios y los ocho principios rectores

ULTRAPLAN es el documento maestro que define cómo montar la infraestructura remota. Se ha iterado hasta la versión 1.8 incorporando adendas. El repo pgk_operativa es su implementación.

### 1.1 Los tres principios fundacionales

1. El fichaje legal es la base, la capa de IA es el diferencial. Nunca al revés. Si el fichaje no cumple el Real Decreto Ley 8/2019, el resto es irrelevante.
2. Gestión genérica multi-empleado desde el día uno. Nada personalizado a Kenyi. Todo reutilizable por Francisco, la socia, y cualquier futuro empleado.
3. Verificación antes de construir. La distancia entre lo que Engram dice y lo que el código hace se reduce primero. Antes de cada fase, se verifica el terreno.

### 1.2 Los ocho principios rectores

1. Excelencia ejecutable sobre exhaustividad teórica. Mejor pocas fases brillantes que muchas a medias.
2. Enterprise grade desde el día uno en fundamentales (seguridad, auditoría, backups), sin sobreingenieria en lo superfluo.
3. Reversibilidad. Cada decisión de proveedor con plan B documentado.
4. Multimodelo IA. Ningún agente depende de un solo proveedor LLM. Z.ai, Anthropic, Groq, OpenAI, Gemini, Perplexity como fallbacks intercambiables.
5. Data portability. Datos siempre exportables en formatos abiertos. Cero lock-in.
6. Open source por defecto, propietario por excepcion.
7. Interfaces conversacionales por defecto, front-end solo cuando no haya alternativa. Sin dashboards. Sin paneles administrativos. Ni cliente ni empleado tienen portal web, todos conversan con Ana.
8. Más limpio, más robusto, menos código. Antes de escribir 300 lineas, 30 minutos de busqueda en GitHub. Componer con piezas existentes (tufup, age, uv, Claude Code) siempre preferible a construir desde cero.

### 1.3 Las fases del plan

El orden global es: Fase 0 (verificación), H1 (Fundaciones Enterprise en paralelo), Fases 1 a 11 (infraestructura de negocio), Fase 12 (AOD, automatización operativa diaria), Adenda v1.7 (distribución a empleados), Adenda v1.8 (guardias integridad y plazos).

Para el equipo: trabajamos sobre pgk_operativa aplicando las fases en este orden, no todas a la vez. La sección 15 convierte el plan fases en un calendario semanal accionable.

### 1.4 Consecuencias del Principio 7 (sin pantallas)

- Ningún empleado tiene dashboard. Pregunta a Ana: "como voy hoy", "que me queda", "cuantas horas he imputado".
- Ningún cliente tiene portal. Paloma responde por email, Ana atiende por chatbot público.
- Administracion es CLI conversacional, no panel. Comandos tipo `pgk admin alta-empleado` se combinan con preguntas a Ana.
- Fichaje movil es bot Mattermost (`/fichar-entrada`), no app.
- Metricas llegan como resumen diario conversacional a Mattermost.
- Única excepcion justificada: web corporativa pública (pgkhiszpania.com) con perfiles y blog, porque es canal de marketing donde la pantalla es el producto.

### 1.5 Modos adaptativos de operación

Una variable global controla la cadencia del sistema:

| Modo | Cuando | Efecto |
|---|---|---|
| normal | Rutina diaria | Resumen diario conciso, recordatorios estándar, seguimientos cada 15 días |
| intenso | Inspección AEAT, cierre trimestre, cliente en crisis | Resumenes 2 veces al día, alertas 7/3/1 días, seguimiento diario |
| vacaciones | Kenyi desconectado | Solo emergencias AEAT reales, resto silenciado |
| pánico | Caida sistema o error grave en cliente | Notificaciones continuas, runbook DR activado |

Activacion automática por detección, o manual via `/modo intenso 2 semanas` en Mattermost.

## 2. Arquitectura del repo

```
pgk_operativa/
├── README.md                   Punto de entrada público
├── AGENTS.md                   Reglas para agentes IA (Devin, Claude, Cursor, etc.)
├── MEMORY.md                   Resumen ejecutivo para arranque rápido
├── HANDOFF.md                  Este documento
├── pyproject.toml              Deps y build system (uv)
├── uv.lock                     Lockfile reproducible
├── .env.example                Plantilla de configuración por máquina
├── .gitignore                  (incluye .env, data/*.db, __pycache__, .venv)
├── .pre-commit-config.yaml     Hooks locales (ruff, mypy, estilo PGK)
├── .github/
│   └── workflows/
│       └── ci.yml              Lint + tests en Python 3.12
├── src/
│   └── pgk_operativa/
│       ├── __init__.py
│       ├── cli/
│       │   └── main.py         CLI pública (pgk ana, pgk doctor, pgk version)
│       ├── core/
│       │   ├── paths.py        Path(__file__).resolve() raíz y subrutas
│       │   ├── config.py       Carga de .env, validación de claves
│       │   ├── llm.py          Cliente OpenAI SDK -> Z.ai GLM-4.6
│       │   ├── graph_state.py  Estado tipado LangGraph
│       │   ├── router.py       Ana router (keywords + LLM fallback)
│       │   └── graph.py        Construcción del grafo mínimo
│       └── nodos/
│           ├── ejecutor.py     Ejecutor genérico del módulo
│           └── prompts.py      Prompts skeleton por módulo
├── tests/                      pytest, 47 tests al cierre de Semana 1
├── docs/
│   ├── ARCHITECTURE.md         Arquitectura actual
│   ├── PLAN_TRABAJO.md         Fases y calendario
│   ├── ADVISOR.md              Rol de Claude Opus 4.7 como advisor
│   ├── BDS.md                  Las tres BDs inviolables
│   ├── ESTILO_PGK.md           Reglas de redacción
│   └── architecture/
│       └── adrs/               ADR-001 a ADR-006
├── archivo/                    Código y docs archivados con README y fecha
│   └── README.md
├── data/                       BDs locales (memoria_operativa.db, engram.db)
│   └── .gitkeep
└── scripts/                    Utilidades puntuales (no son código de producto)
```

Principios de esta estructura:

- `src/pgk_operativa/` es el único lugar donde vive código de producto.
- `tests/` espeja la estructura de `src/`.
- `docs/architecture/adrs/` recoge decisiones arquitectónicas con formato ADR.
- `archivo/` guarda lo que se migra desde los siete repos origen, con README que explique que era, de donde vino y en que fecha se archivo.
- `data/` es local a cada máquina. No se commitea. Se recrea con migraciones.
- `scripts/` son utilidades one-off (smoke tests, generadores), no producto.

## 3. Las tres bases de datos inviolables

ADR-006 fija tres BDs. No hay una cuarta. Si aparece la necesidad de un cuarto almacén, se discute en ADR nuevo, no se crea silenciosamente.

### 3.1 pgk_database (Postgres remoto)

- Servidor: 209.74.72.83, puerto 5432, schema `pgk_admin`.
- Acceso: via tunel SSH. Kenyi tiene la clave; cada empleado recibe un rol propio (`emp_<slug>_<uuid4>`).
- Contenido: tablas de negocio (`clientes_pgk`, `expedientes_pgk`, `facturas_pgk`, `tareas`, `fichajes`, `audit_log`, `procedimientos_pgk`, `plazos_aeat_clientes`, etc.).
- Autoridad: única fuente de verdad de datos de negocio operativos.
- Migraciones: Alembic. Nunca `ALTER TABLE` directo.
- Multi-tenant: toda query filtra por `company_id` cuando aplique.
- Backups: H1.4 define la política (snapshots diarios, restore probado mensual).

### 3.2 memoria_operativa.db (SQLite local)

- Path: `<repo>/data/memoria/memoria_operativa.db` en modo dev. Configurable via `PGK_DATA_ROOT` y, en modo wheel, cae a `~/.local/share/pgk_operativa/memoria/memoria_operativa.db`. La resolución exacta vive en `memoria_operativa_path()` de `src/pgk_operativa/core/paths.py`.
- Contenido: memoria de negocio de los nodos LangGraph. Cada nodo guarda aprendizajes, decisiones y contexto relevante al cierre de un caso.
- API: `src/pgk_operativa/core/memoria_operativa.py` (a construir en Semana 2-3).
- FTS5 para busqueda semántica ligera + Bayesian updating para pesos de decisiones.
- NO se versiona. Cada máquina tiene la suya. Puede exportarse a JSON para auditar.

### 3.3 engram.db (SQLite local)

- Path: controlado por Engram MCP.
- Contenido: memoria de desarrollo para agentes IA (Claude Code, Devin, Cursor, etc.).
- Uso: `mem_save` tras cada acción significativa. `mem_context` al iniciar sesión. `mem_session_summary` al cerrar.
- Es complementaria a memoria_operativa.db, no duplicada. Engram = como codificamos. memoria_operativa = como decide el negocio.

## 4. Forma de trabajar: reglas que no se negocian

Ocho reglas. Ninguna es opcional. Todo PR que las incumpla se rechaza sin discusion.

1. **Rutas absolutas runtime.** `Path(__file__).resolve()`. Nunca hardcoded (`/Users/kenyi/...`). Nunca relativas desde cwd. Ver sección 5.
2. **Ana única cara visible.** Los módulos técnicos conservan su nombre interno (`pgk.fiscal`, `pgk.contable`, etc.), pero jamás aparecen en la UI conversacional. El empleado habla con Ana. Ver sección 8.
3. **Consenso opt-in.** Por defecto Ana usa un solo modelo (Z.ai GLM-4.6 via OpenAI SDK). El comando `/consenso` o la flag `--consenso` dispara dos proveedores distintos. Ver sección 7.
4. **Estilo PGK en todo documento.** Sin em-dash (U+2014), sin lineas horizontales decorativas. Dos puntos, comas, parentesis, listas. Ver sección 6.
5. **Archivo, no legacy.** Código o docs viejos van a `archivo/` con README explicando que era y cuando se archivo. Nada se borra. Ver sección 9.
6. **Emails solo borrador.** Todo email sale como draft en IMAP. Kenyi o el empleado autorizado lo revisa y lo envia. Nunca `smtplib.send_message()`. Ver sección 10.
7. **Tres BDs inviolables.** Ver sección 3. Cualquier nuevo almacén requiere ADR.
8. **Protocolo Engram.** Al iniciar: `mem_context`. Tras cada acción significativa: `mem_save`. Al cerrar sesión: `mem_session_summary`.

Para agentes IA: leer `AGENTS.md` y `MEMORY.md` antes de tocar nada. Son la fuente de verdad.

## 5. Rutas absolutas en profundidad

Es la regla que más se incumple por reflejo, por eso tiene sección propia.

### 5.1 Qué significa "absoluta en runtime"

La ruta se calcula en tiempo de ejecución desde el propio archivo, no se escribe fija en el código.

Patron obligatorio (implementado ya en `src/pgk_operativa/core/paths.py`):

```python
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"
DOCS_DIR = REPO_ROOT / "docs"
ARCHIVO_DIR = REPO_ROOT / "archivo"

def data_root() -> Path:
    """REPO_ROOT/data en dev, ~/.local/share/pgk_operativa en modo wheel.
    Respeta PGK_DATA_ROOT si está definida.
    """
    ...

def memoria_operativa_path() -> Path:
    return data_root() / "memoria" / "memoria_operativa.db"
```

Cualquier otro módulo importa desde aquí:

```python
from pgk_operativa.core.paths import data_root, memoria_operativa_path
```

### 5.2 Lo prohibido

- Hardcoded por máquina: `/Users/kenyi/Documents/PGK` o `C:\Users\Maria\PGK`. Si un script necesita una ruta local del usuario, se lee de variable de entorno (`PGK_LOCAL_DOCUMENTS_PATH` en `.env`).
- Relativas desde cwd: `open("data/memoria.db")`, `Path("./knowledge")`. Si el script se ejecuta desde otro directorio, rompe.
- Hardcoded a la máquina de otro agente: `/home/ubuntu/repos/pgk_operativa`. Es la ruta de un sandbox de Devin, no vale para la socia.

### 5.3 Por qué importa

El repo debe clonarse en cualquier máquina (Mac de Kenyi, Linux de la socia, sandbox de Devin, servidor de producción) y funcionar. Si una ruta depende de como se lanzo el script, tarde o temprano alguien presenta un modelo fiscal con el dictamen de otro cliente. El dolor de este bug no es teórico, el .env original de Kenyi tiene `GOOGLE_APPLICATION_CREDENTIALS=/Users/kenyi/...` y ya ha bloqueado a todo el que no es el.

### 5.4 Variables de entorno para rutas específicas de máquina

Tres rutas varian por empleado y se leen de `.env`, no del código:

```
PGK_USER_HOME=/home/socia
PGK_LOCAL_DOCUMENTS_PATH=/home/socia/Documents/PGK
PGK_GOOGLE_CREDENTIALS_PATH=/home/socia/.config/pgk/google_credentials.json
```

El código siempre las lee así:

```python
import os
from pathlib import Path

local_docs = Path(os.environ["PGK_LOCAL_DOCUMENTS_PATH"])
```

Nunca con valor por defecto hardcoded a `/Users/kenyi/...`.

### 5.5 Check automático

El hook pre-commit incluye un grep que busca `/Users/kenyi`, `C:\Users\` o rutas absolutas sospechosas en el código. Si aparece, rechaza el commit. Correrlo a mano:

```bash
uv run pre-commit run --all-files
```

## 6. Estilo PGK para todo documento

ADR-003b. Aplica a dictámenes, emails, informes, contratos, ADRs, README, código markdown, comentarios largos, cualquier texto que salga del repo.

### 6.1 Prohibiciones

- **Em-dash (carácter Unicode U+2014, guion tipográfico largo).** Carácter con aspecto pretencioso. En su lugar: dos puntos, coma, parentesis, lista, o punto y seguido según el caso.
- **Lineas horizontales decorativas.** Nada de `===========`, `----------`, `***********`, ni `---` como separador visual dentro del cuerpo. Usar encabezados, listas o parrafos para separar secciones.
- **Prosa de plantilla.** Repeticiones tipo "el contribuyente... el contribuyente... el contribuyente" en cadena. Variar con "Sr. X", "mi representado", "el interesado", "obligado tributario" según convenga.
- **Transliteraciones degradadas.** Si un documento final se exporta a PDF y pierde tildes o eñes, el PDF no sale. Fuente de verdad siempre UTF-8 completo.
- **Faltas ortográficas.** Revisar antes de entregar cliente. Sin excepciones.

### 6.2 Obligaciones

- Revisar tildes, acentuación, nombres propios y naturalidad antes de entregar.
- Usar como fuente de verdad el documento maestro vigente. No mantener copias paralelas degradadas para exportación.
- Tres pasadas antes de exportar: ortografía, estilo (eliminar repeticiones mecánicas), fidelidad (verificar que el PDF sale del texto correcto).

### 6.3 Por qué

En marzo 2026, un escrito de alegaciones se exporto a Word desde un script que usaba una copia ASCII del texto. Se degradaron acentos, nombres y naturalidad de la redaccion. Cliente lo noto. Desde entonces, prohibido generar documentos finales desde fuentes duplicadas o linguisticamente rebajadas.

## 7. Consenso opt-in y el default Z.ai

ADR-005. El coste de cada llamada importa. Multiplicar por dos modelos cada respuesta de Ana dispara la factura mensual de 150-250 USD a 500-700 USD.

### 7.1 Default (sin flag)

Una sola llamada a Z.ai GLM-4.6 via OpenAI SDK:

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["ZAI_API_KEY"],
    base_url="https://api.z.ai/api/coding/paas/v4",
)
resp = client.chat.completions.create(
    model="glm-4.6",
    messages=[{"role": "user", "content": pregunta}],
)
```

Ventajas: barato, rápido, sin cableado entre SDKs.

### 7.2 Con `--consenso` o `/consenso`

Dispara un subgrafo que llama a dos proveedores distintos en paralelo. El sintetizador compara y produce respuesta única con nivel de acuerdo.

Restricción de runtime: `assert provider_A != provider_B and model_A != model_B`. Si falla, `consensus_type = "single_model"` y se avisa en la respuesta.

Providers válidos para consenso: Z.ai, Anthropic (API propia o proxy Z.ai Anthropic-compatible), Gemini, Groq, DeepSeek, Perplexity.

### 7.3 Cuando activar consenso

Gatillos recomendados:
- Decisión fiscal con incertidumbre normativa (IRNR compleja, convenios de doble imposicion).
- Escrito legal a AEAT con plazo corto.
- Dictamen para cliente nuevo sin precedentes en memoria.
- Cuando la respuesta de Ana no convence al empleado y quiere segunda opinion.

En el resto, default single-model es más que suficiente.

### 7.4 CLI

```bash
uv run pgk ana "que IVA aplica a Amazon UE"          # default, un modelo
uv run pgk ana --consenso "como declarar IRNR 2025"  # dos modelos
```

En Mattermost: mensaje normal para default, prefijo `/consenso ` para dos modelos.

## 8. Ana única cara visible

ADR-002. Regla estricta.

### 8.1 Qué ve el empleado

Una sola interfaz: Ana. En CLI, en Mattermost, en email, siempre Ana. Nunca ve "Gran Dragón contestando", "Cecilia enrutando", "Edu procesando". La personalidad es siempre Ana.

### 8.2 Qué pasa por dentro

El router (`src/pgk_operativa/core/router.py`) clasifica la consulta en un módulo técnico:

```
pgk.fiscal      impuestos, IRNR, modelos AEAT
pgk.contable    facturas, balance, PGC 2008
pgk.laboral     nominas, seguridad social, convenios
pgk.legal       derecho, sentencias, procedimientos
pgk.docs        redaccion, plantillas, formateo
pgk.calidad     limpieza de codigo, revision
pgk.marketing   SEO, contenido, outbound
pgk.consejo     decisiones estrategicas (7 consejeros)
pgk.forja      seguridad, codegen, refactor
pgk.workflows   orquestacion operativa (5 copilots)
```

La clasificación usa primero keywords (rápido, 0 LLM), luego fallback LLM (Z.ai) si no hay match claro. El nodo ejecutor del módulo recibe la consulta, la procesa con los prompts de personalidad (conservamos los nombres: Gran Dragón, Edu, Jennifer, German, etc. como personajes internos cargados por Ana), y devuelve la respuesta.

### 8.3 Qué muestra el CLI

Por defecto solo `respuesta_final`. Los campos `modulo_tecnico` y `razonamiento_clasificacion` quedan en el audit_trail para diagnóstico, pero no se imprimen.

Flag de debug (no público): `--debug` muestra todo. Útil para desarrollo; jamás para empleado en operación.

### 8.4 Por qué unificamos así

Porque el empleado no sabe ni tiene que saber si está hablando con el módulo fiscal o con el contable. Pregunta en lenguaje natural, Ana decide. Si mañana reemplazamos un prompt de Gran Dragón por uno mejor, el empleado no se entera. Esto reduce fricción y permite refactorizar módulos internos sin romper UX.

## 9. Archivo en lugar de legacy

ADR-003. Cuando migremos código de los siete repos origen (o del portal), lo que no se reutiliza no se borra, se mueve a `archivo/`.

### 9.1 Estructura de `archivo/`

```
archivo/
├── README.md                                  Explica que hay aqui
├── portal_frontend_snapshot_2026-04/          React+Vite del portal (no se reusa)
│   ├── README_ARCHIVO.md                      De donde vino, cuando se archivo, por que
│   └── ...                                    contenido tal cual
├── PGK_Empresa_Autonoma_nodos_py_2026-04/     nodos.py 3844 LoC original
│   ├── README_ARCHIVO.md
│   └── nodos.py
├── pgk-laboral-desk_engine_2026-04/
│   ├── README_ARCHIVO.md
│   └── engine.py
└── ...
```

### 9.2 Regla del README_ARCHIVO.md

Cada subcarpeta de `archivo/` tiene un README_ARCHIVO.md mínimo con:
- Que era (1 parrafo).
- De que repo origen vino (URL + commit hash si disponible).
- Fecha de archivo.
- Por que no se reutiliza (1 parrafo).
- Que se reutilizo en su lugar y donde vive ahora en `src/pgk_operativa/`.

### 9.3 Por qué "archivo" y no "legacy"

Connotacion. "Legacy" suena a deuda, a cosa que habria que haber borrado ya. "Archivo" es neutro, profesional, consultable. Un archivo no se descarta, se consulta. La socia o Kenyi pueden en cualquier momento entrar en `archivo/` y recuperar lógica, ejemplos, prompts.

## 10. Emails siempre borrador

Regla de hierro. Ningún agente envia emails directamente.

### 10.1 Qué hacemos

Integración IMAP que guarda mensajes en `INBOX.Drafts` de la cuenta correspondiente:

```python
from pgk_operativa.integrations.email import guardar_borrador

guardar_borrador(
    cuenta="klient",
    para="cliente@example.com",
    asunto="Modelo 210 IRNR 2025",
    cuerpo=cuerpo_con_estilo_pgk,
    adjuntos=[path_dictamen_pdf],
)
```

El empleado entra en el webmail (Roundcube, Thunderbird, etc.), revisa el borrador, y lo envia cuando quiera.

### 10.2 Lo prohibido

- `smtplib.send_message()`, `smtplib.sendmail()`, `smtp.send()`.
- Cualquier libreria que envie directamente.
- MCP tools que envien (si aparece uno, se deshabilita).

### 10.3 Cuentas de email

Seis cuentas en pgkhiszpania.com y una en bizneswhiszpanii.com:

- info@pgkhiszpania.com: contacto general.
- admin@pgkhiszpania.com: administracion interna.
- klient@pgkhiszpania.com: clientes activos.
- rejestracja@pgkhiszpania.com: alta nuevos.
- biznes@pgkhiszpania.com: propuestas B2B.
- contabilidad@pgkhiszpania.com: contabilidad.
- biznes@bizneswhiszpanii.com: polaco, marca secundaria.

Cada una con credenciales IMAP en `.env`.

### 10.4 Por qué

Un email enviado no se puede retirar. Un borrador si. Incluso con IA impecable, la responsabilidad final es humana. Esto encaja con el principio de HITL obligatorio para todo output que salga hacia cliente.

## 11. Requisitos mínimos de la máquina

### 11.1 Sistema operativo

- macOS 13+ (Kenyi) o Linux reciente (socia, servidor).
- Windows tecnicamente soportado via WSL2, no nativo. Si hay que trabajar en Windows, se instala Ubuntu en WSL2 y se trabaja ahí.

### 11.2 Software base

- Python 3.12 (no 3.13, no 3.11). Gestionado por `uv`.
- `uv` (astral-sh/uv): gestor de deps en Rust. Instalación:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- Git 2.40+.
- SSH cliente (para tunel Postgres).
- Docker opcional (para Postgres local de desarrollo si no hay acceso remoto).

### 11.3 Dependencias opcionales

- `age` (FiloSottile/age): cifrado de `.env` cuando el empleado lo recibe. Via brew (`brew install age`) o apt (`apt install age`).
- `pre-commit`: se instala automáticamente con `uv sync --dev`.

### 11.4 Accesos que deben estar provisionados

| Acceso | Quien lo provisiona | Estado |
|---|---|---|
| Clave SSH autorizada en 209.74.72.83 | Kenyi | Pendiente para la socia |
| Rol Postgres propio (`emp_<slug>_<uuid4>`) | Kenyi via admin_empleados.py | Pendiente |
| `ZAI_API_KEY` en `.env` | Kenyi | En su `.env` maestro |
| Resto de claves LLM (opcional, solo si usa consenso) | Kenyi | En su `.env` maestro |
| Credenciales IMAP de al menos una cuenta | Kenyi | En su `.env` maestro |
| Token GitHub con permisos en POLSKA-GRUPA | Kenyi | En su `.env` maestro |
| Acceso al repo pgk_operativa | Kenyi | Actualmente público, pasara a privado |

### 11.5 Recursos hardware

- 8 GB RAM mínimo, 16 GB recomendado. LangGraph + múltiples SDKs LLM a la vez consume.
- 20 GB de disco libres (incluye docs, BDs locales, y cache de uv).
- Conexión estable. Los LLMs responden mejor con baja latencia.

## 12. Onboarding paso a paso (de cero a primer pgk ana)

Tiempo esperado: 30 minutos si ya hay Mac/Linux con Python y SSH listos. Hasta 1 hora si es máquina nueva.

### 12.1 Clonar el repo

```bash
cd ~
git clone https://github.com/POLSKA-GRUPA/pgk_operativa.git
cd pgk_operativa
```

### 12.2 Instalar uv si no está

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Reiniciar terminal o source ~/.bashrc
```

### 12.3 Crear `.env` a partir de la plantilla

```bash
cp .env.example .env
```

Editar `.env` con los valores reales que Kenyi habra facilitado por canal seguro (age-encrypted en el futuro, por WhatsApp encriptado o 1Password hoy). Claves mínimas para arrancar:

```
PGK_USER_HOME=/home/socia
PGK_LOCAL_DOCUMENTS_PATH=/home/socia/Documents/PGK
PGK_GOOGLE_CREDENTIALS_PATH=/home/socia/.config/pgk/google_credentials.json
ZAI_API_KEY=sk-zai-...
```

El resto (Postgres, otros LLMs, emails) se rellena cuando se vaya necesitando.

### 12.4 Instalar dependencias

```bash
uv sync --all-extras --dev
```

Crea `.venv/` con Python 3.12 y todas las deps reproducibles desde `uv.lock`.

### 12.5 Instalar pre-commit

```bash
uv run pre-commit install
```

Esto activa los hooks locales. Cada `git commit` pasara ruff + mypy + check estilo PGK + check rutas absolutas.

### 12.6 Verificar que todo funciona

```bash
uv run pytest -q
```

Debe salir `47 passed`.

```bash
uv run pgk doctor
```

Revisa que el `.env` tiene lo mínimo y que los providers LLM responden. Al menos Z.ai debe estar verde.

### 12.7 Primera consulta a Ana

```bash
uv run pgk ana "hola Ana, que es el IRNR?"
```

Debe devolver una respuesta conversacional sobre IRNR. Sin mostrar el módulo técnico que contesto.

### 12.8 Si algo falla

- `uv sync` falla por versión Python: instalar `uv python install 3.12` y reintentar.
- `pgk doctor` dice que falta ZAI_API_KEY: revisar `.env`, confirmar que el archivo está en la raíz del repo y tiene la clave sin espacios.
- `pgk ana` da un error de red: comprobar conectividad a `api.z.ai`. Algunas redes corporativas bloquean.
- `pytest` falla: leer el output, confirmar que se está en rama `main` actualizada (`git pull`), reintentar.

Si nada de lo anterior resuelve, abrir Issue en GitHub o avisar a Kenyi directamente.

## 13. Flujo Git y política de PRs

### 13.1 Ramas

- `main`: siempre verde, siempre mergeable, protegida.
- `devin/<timestamp>-<descripcion>`: ramas de trabajo de Devin.
- `socia/<descripcion-corta>`: ramas de la socia. Ejemplo: `socia/modulo-fiscal-inicial`.
- Nunca commitear directo a main. Nunca force push a main.

### 13.2 Commits

Mensaje convencional:

```
<tipo>(<area>): <resumen corto imperativo>

<cuerpo opcional con contexto>
```

Tipos válidos: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`, `style`.

Ejemplos reales del repo:

```
feat(semana-1): grafo minimo con Ana router y ejecutor generico
fix(router): nodo_ana_router maneja excepciones del LLM con fallback a general
docs(handoff): manual de traspaso para la socia
```

### 13.3 Pull Requests

- Abrir PR contra `main` desde rama propia.
- Título conciso y descriptivo.
- Cuerpo: que cambia, por que cambia, como probar. Una sección "Riesgos" si hay efecto no trivial.
- Esperar CI verde antes de pedir review.
- Esperar 0 findings de Devin Review (si aplica).
- Merge solo después de OK explicito de Kenyi o cuando Semana 2+ la socia tenga autoridad delegada.
- Borrar rama remota tras merge para no acumular ruido.

### 13.4 CI

GitHub Actions en `.github/workflows/ci.yml`. Python 3.12. Pasos:

1. Checkout.
2. Setup uv.
3. `uv sync --all-extras --dev`.
4. `uv run ruff check .`.
5. `uv run ruff format --check .`.
6. `uv run mypy src/pgk_operativa`.
7. Checks de estilo PGK (grep em-dash en docs y código fuera de `.venv/`).
8. Checks de rutas absolutas (grep `/Users/`, `C:\\Users`).
9. `uv run pytest -q`.

Todo debe salir verde para que Kenyi mergee.

### 13.5 Nunca hacer

- `git push --force` en `main`.
- `git commit --no-verify` salvo emergencia documentada.
- Modificar `main` directamente desde la UI de GitHub.
- Borrar archivos sin ADR si son código o docs con historia.

## 14. Estado actual: Semana 1 cerrada

### 14.1 Hecho

- **Semana 0 (Scaffolding):** `pyproject.toml`, estructura `src/pgk_operativa/`, CI, `.env.example`, ADRs 001 a 006, pre-commit, README/AGENTS/MEMORY. Merge via PR #1.
- **Semana 1 (Grafo mínimo):**
  - Estado tipado LangGraph.
  - Router Ana con keywords + fallback LLM Z.ai.
  - Ejecutor genérico que llama a Z.ai con prompt skeleton por módulo.
  - CLI `pgk ana "<pregunta>"` end-to-end.
  - 47 tests (core, CLI, routing, graph skeleton).
  - 3 bugs detectados por Devin Review y corregidos en la misma PR:
    - `ts` como keyword con trailing space rompia matching por word-boundary.
    - Parser LLM concatenaba `"fiscal (impuestos)"` a `"fiscalimpuestos"`.
    - `nodo_ana_router` no manejaba excepciones del LLM; ahora cae a `general` con audit_trail.
  - Merge via PR #2.

### 14.2 Repo al cierre

- Rama `main` en `3d70d5a`.
- CI verde en Python 3.12.
- Public temporalmente (pasara a privado tras cerrar scope). El .env está fuera del repo y nunca se commitea.

### 14.3 Quedan pendientes inmediatos (asumibles por la socia)

- Integrar módulos reales en `src/pgk_operativa/nodos/`:
  - `fiscal.py` (rescate de `PGK_Empresa_Autonoma/src/agents/nodos.py` y prompts `pgk-irnr-specialist.md`).
  - `contable.py` (rescate de `conta-pgk-hispania` CFO Agent y sus tools).
  - `laboral.py` (rescate de `pgk-laboral-desk` motor determinista).
  - `legal.py` (rescate de `junior` skills legales).
  - `docs.py`, `calidad.py`, `marketing.py`.
- Construir subgrafo consenso opt-in real (`src/pgk_operativa/core/consenso.py`).
- Arrancar H1.1 (testing + CI robustecido) y H1.2 (seguridad + secrets management) en paralelo a la descomposicion de nodos.

## 15. Hoja de ruta Semana 2 a Semana 6

Plan calendario. Cada semana cierra con PR mergeado y tests verdes.

### Semana 2: Descomposicion de nodos y consenso real

Objetivos:
- Mover `nodos.py` original (3844 LoC) de PGK_Empresa_Autonoma a 8 módulos en `src/pgk_operativa/nodos/`, conservando prompts en `src/pgk_operativa/prompts/core/`.
- Implementar subgrafo consenso opt-in con dos proveedores y sintetizador.
- Tests por módulo, goldens con respuestas esperadas.

Entregable verificable: `pgk ana --consenso "<pregunta fiscal compleja>"` contesta con los dos modelos y sintesis.

### Semana 3: Integraciones core + H1.1-H1.3

Objetivos:
- Integrar Consejo de Dirección (7 consejeros de `PGK-direccion-general`).
- Integrar Forja (REVISOR_UNIFICADO + Trail of Bits).
- Integrar módulo laboral real (motor determinista).
- Integrar módulo legal real (17 skills de junior).
- Integrar módulo contable real (CFO Agent + tools).
- H1.1 (testing): coverage >70%, tests de integración en Postgres staging.
- H1.2 (seguridad): secrets management, rotacion, audit.
- H1.3 (RGPD): inventario de datos personales, DPA con proveedores.

Entregable verificable: 5 casos fiscales/laborales/legales end-to-end.

### Semana 4: H1.4-H1.7 + 5 workflows Copilot + memoria operativa

Objetivos:
- H1.4 (backups): snapshot diario Postgres, restore probado.
- H1.5 (actualizador conocimiento): cron que sube novedades BOE/DGT/TEAC.
- H1.6 (continuidad): runbook DR, staging identico a prod.
- H1.7 (portabilidad): exportador completo a JSON/Markdown.
- Migrar 5 workflows Copilot de `portal/` a `src/pgk_operativa/workflows/`:
  - `modelo_210`
  - `contestacion_hacienda`
  - `alta_autonomo`
  - `revision_trimestral`
  - `preparar_contrato`
- Construir memoria operativa (SQLite FTS5 + Bayesian updating).

Entregable verificable: coverage 80%, memoria persistente entre sesiones, los 5 workflows ejecutables.

### Semana 5: Distribución + piloto

Objetivos:
- Adenda v1.7 implementada: bundle tufup, cifrado `.env.age`, `install.sh` one-liner, wrapper `pgk`.
- Onboarding Kenyi + 1 empleado (probablemente Francisco o la socia).
- Mattermost conectado con canal por empleado.

Entregable verificable: Kenyi + 1 empleado operando desde distinta máquina sin tocar repo directamente.

### Semana 6+: Operaciones

Objetivos:
- Fase 12 AOD: 3 workflows prioridad 1 corriendo (triage email, resumen diario, limpieza mantenimiento).
- Adenda v1.8: Guardia Integridad y Guardia Plazos activas.
- Primeros casos reales de clientes pasando 100% por pgk_operativa.

Entregable verificable: 7 días seguidos de operación sin incidencia grave.

## 16. H1 Fundaciones Enterprise en detalle

H1 es paralelo a Semanas 3-4. Siete subfases:

- **H1.1 Infraestructura de calidad.** pytest configurado, tests unitarios de capa datos, integración contra Postgres staging, coverage >80%, ruff + mypy strict en CI, Semgrep sast-mcp integrado. Sin esto, cada cambio es Russian roulette.
- **H1.2 Seguridad.** Rotacion de claves cuatrimestral, secrets management centralizado, auditoría en Postgres (`audit_log` append-only), RLS por `company_id`, cifrado de `.env` de empleado con age.
- **H1.3 RGPD.** Inventario de datos personales por cliente, DPA firmado con cada proveedor LLM, política de retencion (4 años prescripcion fiscal, más lo mínimo RGPD en `99_Archivo_Muerto`).
- **H1.4 Calidad IA.** Goldens por módulo (respuestas esperadas verificadas), evals semanales en `evaluation/`, alertas si confidence cae >10%, HITL obligatorio en output hacia cliente.
- **H1.5 Actualizador de conocimiento.** Cron semanal que descarga BOE, DGT, TEAC, resume cambios, propone updates a prompts y Engram. Kenyi aprueba con `/actualizador aprobar N`.
- **H1.6 Continuidad.** Runbook DR escrito, staging identico a prod, simulacro de caida trimestral.
- **H1.7 Portabilidad.** Exportador completo a JSON/Markdown, replica del sistema clonable en nueva máquina en <1h.

Cada subfase tiene criterios de hecho medibles. Ninguna se da por cerrada sin verificación.

## 17. Fase 12 AOD: 15 workflows de operativa diaria

Automatización operativa diaria. Libera 50-75h/mes de rutina. Prioridad 1 antes de incorporar primer empleado.

### 17.1 Arquitectura común

Cada workflow se declara en YAML en `scripts/workflows/<nombre>.yaml`. Un runner en `scripts/workflows/_core/runner.py` interpreta el YAML y orquesta. Añadir workflow nuevo = escribir YAML, no código.

Ejemplo:

```yaml
nombre: workflow_triage_email
trigger:
  tipo: evento
  fuente: email_nuevo
  cuentas: [info, admin, klient]
modos_activo: [normal, intenso]
agentes:
  - nombre: Paloma
    rol: clasificador
  - nombre: agente_extractor
    rol: extraccion_datos
acciones:
  - crear_tarea_si: requiere_accion
  - generar_draft_si: necesita_respuesta
  - notificar_mattermost: siempre_con_resumen
hitl:
  envio_cliente: aprobacion_kenyi
  accion_interna: ninguna
timeout: 300s
logs: structured
```

### 17.2 Catalogo por prioridad

**Prioridad 1 (antes de incorporar primer empleado):**
1. `workflow_limpieza_mantenimiento`: cron semanal domingo 02:00. Rota logs, vacuum Postgres, reindex, archiva expedientes cerrados.
2. `workflow_resumen_diario`: cron diario 08:00. Resumen conversacional al Mattermost con lo importante.
3. `workflow_triage_email`: evento email nuevo. Clasifica, crea tarea, genera draft. HITL envio.

**Prioridad 2:**
4. `workflow_recordatorio_plazos_aeat`: cron diario 07:00. Cruce calendario AEAT con expedientes activos.
5. `workflow_deteccion_riesgos`: cron 03:30. Detecta fichajes incompletos, tareas huerfanas, facturas >60d sin cobro.
6. `workflow_factura_drop`: evento Drive. OCR + clasificación reparacion/mejora + registro en BD.

**Prioridad 3:**
7. `workflow_sede_aeat`: cron 4h. Acceso a Sede Electrónica AEAT via certificado, descarga notificaciones, crea tarea con plazo.
8. `workflow_cobros`: cron diario 09:00. Escalado facturas >30/60/90d.
9. `workflow_seguimiento_cliente_inactivo`: cron quincenal. Detecta inactivos >60d y propone draft.

**Prioridad 4:**
10. `workflow_onboarding_cliente_nuevo`: comando `/cliente-nuevo`. Crea carpeta Drive, FICHA_MAESTRA.json, email bienvenida, checklist.
11. `workflow_dictamen_mensual_cliente`: cron mensual día 1. Dictamen por cliente con servicio mensual.

**Prioridad 5:**
12. `workflow_monitor_linkedin_empleado`: cron semanal. Resumen privado por empleado.
13. `workflow_actualizador_conocimiento`: ya en H1.5.
14. `workflow_desactivacion_cliente_inactivo`: cron mensual. Detecta >18 meses inactivo y propone archivar.
15. `workflow_consolidacion_memoria`: cron mensual día 28. Revisa Engram, detecta duplicados y contradicciones.

### 17.3 Criterios de hecho Fase 12

- Los 3 workflows prioridad 1 corriendo >7 días sin fallar.
- Kenyi confirma reduccion real de tiempo en rutina diaria.
- Los modos de operación (`/modo intenso`, `/modo vacaciones`) funcionan y cambian comportamiento observable.
- `scripts/workflows/README.md` completo con ejemplos de añadir workflow.

## 18. Adenda v1.7: distribución a empleados

Los empleados de PGK son oficinistas, no desarrolladores. `git clone`, `gh auth login`, PRs están fuera de su vocabulario. El sistema de distribución tiene que ser one-liner y silencioso.

### 18.1 Arquitectura

```
Servidor PGK (209.74.72.83) -- unica fuente de verdad
├── /pgk-dist/                                    bundles firmados
│   ├── pgk-workstation-v1.0.0.tar.gz             tufup bundle
│   ├── pgk-workstation-v1.0.0.tar.gz.sig
│   ├── 1.root.json                               metadata TUF
│   └── latest.json                               version actual
├── /onboarding/<email>.env.age                   .env cifrado por empleado
├── /install                                      bootstrap one-liner
└── /pub/root.key                                 clave publica verificar firmas
```

### 18.2 Lado Kenyi (alta de empleado)

```
$ python admin_empleados.py alta \
    --email socia@pgkhiszpania.com \
    --nombre "Maria Socia"
  Rol Postgres creado: emp_socia_7b2f4c91-3a8e-4d67-b5c1-9f2e8d3a1b4c
  Usuario SSH en servidor: emp_socia_7b2f4c91-3a8e-4d67-b5c1-9f2e8d3a1b4c
  .env.age generado y subido
  Comando para WhatsApp generado
```

### 18.3 Lado empleado (una linea)

```bash
curl -fsSL https://pgk.pgkhiszpania.com/install | sh
```

Ese script hace:
- Instala uv si falta.
- Instala age si falta.
- Descarga tufup bundle más reciente.
- Verifica firma con `/pub/root.key`.
- Descomprime a `~/PGK/`.
- Pide email, descarga `.env.age`.
- Pide password age (recibida por WhatsApp), descifra `.env`.
- Instala wrapper `pgk` en `/usr/local/bin`.
- Lanza primera sesión conversacional de onboarding (Fase 10a).

### 18.4 Actualizaciones posteriores

Silenciosas. Cada vez que el empleado ejecuta `pgk`, el wrapper comprueba `/pgk-dist/latest.json`, si hay versión nueva la descarga, verifica firma, reemplaza, y continua. Sin preguntas al empleado.

### 18.5 Código propio para esto

Solo 120 lineas + 2 archivos de configuración. El resto lo hace tufup, age, uv, Claude Code. Componer, no construir.

## 19. Adenda v1.8: Guardia Integridad y Guardia Plazos

Dos subsistemas que viven como workflows nocturnos, llegan a Mattermost.

### 19.1 Guardia Integridad

Problema: empleado trabaja con Claude Code sobre un cliente (mencionando NIF o nombre), pero ese cliente no tiene ficha en `clientes_pgk` ni `FICHA_MAESTRA.json` en Drive. Trabajo queda huerfano.

Solución: `scripts/workflows/guardia_integridad.py`, nocturno. Consulta observations Engram últimas 24h, extrae NIFs con regex `[XYZ]?[0-9]{7,8}[A-Z]`, extrae nombres con Haiku barato, cruza con `clientes_pgk.nif` y `FICHA_MAESTRA.json`. Clasifica en Conectado / Parcial / Huerfano. Mensaje Mattermost agrupado con comandos para regularizar (`/integridad crear <NIF>`, `/integridad reconstruir-drive <NIF>`).

Código propio: 60 lineas Python.

### 19.2 Guardia Plazos

Tres niveles:

- **Plazos internos PGK (acuerdos con cliente):** tabla `procedimientos_pgk` con códigos tipo `DICTAMEN_IRNR`, `REQUERIMIENTO_AEAT`. Al crear expediente, sistema calcula `fecha_vencimiento` sumando días hábiles, crea tareas por hito con sus propias fechas, y genera alertas según `alertas_default` (`[7,3,1]`).
- **Plazos legales AEAT (no negociables):** archivo `data/calendario_aeat.yaml` con todas las fechas del año (modelos 111, 303, 390, 720, etc.). Cron actualizador anual que scrapea Sede Electrónica y alerta si hay cambios.
- **Microplazos de workflow:** los que genera cada workflow según necesidad (revisión Kenyi antes de envio, seguimiento cliente tras 7d sin respuesta, etc.).

Todas las alertas acaban en Mattermost con prioridad visual (roja <10d, amarilla <30d, verde resto).

### 19.3 Dependencias

- Guardia Integridad requiere Engram activo y `clientes_pgk` poblada.
- Guardia Plazos requiere `procedimientos_pgk` y `plazos_aeat_clientes` migradas.
- Ambas activas en Semana 6+.

## 20. Qué hace y qué NO hace pgk_operativa

### 20.1 Hace

- Cerebro único conversacional para fiscal, contable, laboral, legal, docs, calidad, marketing, consejo, forja y workflows.
- Enrutamiento silencioso via Ana a módulo técnico.
- Consenso multimodelo opt-in.
- Memoria operativa persistente entre sesiones.
- Memoria de desarrollo via Engram.
- 5 workflows Copilot validados (modelo_210, contestacion_hacienda, alta_autonomo, revision_trimestral, preparar_contrato).
- 15 workflows AOD (en Semana 6+).
- Guardia Integridad y Guardia Plazos.
- Distribución one-liner a empleados.
- Generación de dictámenes y documentos via formateador oficial WeasyPrint.
- Integración Postgres remoto, IMAP, Google Drive, Notion, Mattermost.

### 20.2 NO hace

- Front-end. Ningún portal web ni dashboard. Ni para cliente, ni para empleado, ni para admin.
- Migración automática de facturas historicas. Cada cliente se carga a mano con HITL.
- Reescribir motor laboral. Se reutiliza el de `pgk-laboral-desk` tal cual.
- Integrar sistemas fuera del consolidado (Holded, Quipu, etc.) salvo ADR nuevo.
- Enviar emails directamente. Siempre borrador.
- Refactorizar los siete repos origen. Ellos se quedan como están, pgk_operativa absorbe lo valioso.
- App movil nativa. El movil es Mattermost.
- OCR pesado propio. Se usan MCP tools existentes.
- Billing/ERP propio. Se integra con existente de Kenyi.

Cualquier cosa que no este en 20.1 y alguien proponga, requiere ADR nuevo con justificacion explicita.

## 21. Decisiones tomadas (ADRs) y decisiones pendientes

### 21.1 ADRs activos

- **ADR-001 stack-python-langgraph:** Python 3.12 + LangGraph + FastAPI + uv.
- **ADR-002 ana-única-sin-rebranding:** Ana cara visible, prompts conservan nombres (Gran Dragón, Edu, Jennifer, German) pero no se exponen.
- **ADR-003 archivo-no-legacy:** `archivo/` con README fecha. Nada se borra.
- **ADR-004 rutas-absolutas-runtime:** `Path(__file__).resolve()`, nunca hardcoded.
- **ADR-005 consenso-opt-in:** `/consenso` opt-in, default single-model Z.ai.
- **ADR-006 tres-bds-inviolables:** pgk_database remoto, memoria_operativa.db local, engram.db local.

### 21.2 ADRs pendientes de redactar

- **ADR-007 estilo-pgk-formalizado:** sin em-dash, sin lineas horizontales, reglas de redaccion.
- **ADR-008 emails-solo-borrador:** IMAP Drafts, prohibicion SMTP send.
- **ADR-009 modos-operación-adaptativos:** normal / intenso / vacaciones / pánico.
- **ADR-010 distribución-tufup-age:** arquitectura de distribución a empleados.
- **ADR-011 guardias-integridad-plazos:** subsistemas v1.8.

### 21.3 Decisiones abiertas que la socia puede cerrar

- **D1 Deployment.** Blue/green 17 días vs ventana madrugada 2h. Mi voto CTO: blue/green (más lento pero 0 downtime). Depende de disponibilidad servidor.
- **D2 Nombres internos.** Mantener "Gran Dragón", "Edu", "Jennifer", "German" en prompts (solo internos, nunca visibles al empleado) o neutralizar. Mi voto: mantener, dan personalidad a los prompts y no se filtran.
- **D3 SSH vs WireGuard para acceso remoto empleados a Postgres.** SSH es estándar, WireGuard es más moderno. Mi voto: SSH (ya funciona, menos movimiento).
- **D4 Privatizar repo.** Decisison de Kenyi post-launch. No bloquea desarrollo.

## 22. Glosario

- **Ana:** cara visible conversacional. Única interfaz para empleados y clientes.
- **ADR:** Architecture Decisión Record. Documento corto que fija una decisión.
- **AOD:** Automatización Operativa Diaria. Conjunto de workflows que liberan tiempo rutinario.
- **Claude Code:** entorno de desarrollo basado en Claude que los empleados tendrán instalado.
- **CLI:** interfaz de linea de comandos. `pgk ana`, `pgk doctor`.
- **Consenso:** modo opt-in donde dos LLMs distintos responden y un sintetizador produce respuesta única.
- **Copilot Gestoria:** motor de workflows declarativos rescatado del portal. 5 validados.
- **DeLLMa:** algoritmo de decisión bajo incertidumbre. Usado por Consejo de Dirección.
- **Engram:** sistema de memoria persistente para agentes IA. MCP server propio.
- **Formateador oficial:** pipeline WeasyPrint en `external/formateador/` que genera PDFs con estilo PGK.
- **Goldens:** respuestas esperadas de referencia para evaluacion de modelos.
- **Grafo:** DAG de LangGraph que orquesta el flujo Ana -> router -> módulo -> respuesta.
- **Guardia Integridad:** workflow nocturno que detecta clientes mencionados sin ficha.
- **Guardia Plazos:** workflow que vigila vencimientos internos y AEAT.
- **H1:** Horizonte 1, seis meses. Fundaciones Enterprise.
- **HITL:** Human-in-the-loop. Aprobacion humana obligatoria en outputs sensibles.
- **Mattermost:** canal de mensajeria interno. Sustituto del dashboard.
- **MCP:** Model Context Protocol. Mecanismo para que los LLMs usen tools externos.
- **Memoria operativa:** SQLite local, memoria de negocio de los nodos LangGraph.
- **Modo operativo:** variable global (normal / intenso / vacaciones / pánico) que ajusta cadencia.
- **pgk_database:** Postgres remoto en 209.74.72.83. Única fuente de verdad de datos de negocio.
- **PGC 2008:** Plan General Contable español. Marco para todas las cuentas contables.
- **Sede Electrónica:** portal AEAT para notificaciones y requerimientos.
- **sintetizador:** nodo que combina dos respuestas LLM en consenso.
- **tufup:** The Update Framework wrapper para auto-update firmado de apps Python stand-alone.
- **ULTRAPLAN / SUPERPLAN:** documento maestro v1.8, define arquitectura completa.
- **uv:** gestor de deps Python en Rust. Reemplaza venv + pip.
- **WeasyPrint:** motor HTML+CSS a PDF usado para dictámenes.
- **Z.ai:** proveedor LLM primario. GLM-4.6 via OpenAI SDK.

## 23. Troubleshooting frecuente

### 23.1 `uv sync` no instala Python 3.12

```bash
uv python install 3.12
uv sync --all-extras --dev
```

### 23.2 `pgk doctor` dice que ZAI_API_KEY falta

`.env` en la raíz del repo, sin espacios alrededor del `=`, sin comillas. Ejemplo:

```
ZAI_API_KEY=sk-zai-abc123
```

Ni `ZAI_API_KEY = "sk-..."` ni `ZAI_API_KEY= sk-...`.

### 23.3 Postgres: `connection refused`

El tunel SSH no está levantado. Levantarlo:

```bash
ssh -N -L 5432:127.0.0.1:5432 \
    -i ~/.ssh/id_rsa \
    <PGK_SSH_USER>@209.74.72.83
```

Dejar corriendo en otro terminal. Si el CLI lo automatiza via `sshtunnel`, ignorar.

### 23.4 CI falla con "Job is waiting for a hosted runner"

Org POLSKA-GRUPA sin billing configurado para Actions en repos privados. Solución temporal: repo público. Solución definitiva: añadir método de pago en https://github.com/organizations/POLSKA-GRUPA/billing.

### 23.5 Pre-commit rechaza por em-dash

Se ha metido un guion largo U+2014 en código o docs. Buscar y reemplazar por dos puntos, coma o parentesis según convenga:

```bash
rg -n $'\u2014' docs/ src/ tests/
```

### 23.6 Pre-commit rechaza por ruta absoluta

Se ha metido `/Users/kenyi` o similar en código. Reemplazar por `Path(__file__).resolve()` o por lectura de variable de entorno:

```python
import os
from pathlib import Path

docs_path = Path(os.environ["PGK_LOCAL_DOCUMENTS_PATH"])
```

### 23.7 Test `test_nodo_ana_router_*` falla

Comprobar que la rama está actualizada (`git pull origin main`). Los tests del router se escribieron para la versión actual del parser. Tests viejos en ramas antiguas pueden fallar.

### 23.8 `pgk ana` devuelve error LLM en frío

Z.ai puede tardar en despertar. Reintentar. Si persiste, `pgk doctor` detalla que provider responde y cual no. Si solo falla Z.ai, usar `--consenso` o esperar.

## 24. Contactos y canales

- **Kenyi (CEO).** Decisión final en todo lo estratégico. Disponibilidad alta en horario laboral europeo.
- **Claude Opus 4.7 (advisor).** Rol de senior advisor, revisa handoffs semanales. Ver `docs/ADVISOR.md`.
- **Devin (agente IA).** Implementador autónomo. Sesiones visibles en https://app.devin.ai/.
- **Mattermost PGK.** Canal interno. Será el punto principal de comunicación una vez distribuido.
- **GitHub.** https://github.com/POLSKA-GRUPA/pgk_operativa. Issues y PRs.
- **Emails PGK.** 6 cuentas funcionales, todas con borradores en IMAP Drafts.

Antes de la v1.0 privada, toda comunicación socia <-> Kenyi pasa por los canales que Kenyi indique (WhatsApp, email directo). No hay canal Mattermost operativo aun.

## 25. Anexo: comandos útiles del día a día

### 25.1 Setup inicial

```bash
git clone https://github.com/POLSKA-GRUPA/pgk_operativa.git
cd pgk_operativa
cp .env.example .env  # y editar
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync --all-extras --dev
uv run pre-commit install
```

### 25.2 Desarrollo

```bash
uv run pytest                              # todos los tests
uv run pytest tests/test_router.py -v      # test especifico
uv run ruff check .                        # lint
uv run ruff format .                       # formato
uv run mypy src/pgk_operativa              # tipos
uv run pre-commit run --all-files          # todos los hooks locales
```

### 25.3 CLI de producto

```bash
uv run pgk version
uv run pgk doctor
uv run pgk ana "<pregunta>"
uv run pgk ana --consenso "<pregunta>"
```

### 25.4 Git

```bash
git checkout -b socia/modulo-fiscal
# ... editar ...
git add -A
git commit -m "feat(nodos): modulo fiscal inicial con prompt de Gran Dragón"
git push -u origin socia/modulo-fiscal
# Abrir PR contra main desde GitHub UI
```

### 25.5 Engram (memoria de desarrollo)

Via MCP, dentro del agente IA (Claude Code, Devin):

```
mem_context                       # al iniciar sesion
mem_save <contenido>              # tras cada accion significativa
mem_search <query>                # buscar en sesiones previas
mem_session_summary               # al cerrar sesion
```

### 25.6 Útil

```bash
grep -rn "TODO\|FIXME\|XXX" src/ tests/      # pendientes
rg $'\u2014' docs/ src/ tests/               # detectar em-dash
rg "/Users/" src/ tests/ scripts/            # detectar rutas hardcoded
```

Final del manual. Si algo no está aquí, probablemente está en los ADRs (`docs/architecture/adrs/`), en ULTRAPLAN v1.8 (fuera del repo, pedirlo a Kenyi), o requiere preguntar directamente. El repo se actualiza: este documento se revisa cada cierre de semana para incorporar decisiones nuevas.
