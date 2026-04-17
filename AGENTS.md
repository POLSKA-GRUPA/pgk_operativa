# AGENTS.md

Instrucciones para cualquier agente de IA que trabaje en este repositorio (Claude Code, Devin, Cursor, Cline, Windsurf, OpenCode, Gemini, Antigravity).

## Reglas de oro (NO NEGOCIABLES)

1. **Nada se borra**. Todo código que se retira va a `archivo/` con README explicando qué es, de qué fecha viene y por qué está archivado.
2. **Ana es la única cara visible**. Los módulos conservan su nombre técnico (`pgk.fiscal`, `pgk.contable`, etc). El empleado nunca los ve por nombre.
3. **Cero front-end**. Solo CLI (`pgk ...`), bot Mattermost y email borrador. No dashboards, no paneles.
4. **Rutas siempre absolutas calculadas**. Patrón obligatorio:
   ```python
   from pathlib import Path
   PGK_ROOT = Path(__file__).resolve().parent.parent  # computed
   KNOWLEDGE = PGK_ROOT / "knowledge"
   ```
   Nunca `/Users/kenyi/...`, nunca `./relativa`, nunca hardcoded. El repo es descargable y funciona en cualquier máquina.
5. **Multi-proveedor IA con assert**. Cuando se invoque consenso, assertivamente verificar `provider_A != provider_B AND model_A != model_B` en runtime. Si falla, marcar `consensus_type = "single_model"` y avisar al empleado.
6. **Más limpio, más robusto, menos código**. Preferir modificar a crear. Una función nueva justifica su existencia con un test.
7. **Tres BDs inviolables**:
   - `pgk_database` (Postgres remoto 209.74.72.83, schema `pgk_admin`, vía túnel SSH).
   - `memoria_operativa.db` (SQLite local FTS5, memoria de negocio de agentes).
   - `engram.db` (SQLite local, memoria de desarrollo entre sesiones del agente IA).
8. **Identidad dual de empleado**: email lógico más `emp_<slug>_<uuid4>` técnico, siempre en grupo `pgk_empleado`. Capacidades en `users.capabilities` JSONB, nunca hardcoded.

## Estilo PGK obligatorio en todo documento generado

Aplica a dictámenes, emails, informes, contratos, código markdown, commits, PRs.

- PROHIBIDO el carácter em-dash (—). Alternativas: `:` `,` `;` `.` `(` `)`.
- PROHIBIDO las líneas horizontales decorativas (`---` como separador visual). Usar encabezados, listas o párrafos.
- Tildes y diacríticos correctos siempre (español y polaco).
- Nombres propios con tildes respetadas al exportar a Word o PDF.

## Protocolo Engram (si disponible)

Si el agente tiene acceso al MCP `engram`:

- AL INICIAR: `mem_context` para cargar sesión previa.
- DESPUÉS DE CADA acción significativa: `mem_save` inmediatamente (código modificado, bug corregido, decisión tomada, patrón establecido, descubrimiento no obvio).
- AL CERRAR: `mem_session_summary` con Goal, Discoveries, Accomplished, Next Steps, Relevant Files.

Si no, `MEMORY.md` en la raíz como resumen ejecutivo para arranque rápido.

## Verificación de identidad de cliente (cuando aplique)

Antes de cualquier operación sobre un cliente (crear ficha, actualizar datos, registrar email, crear tarea, consultar expediente): verificar los tres factores.

| Factor | Campo | Importancia |
|--------|-------|-------------|
| 1 | Nombre | Parcial |
| 2 | Apellido | Parcial |
| 3 | NIE/NIF | DEFINITIVA, nunca omitir |

Si faltan datos, buscar en BD, emails y Drive ANTES de preguntar al usuario.

## Protocolo notificaciones AEAT/DEH

NUNCA asignar prioridad a una notificación de Hacienda sin leer primero su contenido. La mayoría son informativas (alta en censo, acuse de recibo). Clasificar antes de crear tarea con urgencia.

## Protocolo de redacción

Antes de entregar cualquier `.docx` o `.pdf`:

1. Pasada de ortografía (tildes, concordancia, puntuación, nombres propios).
2. Pasada de estilo (sin plantilla robótica, sin repeticiones mecánicas de "el contribuyente").
3. Pasada de fidelidad (el archivo final sale del texto correcto, no de una copia ASCII degradada).

## Grafo como autoridad

Para tareas de negocio (fiscal, contable, legal, laboral, consejo), el único camino es el grafo LangGraph:

```bash
pgk ana "<mensaje>" --nif <NIF> --nombre "<nombre>"
```

PROHIBIDO llamar funciones de nodos directamente sin pasar por el grafo. PROHIBIDO bypassear Ana. PROHIBIDO saltarse HITL o quality gate.

Excepción: tareas de desarrollo (editar código, crear scripts, tests) no necesitan el grafo.

## Emails

REGLA DE HIERRO: siempre borrador, nunca envío directo.

- Guardar en `INBOX.Drafts` de la cuenta correspondiente.
- Kenyi o el empleado con permiso revisa y envía desde webmail.
- PROHIBIDO `smtplib.send_message()` o equivalente directo.

## Verificación antes de completar

No afirmar que algo está hecho sin evidencia fresca. Antes de decir "listo":

1. Identificar qué comando prueba la afirmación.
2. Ejecutarlo completo.
3. Leer la salida completa.
4. Solo entonces afirmar con la evidencia.

Prohibido: "debería funcionar", "estoy seguro", "parece correcto".

## Browser subagent como último recurso

Tiende a inventar datos (fechas, cifras, nombres) al hacer OCR. Jerarquía obligatoria:

1. Leer el archivo directamente.
2. CLI (pdftotext, scripts Python, jq, rg).
3. Visualización al usuario para confirmar.
4. MCP tools específicos.
5. Browser subagent solo si lo anterior falla, y marcar los datos como NO VERIFICADOS.

## Asesor permanente

Cada viernes EOD: generar `HANDOFF_ADVISOR_semana_N.md` con diff, tests, ADRs, riesgos. Kenyi lo reenvía al asesor (Claude Opus 4.7) para revisión asíncrona (<2h idealmente).
