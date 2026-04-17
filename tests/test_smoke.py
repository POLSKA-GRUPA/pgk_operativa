"""Smoke tests del scaffolding."""

from __future__ import annotations

from pathlib import Path

import pytest

from pgk_operativa import __version__
from pgk_operativa.core import llm, paths
from pgk_operativa.core.config import Settings, get_settings


def test_version_exists() -> None:
    assert __version__


def test_repo_root_is_absolute() -> None:
    assert paths.REPO_ROOT.is_absolute()


def test_repo_root_has_pyproject() -> None:
    assert (paths.REPO_ROOT / "pyproject.toml").exists()


def test_package_root_contains_init() -> None:
    assert (paths.PACKAGE_ROOT / "__init__.py").exists()


def test_data_root_is_absolute_and_exists() -> None:
    root = paths.data_root()
    assert root.is_absolute()
    assert root.exists()


def test_memoria_operativa_path_is_absolute() -> None:
    p = paths.memoria_operativa_path()
    assert p.is_absolute()
    assert p.name == "memoria_operativa.db"


def test_engram_path_is_absolute() -> None:
    p = paths.engram_path()
    assert p.is_absolute()
    assert p.name == "engram.db"


def test_user_documents_is_absolute() -> None:
    p = paths.user_documents()
    assert p.is_absolute()


def test_no_hardcoded_users_path_in_python_sources() -> None:
    """Regla de oro: ninguna ruta /Users/... en codigo Python."""
    src = paths.SRC_DIR
    offenders: list[Path] = []
    for py in src.rglob("*.py"):
        text = py.read_text(encoding="utf-8")
        if "/Users/" in text:
            offenders.append(py)
    assert not offenders, f"Rutas hardcoded /Users/ encontradas en: {offenders}"


def test_no_em_dash_in_python_sources() -> None:
    """Estilo PGK: ningun em-dash en codigo."""
    src = paths.SRC_DIR
    offenders: list[Path] = []
    for py in src.rglob("*.py"):
        text = py.read_text(encoding="utf-8")
        if "\u2014" in text:
            offenders.append(py)
    assert not offenders, f"Em-dash encontrado en: {offenders}"


def test_settings_loadable() -> None:
    s = get_settings()
    assert isinstance(s, Settings)
    assert s.environment in {"development", "staging", "production"}


def test_default_llm_config_is_zai() -> None:
    cfg = llm.default_config()
    assert cfg.provider == llm.Provider.ZAI
    assert cfg.model


def test_assert_distinct_consensus_rejects_same_provider() -> None:
    a = llm.LLMConfig(provider=llm.Provider.ZAI, model="glm-4.6", api_key_env="ZAI_API_KEY")
    b = llm.LLMConfig(
        provider=llm.Provider.ZAI, model="glm-4.6-thinking", api_key_env="ZAI_API_KEY"
    )
    with pytest.raises(AssertionError, match="mismo provider"):
        llm.assert_distinct_consensus(a, b)


def test_assert_distinct_consensus_rejects_same_model() -> None:
    a = llm.LLMConfig(provider=llm.Provider.ZAI, model="glm-4.6", api_key_env="ZAI_API_KEY")
    b = llm.LLMConfig(
        provider=llm.Provider.ANTHROPIC, model="glm-4.6", api_key_env="ANTHROPIC_API_KEY"
    )
    with pytest.raises(AssertionError, match="mismo modelo"):
        llm.assert_distinct_consensus(a, b)


def test_assert_distinct_consensus_accepts_distinct() -> None:
    a = llm.LLMConfig(provider=llm.Provider.ZAI, model="glm-4.6", api_key_env="ZAI_API_KEY")
    b = llm.LLMConfig(
        provider=llm.Provider.ANTHROPIC,
        model="claude-sonnet-4-5",
        api_key_env="ANTHROPIC_API_KEY",
    )
    llm.assert_distinct_consensus(a, b)
