"""
Estágio de Otimização para TTS.

Insere marcações SSML (pausas, ênfase) e otimiza o texto
para melhor naturalidade na síntese de fala.
"""

from __future__ import annotations

import re

from voxtext.pipeline.base import PipelineStage
from voxtext.models.document import Document, Segment, SegmentType


class TTSOptimizerStage(PipelineStage):
    """Estágio 5: Otimização do texto para TTS com SSML."""

    def process(self, document: Document) -> Document:
        text = document.cleaned_text or document.raw_text
        if not text.strip():
            return document

        pauses = self.settings.pause_durations

        # Gerar versão SSML
        blocks = re.split(r"\n\s*\n", text)
        segments: list[Segment] = []

        for i, block in enumerate(blocks):
            block = block.strip()
            if not block:
                continue

            # Determinar tipo de segmento
            seg_type = self._detect_segment_type(block)

            # Gerar SSML para este bloco
            ssml = self._generate_ssml(block, pauses, seg_type)

            segments.append(Segment(
                text=block,
                segment_type=seg_type,
                index=i,
                ssml_markup=ssml,
            ))

        document.segments = segments
        document.metadata["processing_mode"] = self.settings.processing_mode.value
        self.logger.info("Otimização TTS: %d segmentos gerados", len(segments))
        return document

    def _detect_segment_type(self, block: str) -> SegmentType:
        lines = block.split("\n")
        text = block.strip()

        if len(text) < 80 and not text.endswith((".", "!", "?")):
            return SegmentType.HEADING
        if len(lines) == 1 and len(text) < 200:
            return SegmentType.PARAGRAPH
        return SegmentType.PARAGRAPH

    def _generate_ssml(self, text: str, pauses, seg_type: SegmentType) -> str:
        ssml = text

        # Adicionar pausas após pontuação
        ssml = re.sub(
            r"([.!?])\s+",
            rf'\1 <break time="{pauses.period}ms"/> ',
            ssml,
        )
        ssml = re.sub(
            r",\s+",
            f', <break time="{pauses.comma}ms"/> ',
            ssml,
        )
        ssml = re.sub(
            r"([;:])\s+",
            rf'\1 <break time="{pauses.comma}ms"/> ',
            ssml,
        )

        # Pausa de seção para headings
        if seg_type == SegmentType.HEADING:
            ssml = ssml + f'\n<break time="{pauses.section}ms"/>'

        return ssml
