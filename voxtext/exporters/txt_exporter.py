"""Exportador para formato TXT limpo."""

from __future__ import annotations

from pathlib import Path

from voxtext.exporters.base import Exporter
from voxtext.models.document import ProcessingResult


class TxtExporter(Exporter):
    """Exporta resultado como texto limpo UTF-8."""

    @property
    def format_name(self) -> str:
        return "Texto Limpo (TXT)"

    @property
    def file_extension(self) -> str:
        return ".txt"

    def export(self, result: ProcessingResult, output_path: Path) -> Path:
        output_path = output_path.with_suffix(self.file_extension)
        content = self.export_to_string(result)
        output_path.write_text(content, encoding="utf-8")
        return output_path

    def export_to_string(self, result: ProcessingResult) -> str:
        if result.segments:
            return "\n\n".join(seg.text for seg in result.segments)
        return result.processed_text
