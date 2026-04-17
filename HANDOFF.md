# HANDOFF pgk_operativa

Manual de traspaso para la socia de Kenyi. Documento autocontenido. Leer de principio a fin no es obligatorio, pero la primera vez conviene. El indice permite volver a cualquier seccion sin depender de notas previas.

Version del documento: 2026-04-16.
Estado del repo al generar el handoff: Semana 1 cerrada, PR #2 mergeado a main, 47 de 47 tests verdes, CI verde.

## Indice

0. [Que es pgk_operativa en una pagina](#0-que-es-pgk_operativa-en-una-pagina)
1. [ULTRAPLAN v1.8, los tres principios y los ocho principios rectores](#1-ultraplan-v18-los-tres-principios-y-los-ocho-principios-rectores)
2. [Arquitectura del repo](#2-arquitectura-del-repo)
3. [Las tres bases de datos inviolables](#3-las-tres-bases-de-datos-inviolables)
4. [Forma de trabajar: reglas que no se negocian](#4-forma-de-trabajar-reglas-que-no-se-negocian)
5. [Rutas absolutas en profundidad](#5-rutas-absolutas-en-profundidad)
6. [Estilo PGK para todo documento](#6-estilo-pgk-para-todo-documento)
7. [Consenso opt-in y el default Z.ai](#7-consenso-opt-in-y-el-default-zai)
8. [Ana unica cara visible](#8-ana-unica-cara-visible)
9. [Archivo en lugar de legacy](#9-archivo-en-lugar-de-legacy)
10. [Emails siempre borrador](#10-emails-siempre-borrador)
11. [Requisitos minimos de la maquina](#11-requisitos-minimos-de-la-maquina)
12. [Onboarding paso a paso (de cero a primer pgk ana)](#12-onboarding-paso-a-paso-de-cero-a-primer-pgk-ana)
13. [Flujo Git y politica de PRs](#13-flujo-git-y-politica-de-prs)
14. [Estado actual: Semana 1 cerrada](#14-estado-actual-semana-1-cerrada)
15. [Hoja de ruta Semana 2 a Semana 6](#15-hoja-de-ruta-semana-2-a-semana-6)
16. [H1 Fundaciones Enterprise en detalle](#16-h1-fundaciones-enterprise-en-detalle)
17. [Fase 12 AOD: 15 workflows de operativa diaria](#17-fase-12-aod-15-workflows-de-operativa-diaria)
18. [Adenda v1.7: distribucion a empleados](#18-adenda-v17-distribucion-a-empleados)
19. [Adenda v1.8: Guardia Integridad y Guardia Plazos](#19-adenda-v18-guardia-integridad-y-guardia-plazos)
20. [Que hace y que NO hace pgk_operativa](#20-que-hace-y-que-no-hace-pgk_operativa)
21. [Decisiones tomadas (ADRs) y decisiones pendientes](#21-decisiones-tomadas-adrs-y-decisiones-pendientes)
22. [Glosario](#22-glosario)
23. [Troubleshooting frecuente](#23-troubleshooting-frecuente)
24. [Contactos y canales](#24-contactos-y-canales)
25. [Anexo: comandos utiles del dia a dia](#25-anexo-comandos-utiles-del-dia-a-dia)

---

## 0. Que es pgk_operativa en una pagina

pgk_operativa es el repositorio unico y nuevo de Polska Grupa Konsultingowa S.L. Sustituye (consolidandolos, no borrandolos) a siete repos previos: PGK_Empresa_Autonoma, conta-pgk-hispania, pgk-laboral-desk, junior, PGK-direccion-general, PGK-Marketing-Autonomo y PROGRAMADOR_FRIKI_PGK, mas el portal que vivia dentro de PGK_Empresa_Autonoma.

El negocio es un despacho fiscal-contable-laboral-legal remoto enfocado a no residentes en Espana, principalmente polacos. pgk_operativa es el cerebro unificado que permite que:

- Empleados y Kenyi trabajen con una sola interfaz conversacional llamada Ana.
- Ana enrute la consulta por debajo al modulo tecnico adecuado (fiscal, contable, laboral, legal, docs, calidad, marketing, consejo, forja, workflows).
- Las respuestas lleguen por Mattermost, email, CLI o chat, nunca por dashboards.
- El grafo LangGraph sea la autoridad de negocio (Cecilia, Gran Dragon, Edu, German, Paloma como prompts de personalidad, no como agentes visibles).
- Todo conocimiento (skills, plantillas, BOE, dictamenes previos) quede consolidado en un solo sitio con ADRs que expliquen cada decision.

El objetivo operativo es eliminar el 60% del trabajo repetitivo del despacho via workflows adaptativos, conservando fiabilidad enterprise (auditoria, backups, RGPD).

Estado actual: infraestructura montada y grafo minimo operativo. Quedan por integrar los modulos reales (fiscal, contable, laboral, legal, etc.), migrar los cinco workflows Copilot validados y aplicar las guardias de integridad y plazos.

Si solo puedes leer 5 minutos, lee las secciones 1, 4 y 14.

---

## 1. ULTRAPLAN v1.8, los tres principios y los ocho principios rectores

ULTRAPLAN es el documento maestro que define como montar la infraestructura remota. Se ha iterado hasta la version 1.8 incorporando adendas. El repo pgk_operativa es su implementacion.

### 1.1 Los tres principios fundacionales

1. El fichaje legal es la base, la capa de IA es el diferencial. Nunca al reves. Si el fichaje no cumple el Real Decreto Ley 8/2019, el resto es irrelevante.
2. Gestion generica multi-empleado desde el dia uno. Nada personalizado a Kenyi. Todo reutilizable por Francisco, la socia, y cualquier futuro empleado.
3. Verificacion antes de construir. La distancia entre lo que Engram dice y lo que el codigo hace se reduce primero. Antes de cada fase, se verifica el terreno.

### 1.2 Los ocho principios rectores

1. Excelencia ejecutable sobre exhaustividad teorica. Mejor pocas fases brillantes que muchas a medias.
2. Enterprise grade desde el dia uno en fundamentales (seguridad, auditoria, backups), sin sobreingenieria en lo superfluo.
3. Reversibilidad. Cada decision de proveedor con plan B documentado.
4. Multimodelo IA. Ningun agente depende de un solo proveedor LLM. Z.ai, Anthropic, Groq, OpenAI, Gemini, Perplexity como fallbacks intercambiables.
5. Data portability. Datos siempre exportables en formatos abiertos. Cero lock-in.
6. Open source por defecto, propietario por excepcion.
7. Interfaces conversacionales por defecto, front-end solo cuando no haya alternativa. Sin dashboards. Sin paneles administrativos. Ni cliente ni empleado tienen portal web, todos conversan con Ana.
8. Mas limpio, mas robusto, menos codigo. Antes de escribir 300 lineas, 30 minutos de busqueda en GitHub. Componer con piezas existentes (tufup, age, uv, Claude Code) siempre preferible a construir desde cero.

### 1.3 Las fases del plan

El orden global es: Fase 0 (verificacion), H1 (Fundaciones Enterprise en paralelo), Fases 1 a 11 (infraestructura de negocio), Fase 12 (AOD, automatizacion operativa diaria), Adenda v1.7 (distribucion a empleados), Adenda v1.8 (guardias integridad y plazos).

Para el equipo: trabajamos sobre pgk_operativa aplicando las fases en este orden, no todas a la vez. La seccion 15 convierte el plan fases en un calendario semanal accionable.

### 1.4 Consecuencias del Principio 7 (sin pantallas)

- Ningun empleado tiene dashboard. Pregunta a Ana: "como voy hoy", "que me queda", "cuantas horas he imputado".
- Ningun cliente tiene portal. Paloma responde por email, Ana atiende por chatbot publico.
- Administracion es CLI conversacional, no panel. Comandos tipo `pgk admin alta-empleado` se combinan con preguntas a Ana.
- Fichaje movil es bot Mattermost (`/fichar-entrada`), no app.
- Metricas llegan como resumen diario conversacional a Mattermost.
- Unica excepcion justificada: web corporativa publica (pgkhiszpania.com) con perfiles y blog, porque es canal de marketing donde la pantalla es el producto.

### 1.5 Modos adaptativos de operacion

Una variable global controla la cadencia del sistema:

| Modo | Cuando | Efecto |
|---|---|---|
| normal | Rutina diaria | Resumen diario conciso, recordatorios estandar, seguimientos cada 15 dias |
| intenso | Inspeccion AEAT, cierre trimestre, cliente en crisis | Resumenes 2 veces al dia, alertas 7/3/1 dias, seguimiento diario |
| vacaciones | Kenyi desconectado | Solo emergencias AEAT reales, resto silenciado |
| panico | Caida sistema o error grave en cliente | Notificaciones continuas, runbook DR activado |

Activacion automatica por deteccion, o manual via `/modo intenso 2 semanas` en Mattermost.

---

## 2. Arquitectura del repo

```
pgk_operativa/
├── README.md                   Punto de entrada publico
├── AGENTS.md                   Reglas para agentes IA (Devin, Claude, Cursor, etc.)
├── MEMORY.md                   Resumen ejecutivo para arranque rapido
├── HANDOFF.md                  Este documento
├── pyproject.toml              Deps y build system (uv)
├── uv.lock                     Lockfile reproducible
├── .env.example                Plantilla de configuracion por maquina
├── .gitignore                  (incluye .env, data/*.db, __pycache__, .venv)
├── .pre-commit-config.yaml     Hooks locales (ruff, mypy, estilo PGK)
├── .github/
│   └── workflows/
│       └── ci.yml              Lint + tests en Python 3.12
├── src/
│   └── pgk_operativa/
│       ├── __init__.py
│       ├── cli/
│       │   └── main.py         CLI publica (pgk ana, pgk doctor, pgk version)
│       ├── core/
│       │   ├── paths.py        Path(__file__).resolve() raiz y subrutas
│       │   ├── config.py       Carga de .env, validacion de claves
│       │   ├── llm.py          Cliente OpenAI SDK -> Z.ai GLM-4.6
│       │   ├── graph_state.py  Estado tipado LangGraph
│       │   ├── router.py       Ana router (keywords + LLM fallback)
│       │   └── graph.py        Construccion del grafo minimo
│       └── nodos/
│           ├── ejecutor.py     Ejecutor generico del modulo
│           └── prompts.py      Prompts skeleton por modulo
├── tests/                      pytest, 47 tests al cierre de Semana 1
├── docs/
│   ├── ARCHITECTURE.md         Arquitectura actual
│   ├── PLAN_TRABAJO.md         Fases y calendario
│   ├── ADVISOR.md              Rol de Claude Opus 4.7 como advisor
│   ├── BDS.md                  Las tres BDs inviolables
│   ├── ESTILO_PGK.md           Reglas de redaccion
│   └── architecture/
│       └── adrs/               ADR-001 a ADR-006
├── archivo/                    Codigo y docs archivados con README y fecha
│   └── README.md
├── data/                       BDs locales (memoria_operativa.db, engram.db)
│   └── .gitkeep
└── scripts/                    Utilidades puntuales (no son codigo de producto)
```

Principios de esta estructura:

- `src/pgk_operativa/` es el unico lugar donde vive codigo de producto.
- `tests/` espeja la estructura de `src/`.
- `docs/architecture/adrs/` recoge decisiones arquitectonicas con formato ADR.
- `archivo/` guarda lo que se migra desde los siete repos origen, con README que explique que era, de donde vino y en que fecha se archivo.
- `data/` es local a cada maquina. No se commitea. Se recrea con migraciones.
- `scripts/` son utilidades one-off (smoke tests, generadores), no producto.

---

## 3. Las tres bases de datos inviolables

ADR-006 fija tres BDs. No hay una cuarta. Si aparece la necesidad de un cuarto almacen, se discute en ADR nuevo, no se crea silenciosamente.

### 3.1 pgk_database (Postgres remoto)

- Servidor: 209.74.72.83, puerto 5432, schema `pgk_admin`.
- Acceso: via tunel SSH. Kenyi tiene la clave; cada empleado recibe un rol propio (`emp_<nombre>_<hash>`).
- Contenido: tablas de negocio (`clientes_pgk`, `expedientes_pgk`, `facturas_pgk`, `tareas`, `fichajes`, `audit_log`, `procedimientos_pgk`, `plazos_aeat_clientes`, etc.).
- Autoridad: unica fuente de verdad de datos de negocio operativos.
- Migraciones: Alembic. Nunca `ALTER TABLE` directo.
- Multi-tenant: toda query filtra por `company_id` cuando aplique.
- Backups: H1.4 define la politica (snapshots diarios, restore probado mensual).

### 3.2 memoria_operativa.db (SQLite local)

- Path: `<repo>/data/memoria_operativa.db`.
- Contenido: memoria de negocio de los nodos LangGraph. Cada nodo guarda aprendizajes, decisiones y contexto relevante al cierre de un caso.
- API: `src/pgk_operativa/core/memoria_operativa.py` (a construir en Semana 2-3).
- FTS5 para busqueda semantica ligera + Bayesian updating para pesos de decisiones.
- NO se versiona. Cada maquina tiene la suya. Puede exportarse a JSON para auditar.

### 3.3 engram.db (SQLite local)

- Path: controlado por Engram MCP.
- Contenido: memoria de desarrollo para agentes IA (Claude Code, Devin, Cursor, etc.).
- Uso: `mem_save` tras cada accion significativa. `mem_context` al iniciar sesion. `mem_session_summary` al cerrar.
- Es complementaria a memoria_operativa.db, no duplicada. Engram = como codificamos. memoria_operativa = como decide el negocio.

---

## 4. Forma de trabajar: reglas que no se negocian

Ocho reglas. Ninguna es opcional. Todo PR que las incumpla se rechaza sin discusion.

1. **Rutas absolutas runtime.** `Path(__file__).resolve()`. Nunca hardcoded (`/Users/kenyi/...`). Nunca relativas desde cwd. Ver seccion 5.
2. **Ana unica cara visible.** Los modulos tecnicos conservan su nombre interno (`pgk.fiscal`, `pgk.contable`, etc.), pero jamas aparecen en la UI conversacional. El empleado habla con Ana. Ver seccion 8.
3. **Consenso opt-in.** Por defecto Ana usa un solo modelo (Z.ai GLM-4.6 via OpenAI SDK). El comando `/consenso` o la flag `--consenso` dispara dos proveedores distintos. Ver seccion 7.
4. **Estilo PGK en todo documento.** Sin em-dash (U+2014), sin lineas horizontales decorativas. Dos puntos, comas, parentesis, listas. Ver seccion 6.
5. **Archivo, no legacy.** Codigo o docs viejos van a `archivo/` con README explicando que era y cuando se archivo. Nada se borra. Ver seccion 9.
6. **Emails solo borrador.** Todo email sale como draft en IMAP. Kenyi o el empleado autorizado lo revisa y lo envia. Nunca `smtplib.send_message()`. Ver seccion 10.
7. **Tres BDs inviolables.** Ver seccion 3. Cualquier nuevo almacen requiere ADR.
8. **Protocolo Engram.** Al iniciar: `mem_context`. Tras cada accion significativa: `mem_save`. Al cerrar sesion: `mem_session_summary`.

Para agentes IA: leer `AGENTS.md` y `MEMORY.md` antes de tocar nada. Son la fuente de verdad.

---

## 5. Rutas absolutas en profundidad

Es la regla que mas se incumple por reflejo, por eso tiene seccion propia.

### 5.1 Que significa "absoluta en runtime"

La ruta se calcula en tiempo de ejecucion desde el propio archivo, no se escribe fija en el codigo.

Patron obligatorio (implementado ya en `src/pgk_operativa/core/paths.py`):

```python
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SRC_ROOT = REPO_ROOT / "src" / "pgk_operativa"
DATA_ROOT = REPO_ROOT / "data"
DOCS_ROOT = REPO_ROOT / "docs"
ARCHIVO_ROOT = REPO_ROOT / "archivo"

def memoria_operativa_path() -> Path:
    return DATA_ROOT / "memoria_operativa.db"
```

Cualquier otro modulo importa desde aqui:

```python
from pgk_operativa.core.paths import DATA_ROOT, memoria_operativa_path
```

### 5.2 Lo prohibido

- Hardcoded por maquina: `/Users/kenyi/Documents/PGK` o `C:\Users\Maria\PGK`. Si un script necesita una ruta local del usuario, se lee de variable de entorno (`PGK_LOCAL_DOCUMENTS_PATH` en `.env`).
- Relativas desde cwd: `open("data/memoria.db")`, `Path("./knowledge")`. Si el script se ejecuta desde otro directorio, rompe.
- Hardcoded a la maquina de otro agente: `/home/ubuntu/repos/pgk_operativa`. Es la ruta de un sandbox de Devin, no vale para la socia.

### 5.3 Por que importa

El repo debe clonarse en cualquier maquina (Mac de Kenyi, Linux de la socia, sandbox de Devin, servidor de produccion) y funcionar. Si una ruta depende de como se lanzo el script, tarde o temprano alguien presenta un modelo fiscal con el dictamen de otro cliente. El dolor de este bug no es teorico, el .env original de Kenyi tiene `GOOGLE_APPLICATION_CREDENTIALS=/Users/kenyi/...` y ya ha bloqueado a todo el que no es el.

### 5.4 Variables de entorno para rutas especificas de maquina

Tres rutas varian por empleado y se leen de `.env`, no del codigo:

```
PGK_USER_HOME=/home/socia
PGK_LOCAL_DOCUMENTS_PATH=/home/socia/Documents/PGK
PGK_GOOGLE_CREDENTIALS_PATH=/home/socia/.config/pgk/google_credentials.json
```

El codigo siempre las lee asi:

```python
import os
from pathlib import Path

local_docs = Path(os.environ["PGK_LOCAL_DOCUMENTS_PATH"])
```

Nunca con valor por defecto hardcoded a `/Users/kenyi/...`.

### 5.5 Check automatico

El hook pre-commit incluye un grep que busca `/Users/kenyi`, `C:\Users\` o rutas absolutas sospechosas en el codigo. Si aparece, rechaza el commit. Correrlo a mano:

```bash
uv run pre-commit run --all-files
```

---

## 6. Estilo PGK para todo documento

ADR-003b. Aplica a dictamenes, emails, informes, contratos, ADRs, README, codigo markdown, comentarios largos, cualquier texto que salga del repo.

### 6.1 Prohibiciones

- **Em-dash (caracter Unicode U+2014, guion tipografico largo).** Caracter con aspecto pretencioso. En su lugar: dos puntos, coma, parentesis, lista, o punto y seguido segun el caso.
- **Lineas horizontales decorativas.** Nada de `===========`, `----------`, `***********` dentro del cuerpo. `---` separador de secciones markdown esta permitido con moderacion.
- **Prosa de plantilla.** Repeticiones tipo "el contribuyente... el contribuyente... el contribuyente" en cadena. Variar con "Sr. X", "mi representado", "el interesado", "obligado tributario" segun convenga.
- **Transliteraciones degradadas.** Si un documento final se exporta a PDF y pierde tildes o eñes, el PDF no sale. Fuente de verdad siempre UTF-8 completo.
- **Faltas ortograficas.** Revisar antes de entregar cliente. Sin excepciones.

### 6.2 Obligaciones

- Revisar tildes, acentuacion, nombres propios y naturalidad antes de entregar.
- Usar como fuente de verdad el documento maestro vigente. No mantener copias paralelas degradadas para exportacion.
- Tres pasadas antes de exportar: ortografia, estilo (eliminar repeticiones mecanicas), fidelidad (verificar que el PDF sale del texto correcto).

### 6.3 Por que

En marzo 2026, un escrito de alegaciones se exporto a Word desde un script que usaba una copia ASCII del texto. Se degradaron acentos, nombres y naturalidad de la redaccion. Cliente lo noto. Desde entonces, prohibido generar documentos finales desde fuentes duplicadas o linguisticamente rebajadas.

---

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

Ventajas: barato, rapido, sin cableado entre SDKs.

### 7.2 Con `--consenso` o `/consenso`

Dispara un subgrafo que llama a dos proveedores distintos en paralelo. El sintetizador compara y produce respuesta unica con nivel de acuerdo.

Restriccion de runtime: `assert provider_A != provider_B and model_A != model_B`. Si falla, `consensus_type = "single_model"` y se avisa en la respuesta.

Providers validos para consenso: Z.ai, Anthropic (API propia o proxy Z.ai Anthropic-compatible), Gemini, Groq, DeepSeek, Perplexity.

### 7.3 Cuando activar consenso

Gatillos recomendados:
- Decision fiscal con incertidumbre normativa (IRNR compleja, convenios de doble imposicion).
- Escrito legal a AEAT con plazo corto.
- Dictamen para cliente nuevo sin precedentes en memoria.
- Cuando la respuesta de Ana no convence al empleado y quiere segunda opinion.

En el resto, default single-model es mas que suficiente.

### 7.4 CLI

```bash
uv run pgk ana "que IVA aplica a Amazon UE"          # default, un modelo
uv run pgk ana --consenso "como declarar IRNR 2025"  # dos modelos
```

En Mattermost: mensaje normal para default, prefijo `/consenso ` para dos modelos.

---

## 8. Ana unica cara visible

ADR-002. Regla estricta.

### 8.1 Que ve el empleado

Una sola interfaz: Ana. En CLI, en Mattermost, en email, siempre Ana. Nunca ve "Gran Dragon contestando", "Cecilia enrutando", "Edu procesando". La personalidad es siempre Ana.

### 8.2 Que pasa por dentro

El router (`src/pgk_operativa/core/router.py`) clasifica la consulta en un modulo tecnico:

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

La clasificacion usa primero keywords (rapido, 0 LLM), luego fallback LLM (Z.ai) si no hay match claro. El nodo ejecutor del modulo recibe la consulta, la procesa con los prompts de personalidad (conservamos los nombres: Gran Dragon, Edu, Jennifer, German, etc. como personajes internos cargados por Ana), y devuelve la respuesta.

### 8.3 Que muestra el CLI

Por defecto solo `respuesta_final`. Los campos `modulo_tecnico` y `razonamiento_clasificacion` quedan en el audit_trail para diagnostico, pero no se imprimen.

Flag de debug (no publico): `--debug` muestra todo. Util para desarrollo; jamas para empleado en operacion.

### 8.4 Por que unificamos asi

Porque el empleado no sabe ni tiene que saber si esta hablando con el modulo fiscal o con el contable. Pregunta en lenguaje natural, Ana decide. Si manana reemplazamos un prompt de Gran Dragon por uno mejor, el empleado no se entera. Esto reduce friccion y permite refactorizar modulos internos sin romper UX.

---

## 9. Archivo en lugar de legacy

ADR-003. Cuando migremos codigo de los siete repos origen (o del portal), lo que no se reutiliza no se borra, se mueve a `archivo/`.

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

Cada subcarpeta de `archivo/` tiene un README_ARCHIVO.md minimo con:
- Que era (1 parrafo).
- De que repo origen vino (URL + commit hash si disponible).
- Fecha de archivo.
- Por que no se reutiliza (1 parrafo).
- Que se reutilizo en su lugar y donde vive ahora en `src/pgk_operativa/`.

### 9.3 Por que "archivo" y no "legacy"

Connotacion. "Legacy" suena a deuda, a cosa que habria que haber borrado ya. "Archivo" es neutro, profesional, consultable. Un archivo no se descarta, se consulta. La socia o Kenyi pueden en cualquier momento entrar en `archivo/` y recuperar logica, ejemplos, prompts.

---

## 10. Emails siempre borrador

Regla de hierro. Ningun agente envia emails directamente.

### 10.1 Que hacemos

Integracion IMAP que guarda mensajes en `INBOX.Drafts` de la cuenta correspondiente:

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

### 10.4 Por que

Un email enviado no se puede retirar. Un borrador si. Incluso con IA impecable, la responsabilidad final es humana. Esto encaja con el principio de HITL obligatorio para todo output que salga hacia cliente.

---

## 11. Requisitos minimos de la maquina

### 11.1 Sistema operativo

- macOS 13+ (Kenyi) o Linux reciente (socia, servidor).
- Windows tecnicamente soportado via WSL2, no nativo. Si hay que trabajar en Windows, se instala Ubuntu en WSL2 y se trabaja ahi.

### 11.2 Software base

- Python 3.12 (no 3.13, no 3.11). Gestionado por `uv`.
- `uv` (astral-sh/uv): gestor de deps en Rust. Instalacion:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- Git 2.40+.
- SSH cliente (para tunel Postgres).
- Docker opcional (para Postgres local de desarrollo si no hay acceso remoto).

### 11.3 Dependencias opcionales

- `age` (FiloSottile/age): cifrado de `.env` cuando el empleado lo recibe. Via brew (`brew install age`) o apt (`apt install age`).
- `pre-commit`: se instala automaticamente con `uv sync --dev`.

### 11.4 Accesos que deben estar provisionados

| Acceso | Quien lo provisiona | Estado |
|---|---|---|
| Clave SSH autorizada en 209.74.72.83 | Kenyi | Pendiente para la socia |
| Rol Postgres propio (`emp_socia_<hash>`) | Kenyi via admin_empleados.py | Pendiente |
| `ZAI_API_KEY` en `.env` | Kenyi | En su `.env` maestro |
| Resto de claves LLM (opcional, solo si usa consenso) | Kenyi | En su `.env` maestro |
| Credenciales IMAP de al menos una cuenta | Kenyi | En su `.env` maestro |
| Token GitHub con permisos en POLSKA-GRUPA | Kenyi | En su `.env` maestro |
| Acceso al repo pgk_operativa | Kenyi | Actualmente publico, pasara a privado |

### 11.5 Recursos hardware

- 8 GB RAM minimo, 16 GB recomendado. LangGraph + multiples SDKs LLM a la vez consume.
- 20 GB de disco libres (incluye docs, BDs locales, y cache de uv).
- Conexion estable. Los LLMs responden mejor con baja latencia.

---

## 12. Onboarding paso a paso (de cero a primer pgk ana)

Tiempo esperado: 30 minutos si ya hay Mac/Linux con Python y SSH listos. Hasta 1 hora si es maquina nueva.

### 12.1 Clonar el repo

```bash
cd ~
git clone https://github.com/POLSKA-GRUPA/pgk_operativa.git
cd pgk_operativa
```

### 12.2 Instalar uv si no esta

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Reiniciar terminal o source ~/.bashrc
```

### 12.3 Crear `.env` a partir de la plantilla

```bash
cp .env.example .env
```

Editar `.env` con los valores reales que Kenyi habra facilitado por canal seguro (age-encrypted en el futuro, por WhatsApp encriptado o 1Password hoy). Claves minimas para arrancar:

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

Revisa que el `.env` tiene lo minimo y que los providers LLM responden. Al menos Z.ai debe estar verde.

### 12.7 Primera consulta a Ana

```bash
uv run pgk ana "hola Ana, que es el IRNR?"
```

Debe devolver una respuesta conversacional sobre IRNR. Sin mostrar el modulo tecnico que contesto.

### 12.8 Si algo falla

- `uv sync` falla por version Python: instalar `uv python install 3.12` y reintentar.
- `pgk doctor` dice que falta ZAI_API_KEY: revisar `.env`, confirmar que el archivo esta en la raiz del repo y tiene la clave sin espacios.
- `pgk ana` da un error de red: comprobar conectividad a `api.z.ai`. Algunas redes corporativas bloquean.
- `pytest` falla: leer el output, confirmar que se esta en rama `main` actualizada (`git pull`), reintentar.

Si nada de lo anterior resuelve, abrir Issue en GitHub o avisar a Kenyi directamente.

---

## 13. Flujo Git y politica de PRs

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

Tipos validos: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`, `style`.

Ejemplos reales del repo:

```
feat(semana-1): grafo minimo con Ana router y ejecutor generico
fix(router): nodo_ana_router maneja excepciones del LLM con fallback a general
docs(handoff): manual de traspaso para la socia
```

### 13.3 Pull Requests

- Abrir PR contra `main` desde rama propia.
- Titulo conciso y descriptivo.
- Cuerpo: que cambia, por que cambia, como probar. Una seccion "Riesgos" si hay efecto no trivial.
- Esperar CI verde antes de pedir review.
- Esperar 0 findings de Devin Review (si aplica).
- Merge solo despues de OK explicito de Kenyi o cuando Semana 2+ la socia tenga autoridad delegada.
- Borrar rama remota tras merge para no acumular ruido.

### 13.4 CI

GitHub Actions en `.github/workflows/ci.yml`. Python 3.12. Pasos:

1. Checkout.
2. Setup uv.
3. `uv sync --all-extras --dev`.
4. `uv run ruff check .`.
5. `uv run ruff format --check .`.
6. `uv run mypy src/pgk_operativa`.
7. Checks de estilo PGK (grep em-dash en docs y codigo fuera de `.venv/`).
8. Checks de rutas absolutas (grep `/Users/`, `C:\\Users`).
9. `uv run pytest -q`.

Todo debe salir verde para que Kenyi mergee.

### 13.5 Nunca hacer

- `git push --force` en `main`.
- `git commit --no-verify` salvo emergencia documentada.
- Modificar `main` directamente desde la UI de GitHub.
- Borrar archivos sin ADR si son codigo o docs con historia.

---

## 14. Estado actual: Semana 1 cerrada

### 14.1 Hecho

- **Semana 0 (Scaffolding):** `pyproject.toml`, estructura `src/pgk_operativa/`, CI, `.env.example`, ADRs 001 a 006, pre-commit, README/AGENTS/MEMORY. Merge via PR #1.
- **Semana 1 (Grafo minimo):**
  - Estado tipado LangGraph.
  - Router Ana con keywords + fallback LLM Z.ai.
  - Ejecutor generico que llama a Z.ai con prompt skeleton por modulo.
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
- Public temporalmente (pasara a privado tras cerrar scope). El .env esta fuera del repo y nunca se commitea.

### 14.3 Quedan pendientes inmediatos (asumibles por la socia)

- Integrar modulos reales en `src/pgk_operativa/nodos/`:
  - `fiscal.py` (rescate de `PGK_Empresa_Autonoma/src/agents/nodos.py` y prompts `pgk-irnr-specialist.md`).
  - `contable.py` (rescate de `conta-pgk-hispania` CFO Agent y sus tools).
  - `laboral.py` (rescate de `pgk-laboral-desk` motor determinista).
  - `legal.py` (rescate de `junior` skills legales).
  - `docs.py`, `calidad.py`, `marketing.py`.
- Construir subgrafo consenso opt-in real (`src/pgk_operativa/core/consenso.py`).
- Arrancar H1.1 (testing + CI robustecido) y H1.2 (seguridad + secrets management) en paralelo a la descomposicion de nodos.

---

## 15. Hoja de ruta Semana 2 a Semana 6

Plan calendario. Cada semana cierra con PR mergeado y tests verdes.

### Semana 2: Descomposicion de nodos y consenso real

Objetivos:
- Mover `nodos.py` original (3844 LoC) de PGK_Empresa_Autonoma a 8 modulos en `src/pgk_operativa/nodos/`, conservando prompts en `src/pgk_operativa/prompts/core/`.
- Implementar subgrafo consenso opt-in con dos proveedores y sintetizador.
- Tests por modulo, goldens con respuestas esperadas.

Entregable verificable: `pgk ana --consenso "<pregunta fiscal compleja>"` contesta con los dos modelos y sintesis.

### Semana 3: Integraciones core + H1.1-H1.3

Objetivos:
- Integrar Consejo de Direccion (7 consejeros de `PGK-direccion-general`).
- Integrar Forja (REVISOR_UNIFICADO + Trail of Bits).
- Integrar modulo laboral real (motor determinista).
- Integrar modulo legal real (17 skills de junior).
- Integrar modulo contable real (CFO Agent + tools).
- H1.1 (testing): coverage >70%, tests de integracion en Postgres staging.
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

### Semana 5: Distribucion + piloto

Objetivos:
- Adenda v1.7 implementada: bundle tufup, cifrado `.env.age`, `install.sh` one-liner, wrapper `pgk`.
- Onboarding Kenyi + 1 empleado (probablemente Francisco o la socia).
- Mattermost conectado con canal por empleado.

Entregable verificable: Kenyi + 1 empleado operando desde distinta maquina sin tocar repo directamente.

### Semana 6+: Operaciones

Objetivos:
- Fase 12 AOD: 3 workflows prioridad 1 corriendo (triage email, resumen diario, limpieza mantenimiento).
- Adenda v1.8: Guardia Integridad y Guardia Plazos activas.
- Primeros casos reales de clientes pasando 100% por pgk_operativa.

Entregable verificable: 7 dias seguidos de operacion sin incidencia grave.

---

## 16. H1 Fundaciones Enterprise en detalle

H1 es paralelo a Semanas 3-4. Siete subfases:

- **H1.1 Infraestructura de calidad.** pytest configurado, tests unitarios de capa datos, integracion contra Postgres staging, coverage >80%, ruff + mypy strict en CI, Semgrep sast-mcp integrado. Sin esto, cada cambio es Russian roulette.
- **H1.2 Seguridad.** Rotacion de claves cuatrimestral, secrets management centralizado, auditoria en Postgres (`audit_log` append-only), RLS por `company_id`, cifrado de `.env` de empleado con age.
- **H1.3 RGPD.** Inventario de datos personales por cliente, DPA firmado con cada proveedor LLM, politica de retencion (4 anos prescripcion fiscal, mas lo minimo RGPD en `99_Archivo_Muerto`).
- **H1.4 Calidad IA.** Goldens por modulo (respuestas esperadas verificadas), evals semanales en `evaluation/`, alertas si confidence cae >10%, HITL obligatorio en output hacia cliente.
- **H1.5 Actualizador de conocimiento.** Cron semanal que descarga BOE, DGT, TEAC, resume cambios, propone updates a prompts y Engram. Kenyi aprueba con `/actualizador aprobar N`.
- **H1.6 Continuidad.** Runbook DR escrito, staging identico a prod, simulacro de caida trimestral.
- **H1.7 Portabilidad.** Exportador completo a JSON/Markdown, replica del sistema clonable en nueva maquina en <1h.

Cada subfase tiene criterios de hecho medibles. Ninguna se da por cerrada sin verificacion.

---

## 17. Fase 12 AOD: 15 workflows de operativa diaria

Automatizacion operativa diaria. Libera 50-75h/mes de rutina. Prioridad 1 antes de incorporar primer empleado.

### 17.1 Arquitectura comun

Cada workflow se declara en YAML en `scripts/workflows/<nombre>.yaml`. Un runner en `scripts/workflows/_core/runner.py` interpreta el YAML y orquesta. Añadir workflow nuevo = escribir YAML, no codigo.

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
6. `workflow_factura_drop`: evento Drive. OCR + clasificacion reparacion/mejora + registro en BD.

**Prioridad 3:**
7. `workflow_sede_aeat`: cron 4h. Acceso a Sede Electronica AEAT via certificado, descarga notificaciones, crea tarea con plazo.
8. `workflow_cobros`: cron diario 09:00. Escalado facturas >30/60/90d.
9. `workflow_seguimiento_cliente_inactivo`: cron quincenal. Detecta inactivos >60d y propone draft.

**Prioridad 4:**
10. `workflow_onboarding_cliente_nuevo`: comando `/cliente-nuevo`. Crea carpeta Drive, FICHA_MAESTRA.json, email bienvenida, checklist.
11. `workflow_dictamen_mensual_cliente`: cron mensual dia 1. Dictamen por cliente con servicio mensual.

**Prioridad 5:**
12. `workflow_monitor_linkedin_empleado`: cron semanal. Resumen privado por empleado.
13. `workflow_actualizador_conocimiento`: ya en H1.5.
14. `workflow_desactivacion_cliente_inactivo`: cron mensual. Detecta >18 meses inactivo y propone archivar.
15. `workflow_consolidacion_memoria`: cron mensual dia 28. Revisa Engram, detecta duplicados y contradicciones.

### 17.3 Criterios de hecho Fase 12

- Los 3 workflows prioridad 1 corriendo >7 dias sin fallar.
- Kenyi confirma reduccion real de tiempo en rutina diaria.
- Los modos de operacion (`/modo intenso`, `/modo vacaciones`) funcionan y cambian comportamiento observable.
- `scripts/workflows/README.md` completo con ejemplos de añadir workflow.

---

## 18. Adenda v1.7: distribucion a empleados

Los empleados de PGK son oficinistas, no desarrolladores. `git clone`, `gh auth login`, PRs estan fuera de su vocabulario. El sistema de distribucion tiene que ser one-liner y silencioso.

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
  Rol Postgres creado: emp_socia_a3f9
  Usuario SSH en servidor: emp_socia_a3f9
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
- Descarga tufup bundle mas reciente.
- Verifica firma con `/pub/root.key`.
- Descomprime a `~/PGK/`.
- Pide email, descarga `.env.age`.
- Pide password age (recibida por WhatsApp), descifra `.env`.
- Instala wrapper `pgk` en `/usr/local/bin`.
- Lanza primera sesion conversacional de onboarding (Fase 10a).

### 18.4 Actualizaciones posteriores

Silenciosas. Cada vez que el empleado ejecuta `pgk`, el wrapper comprueba `/pgk-dist/latest.json`, si hay version nueva la descarga, verifica firma, reemplaza, y continua. Sin preguntas al empleado.

### 18.5 Codigo propio para esto

Solo 120 lineas + 2 archivos de configuracion. El resto lo hace tufup, age, uv, Claude Code. Componer, no construir.

---

## 19. Adenda v1.8: Guardia Integridad y Guardia Plazos

Dos subsistemas que viven como workflows nocturnos, llegan a Mattermost.

### 19.1 Guardia Integridad

Problema: empleado trabaja con Claude Code sobre un cliente (mencionando NIF o nombre), pero ese cliente no tiene ficha en `clientes_pgk` ni `FICHA_MAESTRA.json` en Drive. Trabajo queda huerfano.

Solucion: `scripts/workflows/guardia_integridad.py`, nocturno. Consulta observations Engram ultimas 24h, extrae NIFs con regex `[XYZ]?[0-9]{7,8}[A-Z]`, extrae nombres con Haiku barato, cruza con `clientes_pgk.nif` y `FICHA_MAESTRA.json`. Clasifica en Conectado / Parcial / Huerfano. Mensaje Mattermost agrupado con comandos para regularizar (`/integridad crear <NIF>`, `/integridad reconstruir-drive <NIF>`).

Codigo propio: 60 lineas Python.

### 19.2 Guardia Plazos

Tres niveles:

- **Plazos internos PGK (acuerdos con cliente):** tabla `procedimientos_pgk` con codigos tipo `DICTAMEN_IRNR`, `REQUERIMIENTO_AEAT`. Al crear expediente, sistema calcula `fecha_vencimiento` sumando dias habiles, crea tareas por hito con sus propias fechas, y genera alertas segun `alertas_default` (`[7,3,1]`).
- **Plazos legales AEAT (no negociables):** archivo `data/calendario_aeat.yaml` con todas las fechas del año (modelos 111, 303, 390, 720, etc.). Cron actualizador anual que scrapea Sede Electronica y alerta si hay cambios.
- **Microplazos de workflow:** los que genera cada workflow segun necesidad (revision Kenyi antes de envio, seguimiento cliente tras 7d sin respuesta, etc.).

Todas las alertas acaban en Mattermost con prioridad visual (roja <10d, amarilla <30d, verde resto).

### 19.3 Dependencias

- Guardia Integridad requiere Engram activo y `clientes_pgk` poblada.
- Guardia Plazos requiere `procedimientos_pgk` y `plazos_aeat_clientes` migradas.
- Ambas activas en Semana 6+.

---

## 20. Que hace y que NO hace pgk_operativa

### 20.1 Hace

- Cerebro unico conversacional para fiscal, contable, laboral, legal, docs, calidad, marketing, consejo, forja y workflows.
- Enrutamiento silencioso via Ana a modulo tecnico.
- Consenso multimodelo opt-in.
- Memoria operativa persistente entre sesiones.
- Memoria de desarrollo via Engram.
- 5 workflows Copilot validados (modelo_210, contestacion_hacienda, alta_autonomo, revision_trimestral, preparar_contrato).
- 15 workflows AOD (en Semana 6+).
- Guardia Integridad y Guardia Plazos.
- Distribucion one-liner a empleados.
- Generacion de dictamenes y documentos via formateador oficial WeasyPrint.
- Integracion Postgres remoto, IMAP, Google Drive, Notion, Mattermost.

### 20.2 NO hace

- Front-end. Ningun portal web ni dashboard. Ni para cliente, ni para empleado, ni para admin.
- Migracion automatica de facturas historicas. Cada cliente se carga a mano con HITL.
- Reescribir motor laboral. Se reutiliza el de `pgk-laboral-desk` tal cual.
- Integrar sistemas fuera del consolidado (Holded, Quipu, etc.) salvo ADR nuevo.
- Enviar emails directamente. Siempre borrador.
- Refactorizar los siete repos origen. Ellos se quedan como estan, pgk_operativa absorbe lo valioso.
- App movil nativa. El movil es Mattermost.
- OCR pesado propio. Se usan MCP tools existentes.
- Billing/ERP propio. Se integra con existente de Kenyi.

Cualquier cosa que no este en 20.1 y alguien proponga, requiere ADR nuevo con justificacion explicita.

---

## 21. Decisiones tomadas (ADRs) y decisiones pendientes

### 21.1 ADRs activos

- **ADR-001 stack-python-langgraph:** Python 3.12 + LangGraph + FastAPI + uv.
- **ADR-002 ana-unica-sin-rebranding:** Ana cara visible, prompts conservan nombres (Gran Dragon, Edu, Jennifer, German) pero no se exponen.
- **ADR-003 archivo-no-legacy:** `archivo/` con README fecha. Nada se borra.
- **ADR-004 rutas-absolutas-runtime:** `Path(__file__).resolve()`, nunca hardcoded.
- **ADR-005 consenso-opt-in:** `/consenso` opt-in, default single-model Z.ai.
- **ADR-006 tres-bds-inviolables:** pgk_database remoto, memoria_operativa.db local, engram.db local.

### 21.2 ADRs pendientes de redactar

- **ADR-007 estilo-pgk-formalizado:** sin em-dash, sin lineas horizontales, reglas de redaccion.
- **ADR-008 emails-solo-borrador:** IMAP Drafts, prohibicion SMTP send.
- **ADR-009 modos-operacion-adaptativos:** normal / intenso / vacaciones / panico.
- **ADR-010 distribucion-tufup-age:** arquitectura de distribucion a empleados.
- **ADR-011 guardias-integridad-plazos:** subsistemas v1.8.

### 21.3 Decisiones abiertas que la socia puede cerrar

- **D1 Deployment.** Blue/green 17 dias vs ventana madrugada 2h. Mi voto CTO: blue/green (mas lento pero 0 downtime). Depende de disponibilidad servidor.
- **D2 Nombres internos.** Mantener "Gran Dragon", "Edu", "Jennifer", "German" en prompts (solo internos, nunca visibles al empleado) o neutralizar. Mi voto: mantener, dan personalidad a los prompts y no se filtran.
- **D3 SSH vs WireGuard para acceso remoto empleados a Postgres.** SSH es estandar, WireGuard es mas moderno. Mi voto: SSH (ya funciona, menos movimiento).
- **D4 Privatizar repo.** Decisison de Kenyi post-launch. No bloquea desarrollo.

---

## 22. Glosario

- **Ana:** cara visible conversacional. Unica interfaz para empleados y clientes.
- **ADR:** Architecture Decision Record. Documento corto que fija una decision.
- **AOD:** Automatizacion Operativa Diaria. Conjunto de workflows que liberan tiempo rutinario.
- **Claude Code:** entorno de desarrollo basado en Claude que los empleados tendran instalado.
- **CLI:** interfaz de linea de comandos. `pgk ana`, `pgk doctor`.
- **Consenso:** modo opt-in donde dos LLMs distintos responden y un sintetizador produce respuesta unica.
- **Copilot Gestoria:** motor de workflows declarativos rescatado del portal. 5 validados.
- **DeLLMa:** algoritmo de decision bajo incertidumbre. Usado por Consejo de Direccion.
- **Engram:** sistema de memoria persistente para agentes IA. MCP server propio.
- **Formateador oficial:** pipeline WeasyPrint en `external/formateador/` que genera PDFs con estilo PGK.
- **Goldens:** respuestas esperadas de referencia para evaluacion de modelos.
- **Grafo:** DAG de LangGraph que orquesta el flujo Ana -> router -> modulo -> respuesta.
- **Guardia Integridad:** workflow nocturno que detecta clientes mencionados sin ficha.
- **Guardia Plazos:** workflow que vigila vencimientos internos y AEAT.
- **H1:** Horizonte 1, seis meses. Fundaciones Enterprise.
- **HITL:** Human-in-the-loop. Aprobacion humana obligatoria en outputs sensibles.
- **Mattermost:** canal de mensajeria interno. Sustituto del dashboard.
- **MCP:** Model Context Protocol. Mecanismo para que los LLMs usen tools externos.
- **Memoria operativa:** SQLite local, memoria de negocio de los nodos LangGraph.
- **Modo operativo:** variable global (normal / intenso / vacaciones / panico) que ajusta cadencia.
- **pgk_database:** Postgres remoto en 209.74.72.83. Unica fuente de verdad de datos de negocio.
- **PGC 2008:** Plan General Contable espanol. Marco para todas las cuentas contables.
- **Sede Electronica:** portal AEAT para notificaciones y requerimientos.
- **sintetizador:** nodo que combina dos respuestas LLM en consenso.
- **tufup:** The Update Framework wrapper para auto-update firmado de apps Python stand-alone.
- **ULTRAPLAN / SUPERPLAN:** documento maestro v1.8, define arquitectura completa.
- **uv:** gestor de deps Python en Rust. Reemplaza venv + pip.
- **WeasyPrint:** motor HTML+CSS a PDF usado para dictamenes.
- **Z.ai:** proveedor LLM primario. GLM-4.6 via OpenAI SDK.

---

## 23. Troubleshooting frecuente

### 23.1 `uv sync` no instala Python 3.12

```bash
uv python install 3.12
uv sync --all-extras --dev
```

### 23.2 `pgk doctor` dice que ZAI_API_KEY falta

`.env` en la raiz del repo, sin espacios alrededor del `=`, sin comillas. Ejemplo:

```
ZAI_API_KEY=sk-zai-abc123
```

Ni `ZAI_API_KEY = "sk-..."` ni `ZAI_API_KEY= sk-...`.

### 23.3 Postgres: `connection refused`

El tunel SSH no esta levantado. Levantarlo:

```bash
ssh -N -L 5432:127.0.0.1:5432 \
    -i ~/.ssh/id_rsa \
    <PGK_SSH_USER>@209.74.72.83
```

Dejar corriendo en otro terminal. Si el CLI lo automatiza via `sshtunnel`, ignorar.

### 23.4 CI falla con "Job is waiting for a hosted runner"

Org POLSKA-GRUPA sin billing configurado para Actions en repos privados. Solucion temporal: repo publico. Solucion definitiva: añadir metodo de pago en https://github.com/organizations/POLSKA-GRUPA/billing.

### 23.5 Pre-commit rechaza por em-dash

Se ha metido un guion largo U+2014 en codigo o docs. Buscar y reemplazar por dos puntos, coma o parentesis segun convenga:

```bash
rg -n $'\u2014' docs/ src/ tests/
```

### 23.6 Pre-commit rechaza por ruta absoluta

Se ha metido `/Users/kenyi` o similar en codigo. Reemplazar por `Path(__file__).resolve()` o por lectura de variable de entorno:

```python
import os
from pathlib import Path

docs_path = Path(os.environ["PGK_LOCAL_DOCUMENTS_PATH"])
```

### 23.7 Test `test_nodo_ana_router_*` falla

Comprobar que la rama esta actualizada (`git pull origin main`). Los tests del router se escribieron para la version actual del parser. Tests viejos en ramas antiguas pueden fallar.

### 23.8 `pgk ana` devuelve error LLM en frio

Z.ai puede tardar en despertar. Reintentar. Si persiste, `pgk doctor` detalla que provider responde y cual no. Si solo falla Z.ai, usar `--consenso` o esperar.

---

## 24. Contactos y canales

- **Kenyi (CEO).** Decision final en todo lo estrategico. Disponibilidad alta en horario laboral europeo.
- **Claude Opus 4.7 (advisor).** Rol de senior advisor, revisa handoffs semanales. Ver `docs/ADVISOR.md`.
- **Devin (agente IA).** Implementador autonomo. Sesiones visibles en https://app.devin.ai/.
- **Mattermost PGK.** Canal interno. Sera el punto principal de comunicacion una vez distribuido.
- **GitHub.** https://github.com/POLSKA-GRUPA/pgk_operativa. Issues y PRs.
- **Emails PGK.** 6 cuentas funcionales, todas con borradores en IMAP Drafts.

Antes de la v1.0 privada, toda comunicacion socia <-> Kenyi pasa por los canales que Kenyi indique (WhatsApp, email directo). No hay canal Mattermost operativo aun.

---

## 25. Anexo: comandos utiles del dia a dia

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
git commit -m "feat(nodos): modulo fiscal inicial con prompt de Gran Dragon"
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

### 25.6 Util

```bash
grep -rn "TODO\|FIXME\|XXX" src/ tests/      # pendientes
rg $'\u2014' docs/ src/ tests/               # detectar em-dash
rg "/Users/" src/ tests/ scripts/            # detectar rutas hardcoded
```

---

Final del manual. Si algo no esta aqui, probablemente esta en los ADRs (`docs/architecture/adrs/`), en ULTRAPLAN v1.8 (fuera del repo, pedirlo a Kenyi), o requiere preguntar directamente. El repo se actualiza: este documento se revisa cada cierre de semana para incorporar decisiones nuevas.
