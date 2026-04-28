"""
Corretor de Texto por IA.

Orquestra a divisão do texto em chunks, envio ao provider LLM
e recombinação do resultado corrigido.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

from voxtext.ai.providers import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)

# Prompt de sistema otimizado para correção TTS em PT-BR
SYSTEM_PROMPT = """Você é um revisor especializado em textos para síntese de fala (TTS) em português brasileiro.

Sua tarefa é revisar e corrigir o texto fornecido seguindo estas regras:

1. CORRIJA erros gramaticais, ortográficos e de concordância.
2. MELHORE a fluidez para leitura em voz alta — o texto será falado, não lido.
3. NORMALIZE a pontuação para pausas naturais na fala.
4. SUBSTITUA construções confusas por alternativas mais claras.
5. MANTENHA o significado original — NÃO adicione informações novas.
6. PRESERVE a estrutura de parágrafos e quebras de linha.
7. NÃO adicione explicações, comentários ou notas — retorne APENAS o texto corrigido.
8. Se o texto já estiver correto, retorne-o sem alterações.

Retorne SOMENTE o texto corrigido, sem qualquer marcação adicional."""


@dataclass
class CorrectionResult:
    """Resultado da correção por IA."""
    original_text: str
    corrected_text: str
    chunks_processed: int
    total_tokens: int
    provider: str
    model: str
    success: bool = True
    error: str = ""


class AICorrector:
    """
    Corretor de texto usando LLMs.

    Divide o texto em chunks para respeitar limites de contexto,
    envia cada chunk ao provider e recombina o resultado.
    """

    def __init__(
        self,
        provider: LLMProvider,
        max_chunk_size: int = 3000,
        system_prompt: str = "",
    ) -> None:
        self.provider = provider
        self.max_chunk_size = max_chunk_size
        self.system_prompt = system_prompt or SYSTEM_PROMPT

    def correct(
        self,
        text: str,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> CorrectionResult:
        """
        Corrige o texto usando o provider de IA.

        Args:
            text: Texto a ser corrigido.
            on_progress: Callback (chunk_atual, total_chunks).

        Returns:
            CorrectionResult com o texto corrigido.
        """
        if not text.strip():
            return CorrectionResult(
                original_text=text,
                corrected_text=text,
                chunks_processed=0,
                total_tokens=0,
                provider="",
                model="",
            )

        # Dividir em chunks
        chunks = self._split_into_chunks(text)
        total = len(chunks)
        corrected_chunks: list[str] = []
        total_tokens = 0
        last_response: LLMResponse | None = None

        logger.info("Correção IA: %d chunk(s) para processar", total)

        for i, chunk in enumerate(chunks):
            if on_progress:
                on_progress(i, total)

            prompt = f"Corrija o seguinte texto:\n\n{chunk}"
            response = self.provider.generate(prompt, self.system_prompt)
            last_response = response

            if not response.success:
                return CorrectionResult(
                    original_text=text,
                    corrected_text=text,
                    chunks_processed=i,
                    total_tokens=total_tokens,
                    provider=response.provider,
                    model=response.model,
                    success=False,
                    error=response.error,
                )

            corrected_chunks.append(response.text)
            total_tokens += response.tokens_used

            logger.info("Chunk %d/%d corrigido (%d tokens)", i + 1, total, response.tokens_used)

        if on_progress:
            on_progress(total, total)

        # Recombinar
        corrected_text = "\n\n".join(corrected_chunks)

        return CorrectionResult(
            original_text=text,
            corrected_text=corrected_text,
            chunks_processed=total,
            total_tokens=total_tokens,
            provider=last_response.provider if last_response else "",
            model=last_response.model if last_response else "",
        )

    def _split_into_chunks(self, text: str) -> list[str]:
        """
        Divide o texto em chunks respeitando parágrafos.

        Tenta cortar entre parágrafos. Se um parágrafo for maior
        que o limite, corta no último ponto final.
        """
        if len(text) <= self.max_chunk_size:
            return [text]

        paragraphs = text.split("\n\n")
        chunks: list[str] = []
        current_chunk = ""

        for para in paragraphs:
            # Se adicionar este parágrafo ultrapassa o limite
            test = (current_chunk + "\n\n" + para).strip() if current_chunk else para
            if len(test) > self.max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = para
            elif len(para) > self.max_chunk_size:
                # Parágrafo individual muito grande — cortar em sentenças
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                chunks.extend(self._split_large_paragraph(para))
            else:
                current_chunk = test

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def _split_large_paragraph(self, text: str) -> list[str]:
        """Divide um parágrafo grande em pedaços menores no último ponto."""
        parts: list[str] = []
        remaining = text

        while len(remaining) > self.max_chunk_size:
            window = remaining[:self.max_chunk_size]
            # Encontrar último ponto final
            cut = window.rfind(".")
            if cut == -1:
                cut = window.rfind(" ")
            if cut == -1:
                cut = self.max_chunk_size

            parts.append(remaining[:cut + 1].strip())
            remaining = remaining[cut + 1:].strip()

        if remaining:
            parts.append(remaining)

        return parts
