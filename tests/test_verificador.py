"""Tests del verificador: manifest parsing + checks estaticos + orquestador."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from pgk_operativa.verificador.auditor import audit
from pgk_operativa.verificador.checks.fidelity_check import (
    _parse_lineas,
)
from pgk_operativa.verificador.checks.fidelity_check import (
    run as _run_fidelity,
)
from pgk_operativa.verificador.checks.imports_check import run as _run_imports
from pgk_operativa.verificador.checks.lines_check import run as _run_lines
from pgk_operativa.verificador.checks.shell_check import run as _run_shell
from pgk_operativa.verificador.checks.targets_check import run as _run_targets
from pgk_operativa.verificador.checks.tests_check import (
    _is_noop_test,
)
from pgk_operativa.verificador.checks.tests_check import (
    run as _run_tests_check,
)
from pgk_operativa.verificador.checks.todo_check import run as _run_todo
from pgk_operativa.verificador.manifest import (
    ArchivoManifest,
    Manifest,
    Origen,
    Relacion,
    list_manifests,
    manifests_dir,
)
from pgk_operativa.verificador.report import Finding, Severity


def _write_manifest(path: Path, data: dict[str, object]) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def test_manifest_load_minimal(tmp_path: Path) -> None:
    manifest_path = tmp_path / "PR-0001.yaml"
    _write_manifest(
        manifest_path,
        {
            "pr": 1,
            "fecha": "2026-04-16",
            "titulo": "Test PR",
            "archivos": [
                {"target": "src/a.py", "relacion": "nuevo", "notas": "archivo nuevo"},
            ],
        },
    )
    m = Manifest.load(manifest_path)
    assert m.pr == 1
    assert m.titulo == "Test PR"
    assert len(m.archivos) == 1
    assert m.archivos[0].relacion == Relacion.NUEVO
    assert m.archivos[0].origen is None


def test_manifest_load_with_origen(tmp_path: Path) -> None:
    manifest_path = tmp_path / "PR-0002.yaml"
    _write_manifest(
        manifest_path,
        {
            "pr": 2,
            "fecha": "2026-04-17",
            "titulo": "Copia adaptada",
            "archivos": [
                {
                    "target": "src/b.py",
                    "relacion": "adaptado",
                    "origen": {
                        "repo": "repo_origen",
                        "path": "src/original.py",
                        "simbolos": ["foo", "bar"],
                    },
                    "notas": "adaptado",
                }
            ],
        },
    )
    m = Manifest.load(manifest_path)
    assert m.archivos[0].origen is not None
    assert m.archivos[0].origen.repo == "repo_origen"
    assert m.archivos[0].origen.simbolos == ["foo", "bar"]


def test_manifest_rejects_adaptado_without_origen(tmp_path: Path) -> None:
    manifest_path = tmp_path / "PR-0003.yaml"
    _write_manifest(
        manifest_path,
        {
            "pr": 3,
            "fecha": "2026-04-17",
            "titulo": "Broken",
            "archivos": [{"target": "src/x.py", "relacion": "adaptado"}],
        },
    )
    with pytest.raises(ValueError, match="requiere origen"):
        Manifest.load(manifest_path)


def test_manifest_rejects_invalid_relacion(tmp_path: Path) -> None:
    manifest_path = tmp_path / "PR-0004.yaml"
    _write_manifest(
        manifest_path,
        {
            "pr": 4,
            "fecha": "2026-04-17",
            "titulo": "Broken",
            "archivos": [{"target": "src/x.py", "relacion": "plagiado"}],
        },
    )
    with pytest.raises(ValueError, match="relacion invalida"):
        Manifest.load(manifest_path)


def test_manifest_rejects_malformed_yaml(tmp_path: Path) -> None:
    """YAML sintacticamente invalido debe convertirse en ValueError, no crashear."""
    manifest_path = tmp_path / "PR-9999.yaml"
    manifest_path.write_text("pr: 1\n  bad: [indent\n", encoding="utf-8")
    with pytest.raises(ValueError, match="YAML invalido"):
        Manifest.load(manifest_path)


def _make_manifest(archivos: list[ArchivoManifest], pr: int = 99) -> Manifest:
    return Manifest(pr=pr, fecha="2026-04-17", titulo="Test", archivos=archivos)


def test_targets_check_detects_missing(tmp_path: Path) -> None:
    archivo = ArchivoManifest(
        target="src/no_existe.py",
        relacion=Relacion.NUEVO,
        origen=None,
        notas="",
    )
    manifest = _make_manifest([archivo])
    findings = _run_targets(manifest, tmp_path, tmp_path)
    assert any(f.severity == Severity.CRITICAL for f in findings)
    assert any("no existe" in f.mensaje.lower() for f in findings)


def test_targets_check_passes_for_existing(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
    archivo = ArchivoManifest(target="src/a.py", relacion=Relacion.NUEVO, origen=None, notas="")
    manifest = _make_manifest([archivo])
    findings = _run_targets(manifest, tmp_path, tmp_path)
    assert not findings


def test_lines_check_detects_empty_shell(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "empty.py").write_text("# solo comentario\n", encoding="utf-8")
    archivo = ArchivoManifest(target="src/empty.py", relacion=Relacion.NUEVO, origen=None, notas="")
    findings = _run_lines(_make_manifest([archivo]), tmp_path, tmp_path)
    assert any(f.severity == Severity.HIGH for f in findings)


def test_lines_check_skips_init(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "__init__.py").write_text("", encoding="utf-8")
    archivo = ArchivoManifest(
        target="src/__init__.py", relacion=Relacion.NUEVO, origen=None, notas=""
    )
    findings = _run_lines(_make_manifest([archivo]), tmp_path, tmp_path)
    assert not findings


def test_shell_check_detects_pass_body(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "stub.py").write_text(
        "def foo() -> None:\n    pass\n\ndef bar() -> None:\n    pass\n",
        encoding="utf-8",
    )
    archivo = ArchivoManifest(target="src/stub.py", relacion=Relacion.NUEVO, origen=None, notas="")
    findings = _run_shell(_make_manifest([archivo]), tmp_path, tmp_path)
    assert findings


def test_todo_check_detects_unassigned(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "t.py").write_text("# TODO: arreglar algo\nx = 1\n", encoding="utf-8")
    archivo = ArchivoManifest(target="src/t.py", relacion=Relacion.NUEVO, origen=None, notas="")
    findings = _run_todo(_make_manifest([archivo]), tmp_path, tmp_path)
    assert findings
    assert all(f.severity == Severity.LOW for f in findings)


def test_tests_check_detects_noop(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text(
        "def test_uno() -> None:\n    assert True\n",
        encoding="utf-8",
    )
    archivo = ArchivoManifest(
        target="tests/test_x.py", relacion=Relacion.NUEVO, origen=None, notas=""
    )
    findings = _run_tests_check(_make_manifest([archivo]), tmp_path, tmp_path)
    assert findings


def test_imports_check_pgk_operativa(tmp_path: Path) -> None:
    (tmp_path / "src" / "pgk_operativa" / "core").mkdir(parents=True)
    (tmp_path / "src" / "pgk_operativa" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "src" / "pgk_operativa" / "core" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "src" / "pgk_operativa" / "core" / "paths.py").write_text(
        "REPO_ROOT = 1\n", encoding="utf-8"
    )
    archivo_ok = ArchivoManifest(target="mod_ok.py", relacion=Relacion.NUEVO, origen=None, notas="")
    (tmp_path / "mod_ok.py").write_text(
        "from pgk_operativa.core.paths import REPO_ROOT\nx = REPO_ROOT\n",
        encoding="utf-8",
    )
    archivo_ko = ArchivoManifest(target="mod_ko.py", relacion=Relacion.NUEVO, origen=None, notas="")
    (tmp_path / "mod_ko.py").write_text(
        "from pgk_operativa.inexistente import X\n",
        encoding="utf-8",
    )
    findings = _run_imports(_make_manifest([archivo_ok, archivo_ko]), tmp_path, tmp_path)
    # Solo debe levantar un finding para el import inexistente.
    assert any("inexistente" in f.mensaje for f in findings)
    assert not any("paths" in f.mensaje for f in findings)


def test_fidelity_check_warns_missing_symbols(tmp_path: Path) -> None:
    # Origen con clase Foo pero manifest declara Bar.
    origen_root = tmp_path / "repos" / "repo_x"
    (origen_root / "src").mkdir(parents=True)
    (origen_root / "src" / "file.py").write_text(
        "class Foo:\n    pass\n",
        encoding="utf-8",
    )
    (tmp_path / "src").mkdir(exist_ok=True)
    (tmp_path / "src" / "copia.py").write_text("class Foo:\n    pass\n", encoding="utf-8")
    archivo = ArchivoManifest(
        target="src/copia.py",
        relacion=Relacion.ADAPTADO,
        origen=Origen(repo="repo_x", path="src/file.py", simbolos=["Bar"]),
        notas="",
    )
    findings = _run_fidelity(_make_manifest([archivo]), tmp_path, tmp_path / "repos")
    assert any(f.severity == Severity.HIGH for f in findings)


def test_audit_aggregates_findings(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "good.py").write_text(
        "def foo() -> int:\n"
        "    value = 42\n"
        "    return value\n"
        "\n\n"
        "def bar() -> int:\n"
        "    result = foo() + 1\n"
        "    return result\n",
        encoding="utf-8",
    )
    archivo = ArchivoManifest(target="src/good.py", relacion=Relacion.NUEVO, origen=None, notas="")
    manifest = _make_manifest([archivo])
    report = audit(manifest, repo_root=tmp_path, repos_root=tmp_path)
    # Sin hallazgos CRITICAL o HIGH en este caso.
    assert not report.has_critical
    assert not report.has_high


def test_audit_skips_semantic_by_default(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "x.py").write_text("x = 1\n", encoding="utf-8")
    archivo = ArchivoManifest(target="src/x.py", relacion=Relacion.NUEVO, origen=None, notas="")
    report = audit(
        _make_manifest([archivo]), repo_root=tmp_path, repos_root=tmp_path, semantico=False
    )
    # No debe haber findings de check "semantic".
    assert not any(f.check == "semantic" for f in report.findings)


def test_report_finding_severity_ordering() -> None:
    f_low = Finding(check="x", severity=Severity.LOW, target="a", mensaje="m", detalle="d")
    f_crit = Finding(check="x", severity=Severity.CRITICAL, target="a", mensaje="m", detalle="d")
    assert Severity.CRITICAL.value > Severity.LOW.value
    assert f_crit.severity.value > f_low.severity.value


def test_manifest_rejects_non_dict_archivos_entries(tmp_path: Path) -> None:
    """archivos con entries str/None debe dar ValueError, no AttributeError."""
    manifest_path = tmp_path / "PR-7777.yaml"
    _write_manifest(
        manifest_path,
        {
            "pr": 7777,
            "fecha": "2026-04-17",
            "titulo": "Bad entries",
            "archivos": ["src/a.py", None],
        },
    )
    with pytest.raises(ValueError, match="archivos\\[0\\] debe ser un dict"):
        Manifest.load(manifest_path)


def test_fidelity_check_handles_syntax_error_in_origen(tmp_path: Path) -> None:
    """Origen con SyntaxError no debe disparar HIGH falso positivo por simbolos."""
    origen_root = tmp_path / "repos" / "repo_x"
    (origen_root / "src").mkdir(parents=True)
    # Archivo con syntax error: `def foo(` sin cerrar.
    (origen_root / "src" / "broken.py").write_text("def foo(\n    pass\n", encoding="utf-8")
    (tmp_path / "src").mkdir(exist_ok=True)
    (tmp_path / "src" / "copia.py").write_text("x = 1\n", encoding="utf-8")
    archivo = ArchivoManifest(
        target="src/copia.py",
        relacion=Relacion.ADAPTADO,
        origen=Origen(repo="repo_x", path="src/broken.py", simbolos=["foo"]),
        notas="",
    )
    findings = _run_fidelity(_make_manifest([archivo]), tmp_path, tmp_path / "repos")
    # Debe avisar con MEDIUM (no parseable), no HIGH por "missing".
    assert any(f.severity == Severity.MEDIUM and "parsear" in f.mensaje.lower() for f in findings)
    assert not any(
        f.severity == Severity.HIGH and "no existen" in f.mensaje.lower() for f in findings
    )


def test_parse_lineas_rejects_zero_and_negative_single() -> None:
    """_parse_lineas no debe aceptar '0' ni '-1' como rango valido."""
    assert _parse_lineas("0") is None
    assert _parse_lineas("-1") is None
    assert _parse_lineas("1") == (1, 1)
    assert _parse_lineas("42") == (42, 42)


def test_is_noop_test_failing_compare_is_not_noop() -> None:
    """`assert 1 == 2` no es no-op: siempre falla, merece respeto del auditor."""
    import ast as _ast

    tree = _ast.parse("def test_x():\n    assert 1 == 2\n")
    fn = tree.body[0]
    assert isinstance(fn, _ast.FunctionDef)
    assert _is_noop_test(fn) is False


def test_is_noop_test_true_compare_is_noop() -> None:
    """`assert 1 == 1` y `assert 2 > 1` sí son no-op triviales."""
    import ast as _ast

    for src in ("def t():\n    assert 1 == 1\n", "def t():\n    assert 2 > 1\n"):
        tree = _ast.parse(src)
        fn = tree.body[0]
        assert isinstance(fn, _ast.FunctionDef)
        assert _is_noop_test(fn) is True


def test_imports_check_does_not_match_sibling_package(tmp_path: Path) -> None:
    """`pgk_operativa_extra` no es submodulo de pgk_operativa y no debe colarse."""
    (tmp_path / "src" / "pgk_operativa").mkdir(parents=True)
    (tmp_path / "src" / "pgk_operativa" / "__init__.py").write_text("", encoding="utf-8")
    archivo = ArchivoManifest(target="mod.py", relacion=Relacion.NUEVO, origen=None, notas="")
    (tmp_path / "mod.py").write_text("import pgk_operativa_extra\n", encoding="utf-8")
    findings = _run_imports(_make_manifest([archivo]), tmp_path, tmp_path)
    # No debe flagear nada: no es nuestro paquete.
    assert not findings


def test_manifests_dir_resolves() -> None:
    md = manifests_dir()
    assert md.name == "pr_manifests"


def test_list_manifests_returns_sorted() -> None:
    manifests = list_manifests()
    assert len(manifests) >= 4  # PR-0001..PR-0004
    assert manifests == sorted(manifests)
    assert all(p.suffix == ".yaml" for p in manifests)
