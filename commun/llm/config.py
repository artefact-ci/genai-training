"""Runtime configuration for the training labs.

Every lab reads its model settings from environment variables, so that switching
provider stays a configuration change rather than a rewrite of the exercises.
Values are loaded from a `.env` file at the repository root; see
`commun/setup/README.md`.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(REPO_ROOT / ".env")

SUPPORTED_PROVIDERS = ("azure_openai",)
DEFAULT_PROVIDER = "azure_openai"


class ConfigurationError(RuntimeError):
    """Raised when the environment is missing something a lab needs."""


@dataclass(frozen=True)
class Settings:
    """Everything the labs need to reach a model."""

    provider: str
    api_key: str
    endpoint: str
    api_version: str
    chat_deployment: str
    embedding_deployment: str

    @property
    def has_embeddings(self) -> bool:
        return bool(self.embedding_deployment)


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigurationError(
            f"Missing environment variable {name}. "
            "Copy commun/setup/.env.example to .env at the repository root and fill it in."
        )
    return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Read and validate the environment once per process."""
    provider = os.getenv("LLM_PROVIDER", DEFAULT_PROVIDER).strip()
    if provider not in SUPPORTED_PROVIDERS:
        supported = ", ".join(SUPPORTED_PROVIDERS)
        raise ConfigurationError(
            f"Unsupported LLM_PROVIDER {provider!r}. Supported providers: {supported}. "
            "Adding one means implementing it in commun/llm/client.py, not in the labs."
        )

    return Settings(
        provider=provider,
        api_key=_required("AZURE_OPENAI_API_KEY"),
        endpoint=_required("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21").strip(),
        chat_deployment=_required("AZURE_OPENAI_CHAT_DEPLOYMENT"),
        embedding_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "").strip(),
    )
