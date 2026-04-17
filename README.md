# pgk_operativa

Super-agente unificado de Polska Grupa Konsultingowa S.L.

Cerebro único de negocio: grafo LangGraph con Ana como cara visible. Los trabajadores conversan solamente con Ana, nunca ven los nombres de los módulos internos.

## Qué es

Repositorio que consolida 7 sistemas previos en uno solo:

- Grafo multi-agente (PGK_Empresa_Autonoma)
- Motor fiscal y contable (conta-pgk-hispania)
- Motor laboral determinista (pgk-laboral-desk)
- Consejo de dirección (PGK-direccion-general)
- Revisor unificado (PROGRAMADOR_FRIKI_PGK)
- Marketing (PGK-Marketing-Autonomo)
- Arquitectura base (pgk-core-architecture)

Más 17 skills legales de `junior` integradas como conocimiento.

## Principios no negociables

1. Ana única cara visible para empleados y clientes.
2. Rutas siempre absolutas calculadas en runtime con `Path(__file__).resolve()`. Nunca hardcoded, nunca relativas.
3. Consenso como comando opt-in `/consenso`, no como default.
4. Default LLM: Z.ai GLM coding plan vía OpenAI SDK proxy.
5. Tres bases de datos inviolables: `pgk_database` remoto Postgres, `memoria_operativa.db` SQLite local, `engram.db` SQLite local.
6. Identidad dual de empleado: email lógico más `emp_<slug>_<uuid4>` técnico, siempre en grupo `pgk_empleado`.
7. Emails siempre como borrador, nunca envío directo.
8. Nada se borra: lo antiguo pasa a `archivo/` con README explicativo y fecha.
9. Estilo PGK en todo documento generado: sin em-dash, sin líneas decorativas.

## Arquitectura en una línea

```
empleado -> Ana (CLI / Mattermost / email) -> grafo LangGraph -> módulos técnicos -> 3 BDs
```

Módulos técnicos: `pgk.fiscal`, `pgk.contable`, `pgk.laboral`, `pgk.legal`, `pgk.docs`, `pgk.calidad`, `pgk.marketing`, `pgk.consejo`, `pgk.forja`, `pgk.workflows`.

El empleado nunca los ve. Ana enruta, responde, firma.

## Uso básico

```bash
# Consulta normal (1 solo modelo, Z.ai por defecto)
pgk ana "¿cómo declaro el IRNR de Kowalski 2024?"

# Consulta con consenso explícito (2 proveedores distintos)
pgk ana --consenso "decisión fiscal de alto impacto sobre X"

# Fichaje legal
pgk ana "entrada"
pgk ana "salida"

# Administración (solo admin)
pgk admin alta --email nuevo@pgkhiszpania.com
```

## Estado

En construcción. Semana 0 Día 0. Scaffolding inicial.

## Documentación

Ver `docs/`:

- `docs/ARCHITECTURE.md`: arquitectura detallada.
- `docs/BDS.md`: las 3 bases de datos, su rol, su schema.
- `docs/ADVISOR.md`: rol del asesor permanente (Claude Opus 4.7).
- `docs/ESTILO_PGK.md`: normas de redacción.
- `docs/architecture/adrs/`: decisiones arquitectónicas registradas.

## Licencia

Privado, propiedad de Polska Grupa Konsultingowa S.L.
