"""
Estágio de Parsing — Leitura e extração de texto de arquivos.

Suporta PDF (com detecção de colunas, remoção de cabeçalhos/rodapés)
e TXT (com detecção automática de encoding).
"""

from __future__ import annotations

import re
from pathlib import Path
from collections import Counter

import chardet

from voxtext.pipeline.base import PipelineStage
from voxtext.models.document import Document
from voxtext.config.settings import Settings


class ParserStage(PipelineStage):
    """Estágio 1: Leitura e extração de texto de arquivos."""

    def process(self, document: Document) -> Document:
        if document.source_path is None:
            self.logger.warning("Nenhum arquivo de origem definido; pulando parser.")
            return document

        path = document.source_path
        ext = path.suffix.lower()

        if ext == ".pdf":
            document = self._parse_pdf(document, path)
        elif ext == ".txt":
            document = self._parse_txt(document, path)
        else:
            raise ValueError(f"Formato não suportado: {ext}")

        self.logger.info(
            "Texto extraído: %d caracteres de '%s'",
            len(document.raw_text), path.name
        )
        return document

    def _parse_pdf(self, document: Document, path: Path) -> Document:
        """Extrai texto de PDF usando pdfplumber com heurísticas avançadas."""
        try:
            import pdfplumber
        except ImportError:
            raise ImportError("pdfplumber é necessário para processar PDFs. "
                              "Instale com: pip install pdfplumber")

        pages_text: list[str] = []
        all_first_lines: list[str] = []
        all_last_lines: list[str] = []

        with pdfplumber.open(str(path)) as pdf:
            document.metadata["page_count"] = len(pdf.pages)

            for page in pdf.pages:
                text = page.extract_text() or ""
                if text.strip():
                    lines = text.split("\n")
                    if lines:
                        all_first_lines.append(lines[0].strip())
                    if len(lines) > 1:
                        all_last_lines.append(lines[-1].strip())
                    pages_text.append(text)

        # Detectar cabeçalhos/rodapés repetidos
        headers_to_remove = set()
        footers_to_remove = set()

        if self.settings.remove_headers_footers and len(pages_text) > 2:
            headers_to_remove = self._detect_repeated_patterns(all_first_lines)
            footers_to_remove = self._detect_repeated_patterns(all_last_lines)

        # Processar cada página
        cleaned_pages: list[str] = []
        for page_text in pages_text:
            lines = page_text.split("\n")

            # Remover cabeçalho
            if lines and lines[0].strip() in headers_to_remove:
                lines = lines[1:]

            # Remover rodapé
            if lines and lines[-1].strip() in footers_to_remove:
                lines = lines[:-1]

            # Remover numeração de páginas isolada
            lines = [ln for ln in lines if not re.match(r"^\s*[-–—]?\s*\d+\s*[-–—]?\s*$", ln)]

            page_clean = "\n".join(lines)
            cleaned_pages.append(page_clean)

        raw_text = "\n\n".join(cleaned_pages)

        # Reconstruir palavras hifenizadas entre linhas
        if self.settings.reconstruct_hyphenated:
            raw_text = self._reconstruct_hyphenated(raw_text)

        document.raw_text = raw_text
        return document

    def _parse_txt(self, document: Document, path: Path) -> Document:
        """Lê arquivo TXT com detecção automática de encoding."""
        raw_bytes = path.read_bytes()

        # Detectar encoding
        detected = chardet.detect(raw_bytes)
        encoding = detected.get("encoding", "utf-8") or "utf-8"
        self.logger.info("Encoding detectado: %s (confiança: %.0f%%)",
                         encoding, (detected.get("confidence", 0) or 0) * 100)

        document.raw_text = raw_bytes.decode(encoding, errors="replace")
        document.metadata["encoding"] = encoding
        return document

    def _detect_repeated_patterns(
        self, lines: list[str], threshold: float = 0.5
    ) -> set[str]:
        """Detecta linhas que se repetem em mais de `threshold` das páginas."""
        if not lines:
            return set()

        counter = Counter(lines)
        total = len(lines)
        repeated = set()

        for text, count in counter.items():
            if text and count / total >= threshold:
                repeated.add(text)

        return repeated

    def _reconstruct_hyphenated(self, text: str) -> str:
        """Reconstrói palavras que foram hifenizadas na quebra de linha."""
        # Padrão: palavra- \n continuação
        return re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)
