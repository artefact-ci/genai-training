"""Single entry point to the model for every lab in the training.

Labs must not import a provider SDK directly. Going through this module keeps a
provider change to a `.env` edit, and gives every chapter the same helpers for
token accounting and cost reporting.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Iterable, Sequence

from openai import AzureOpenAI

from .config import ConfigurationError, Settings, get_settings

Message = dict[str, str]


@dataclass(frozen=True)
class Completion:
    """A model answer, with what it cost to obtain it."""

    text: str
    prompt_tokens: int
    completion_tokens: int
    model: str

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@lru_cache(maxsize=1)
def get_client() -> AzureOpenAI:
    """The underlying SDK client, cached for the lifetime of the process.

    Chapters that deliberately show provider-specific behaviour may use this;
    everything else should prefer `chat()` and `embed()`.
    """
    settings: Settings = get_settings()
    return AzureOpenAI(
        api_key=settings.api_key,
        azure_endpoint=settings.endpoint,
        api_version=settings.api_version,
    )


def complete(
    messages: Sequence[Message],
    *,
    temperature: float = 0.0,
    max_tokens: int | None = None,
    **kwargs: Any,
) -> Completion:
    """Send a conversation to the model and return the answer with its token usage."""
    settings = get_settings()
    response = get_client().chat.completions.create(
        model=settings.chat_deployment,
        messages=list(messages),
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs,
    )
    usage = response.usage
    return Completion(
        text=response.choices[0].message.content or "",
        prompt_tokens=usage.prompt_tokens if usage else 0,
        completion_tokens=usage.completion_tokens if usage else 0,
        model=response.model,
    )


def chat(
    messages: Sequence[Message],
    *,
    temperature: float = 0.0,
    max_tokens: int | None = None,
    **kwargs: Any,
) -> str:
    """Send a conversation to the model and return the answer text.

    The shortest path, and the one used in most labs:

        from commun.llm import chat

        chat([{"role": "user", "content": "Bonjour"}])
    """
    return complete(
        messages, temperature=temperature, max_tokens=max_tokens, **kwargs
    ).text


def ask(prompt: str, *, system: str | None = None, **kwargs: Any) -> str:
    """Single-turn convenience wrapper around `chat()`."""
    messages: list[Message] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return chat(messages, **kwargs)


def embed(texts: Iterable[str]) -> list[list[float]]:
    """Embed a batch of texts. Used from chapter 3 onwards."""
    settings = get_settings()
    if not settings.has_embeddings:
        raise ConfigurationError(
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT is not set, and this lab needs embeddings."
        )
    response = get_client().embeddings.create(
        model=settings.embedding_deployment,
        input=list(texts),
    )
    return [item.embedding for item in response.data]


def get_langchain_chat_model(**kwargs: Any):
    """A LangChain chat model backed by the same configuration.

    Chapters 3 and 4 build on LangChain and LangGraph; they get their model from
    here so that the provider stays configured in one place. Imported lazily:
    LangChain is not needed before chapter 3.
    """
    from langchain_openai import AzureChatOpenAI

    settings = get_settings()
    return AzureChatOpenAI(
        api_key=settings.api_key,
        azure_endpoint=settings.endpoint,
        api_version=settings.api_version,
        azure_deployment=settings.chat_deployment,
        temperature=kwargs.pop("temperature", 0.0),
        **kwargs,
    )


def get_langchain_embeddings(**kwargs: Any):
    """LangChain embeddings backed by the same configuration."""
    from langchain_openai import AzureOpenAIEmbeddings

    settings = get_settings()
    if not settings.has_embeddings:
        raise ConfigurationError(
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT is not set, and this lab needs embeddings."
        )
    return AzureOpenAIEmbeddings(
        api_key=settings.api_key,
        azure_endpoint=settings.endpoint,
        api_version=settings.api_version,
        azure_deployment=settings.embedding_deployment,
        **kwargs,
    )
