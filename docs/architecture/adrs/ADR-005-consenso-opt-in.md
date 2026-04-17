# ADR-005: Consenso como comando opt-in, default single-model

Fecha: 2026-04-17
Estado: Aceptado.

## Contexto

La propuesta inicial asumía consenso de 2 modelos como default para toda respuesta de Ana. Presupuesto estimado: 500 a 700 USD/mes. Latencia doblada.

Kenyi ordenó: "QUIERO QUE SEA UNA FUNCIÓN, NO OBLIGATORIO, UN COMANDO".

## Decisión

- **Default**: Ana responde con 1 solo modelo. OpenAI SDK apuntando a Z.ai coding plan (`base_url=https://api.z.ai/api/coding/paas/v4`, modelo `glm-4.6`).
- **Opt-in**: el empleado invoca `/consenso` explícitamente cuando quiere segunda opinión.
  - Flag CLI: `pgk ana --consenso "<mensaje>"`.
  - En chat: mensaje que empiece por `/consenso `.
- **Garantía runtime**: al activarse, `assert provider_A != provider_B AND model_A != model_B`. Si solo hay 1 proveedor, degrada a `consensus_type = "single_model"` con aviso al empleado.

## Proveedores disponibles (presupuesto real por mes)

- Z.ai GLM-4.6 coding plan (default): barato.
- Anthropic Sonnet 4.5 vía Z.ai proxy: coste medio.
- Gemini 2.5 Pro: medio.
- Grok-3: medio.
- DeepSeek: bajo.
- GPT-4o: medio-alto.

Presupuesto proyectado: 80 a 250 USD/mes (antes 500 a 700).

## Consecuencias

- Respuestas normales rápidas y baratas.
- Consenso reservado a decisiones de alto impacto (fiscal, legal, financiero).
- Red team se ejecuta solo con `/consenso` activo o por umbrales automáticos (monto > X, tipo legal Y).
