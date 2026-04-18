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


def test_manifest_rejects_bool_as_pr(tmp_path: Path) -> None:
    """pr: true en YAML no debe colarse como pr=1.

    bool hereda de int en Python: isinstance(True, int) es True. Sin la
    guarda explicita, `pr: true` pasaba silenciosamente y producia informes
    con numero equivocado.
    """
    manifest_path = tmp_path / "PR-0001.yaml"
    _write_manifest(
        manifest_path,
        {
            "pr": True,
            "fecha": "2026-04-16",
            "titulo": "Bool as pr",
            "archivos": [{"target": "x.py", "relacion": "nuevo"}],
        },
    )
    with pytest.raises(ValueError, match="pr debe ser int"):
        Manifest.load(manifest_path)


def test_manifest_detects_filename_yaml_mismatch(tmp_path: Path) -> None:
    """Filename PR-0099.yaml con pr: 5 en YAML debe disparar error."""
    manifest_path = tmp_path / "PR-0099.yaml"
    _write_manifest(
        manifest_path,
        {
            "pr": 5,
            "fecha": "2026-04-16",
            "titulo": "Mismatch",
            "archivos": [{"target": "x.py", "relacion": "nuevo"}],
        },
    )
    with pytest.raises(ValueError, match="Inconsistencia"):
        Manifest.load(manifest_path)


def test_fidelity_symbols_only_top_level(tmp_path: Path) -> None:
    """Simbolo declarado debe existir top-level, no como metodo anidado.

    Regresion: con ast.walk recursivo un manifest que declarase
    simbolos=["foo"] esperando funcion top-level pasaba aunque el origen
    real tuviese `class X: def foo(self)`.
    """
    repos_root = tmp_path / "repos"
    (repos_root / "origen_repo").mkdir(parents=True)
    origen_file = repos_root / "origen_repo" / "src.py"
    origen_file.write_text("class X:\n    def foo(self):\n        pass\n", encoding="utf-8")
    repo_root = tmp_path / "pgk"
    repo_root.mkdir()
    (repo_root / "mod.py").write_text("# copia\n", encoding="utf-8")
    archivo = ArchivoManifest(
        target="mod.py",
        relacion=Relacion.ADAPTADO,
        origen=Origen(repo="origen_repo", path="src.py", simbolos=["foo"]),
        notas="",
    )
    findings = _run_fidelity(_make_manifest([archivo]), repo_root, repos_root)
    # foo es metodo, no top-level: debe aparecer como HIGH por simbolo faltante.
    high = [f for f in findings if f.severity == Severity.HIGH]
    assert len(high) == 1
    assert "foo" in high[0].mensaje


def test_todo_check_ignores_strings_in_python(tmp_path: Path) -> None:
    """TODO dentro de una cadena Python no debe disparar finding."""
    repo_root = tmp_path
    (repo_root / "mod.py").write_text('msg = "TODO: implementar algo"\n', encoding="utf-8")
    archivo = ArchivoManifest(target="mod.py", relacion=Relacion.NUEVO, origen=None, notas="")
    findings = _run_todo(_make_manifest([archivo]), repo_root, repo_root)
    assert findings == []


def test_todo_check_still_matches_real_comment(tmp_path: Path) -> None:
    """TODO en comentario real sigue detectandose."""
    repo_root = tmp_path
    (repo_root / "mod.py").write_text("x = 1  # TODO arreglar esto\n", encoding="utf-8")
    archivo = ArchivoManifest(target="mod.py", relacion=Relacion.NUEVO, origen=None, notas="")
    findings = _run_todo(_make_manifest([archivo]), repo_root, repo_root)
    assert len(findings) == 1


