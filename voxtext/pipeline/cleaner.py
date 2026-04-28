"""
Estágio de Limpeza Estrutural.

Remove ruído do texto extraído: normaliza espaços, remove artefatos de OCR,
reconstrói parágrafos quebrados e elimina linhas em branco excessivas.
"""

from __future__ import annotations

import re
import unicodedata

from voxtext.pipeline.base import PipelineStage
from voxtext.models.document import Document


class CleanerStage(PipelineStage):
    """Estágio 2: Limpeza e normalização estrutural do texto."""

    def process(self, document: Document) -> Document:
        text = document.raw_text

        if not text.strip():
            self.logger.warning("Texto vazio recebido no Cleaner.")
            document.cleaned_text = ""
            return document

        # Pipeline de limpeza sequencial
        text = self._normalize_unicode(text)
        text = self._remove_control_chars(text)
        text = self._normalize_whitespace(text)
        text = self._remove_ocr_artifacts(text)
        text = self._remove_page_numbers(text)
        text = self._reconstruct_paragraphs(text)
        text = self._collapse_blank_lines(text)
        text = text.strip()

        document.cleaned_text = text
        self.logger.info("Limpeza concluída: %d → %d caracteres",
                         len(document.raw_text), len(text))
        return document

    def _normalize_unicode(self, text: str) -> str:
        """Normaliza para NFC (forma canônica composta)."""
        return unicodedata.normalize("NFC", text)

    def _remove_control_chars(self, text: str) -> str:
        """Remove caracteres de controle exceto newline e tab."""
        return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)

    def _normalize_whitespace(self, text: str) -> str:
        """Normaliza espaços em branco dentro de linhas."""
        lines = text.split("\n")
        cleaned = []
        for line in lines:
            # Converter tabs para espaços
            line = line.replace("\t", " ")
            # Múltiplos espaços → um espaço
            line = re.sub(r" {2,}", " ", line)
            # Remover espaços no início e fim da linha
            line = line.strip()
            cleaned.append(line)
        return "\n".join(cleaned)

    def _remove_ocr_artifacts(self, text: str) -> str:
        """Remove artefatos comuns de OCR."""
        # Sequências de caracteres não-alfabéticos suspeitos (3+ seguidos)
        text = re.sub(r"[^\w\s.,;:!?()\"'\-–—…]{3,}", "", text)
        # Caracteres de substituição Unicode
        text = text.replace("\ufffd", "")
        # Sequências repetidas de pontuação
        text = re.sub(r"([.!?])\1{3,}", r"\1\1\1", text)
        return text

    def _remove_page_numbers(self, text: str) -> str:
        """Remove numeração de páginas em diferentes formatos."""
        lines = text.split("\n")
        cleaned = []
        for line in lines:
            stripped = line.strip()
            # Padrões comuns de numeração de página
            if re.match(r"^[-–—]?\s*\d{1,4}\s*[-–—]?$", stripped):
                continue
            if re.match(r"^(Página|Page|Pág\.?)\s*\d+", stripped, re.IGNORECASE):
                continue
            if re.match(r"^\d+\s*/\s*\d+$", stripped):  # "3 / 15"
                continue
            cleaned.append(line)
        return "\n".join(cleaned)

    def _reconstruct_paragraphs(self, text: str) -> str:
        """
        Reconstrói parágrafos que foram quebrados por formatação de PDF.

        Junta linhas consecutivas que parecem fazer parte do mesmo parágrafo
        (linha não termina com pontuação final e próxima começa com minúscula).
        """
        lines = text.split("\n")
        if not lines:
            return text

        result: list[str] = []
        buffer = ""

        for line in lines:
            stripped = line.strip()

            if not stripped:
                # Linha em branco → finaliza parágrafo
                if buffer:
                    result.append(buffer)
                    buffer = ""
                result.append("")
                continue

            if not buffer:
                buffer = stripped
                continue

            # Verificar se deve juntar com a linha anterior
            prev_ends_with_punctuation = buffer[-1] in ".!?:;\"')"
            current_starts_lowercase = stripped[0].islower()
            prev_ends_with_hyphen = buffer.endswith("-")

            if prev_ends_with_hyphen:
                # Palavra hifenizada
                buffer = buffer[:-1] + stripped
            elif not prev_ends_with_punctuation and (
                current_starts_lowercase or len(stripped) > 30
            ):
                # Continuação do parágrafo
                buffer = buffer + " " + stripped
            else:
                # Nova frase/parágrafo
                result.append(buffer)
                buffer = stripped

        if buffer:
            result.append(buffer)

        return "\n".join(result)

    def _collapse_blank_lines(self, text: str) -> str:
        """Reduz múltiplas linhas em branco para no máximo uma."""
        return re.sub(r"\n{3,}", "\n\n", text)
