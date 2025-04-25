from abc import ABC, abstractmethod
import os
from enum import Enum
from typing import TypeVar

from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding


__all__ = ["OllamaProvider", "ProviderEnum"]

T = TypeVar("T")


class ProviderEnum(Enum):
    OLLAMA = "Ollama"


class AbstractProvider(ABC):
    @abstractmethod
    def stream_chat_response(self, message: str) -> str:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def provider_name(cls):
        raise NotImplementedError


class OllamaProvider(AbstractProvider):
    __provider_name__ = ProviderEnum.OLLAMA

    def __init__(self):
        self._host = os.environ.get("OLLAMA_HOST", "http://ollama_qa:11434")
        self._embedding_model_name = os.environ.get("OLLAMA_EMBEDDING_MODEL","nomic-embed-text:137m-v1.5-fp16")
        
        self._chat_model_name =os.environ.get("OLLAMA_CHAT_MODEL",  "llama3.2:1b")

    def stream_chat_response(self, message: str):
        llm = self._get_chat_model()
        generator = llm.stream_complete(message)
        for chunk in generator:
            yield chunk.delta

    def _get_chat_model(self) -> Ollama:
        return Ollama(
            model=self._chat_model_name, request_timeout=3600, base_url=self._host
        )

    def _get_embedding_model(self) -> OllamaEmbedding:
        return OllamaEmbedding(
            model_name=self._embedding_model_name, base_url=self._host
        )

    @classmethod
    def provider_name(cls) -> str:
        """Get the provider name"""
        if not hasattr(cls, "__provider_name__"):
            raise AttributeError("Provider name is not set")
        return cls.__provider_name__
