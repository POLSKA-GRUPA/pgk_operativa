"""Configuracion central via Pydantic Settings.

Fuente: variables de entorno y archivo `.env` en la raiz del repo.
El archivo `.env` NO entra en Git. Plantilla: `.env.example`.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from pgk_operativa.core.paths import REPO_ROOT


class Settings(BaseSettings):
    """Configuracion global. Se carga una sola vez."""

    model_config = SettingsConfigDict(
        env_file=str(REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ===== Runtime =====
    environment: str = Field(default="development", alias="PGK_ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="PGK_LOG_LEVEL")
    consenso_default: bool = Field(default=False, alias="PGK_CONSENSO_DEFAULT")

    # ===== Rutas de usuario =====
    user_home: Path | None = Field(default=None, alias="PGK_USER_HOME")
    local_documents_path: Path | None = Field(default=None, alias="PGK_LOCAL_DOCUMENTS_PATH")
    google_credentials_path: Path | None = Field(default=None, alias="PGK_GOOGLE_CREDENTIALS_PATH")

    # ===== Postgres remoto =====
    db_host: str = Field(default="127.0.0.1", alias="PGK_DB_HOST")
    db_port: int = Field(default=5432, alias="PGK_DB_PORT")
    db_name: str = Field(default="pgk_database", alias="PGK_DB_NAME")
    db_schema: str = Field(default="pgk_admin", alias="PGK_DB_SCHEMA")
    db_user: str = Field(default="dev_devin", alias="PGK_DB_USER")
    db_password: SecretStr | None = Field(default=None, alias="PGK_DB_PASSWORD")
    ssh_host: str = Field(default="209.74.72.83", alias="PGK_SSH_HOST")
    ssh_port: int = Field(default=22, alias="PGK_SSH_PORT")
    ssh_user: str | None = Field(default=None, alias="PGK_SSH_USER")
    ssh_key_path: Path | None = Field(default=None, alias="PGK_SSH_KEY_PATH")

    # ===== Z.AI (default) =====
    zai_api_key: SecretStr | None = Field(default=None, alias="ZAI_API_KEY")
    zai_openai_base_url: str = Field(
        default="https://api.z.ai/api/coding/paas/v4", alias="ZAI_OPENAI_BASE_URL"
    )
    zai_openai_model: str = Field(default="glm-4.6", alias="ZAI_OPENAI_MODEL")
    zai_anthropic_base_url: str = Field(
        default="https://api.z.ai/api/anthropic", alias="ZAI_ANTHROPIC_BASE_URL"
    )

    # ===== Proveedores consenso opt-in =====
    anthropic_api_key: SecretStr | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-sonnet-4-5-20250929", alias="ANTHROPIC_MODEL")

    gemini_api_key: SecretStr | None = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-pro", alias="GEMINI_MODEL")

    xai_api_key: SecretStr | None = Field(default=None, alias="XAI_API_KEY")
    xai_model: str = Field(default="grok-3", alias="XAI_MODEL")

    deepseek_api_key: SecretStr | None = Field(default=None, alias="DEEPSEEK_API_KEY")
    deepseek_model: str = Field(default="deepseek-chat", alias="DEEPSEEK_MODEL")

    openai_api_key: SecretStr | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", alias="OPENAI_MODEL")

    # ===== Verificacion normativa =====
    perplexity_api_key: SecretStr | None = Field(default=None, alias="PERPLEXITY_API_KEY")
    perplexity_model: str = Field(default="sonar-pro", alias="PERPLEXITY_MODEL")

    # ===== Embeddings =====
    openai_embedding_key: SecretStr | None = Field(default=None, alias="OPENAI_EMBEDDING_KEY")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")

    def has_zai(self) -> bool:
        """True si Z.ai (default) esta configurado."""
        return self.zai_api_key is not None

    def has_consenso_ready(self) -> bool:
        """True si al menos 2 proveedores distintos estan listos."""
        keys = [
            self.zai_api_key,
            self.anthropic_api_key,
            self.gemini_api_key,
            self.xai_api_key,
            self.deepseek_api_key,
            self.openai_api_key,
        ]
        return sum(1 for k in keys if k is not None) >= 2


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Singleton de configuracion."""
    return Settings()


__all__ = ["Settings", "get_settings"]
