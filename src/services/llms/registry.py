from typing import Dict

from .providers import OllamaProvider, AbstractProvider, ProviderEnum


class ProviderRegistry:
    def __init__(self):
        self.providers: Dict[str, AbstractProvider] = {}

    def register_provider(self, provider_name, provider: AbstractProvider):
        self.providers[provider_name] = provider

    def create(self, provider_name, *args, **kwargs) -> AbstractProvider:
        if provider_name not in self.providers:
            raise ValueError(f"Provider {provider_name} is not registered")

        return self.providers[provider_name](*args, **kwargs)


provider_registry = ProviderRegistry()
provider_registry.register_provider(OllamaProvider.provider_name(), OllamaProvider)


def get_provider(provider_name: ProviderEnum):
    return provider_registry.create(provider_name)
