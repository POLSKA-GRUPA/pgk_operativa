# scripts/

Scripts de mantenimiento y desarrollo. Todos con rutas absolutas runtime.

## Reglas

- No hardcodear rutas a máquina específica.
- Usar `Path(__file__).resolve()` o variables de entorno.
- Docstring explicando qué hace.
- Si el script es one-off, vivir en `archivo/scripts_oneoff/`.

## Contenido previsto

- `setup_dev.sh`: instala dependencias y pre-commit.
- `smoke_llm.py`: prueba rápida de todos los proveedores LLM configurados.
- `smoke_tunnel.py`: prueba túnel SSH y query a Postgres.
- `importar_engram.py`: copia aprendizajes de `engram.db` a `memoria_operativa.db`.

Estado actual: vacío.
