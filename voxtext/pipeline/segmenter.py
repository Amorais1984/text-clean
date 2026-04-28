"""
Estágio de Segmentação Inteligente.

Divide o texto em blocos de 200–500 caracteres respeitando
limites de sentença e coerência semântica.
"""

from __future__ import annotations

import re

from voxtext.pipeline.base import PipelineStage
from voxtext.models.document import Document, Segment, SegmentType


class SegmenterStage(PipelineStage):
    """Estágio 6: Segmentação inteligente do texto."""

    def process(self, document: Document) -> Document:
        if not document.segments:
            return document

        min_len = self.settings.min_segment_length
        max_len = self.settings.max_segment_length
        new_segments: list[Segment] = []
        idx = 0

        for segment in document.segments:
            if segment.char_count <= max_len:
                segment.index = idx
                new_segments.append(segment)
                idx += 1
                continue

            # Segmento muito longo → dividir por sentenças
            sub_segments = self._split_segment(
                segment.text, segment.ssml_markup,
                min_len, max_len
            )
            for sub_text, sub_ssml in sub_segments:
                new_segments.append(Segment(
                    text=sub_text,
                    segment_type=segment.segment_type,
                    index=idx,
                    ssml_markup=sub_ssml,
                ))
                idx += 1

        document.segments = new_segments
        self.logger.info("Segmentação: %d segmentos finais", len(new_segments))
        return document

    def _split_segment(
        self, text: str, ssml: str,
        min_len: int, max_len: int
    ) -> list[tuple[str, str]]:
        """Divide texto longo em sub-segmentos respeitando sentenças."""
        sentences = self._split_into_sentences(text)
        ssml_sentences = self._split_into_sentences(ssml) if ssml else sentences

        result: list[tuple[str, str]] = []
        current_text = ""
        current_ssml = ""

        for i, sent in enumerate(sentences):
            sent_ssml = ssml_sentences[i] if i < len(ssml_sentences) else sent

            if not current_text:
                current_text = sent
                current_ssml = sent_ssml
                continue

            combined_len = len(current_text) + len(sent) + 1
            if combined_len <= max_len:
                current_text += " " + sent
                current_ssml += " " + sent_ssml
            else:
                if len(current_text) >= min_len:
                    result.append((current_text.strip(), current_ssml.strip()))
                    current_text = sent
                    current_ssml = sent_ssml
                else:
                    current_text += " " + sent
                    current_ssml += " " + sent_ssml

        if current_text.strip():
            result.append((current_text.strip(), current_ssml.strip()))

        return result if result else [(text, ssml)]

    def _split_into_sentences(self, text: str) -> list[str]:
        """Divide texto em sentenças usando regex."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