@pytest.mark.parametrize(
    "target",
    [
        "/etc/passwd",
        "../../etc/passwd",
        "src/../../../etc/passwd",
        "..",
        "\\windows\\system32",
    ],
)
def test_manifest_rejects_target_path_traversal(tmp_path: Path, target: str) -> None:
    """archivo.target con rutas absolutas o '..' debe ser rechazado.

    Sin esta guarda, `repo_root / target` resolvia FUERA del repo y los
    checks `exists()` apuntaban a archivos ajenos al proyecto, produciendo
    findings enganosos ("archivo existe" cuando ni siquiera esta en el repo).
    """
    manifest_path = tmp_path / "PR-0001.yaml"
    _write_manifest(
        manifest_path,
        {
            "pr": 1,
            "fecha": "2026-04-16",
            "titulo": "Traversal",
            "archivos": [{"target": target, "relacion": "nuevo"}],
        },
    )
    with pytest.raises(ValueError, match=r"archivo\.target"):
        Manifest.load(manifest_path)


@pytest.mark.parametrize(
    "field,value",
    [
        ("repo", "../../.ssh"),
        ("repo", "/absolute/repo"),
        ("path", "../../etc/passwd"),
        ("path", "/etc/passwd"),
        ("path", "src/../../../secret"),
    ],
)
def test_manifest_rejects_origen_path_traversal(tmp_path: Path, field: str, value: str) -> None:
    """origen.repo y origen.path con `..` o absolutos deben ser rechazados."""
    origen: dict[str, object] = {"repo": "legit_repo", "path": "legit/path.py"}
    origen[field] = value
    manifest_path = tmp_path / "PR-0001.yaml"
    _write_manifest(
        manifest_path,
        {
            "pr": 1,
            "fecha": "2026-04-16",
            "titulo": "Traversal origen",
            "archivos": [
                {
                    "target": "src/a.py",
                    "relacion": "adaptado",
                    "origen": origen,
                }
            ],
        },
    )
    with pytest.raises(ValueError, match=rf"origen\.{field}"):
        Manifest.load(manifest_path)


def test_list_manifests_rejects_non_canonical_names(tmp_path: Path) -> None:
    """Regresion Bug #16: list_manifests() acepta PR-abc.yaml por el glob laxo.

    El glob `PR-*.yaml` matchea cualquier cosa. Si alguien deja un `PR-wip.yaml`
    en la carpeta, al enumerar manifests se explota al intentar convertir
    'wip' a int. Filtramos por regex estricto `^PR-\\d{4}\\.yaml$`.
    """
    (tmp_path / "PR-0001.yaml").write_text("pr: 1\n", encoding="utf-8")
    (tmp_path / "PR-9999.yaml").write_text("pr: 9999\n", encoding="utf-8")
    (tmp_path / "PR-abc.yaml").write_text("garbage", encoding="utf-8")
    (tmp_path / "PR-1.yaml").write_text("garbage", encoding="utf-8")
    (tmp_path / "PR-00001.yaml").write_text("garbage", encoding="utf-8")
    (tmp_path / "PR-0001.yaml.bak").write_text("garbage", encoding="utf-8")
    (tmp_path / "README.md").write_text("no", encoding="utf-8")

    result = list_manifests(manifests_dir_override=tmp_path)
    nombres = [p.name for p in result]

    assert nombres == ["PR-0001.yaml", "PR-9999.yaml"]


@pytest.mark.parametrize(
    ("label", "raw"),
    [
        ("archivo.target", "src\\..\\..\\etc\\passwd"),
        ("archivo.target", "foo\\bar\\..\\..\\etc"),
        ("origen.path", "a\\b\\..\\c"),
    ],
)
def test_reject_escaping_path_detects_windows_backslash(label: str, raw: str) -> None:
    """Regresion Bug #17: _reject_escaping_path usaba solo PurePosixPath.

    PurePosixPath trata `\\` como un caracter literal, no como separador, por
    lo que `src\\..\\..\\etc` queda como un unico part sin `..`. Un manifest
    editado en Windows puede escapar del repo. Evaluamos tambien con
    PureWindowsPath para detectar el caso.
    """
    from pgk_operativa.verificador.manifest import _reject_escaping_path

    with pytest.raises(ValueError, match=r"path traversal|relativa"):
        _reject_escaping_path(label, raw)


