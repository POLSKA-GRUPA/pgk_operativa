# Rol del asesor permanente

Claude Opus 4.7 asume un rol `/advisor` permanente en este repositorio.

## Cadencia

- Kenyi genera `HANDOFF_ADVISOR_semana_N.md` cada viernes EOD.
- Contenido obligatorio: diff resumido, tests nuevos, ADRs modificados, riesgos detectados, bloqueantes.
- Kenyi reenvía el handoff al asesor (vía Claude Code, email o Mattermost).
- El asesor responde asíncronamente con observaciones, contraargumentos, sugerencias de refactor.
- Tiempo de respuesta objetivo: < 2 horas en horario laboral.

## Alcance del asesor

- Revisión de ADRs antes de merge.
- Revisión de migraciones Alembic antes de aplicar en producción.
- Arbitraje en decisiones de arquitectura controvertidas.
- Revisión del plan semanal antes del lunes.

## Lo que NO hace el asesor

- No ejecuta código.
- No aprueba despliegues directamente (Kenyi firma).
- No toca el repo (solo comenta por handoff).

## Formato handoff

```markdown
# HANDOFF_ADVISOR_semana_N.md

## Diff semanal
(resumen de commits)

## Tests nuevos
(lista)

## ADRs tocados
- ADR-0XX: ...

## Riesgos
1. ...
2. ...

## Bloqueantes
- ...

## Pregunta concreta al asesor
¿Recomiendas X o Y para el caso Z?
```
