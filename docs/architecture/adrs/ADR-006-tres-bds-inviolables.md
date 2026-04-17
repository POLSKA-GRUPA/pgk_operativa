# ADR-006: Tres bases de datos inviolables

Fecha: 2026-04-17
Estado: Aceptado.

## Contexto

Propuestas previas consideraron unificar `memoria_operativa.db` con `pgk_database`. Rechazado: son memorias con ciclos de vida distintos, accesos distintos, sensibilidad distinta.

## Decisión

Tres bases de datos, ninguna se fusiona:

1. **`pgk_database`** (Postgres remoto 209.74.72.83, schema `pgk_admin`, vía túnel SSH).
   - Datos administrativos y de negocio (users, fichajes, clientes, expedientes, audit).
   - Backup en servidor remoto.
   - RLS obligatorio, append-only en audit y fichajes.

2. **`memoria_operativa.db`** (SQLite local).
   - Memoria de negocio del agente: aprendizajes, decisiones, patrones.
   - Vive por máquina (no sincronizada entre empleados).
   - Importable desde `engram.db` con script dedicado.
   - FTS5 habilitado.

3. **`engram.db`** (SQLite local).
   - Memoria de desarrollo del agente IA entre sesiones (gestionada por MCP `engram`).
   - Vive por máquina del desarrollador.
   - Se exporta a `memoria_operativa.db` cuando una decisión de desarrollo se vuelve patrón de negocio.

## Consecuencias

- Cada BD tiene su schema, sus migraciones, su backup.
- El módulo `pgk.memoria` expone una API unificada con routers internos, pero la persistencia está separada.
- Cambios de motor o fusiones requieren nuevo ADR.