def test_reject_escaping_path_rejects_nul_byte() -> None:
    """Regresion Bug #17b: ruta con NUL byte debe rechazarse.

    En POSIX `foo\\x00/etc/passwd` corta la ruta al abrir syscalls, pudiendo
    acceder a archivos distintos del declarado. En Windows lanza OSError
    silenciosamente. Validamos de forma proactiva.
    """
    from pgk_operativa.verificador.manifest import _reject_escaping_path

    with pytest.raises(ValueError, match="NUL"):
        _reject_escaping_path("archivo.target", "foo\x00.py")


def test_auditor_isolates_crashing_check(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Regresion Bug #15: un check que crashee no debe abortar la auditoria.

    Sin try/except por check, un `OSError`/`IndexError`/`KeyError` dentro de
    cualquier runner mata toda la auditoria y oculta findings de los checks
    posteriores. Monkeypatcheamos `targets_check` para lanzar y comprobamos
    que (a) el runner siguiente se ejecuta y (b) aparece finding HIGH del
    crash.
    """
    from pgk_operativa.verificador import auditor, checks

    manifest_path = tmp_path / "PR-0001.yaml"
    _write_manifest(
        manifest_path,
        {
            "pr": 1,
            "fecha": "2026-04-16",
            "titulo": "Test crash isolation",
            "archivos": [
                {"target": "mod.py", "relacion": "nuevo", "notas": "new"},
            ],
        },
    )
    (tmp_path / "mod.py").write_text("x = 1\n", encoding="utf-8")
    manifest = Manifest.load(manifest_path)

    def _boom(*args: object, **kwargs: object) -> list[Finding]:
        raise RuntimeError("boom explicito")

    monkeypatch.setattr(checks, "targets_check", _boom)

    report = auditor.audit(manifest, repo_root=tmp_path, repos_root=tmp_path, semantico=False)

    crash_findings = [f for f in report.findings if f.check == "targets"]
    assert len(crash_findings) == 1
    assert crash_findings[0].severity == Severity.HIGH
    assert "crasheo" in crash_findings[0].mensaje
    assert "RuntimeError" in crash_findings[0].mensaje
    assert "boom explicito" in crash_findings[0].detalle
    # los otros checks siguen ejecutandose: el reporte no quedo vacio ni abortado
    assert len(report.findings) >= 1


def test_shell_check_flags_empty_nested_method(tmp_path: Path) -> None:
    """Regresion: tras quitar el isinstance redundante post-_iter_named,
    metodos anidados con cuerpo trivial siguen siendo detectados.
    """
    repo_root = tmp_path
    (repo_root / "mod.py").write_text(
        "class Foo:\n"
        "    def metodo_real(self):\n"
        "        return 42\n"
        "    def metodo_vacio(self):\n"
        "        pass\n",
        encoding="utf-8",
    )
    archivo = ArchivoManifest(target="mod.py", relacion=Relacion.ADAPTADO, origen=None, notas="")
    findings = _run_shell(_make_manifest([archivo]), repo_root, repo_root)
    nombres = {f.mensaje for f in findings}
    assert any("metodo_vacio" in m for m in nombres)
    assert not any("metodo_real" in m for m in nombres)
    assert all(f.check == "shell" for f in findings)


def test_extract_json_ignores_prose_with_braces() -> None:
    """Regresion Bug #22: find('{') + rfind('}') captura prosa con llaves.

    El LLM puede responder con prosa que incluye placeholders como
    '{funcion_foo}' antes del JSON real. El algoritmo ingenuo creaba un
    slice invalido ('{funcion_foo} ... {"preserva": true}') que fallaba
    al parsearse. Iteramos con raw_decode() desde cada candidato.
    """
    from pgk_operativa.verificador.semantic import _extract_json

    text = (
        "Analizando el archivo, veo que {la funcion foo} esta presente "
        "y cumple su rol. Decision final:\n"
        '{"preserva_intencion": true, "diferencias_materiales": []}'
    )
    data = _extract_json(text)
    assert data["preserva_intencion"] is True
    assert data["diferencias_materiales"] == []


def test_extract_json_handles_fenced_block_with_trailing_prose() -> None:
    """El bloque ```json ... ``` con prosa posterior debe parsearse limpio."""
    from pgk_operativa.verificador.semantic import _extract_json

    text = (
        "```json\n"
        '{"preserva_intencion": false, "diferencias_materiales": ["falta manejo de None"]}\n'
        "```\n"
        "Nota final: revisar con el equipo {antes de mergear}."
    )
    data = _extract_json(text)
    assert data["preserva_intencion"] is False
    assert data["diferencias_materiales"] == ["falta manejo de None"]


def test_manifest_rejects_duplicate_yaml_keys(tmp_path: Path) -> None:
    """Regresion Bug #23: PyYAML safe_load acepta claves duplicadas silenciosamente.

    Un manifest con `pr: 1` y despues `pr: 2` en el mismo mapping se
    cargaria como {'pr': 2} sin aviso, enmascarando un merge conflict
    mal resuelto o un copy-paste accidental. El StrictSafeLoader rechaza
    la carga con ConstructorError, envuelto como ValueError por load().
    """
    manifest_path = tmp_path / "PR-0077.yaml"
    manifest_path.write_text(
        "pr: 77\n"
        "fecha: '2026-04-17'\n"
        "titulo: 'Test duplicate keys'\n"
        "titulo: 'OVERWRITTEN'\n"
        "archivos: []\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="clave YAML duplicada"):
        Manifest.load(manifest_path)


def test_manifest_load_by_pr_number_out_of_range(tmp_path: Path) -> None:
    """Regresion Bug #24: load_by_pr_number aceptaba >9999 produciendo inconsistencia.

    `PR-{pr_number:04d}.yaml` con pr_number=12345 produce `PR-12345.yaml`,
    que luego list_manifests() filtra fuera (regex exige exactamente 4
    digitos). El sistema quedaba con un manifest cargable por numero pero
    invisible al listado global. Se exige rango [1, 9999].
    """
    with pytest.raises(ValueError, match="fuera de rango"):
        Manifest.load_by_pr_number(12345, manifests_dir=tmp_path)
    with pytest.raises(ValueError, match="fuera de rango"):
        Manifest.load_by_pr_number(0, manifests_dir=tmp_path)
    with pytest.raises(ValueError, match="fuera de rango"):
        Manifest.load_by_pr_number(-1, manifests_dir=tmp_path)
    with pytest.raises(ValueError, match="int"):
        Manifest.load_by_pr_number(True, manifests_dir=tmp_path)  # type: ignore[arg-type]


def test_todo_check_respects_escaped_quotes(tmp_path: Path) -> None:
    """Regresion Bug #25: _is_in_comment no respetaba escapes dentro de strings.

    Una cadena como `msg = "cerrado \\" # TODO: algo"` con un escape impar
    cerraba prematuramente el string en la maquina de estados y el `#`
    dentro del string se interpretaba como inicio de comentario,
    emitiendo un falso positivo LOW.
    """
    from pgk_operativa.verificador.checks.todo_check import _is_in_comment

    # TODO dentro de string con escape: NO debe detectarse como comentario.
    linea = 'msg = "hola \\" # TODO: fake"'
    pos = linea.find("TODO")
    assert not _is_in_comment(linea, pos), 'escape \\" no debe cerrar string prematuramente'

    # TODO en comentario real: SI debe detectarse.
    linea2 = "x = 1  # TODO: real"
    pos2 = linea2.find("TODO")
    assert _is_in_comment(linea2, pos2), "TODO en comentario real debe detectarse"

    # Backslash fuera de string no es escape, no debe alterar el parser.
    linea3 = "x = 1 \\\n    # TODO: continuacion"
    pos3 = linea3.find("TODO")
    assert _is_in_comment(linea3, pos3), "backslash fuera de string no es escape"
