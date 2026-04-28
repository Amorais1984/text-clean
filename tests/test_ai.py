"""Testes para o módulo de correção por IA."""

import pytest
from unittest.mock import MagicMock, patch

from voxtext.ai.providers import (
    LLMProvider, LLMResponse, OllamaProvider, GeminiProvider, create_provider,
)
from voxtext.ai.corrector import AICorrector, CorrectionResult, SYSTEM_PROMPT


# ── Mock Provider ──────────────────────────────────────────


class MockProvider(LLMProvider):
    """Provider mock para testes sem chamadas reais."""

    def __init__(self, response_text: str = "Texto corrigido.", success: bool = True):
        self._response_text = response_text
        self._success = success
        self.call_count = 0

    def generate(self, prompt: str, system_prompt: str = "") -> LLMResponse:
        self.call_count += 1
        if not self._success:
            return LLMResponse(
                text="", model="mock", provider="mock",
                success=False, error="Erro simulado",
            )
        return LLMResponse(
            text=self._response_text,
            model="mock",
            provider="mock",
            tokens_used=42,
        )

    def test_connection(self) -> tuple[bool, str]:
        return True, "Mock OK"

    def list_models(self) -> list[str]:
        return ["mock-model"]


# ── Testes do Corrector ────────────────────────────────────


class TestAICorrector:
    """Testes do AICorrector."""

    def test_correct_empty_text(self):
        provider = MockProvider()
        corrector = AICorrector(provider)
        result = corrector.correct("")
        assert result.success
        assert result.chunks_processed == 0
        assert result.corrected_text == ""

    def test_correct_short_text(self):
        provider = MockProvider(response_text="Texto revisado.")
        corrector = AICorrector(provider)
        result = corrector.correct("Texto original.")
        assert result.success
        assert result.corrected_text == "Texto revisado."
        assert result.chunks_processed == 1
        assert provider.call_count == 1

    def test_correct_long_text_multiple_chunks(self):
        """Texto maior que max_chunk_size deve ser dividido."""
        provider = MockProvider(response_text="Chunk corrigido.")
        corrector = AICorrector(provider, max_chunk_size=50)

        # Criar texto com múltiplos parágrafos
        text = "Primeiro parágrafo com conteúdo.\n\nSegundo parágrafo com mais conteúdo.\n\nTerceiro parágrafo final."
        result = corrector.correct(text)

        assert result.success
        assert provider.call_count > 1
        assert result.chunks_processed == provider.call_count

    def test_correct_with_error(self):
        provider = MockProvider(success=False)
        corrector = AICorrector(provider)
        result = corrector.correct("Texto com erro.")
        assert not result.success
        assert "Erro simulado" in result.error

    def test_correct_with_progress_callback(self):
        provider = MockProvider()
        corrector = AICorrector(provider, max_chunk_size=30)
        progress_calls = []

        def on_progress(current, total):
            progress_calls.append((current, total))

        text = "Primeira frase. Segunda frase. Terceira frase."
        corrector.correct(text, on_progress=on_progress)

        # Deve ter chamado o callback pelo menos uma vez
        assert len(progress_calls) > 0

    def test_system_prompt_is_set(self):
        """Verifica que o prompt de sistema padrão existe."""
        assert "português brasileiro" in SYSTEM_PROMPT.lower()
        assert "TTS" in SYSTEM_PROMPT

    def test_chunk_splitting_respects_paragraphs(self):
        provider = MockProvider()
        corrector = AICorrector(provider, max_chunk_size=100)

        text = "Parágrafo um.\n\nParágrafo dois.\n\nParágrafo três."
        chunks = corrector._split_into_chunks(text)

        # Cada chunk deve ser texto válido
        for chunk in chunks:
            assert len(chunk.strip()) > 0

    def test_single_chunk_for_short_text(self):
        provider = MockProvider()
        corrector = AICorrector(provider, max_chunk_size=1000)

        chunks = corrector._split_into_chunks("Texto curto.")
        assert len(chunks) == 1

    def test_tokens_accumulated(self):
        provider = MockProvider()
        corrector = AICorrector(provider, max_chunk_size=30)

        text = "Primeira frase. Segunda frase."
        result = corrector.correct(text)

        assert result.total_tokens > 0


# ── Testes dos Providers ───────────────────────────────────


class TestProviderFactory:
    """Testes da factory de providers."""

    def test_create_ollama(self):
        provider = create_provider("ollama", model="llama3.2")
        assert isinstance(provider, OllamaProvider)
        assert provider.model == "llama3.2"

    def test_create_gemini(self):
        provider = create_provider("gemini", model="gemini-2.5-flash", api_key="test-key")
        assert isinstance(provider, GeminiProvider)
        assert provider.model == "gemini-2.5-flash"

    def test_create_unknown_raises(self):
        with pytest.raises(ValueError, match="Provider desconhecido"):
            create_provider("unknown")

    def test_ollama_default_url(self):
        provider = create_provider("ollama")
        assert isinstance(provider, OllamaProvider)
        assert provider.base_url == "http://localhost:11434"

    def test_gemini_list_models(self):
        provider = GeminiProvider()
        models = provider.list_models()
        assert "gemini-2.5-flash" in models


class TestOllamaProvider:
    """Testes do OllamaProvider (mocked)."""

    @patch("requests.post")
    def test_generate_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "message": {"content": "Resposta do Ollama"},
            "eval_count": 100,
        }
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        provider = OllamaProvider(model="test-model")
        response = provider.generate("Test prompt", "System prompt")

        assert response.success
        assert response.text == "Resposta do Ollama"
        assert response.tokens_used == 100
        assert response.provider == "ollama"

    @patch("requests.post", side_effect=Exception("Connection refused"))
    def test_generate_error(self, mock_post):
        provider = OllamaProvider()
        response = provider.generate("Test")
        assert not response.success
        assert "Erro Ollama" in response.error

    @patch("requests.get")
    def test_list_models(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "models": [{"name": "llama3.2"}, {"name": "mistral"}]
        }
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        provider = OllamaProvider()
        models = provider.list_models()
        assert "llama3.2" in models
        assert "mistral" in models
