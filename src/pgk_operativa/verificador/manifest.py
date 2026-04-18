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

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import cast

import yaml

from pgk_operativa.core.paths import REPO_ROOT

# Matchea PR-0001.yaml, PR-9999.yaml. Rechaza PR-abc.yaml, PR-1.yaml, PR-00001.yaml.
_PR_MANIFEST_FILENAME = re.compile(r"^PR-\d{4}\.yaml$")


class _StrictSafeLoader(yaml.SafeLoader):
    """SafeLoader que rechaza claves duplicadas en mappings.

    PyYAML por defecto acepta `pr: 1\\npr: 2` y devuelve `{'pr': 2}` sin
    aviso. Un manifest con un campo accidentalmente duplicado (copy-paste
    sospechoso, merge conflict mal resuelto) perderia el primer valor sin
    que ningun check lo detecte. Con este loader la carga lanza
    ConstructorError, que `Manifest.load()` envuelve como ValueError.
    """


def _construct_mapping_no_duplicates(
    loader: yaml.SafeLoader, node: yaml.MappingNode
) -> dict[object, object]:
    mapping: dict[object, object] = {}
    for key_node, value_node in node.value:
        # construct_object no esta tipada en PyYAML; cast explicito al tipo
        # real para no propagar `Any` al resto del modulo.
        key = cast(object, loader.construct_object(key_node, deep=True))  # type: ignore[no-untyped-call]
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                None,
                None,
                f"clave YAML duplicada: {key!r}",
                key_node.start_mark,
            )
        mapping[key] = cast(
            object,
            loader.construct_object(value_node, deep=True),  # type: ignore[no-untyped-call]
        )
    return mapping


_StrictSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping_no_duplicates,
)


class Relacion(str, Enum):
    """Tipo de relacion entre archivo destino y origen."""

    COPIA_LITERAL = "copia_literal"
    ADAPTADO = "adaptado"
    INSPIRADO = "inspirado"
    NUEVO = "nuevo"


def _reject_escaping_path(label: str, raw: str) -> None:
    """Rechaza rutas absolutas o que escapan con `..`.

    Sin esta guarda, un manifest con `target: "../../etc/passwd"` se
    resolveria FUERA del repo destino, y los checks `exists()` apuntarian
    a archivos ajenos al proyecto, produciendo findings enganosos.
    Analogamente para `origen.path` y `origen.repo`.

    Validacion cross-platform: evaluamos la ruta como PurePosixPath y
    PureWindowsPath porque un manifest editado en Windows podria escribir
    `src\\..\\..\\etc\\passwd`, que PurePosixPath trata como un unico
    segmento literal (no detecta el `..`) pero PureWindowsPath si descompone
    correctamente.
    """
    # tambien rechazamos NUL bytes: en POSIX cortan la ruta y en Windows
    # lanzan OSError al abrir, silenciando el path real.
    if "\x00" in raw:
        raise ValueError(f"{label} contiene NUL byte, got {raw!r}")
    posix = PurePosixPath(raw)
    win = PureWindowsPath(raw)
    if posix.is_absolute() or win.is_absolute() or raw.startswith(("/", "\\")):
        raise ValueError(f"{label} debe ser ruta relativa, got {raw!r}")
    if ".." in posix.parts or ".." in win.parts:
        raise ValueError(f"{label} no puede contener '..' (path traversal), got {raw!r}")


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
        _reject_escaping_path("origen.repo", repo)
        _reject_escaping_path("origen.path", path)
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
        _reject_escaping_path("archivo.target", target)

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
                data = yaml.load(f, Loader=_StrictSafeLoader)  # noqa: S506
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

        # bool hereda de int en Python: isinstance(True, int) es True.
        # Un YAML con `pr: true` se cargaria como pr=1 silenciosamente.
        # Excluimos bool explicitamente para forzar un entero real.
        if isinstance(pr_raw, bool) or not isinstance(pr_raw, int) or pr_raw <= 0:
            raise ValueError(f"pr debe ser int > 0, got {pr_raw!r}")

        # Validacion filename/YAML: si el archivo sigue el convenio PR-NNNN.yaml,
        # el numero del nombre debe coincidir con el campo pr del YAML. Sin esta
        # guarda, renombrar un manifest sin editar el campo genera informes con
        # el numero equivocado.
        stem = manifest_path.stem
        if stem.startswith("PR-") and stem[3:].isdigit():
            expected = int(stem[3:])
            if expected != pr_raw:
                raise ValueError(
                    f"Inconsistencia: filename '{manifest_path.name}' sugiere "
                    f"pr={expected} pero el YAML declara pr={pr_raw}."
                )
        if not isinstance(archivos_raw, list):
            raise ValueError("archivos debe ser lista")

        # Validamos cada entrada antes de pasarla a from_dict: si es str/None
        # o cualquier tipo no-dict, .get() lanzaria AttributeError, que el CLI
        # no captura (solo atrapa FileNotFoundError/ValueError). Hacemos la
        # validacion aqui para devolver un ValueError util.
        archivos: list[ArchivoManifest] = []
        for idx, a in enumerate(archivos_raw):
            if not isinstance(a, dict):
                raise ValueError(
                    f"archivos[{idx}] debe ser un dict YAML, got {type(a).__name__}: {a!r}"
                )
            archivos.append(ArchivoManifest.from_dict(cast(dict[str, object], a)))
        return cls(
            pr=pr_raw,
            fecha=str(fecha_raw),
            titulo=str(titulo_raw),
            archivos=archivos,
            path=manifest_path,
        )

    @classmethod
    def load_by_pr_number(cls, pr_number: int, manifests_dir: Path | None = None) -> Manifest:
        """Carga manifest por numero de PR desde `docs/pr_manifests/`.

        Rango [1, 9999] porque `PR-{pr_number:04d}.yaml` solo pad-cero a 4
        digitos: pr_number=12345 produciria `PR-12345.yaml`, que luego
        list_manifests() filtra fuera (regex exige 4 digitos) y la carga
        por numero resulta inconsistente con el resto del sistema.
        """
        if not isinstance(pr_number, int) or isinstance(pr_number, bool):
            raise ValueError(f"pr_number debe ser int, got {type(pr_number).__name__}")
        if pr_number <= 0 or pr_number > 9999:
            raise ValueError(
                f"pr_number fuera de rango [1, 9999]: {pr_number}. "
                "El convenio PR-NNNN.yaml limita a 4 digitos."
            )
        base = manifests_dir or (REPO_ROOT / "docs" / "pr_manifests")
        candidate = base / f"PR-{pr_number:04d}.yaml"
        return cls.load(candidate)


def manifests_dir() -> Path:
    """Directorio canonico de manifests en el repo."""
    return REPO_ROOT / "docs" / "pr_manifests"


def list_manifests(manifests_dir_override: Path | None = None) -> list[Path]:
    """Lista manifests con nombre canonico ``PR-NNNN.yaml``.

    El glob `PR-*.yaml` matchea tambien `PR-foo.yaml`, `PR-.yaml`,
    `PR-1.yaml` o `PR-0001.yaml.bak` (no, pero ilustra el punto): cualquier
    nombre no canonico explotaria al llamar `load_by_pr_number` con un
    error confuso (`ValueError: invalid literal for int()`). Filtramos por
    regex estricto para que `list_manifests()` devuelva SOLO archivos que
    `Manifest.load()` puede parsear limpiamente.
    """
    base = manifests_dir_override or manifests_dir()
    if not base.exists():
        return []
    return sorted(p for p in base.glob("PR-*.yaml") if _PR_MANIFEST_FILENAME.match(p.name))
