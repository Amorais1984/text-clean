"""
Providers de LLM para correção de texto por IA.

Abstração que suporta Ollama (local) e Gemini (cloud),
permitindo troca transparente de backend.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Resposta de um provider LLM."""
    text: str
    model: str
    provider: str
    tokens_used: int = 0
    success: bool = True
    error: str = ""


class LLMProvider(ABC):
    """Interface base para providers de IA."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "") -> LLMResponse:
        """
        Gera uma resposta a partir de um prompt.

        Args:
            prompt: Texto de entrada do usuário.
            system_prompt: Instrução de sistema para o modelo.

        Returns:
            LLMResponse com o texto gerado.
        """
        ...

    @abstractmethod
    def test_connection(self) -> tuple[bool, str]:
        """
        Testa a conexão com o provider.

        Returns:
            Tupla (sucesso, mensagem).
        """
        ...

    @abstractmethod
    def list_models(self) -> list[str]:
        """Retorna lista de modelos disponíveis."""
        ...


class OllamaProvider(LLMProvider):
    """
    Provider local via Ollama REST API.

    Usa requests para se comunicar com o servidor Ollama em
    http://localhost:11434. Não requer dependências extras.
    """

    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434") -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str, system_prompt: str = "") -> LLMResponse:
        import requests

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            resp = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                },
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()

            content = data.get("message", {}).get("content", "")
            tokens = data.get("eval_count", 0)

            return LLMResponse(
                text=content,
                model=self.model,
                provider="ollama",
                tokens_used=tokens,
            )

        except requests.ConnectionError:
            return LLMResponse(
                text="", model=self.model, provider="ollama",
                success=False,
                error="Não foi possível conectar ao Ollama. Verifique se está rodando em "
                      f"{self.base_url}",
            )
        except requests.Timeout:
            return LLMResponse(
                text="", model=self.model, provider="ollama",
                success=False, error="Timeout: o Ollama demorou muito para responder.",
            )
        except Exception as e:
            return LLMResponse(
                text="", model=self.model, provider="ollama",
                success=False, error=f"Erro Ollama: {e}",
            )

    def test_connection(self) -> tuple[bool, str]:
        import requests
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
            if not models:
                return False, "Ollama conectado, mas nenhum modelo instalado."
            return True, f"Ollama OK — {len(models)} modelo(s): {', '.join(models[:5])}"
        except requests.ConnectionError:
            return False, f"Não foi possível conectar ao Ollama em {self.base_url}"
        except Exception as e:
            return False, f"Erro: {e}"

    def list_models(self) -> list[str]:
        import requests
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            resp.raise_for_status()
            return [m["name"] for m in resp.json().get("models", [])]
        except Exception:
            return []


class GeminiProvider(LLMProvider):
    """
    Provider cloud via Google Gemini API.

    Usa o SDK google-genai. Requer API key do Google AI Studio.
    """

    def __init__(self, model: str = "gemini-2.5-flash", api_key: str = "") -> None:
        self.model = model
        self.api_key = api_key
        self._client = None

    def _get_client(self):
        """Lazy init do client Gemini."""
        if self._client is None:
            try:
                from google import genai
            except ImportError:
                raise RuntimeError(
                    "SDK do Gemini não instalado. Execute:\n"
                    "pip install google-genai"
                )

            import os
            key = self.api_key or os.environ.get("GEMINI_API_KEY", "")
            if not key:
                raise RuntimeError(
                    "API key do Gemini não configurada.\n"
                    "Defina GEMINI_API_KEY como variável de ambiente ou "
                    "insira a chave no campo da interface."
                )

            self._client = genai.Client(api_key=key)
        return self._client

    def generate(self, prompt: str, system_prompt: str = "") -> LLMResponse:
        try:
            client = self._get_client()

            contents = prompt
            if system_prompt:
                contents = f"{system_prompt}\n\n---\n\n{contents}"

            response = client.models.generate_content(
                model=self.model,
                contents=contents,
            )

            text = response.text or ""
            tokens = 0
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                tokens = getattr(response.usage_metadata, "total_token_count", 0)

            return LLMResponse(
                text=text,
                model=self.model,
                provider="gemini",
                tokens_used=tokens,
            )

        except RuntimeError as e:
            return LLMResponse(
                text="", model=self.model, provider="gemini",
                success=False, error=str(e),
            )
        except Exception as e:
            return LLMResponse(
                text="", model=self.model, provider="gemini",
                success=False, error=f"Erro Gemini: {e}",
            )

    def test_connection(self) -> tuple[bool, str]:
        try:
            client = self._get_client()
            response = client.models.generate_content(
                model=self.model,
                contents="Responda apenas: OK",
            )
            if response.text:
                return True, f"Gemini OK — modelo: {self.model}"
            return False, "Gemini conectado mas sem resposta."
        except Exception as e:
            return False, str(e)

    def list_models(self) -> list[str]:
        return [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-2.0-flash",
        ]


def create_provider(
    provider_name: str,
    model: str = "",
    api_key: str = "",
    base_url: str = "http://localhost:11434",
) -> LLMProvider:
    """
    Factory para criar o provider correto.

    Args:
        provider_name: 'ollama' ou 'gemini'.
        model: Nome do modelo.
        api_key: API key (para Gemini).
        base_url: URL base (para Ollama).

    Returns:
        Instância do provider configurado.
    """
    if provider_name == "ollama":
        return OllamaProvider(
            model=model or "llama3.2",
            base_url=base_url,
        )
    elif provider_name == "gemini":
        return GeminiProvider(
            model=model or "gemini-2.5-flash",
            api_key=api_key,
        )
    else:
        raise ValueError(f"Provider desconhecido: {provider_name}. Use 'ollama' ou 'gemini'.")
