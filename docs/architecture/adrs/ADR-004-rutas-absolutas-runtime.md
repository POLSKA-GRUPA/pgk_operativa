# ADR-004: Rutas siempre absolutas calculadas en runtime

Fecha: 2026-04-17
Estado: Aceptado.

## Contexto

La auditoría de portabilidad (documento 16) detectó 49 scripts one-off con rutas hardcoded a la máquina de Kenyi (`/Users/kenyi/Downloads/`, `~/Library/CloudStorage/...`). Eso bloqueaba que otros empleados clonaran el repo y arrancaran.

Kenyi ordenó: "RUTAS ABSOLUTAS SIEMPRE, QUIERO QUE ESTO SEA DESCARGABLE".

## Decisión

Patrón obligatorio en todo código Python del repo:

```python
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[N]  # N según profundidad
```

Todas las rutas se derivan de:

1. `Path(__file__).resolve()` (posición del archivo).
2. `Path.home()` (home del usuario actual).
3. Variable de entorno explícita (`PGK_USER_HOME`, `PGK_DATA_ROOT`, etc).

PROHIBIDO:

- Rutas relativas (`./data`, `../config`).
- Rutas hardcoded a máquina específica (`/Users/kenyi/...`, `/home/ubuntu/...`).
- `os.getcwd()` como base de cálculo (depende del directorio desde el que se ejecute).

## Implementación

- `src/pgk_operativa/core/paths.py` centraliza todo el cómputo de rutas.
- Resto del código importa de ahí: `from pgk_operativa.core.paths import REPO_ROOT, data_root, ...`.
- Tests smoke validan que no hay `/Users/` ni em-dash en código.
- Pre-commit y CI bloquean regresiones.

## Consecuencias

- El repo arranca en cualquier máquina (Mac, Linux, WSL) tras `uv sync` y `.env` configurado.
- Los 49 scripts one-off con rutas Mac se portan a `archivo/scripts_oneoff/` para auditoría y se reescriben en `scripts/` si se reutilizan.
