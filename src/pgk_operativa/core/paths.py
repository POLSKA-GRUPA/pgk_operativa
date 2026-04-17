"""Rutas absolutas calculadas en runtime.

Regla inviolable: ninguna ruta hardcoded, ninguna ruta relativa.
Todas las rutas se derivan de `Path(__file__).resolve()` o de variables
de entorno explicitas.

El repo es descargable y funciona en cualquier maquina.
"""

from __future__ import annotations

import os
from pathlib import Path


def _repo_root() -> Path:
    """Raiz del repo, calculada desde la ubicacion de este archivo.

    Estructura: <REPO>/src/pgk_operativa/core/paths.py
    Por tanto repo_root = parents[3].
    """
    return Path(__file__).resolve().parents[3]


def _package_root() -> Path:
    """Raiz del paquete Python instalado.

    Util cuando el paquete se distribuye como wheel y no hay repo.
    Estructura: <PKG>/core/paths.py -> parents[1].
    """
    return Path(__file__).resolve().parents[1]


REPO_ROOT: Path = _repo_root()
PACKAGE_ROOT: Path = _package_root()

# Carpetas del repo (existen en modo dev, pueden no existir en modo wheel)
SRC_DIR: Path = REPO_ROOT / "src"
TESTS_DIR: Path = REPO_ROOT / "tests"
DOCS_DIR: Path = REPO_ROOT / "docs"
ARCHIVO_DIR: Path = REPO_ROOT / "archivo"
SCRIPTS_DIR: Path = REPO_ROOT / "scripts"


def data_root() -> Path:
    """Raiz de datos locales (memoria, vectores, caches, logs).

    Prioridad:
      1. `PGK_DATA_ROOT` si esta en entorno.
      2. `~/.local/share/pgk_operativa` en modo usuario.
      3. `REPO_ROOT/data` en modo dev.

    Siempre devuelve ruta absoluta existente (la crea si falta).
    """
    env = os.environ.get("PGK_DATA_ROOT")
    if env:
        root = Path(env).expanduser().resolve()
    elif (REPO_ROOT / "data").exists() or os.environ.get("PGK_ENVIRONMENT") == "development":
        root = REPO_ROOT / "data"
    else:
        root = Path.home() / ".local" / "share" / "pgk_operativa"
    root.mkdir(parents=True, exist_ok=True)
    return root


def memoria_operativa_path() -> Path:
    """Ruta al SQLite de memoria operativa (BD 2 de las 3 inviolables)."""
    return data_root() / "memoria" / "memoria_operativa.db"


def engram_path() -> Path:
    """Ruta al SQLite de engram (BD 3 de las 3 inviolables)."""
    return data_root() / "engram" / "engram.db"


def vector_db_path() -> Path:
    """Ruta a ChromaDB local."""
    return data_root() / "vector_db"


def logs_path() -> Path:
    """Ruta de logs locales."""
    p = data_root() / "logs"
    p.mkdir(parents=True, exist_ok=True)
    return p


def user_documents() -> Path:
    """Ruta del directorio de documentos del empleado (Drive local etc).

    Obligatorio leer de entorno `PGK_LOCAL_DOCUMENTS_PATH`. Sin valor,
    devuelve `~/Documents/PGK`.
    """
    env = os.environ.get("PGK_LOCAL_DOCUMENTS_PATH")
    if env:
        return Path(env).expanduser().resolve()
    return (Path.home() / "Documents" / "PGK").resolve()


__all__ = [
    "ARCHIVO_DIR",
    "DOCS_DIR",
    "PACKAGE_ROOT",
    "REPO_ROOT",
    "SCRIPTS_DIR",
    "SRC_DIR",
    "TESTS_DIR",
    "data_root",
    "engram_path",
    "logs_path",
    "memoria_operativa_path",
    "user_documents",
    "vector_db_path",
]
