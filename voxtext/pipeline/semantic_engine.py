"""
Estágio de Reestruturação Semântica.

Transforma estruturas visuais (listas, tabelas textuais, blocos longos)
em formas narrativas adequadas para leitura por voz.
"""

from __future__ import annotations

import re

from voxtext.pipeline.base import PipelineStage
from voxtext.models.document import Document


class SemanticEngineStage(PipelineStage):
    """Estágio 3: Reorganização semântica do texto para fala."""

    def process(self, document: Document) -> Document:
        text = document.cleaned_text or document.raw_text
        if not text.strip():
            return document

        blocks = re.split(r"\n\s*\n", text)
        processed_blocks: list[str] = []
        lists_converted = 0

        for block in blocks:
            block = block.strip()
            if not block:
                continue
            if self._is_list(block):
                processed_blocks.append(self._convert_list_to_narrative(block))
                lists_converted += 1
            else:
                processed_blocks.append(block)

        document.cleaned_text = "\n\n".join(processed_blocks)
        document.metadata["lists_converted"] = lists_converted
        self.logger.info("Reestruturação: %d listas convertidas", lists_converted)
        return document

    def _is_list(self, block: str) -> bool:
        lines = [ln for ln in block.strip().split("\n") if ln.strip()]
        if len(lines) < 2:
            return False
        patterns = [
            r"^\s*[-•●○▪▸►]\s+",
            r"^\s*\d+[.)]\s+",
            r"^\s*[a-z][.)]\s+",
        ]
        matching = sum(
            1 for ln in lines
            if any(re.match(p, ln.strip()) for p in patterns)
        )
        return matching / len(lines) >= 0.6

    def _convert_list_to_narrative(self, block: str) -> str:
        lines = block.strip().split("\n")
        header = ""
        items: list[str] = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            cleaned = re.sub(r"^\s*[-•●○▪▸►]\s+", "", stripped)
            cleaned = re.sub(r"^\s*\d+[.)]\s+", "", cleaned)
            cleaned = re.sub(r"^\s*[a-z][.)]\s+", "", cleaned)

            if cleaned == stripped and not items:
                header = cleaned.rstrip(":")
                continue
            if cleaned:
                items.append(cleaned.rstrip(".;,"))

        if not items:
            return block

        if len(items) == 1:
            narrative = items[0] + "."
        elif len(items) == 2:
            narrative = f"{items[0]} e {items[1]}."
        else:
            narrative = ", ".join(items[:-1]) + f" e {items[-1]}."

        return f"{header}: {narrative}" if header else narrative
