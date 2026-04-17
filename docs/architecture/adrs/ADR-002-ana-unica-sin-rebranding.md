# ADR-002: Ana como única cara visible, sin rebranding de módulos

Fecha: 2026-04-17
Estado: Aceptado.

## Contexto

Propuestas previas (documentos 18 y 20 del análisis) sugirieron renombrar los agentes internos a nombres de persona (Ada, Hugo, Leo, Irene, etc.). Kenyi rechazó el rebranding: los empleados no necesitan saber quién está trabajando en cada momento, solo hablan con Ana.

## Decisión

- Cara visible única: **Ana**.
- Módulos conservan su nombre técnico: `pgk.fiscal`, `pgk.contable`, `pgk.laboral`, `pgk.legal`, `pgk.docs`, `pgk.calidad`, `pgk.marketing`, `pgk.consejo`, `pgk.forja`, `pgk.workflows`.
- Los prompts de personalidad (ejemplo: `edu_asesor_contable.md`, `german_derecho.md`) se preservan intactos en `prompts/core/` y se cargan bajo la voz de Ana.
- El empleado no ve nunca los nombres de módulos.

## Consecuencias

- Toda UX orientada al empleado: responde solo "Ana".
- Logs internos sí conservan el nombre del módulo para depuración.
- Documentación técnica (docs, código) usa los nombres de módulos libremente.
