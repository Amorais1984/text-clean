"""Exportador para formato JSON estruturado."""

from __future__ import annotations

import json
from pathlib import Path

from voxtext.exporters.base import Exporter
from voxtext.models.document import ProcessingResult


class JsonExporter(Exporter):
    """Exporta resultado como JSON estruturado."""

    @property
    def format_name(self) -> str:
        return "JSON Estruturado"

    @property
    def file_extension(self) -> str:
        return ".json"

    def export(self, result: ProcessingResult, output_path: Path) -> Path:
        output_path = output_path.with_suffix(self.file_extension)
        content = self.export_to_string(result)
        output_path.write_text(content, encoding="utf-8")
        return output_path

    def export_to_string(self, result: ProcessingResult) -> str:
        data = {
            "metadata": {
                "processing_mode": result.processing_mode,
                "segment_count": result.stats.segment_count,
                "original_char_count": result.stats.original_char_count,
                "processed_char_count": result.stats.processed_char_count,
                "processing_time_seconds": round(result.stats.processing_time_seconds, 3),
                "compression_ratio": round(result.stats.compression_ratio, 3),
            },
            "segments": [
                {
                    "index": seg.index,
                    "type": seg.segment_type.value,
                    "text": seg.text,
                    "char_count": seg.char_count,
                    "word_count": seg.word_count,
                    "ssml": seg.ssml_markup,
                }
                for seg in result.segments
            ],
            "errors": result.errors,
            "warnings": result.warnings,
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
