from abc import ABC, abstractmethod
import os
from typing import TypeVar

from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from .enum import ProviderEnum

__all__ = ["OllamaProvider"]

T = TypeVar("T")


class AbstractProvider(ABC):
    @abstractmethod
    def stream_chat_response(self, message: str) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def llm(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def embedding(self):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def provider_name(cls):
        raise NotImplementedError


class OllamaProvider(AbstractProvider):
    __provider_name__ = ProviderEnum.OLLAMA

    def __init__(
        self, host: str = os.environ.get("OLLAMA_HOST", "http://ollama_qa:11434")
    ):
        self._host = host
        self._embedding_model_name = os.environ.get(
            "OLLAMA_EMBEDDING_MODEL",
            "nomic-embed-text:137m-v1.5-fp16",
        )
        self._chat_model_name = os.environ.get(
            "OLLAMA_CHAT_MODEL",
            "llama3.2:1b",
        )
        self._llm = Ollama(
            model=self._chat_model_name,
            request_timeout=3600,
            base_url=self._host,
        )
        self._embedding = OllamaEmbedding(
            model_name=self._embedding_model_name,
            base_url=self._host,
        )

    def stream_chat_response(self, message: str):
        generator = self.llm.stream_complete(message)
        for chunk in generator:
            yield chunk.delta

    @property
    def llm(self):
        return self._llm

    @property
    def embedding(self):
        return self._embedding

    @classmethod
    def provider_name(cls) -> str:
        """Get the provider name"""
        if not hasattr(cls, "__provider_name__"):
            raise AttributeError("Provider name is not set")
        return cls.__provider_name__
