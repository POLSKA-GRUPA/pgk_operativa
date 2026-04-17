# Estilo PGK

Normas de redacción para todo documento generado por Ana o por agentes IA en este repositorio.

## Caracteres prohibidos

- **Em-dash (—)**: usar dos puntos, coma, punto y coma, punto, o paréntesis según contexto.
- **Líneas horizontales decorativas** como `---` usadas solo para separar visualmente sin función estructural: usar encabezados, listas, o párrafos.

## Tildes y diacríticos

- Todas las tildes y eñes respetadas, tanto en castellano como en polaco.
- Nombres propios con tildes preservadas al exportar a Word o PDF.
- Nunca exportar desde una copia ASCII degradada.

## Pasadas obligatorias antes de entregar `.docx` o `.pdf`

1. **Ortografía**: tildes, concordancia, puntuación, nombres propios.
2. **Estilo**: eliminar prosa de plantilla, repeticiones mecánicas (ejemplo: evitar "el contribuyente" en cadena cuando hay alternativas como "Sr. X", "mi representado", "el interesado", "obligado tributario").
3. **Fidelidad**: el `.docx` o `.pdf` final sale del texto correcto, no de una copia ASCII simplificada.

## Aplicación

- Dictámenes.
- Emails (borradores para Kenyi o empleado).
- Informes fiscales.
- Contratos.
- Código markdown del repo (README, AGENTS, docs, ADRs).
- Commits y descripciones de PR.

## Excepciones

- `.pre-commit-config.yaml` permite em-dash porque contiene el patrón prohibido como regla.
- `AGENTS.md` y `docs/ESTILO_PGK.md` los permiten para poder documentar la prohibición.
- `archivo/` no se revisa (código antiguo preservado intacto).

## CI

El pipeline incluye un paso que bloquea merges con em-dash fuera de las excepciones.
