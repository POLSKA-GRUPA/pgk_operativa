"""Factoria de clientes LLM.

Default: OpenAI SDK apuntando a Z.ai coding plan (GLM-4.6).
Consenso opt-in: al invocarse `/consenso`, se eligen 2 proveedores
distintos verificando en runtime `provider_A != provider_B AND
model_A != model_B`. Si falla, degrada a `consensus_type = "single_model"`
con aviso al empleado.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from pgk_operativa.core.config import get_settings

if TYPE_CHECKING:
    from openai import OpenAI


class Provider(str, Enum):
    """Proveedores LLM disponibles."""

    ZAI = "zai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    XAI = "xai"
    DEEPSEEK = "deepseek"
    OPENAI = "openai"


@dataclass(frozen=True, slots=True)
class LLMConfig:
    """Configuracion inmutable para un cliente LLM."""

    provider: Provider
    model: str
    base_url: str | None = None
    api_key_env: str = ""


def default_config() -> LLMConfig:
    """Configuracion por defecto: Z.ai GLM coding plan via OpenAI SDK."""
    s = get_settings()
    return LLMConfig(
        provider=Provider.ZAI,
        model=s.zai_openai_model,
        base_url=s.zai_openai_base_url,
        api_key_env="ZAI_API_KEY",
    )


def available_providers() -> list[Provider]:
    """Proveedores que tienen API key configurada."""
    s = get_settings()
    result: list[Provider] = []
    if s.zai_api_key:
        result.append(Provider.ZAI)
    if s.anthropic_api_key:
        result.append(Provider.ANTHROPIC)
    if s.gemini_api_key:
        result.append(Provider.GEMINI)
    if s.xai_api_key:
        result.append(Provider.XAI)
    if s.deepseek_api_key:
        result.append(Provider.DEEPSEEK)
    if s.openai_api_key:
        result.append(Provider.OPENAI)
    return result


def build_openai_client(model: str | None = None) -> tuple[OpenAI, str]:
    """Construye cliente OpenAI apuntando a Z.ai coding plan.

    Returns:
        (cliente, modelo). Modelo por defecto: GLM-4.6.
    """
    from openai import OpenAI

    s = get_settings()
    if s.zai_api_key is None:
        raise RuntimeError("ZAI_API_KEY no configurada. Imposible instanciar cliente por defecto.")
    client = OpenAI(
        api_key=s.zai_api_key.get_secret_value(),
        base_url=s.zai_openai_base_url,
    )
    return client, model or s.zai_openai_model


def assert_distinct_consensus(a: LLMConfig, b: LLMConfig) -> None:
    """Verifica en runtime que dos configs son realmente distintas.

    Raises:
        AssertionError: si provider o model coinciden.
    """
    assert a.provider != b.provider, (
        f"Consenso invalido: mismo provider en A y B ({a.provider.value})"
    )
    assert a.model != b.model, f"Consenso invalido: mismo modelo en A y B ({a.model})"


def pick_consensus_pair() -> tuple[LLMConfig, LLMConfig] | None:
    """Elige 2 proveedores distintos para consenso.

    Prioridad: (Z.ai, Anthropic) > (Z.ai, Gemini) > (Z.ai, XAI) >
    (Anthropic, Gemini) > ... hasta agotar combinaciones.

    Returns:
        None si no hay 2 proveedores disponibles.
    """
    s = get_settings()
    available = available_providers()
    if len(available) < 2:
        return None

    priority = [
        (Provider.ZAI, Provider.ANTHROPIC),
        (Provider.ZAI, Provider.GEMINI),
        (Provider.ZAI, Provider.XAI),
        (Provider.ZAI, Provider.DEEPSEEK),
        (Provider.ANTHROPIC, Provider.GEMINI),
        (Provider.ANTHROPIC, Provider.XAI),
        (Provider.GEMINI, Provider.XAI),
    ]

    models: dict[Provider, tuple[str, str]] = {
        Provider.ZAI: (s.zai_openai_model, "ZAI_API_KEY"),
        Provider.ANTHROPIC: (s.anthropic_model, "ANTHROPIC_API_KEY"),
        Provider.GEMINI: (s.gemini_model, "GEMINI_API_KEY"),
        Provider.XAI: (s.xai_model, "XAI_API_KEY"),
        Provider.DEEPSEEK: (s.deepseek_model, "DEEPSEEK_API_KEY"),
        Provider.OPENAI: (s.openai_model, "OPENAI_API_KEY"),
    }

    for p_a, p_b in priority:
        if p_a in available and p_b in available:
            model_a, env_a = models[p_a]
            model_b, env_b = models[p_b]
            cfg_a = LLMConfig(provider=p_a, model=model_a, api_key_env=env_a)
            cfg_b = LLMConfig(provider=p_b, model=model_b, api_key_env=env_b)
            assert_distinct_consensus(cfg_a, cfg_b)
            return cfg_a, cfg_b
    return None


__all__ = [
    "LLMConfig",
    "Provider",
    "assert_distinct_consensus",
    "available_providers",
    "build_openai_client",
    "default_config",
    "pick_consensus_pair",
]
