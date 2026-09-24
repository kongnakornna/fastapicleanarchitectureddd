"""embeddings services — clients · registry · event bus"""
from __future__ import annotations
import logging
from typing import Any, Optional

from app.modules.embeddings.application.interfaces import (
    EmbeddingClient, EmbeddingRegistry, EventBus,
)
from app.modules.embeddings.domain.helpers.normalizer import (
    normalize_vector,
)

logger = logging.getLogger(__name__)


class OpenAIEmbeddingClient(EmbeddingClient):
    provider_type = "openai"

    def __init__(
        self, api_key: str = "", base_url: str = "", timeout: int = 60,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout

    async def embed(
        self, texts: list[str], model: str,
        *, normalize: bool = True,
        dimensions: Optional[int] = None,
    ) -> list[list[float]]:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(
            api_key=self._api_key or "sk-placeholder",
            base_url=self._base_url or None,
            timeout=self._timeout,
        )
        kwargs: dict[str, Any] = {"model": model, "input": texts}
        if dimensions is not None:
            kwargs["dimensions"] = dimensions
        resp = await client.embeddings.create(**kwargs)
        vectors = [list(item.embedding) for item in resp.data]
        if normalize:
            vectors = [normalize_vector(v) for v in vectors]
        return vectors


class CohereEmbeddingClient(EmbeddingClient):
    provider_type = "cohere"

    def __init__(
        self, api_key: str = "", base_url: str = "", timeout: int = 60,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout

    async def embed(
        self, texts: list[str], model: str,
        *, normalize: bool = True,
        dimensions: Optional[int] = None,
    ) -> list[list[float]]:
        import cohere
        client = cohere.AsyncClient(
            api_key=self._api_key or "placeholder",
        )
        resp = await client.embed(
            texts=texts, model=model,
            input_type="search_document",
        )
        vectors = [list(v) for v in resp.embeddings]
        if normalize:
            vectors = [normalize_vector(v) for v in vectors]
        return vectors


class LocalEmbeddingClient(EmbeddingClient):
    provider_type = "huggingface"

    def __init__(
        self, api_key: str = "", base_url: str = "", timeout: int = 60,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout
        self._model_cache: dict[str, Any] = {}

    @staticmethod
    def _model_name(name: str) -> str:
        return name if "/" in name else f"sentence-transformers/{name}"

    def _get_model(self, name: str) -> Any:
        if name not in self._model_cache:
            from sentence_transformers import SentenceTransformer
            self._model_cache[name] = SentenceTransformer(name)
        return self._model_cache[name]

    async def embed(
        self, texts: list[str], model: str,
        *, normalize: bool = True,
        dimensions: Optional[int] = None,
    ) -> list[list[float]]:
        import asyncio
        st_model = self._get_model(self._model_name(model))

        def _run() -> list[list[float]]:
            embs = st_model.encode(
                texts, normalize_embeddings=normalize,
                convert_to_numpy=True,
            )
            return [list(map(float, row)) for row in embs]

        vectors = await asyncio.to_thread(_run)
        if dimensions and vectors and len(vectors[0]) > dimensions:
            vectors = [v[:dimensions] for v in vectors]
        return vectors


class DefaultEmbeddingRegistry(EmbeddingRegistry):
    _CLIENTS = {
        "openai": OpenAIEmbeddingClient,
        "cohere": CohereEmbeddingClient,
        "voyage": OpenAIEmbeddingClient,
        "huggingface": LocalEmbeddingClient,
        "bge": LocalEmbeddingClient,
        "local": LocalEmbeddingClient,
    }

    def get_client(self, provider: Any) -> EmbeddingClient:
        cls = self._CLIENTS.get(
            str(provider.provider_type), OpenAIEmbeddingClient,
        )
        return cls(
            api_key=provider.api_key_encrypted or "",
            base_url=provider.base_url,
            timeout=provider.timeout_seconds,
        )


class LoggingEventBus(EventBus):
    async def publish(self, event: object) -> None:
        try:
            logger.info("event %s", type(event).__name__)
        except Exception:
            pass
