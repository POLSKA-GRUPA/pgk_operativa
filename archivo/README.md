# archivo/

Aquí se preservan los activos que salen de la operativa viva pero que no se borran. Cada subcarpeta incluye su propio `README.md` con:

- Qué es.
- De qué repo y rama viene.
- Fecha de archivo.
- Motivo del archivo.
- Cómo consultarlo si hace falta.

## Reglas

- Nada entra aquí sin README explicativo.
- Nada se borra de aquí.
- CI y lint excluyen esta carpeta.
- No se re-importa código de aquí a `src/` sin ADR que lo justifique.

## Contenido previsto (Día 1 en adelante)

- `portal_frontend_snapshot/`: React + Vite del portal de PGK_Empresa_Autonoma.
- `portal_backend_snapshot/`: endpoints del portal no migrados (todo lo que no sean los 5 workflows Copilot).
- `scripts_oneoff/`: 49 scripts con rutas hardcoded a la máquina de Kenyi.
- `streamlit_prototipos/`: UIs Streamlit experimentales.
- `pgk-despacho-desktop/`: app Electron (TypeScript/Bun) completa.

Estado actual: vacía. Se poblará en Semana 1 cuando arranquen las migraciones desde los repos origen.

Ver `docs/architecture/adrs/ADR-003-archivo-no-legacy.md`.
