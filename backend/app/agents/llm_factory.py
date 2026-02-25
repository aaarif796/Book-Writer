import os
from abc import ABC, abstractmethod
from typing import Dict, Any
from openai import AsyncOpenAI
import ollama


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass


# -------------------------
# OpenAI Provider
# -------------------------
class OpenAIProvider(LLMProvider):
    """OpenAI and OpenAI-compatible provider."""

    def __init__(self, model_config: Dict[str, Any]):
        self.model_name = model_config.get("model_name", "gpt-4o-mini")
        self.max_tokens = model_config.get("max_tokens", 2000)
        self.temperature = model_config.get("temperature", 0.7)

        base_url = model_config.get("base_url")
        api_key = (
            os.getenv("OPENAI_API_KEY")
            or os.getenv("OLLAMA_API_KEY")
            or "dummy"
        )

        if base_url:
            self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = AsyncOpenAI(api_key=api_key)

    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                **kwargs
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            raise RuntimeError(f"OpenAI generation failed: {e}")


# -------------------------
# Ollama Provider (SYNC wrapped in ASYNC)
# -------------------------
class OllamaProvider(LLMProvider):
    """Local Ollama LLM provider."""

    def __init__(self, model_config: Dict[str, Any]):
        self.model_name = model_config.get("model_name", "llama3.1")
        self.max_tokens = model_config.get("max_tokens", 2000)
        self.temperature = model_config.get("temperature", 0.7)

    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Wrap synchronous ollama.chat inside async function.
        """
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                }
            )

            return response["message"]["content"].strip()

        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {e}")


# -------------------------
# Factory
# -------------------------
class LLMFactory:
    """Factory for creating LLM providers."""

    @staticmethod
    def create(provider_name: str, model_config: Dict[str, Any]) -> LLMProvider:
        if provider_name == "openai":
            return OpenAIProvider(model_config)

        if provider_name == "ollama":
            return OllamaProvider(model_config)

        raise ValueError(f"Unsupported provider: {provider_name}")