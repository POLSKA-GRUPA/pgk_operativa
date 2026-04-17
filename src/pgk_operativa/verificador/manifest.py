"""Lectura y validacion de manifests de PR.

Schema YAML:

    pr: 4
    fecha: "2026-04-17"
    titulo: "feat(semana2): descomposicion modulos + subgraph consenso"
    archivos:
      - target: src/pgk_operativa/core/consenso/subgraph.py
        relacion: inspirado      # copia_literal | adaptado | inspirado | nuevo
        origen:
          repo: PROGRAMADOR_FRIKI_PGK
          path: orchestrator/orchestrator.py
          lineas: "120-280"      # opcional, rango inclusivo
          simbolos: ["SharedReasoningDiary"]
        notas: "Topologia StateGraph extraida del patron orchestrator.py."

Relaciones:
- copia_literal: archivo copiado sin cambios materiales. Debe preservar
  la semantica al 100%.
- adaptado: archivo copiado con cambios menores (renames, tipos,
  imports). La intencion del origen debe preservarse.
- inspirado: diseno derivado pero no copiado linea a linea.
- nuevo: archivo original, sin origen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import cast

import yaml

from pgk_operativa.core.paths import REPO_ROOT


class Relacion(str, Enum):
    """Tipo de relacion entre archivo destino y origen."""

    COPIA_LITERAL = "copia_literal"
    ADAPTADO = "adaptado"
    INSPIRADO = "inspirado"
    NUEVO = "nuevo"


@dataclass(frozen=True)
class Origen:
    """Referencia a archivo del repo origen."""

    repo: str
    path: str
    lineas: str | None = None
    simbolos: list[str] = field(default_factory=list)

    def absolute_path(self, repos_root: Path) -> Path:
        """Resuelve la ruta absoluta del archivo origen."""
        return repos_root / self.repo / self.path

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Origen:
        lineas_raw = data.get("lineas")
        lineas = str(lineas_raw) if lineas_raw is not None else None
        simbolos_raw = data.get("simbolos") or []
        if not isinstance(simbolos_raw, list):
            raise ValueError(f"origen.simbolos debe ser lista, got {type(simbolos_raw)}")
        simbolos: list[str] = [str(s) for s in simbolos_raw]
        repo = data.get("repo")
        path = data.get("path")
        if not isinstance(repo, str) or not repo:
            raise ValueError("origen.repo requerido (str no vacio)")
        if not isinstance(path, str) or not path:
            raise ValueError("origen.path requerido (str no vacio)")
        return cls(repo=repo, path=path, lineas=lineas, simbolos=simbolos)


@dataclass(frozen=True)
class ArchivoManifest:
    """Entrada por archivo en el manifest."""

    target: str
    relacion: Relacion
    origen: Origen | None
    notas: str

    def target_path(self, repo_root: Path) -> Path:
        """Ruta absoluta del archivo destino en el repo pgk_operativa."""
        return repo_root / self.target

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> ArchivoManifest:
        target = data.get("target")
        relacion_raw = data.get("relacion")
        origen_raw = data.get("origen")
        notas = data.get("notas") or ""

        if not isinstance(target, str) or not target:
            raise ValueError("archivo.target requerido (str no vacio)")
        if not isinstance(relacion_raw, str):
            raise ValueError("archivo.relacion requerido (str)")

        try:
            relacion = Relacion(relacion_raw)
        except ValueError as exc:
            valid = ", ".join(r.value for r in Relacion)
            raise ValueError(
                f"archivo.relacion invalida: {relacion_raw!r}. Validas: {valid}"
            ) from exc

        origen: Origen | None = None
        if relacion != Relacion.NUEVO:
            if not isinstance(origen_raw, dict):
                raise ValueError(f"archivo {target!r}: relacion={relacion.value} requiere origen")
            origen = Origen.from_dict(cast(dict[str, object], origen_raw))

        return cls(target=target, relacion=relacion, origen=origen, notas=str(notas))


@dataclass(frozen=True)
class Manifest:
    """Manifest completo de un PR."""

    pr: int
    fecha: str
    titulo: str
    archivos: list[ArchivoManifest]
    path: Path | None = None

    @classmethod
    def load(cls, manifest_path: Path) -> Manifest:
        """Carga un manifest desde disco y valida su estructura."""
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest no encontrado: {manifest_path}")
        try:
            with manifest_path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            # yaml.YAMLError (ScannerError, ParserError, ...) no hereda de ValueError.
            # Lo envolvemos para que el CLI pueda capturarlo con su except estrecho.
            raise ValueError(f"YAML invalido en {manifest_path}: {exc}") from exc
        if not isinstance(data, dict):
            raise ValueError(f"Manifest {manifest_path} debe ser un dict YAML")

        pr_raw = data.get("pr")
        fecha_raw = data.get("fecha") or ""
        titulo_raw = data.get("titulo") or ""
        archivos_raw = data.get("archivos") or []

        if not isinstance(pr_raw, int) or pr_raw <= 0:
            raise ValueError(f"pr debe ser int > 0, got {pr_raw!r}")
        if not isinstance(archivos_raw, list):
            raise ValueError("archivos debe ser lista")

        archivos = [ArchivoManifest.from_dict(cast(dict[str, object], a)) for a in archivos_raw]
        return cls(
            pr=pr_raw,
            fecha=str(fecha_raw),
            titulo=str(titulo_raw),
            archivos=archivos,
            path=manifest_path,
        )

    @classmethod
    def load_by_pr_number(cls, pr_number: int, manifests_dir: Path | None = None) -> Manifest:
        """Carga manifest por numero de PR desde `docs/pr_manifests/`."""
        base = manifests_dir or (REPO_ROOT / "docs" / "pr_manifests")
        candidate = base / f"PR-{pr_number:04d}.yaml"
        return cls.load(candidate)


def manifests_dir() -> Path:
    """Directorio canonico de manifests en el repo."""
    return REPO_ROOT / "docs" / "pr_manifests"


def list_manifests(manifests_dir_override: Path | None = None) -> list[Path]:
    """Lista todos los manifests disponibles, ordenados por nombre."""
    base = manifests_dir_override or manifests_dir()
    if not base.exists():
        return []
    return sorted(base.glob("PR-*.yaml"))
