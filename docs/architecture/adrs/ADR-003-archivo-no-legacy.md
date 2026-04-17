# ADR-003: Carpeta `archivo/` en lugar de `legacy/`, nada se borra

Fecha: 2026-04-17
Estado: Aceptado.

## Contexto

Código que se retira de la operativa no debe perderse. El término "legacy" tiene connotación negativa (algo obsoleto que estorba). Se prefiere "archivo" (algo que se consulta).

## Decisión

- Carpeta raíz: `archivo/`.
- Nunca `legacy/`.
- Cada subcarpeta contiene un `README.md` explicando:
  - Qué es.
  - De qué repo o rama viene.
  - Fecha de archivo.
  - Por qué se archivó.
  - Cómo se consulta en caso necesario.

## Qué va a `archivo/` en Día 1

- `archivo/portal_frontend_snapshot/`: 23 000 LoC de React + Vite del portal de PGK_Empresa_Autonoma.
- `archivo/portal_backend_snapshot/`: endpoints del portal que no son los 5 workflows Copilot.
- `archivo/scripts_oneoff/`: 49 scripts one-off con rutas hardcoded a Mac de Kenyi.
- `archivo/streamlit_prototipos/`: UIs Streamlit de experimentos.
- `archivo/pgk-despacho-desktop/`: app Electron completa (TypeScript/Bun).

## Consecuencias

- El repo pesa más al inicio (archivo/ es grande).
- Pero garantía de que nada se pierde.
- El pipeline de CI excluye `archivo/` de lint y tests.
