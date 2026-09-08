"""Tests for the shared configuration layer.

These run without any credentials and without reaching the network: they are the
smoke test that tells us the labs' entry point still holds together.
"""

from __future__ import annotations

import pytest

from commun.llm import ConfigurationError, get_settings
from commun.llm.config import DEFAULT_PROVIDER, SUPPORTED_PROVIDERS

AZURE_VARS = {
    "AZURE_OPENAI_API_KEY": "test-key",
    "AZURE_OPENAI_ENDPOINT": "https://example.openai.azure.com/",
    "AZURE_OPENAI_CHAT_DEPLOYMENT": "chat-deployment",
}


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """get_settings() is cached, so each test needs a clean slate."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def azure_env(monkeypatch):
    for name in (
        "LLM_PROVIDER",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT",
    ):
        monkeypatch.delenv(name, raising=False)
    for name, value in AZURE_VARS.items():
        monkeypatch.setenv(name, value)


def test_default_provider_is_supported():
    assert DEFAULT_PROVIDER in SUPPORTED_PROVIDERS


def test_reads_azure_settings(azure_env):
    settings = get_settings()
    assert settings.provider == "azure_openai"
    assert settings.chat_deployment == "chat-deployment"
    assert settings.api_version  # a default is always applied


def test_embeddings_are_optional(azure_env, monkeypatch):
    assert get_settings().has_embeddings is False

    get_settings.cache_clear()
    monkeypatch.setenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "embed-deployment")
    assert get_settings().has_embeddings is True


def test_missing_variable_names_itself(azure_env, monkeypatch):
    monkeypatch.delenv("AZURE_OPENAI_API_KEY")
    with pytest.raises(ConfigurationError, match="AZURE_OPENAI_API_KEY"):
        get_settings()


def test_unknown_provider_is_rejected(azure_env, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "some_other_provider")
    with pytest.raises(ConfigurationError, match="some_other_provider"):
        get_settings()
