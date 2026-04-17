# Las 3 bases de datos inviolables

Ninguna se unifica. Ninguna se renombra. Ninguna cambia de motor sin ADR.

## 1. `pgk_database` (Postgres remoto)

Host: `209.74.72.83:5432` vía túnel SSH.
Schema: `pgk_admin`.
Usuarios de aplicación: `dev_devin` (desarrollo), `admin_kenyi` (admin).

Tablas principales:

- `users`: empleados (email lógico + `emp_<slug>_<uuid4>`).
- `fichajes`: entradas y salidas append-only (RLS activo).
- `audit_log`: auditoría de acciones críticas.
- `clientes_pgk`: ficha fiscal del cliente (NIF/NIE, nombre, dirección, régimen).
- `expedientes`: expedientes abiertos por cliente.
- `procedimientos_pgk`: tipos de procedimiento fiscal/legal.
- `plazos_aeat_clientes`: plazos AEAT calculados por cliente.

Reglas:

- RLS obligatorio en `fichajes` y `audit_log`.
- Trigger append-only: UPDATE y DELETE prohibidos a nivel motor.
- Migraciones por Alembic siempre, nunca `ALTER TABLE` directo.
- Todas las queries filtradas por `company_id` cuando aplique.

## 2. `memoria_operativa.db` (SQLite local)

Ubicación runtime: `data_root() / "memoria" / "memoria_operativa.db"`.

Memoria de negocio del agente. FTS5 habilitado.

Tablas:

- `aprendizajes`: patrones aprendidos por caso.
- `decisiones`: decisiones tomadas con contexto.
- `memorias_caso`: memoria asociada a un expediente.
- `reglas_refinadas`: reglas de negocio que se afinan con el uso.

API runtime:

```python
from pgk_operativa.memoria import get_memoria_operativa
mo = get_memoria_operativa()  # singleton thread-safe
```

Reglas:

- Los nodos cargan memorias relevantes antes de ejecutarse (auto-context).
- Los nodos guardan aprendizajes al finalizar cada caso (auto-save).
- Importable desde Engram con `scripts/importar_engram.py`.

## 3. `engram.db` (SQLite local)

Ubicación runtime: `data_root() / "engram" / "engram.db"`.

Memoria de desarrollo del agente IA entre sesiones. Gestionada por MCP `engram`.

Reglas:

- `mem_save` después de cada acción significativa (código, bug, decisión, patrón, descubrimiento).
- `mem_context` al iniciar sesión.
- `mem_session_summary` al cerrar sesión.
- NO esperar al final de sesión: el contexto puede llenarse antes.
