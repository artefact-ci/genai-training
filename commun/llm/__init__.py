"""Shared model access for the training labs.

Import from here rather than from a provider SDK:

    from commun.llm import ask, chat, complete, embed

The provider is configured in `.env` and resolved in `commun/llm/config.py`.
"""

from .client import (
    Completion,
    ask,
    chat,
    complete,
    embed,
    get_client,
    get_langchain_chat_model,
    get_langchain_embeddings,
)
from .config import ConfigurationError, Settings, get_settings

__all__ = [
    "Completion",
    "ConfigurationError",
    "Settings",
    "ask",
    "chat",
    "complete",
    "embed",
    "get_client",
    "get_langchain_chat_model",
    "get_langchain_embeddings",
    "get_settings",
]
