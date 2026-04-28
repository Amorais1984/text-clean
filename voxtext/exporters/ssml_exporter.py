"""Exportador para formato SSML."""

from __future__ import annotations

from pathlib import Path

from voxtext.exporters.base import Exporter
from voxtext.models.document import ProcessingResult


class SsmlExporter(Exporter):
    """Exporta resultado como documento SSML completo."""

    @property
    def format_name(self) -> str:
        return "SSML"

    @property
    def file_extension(self) -> str:
        return ".ssml"

    def export(self, result: ProcessingResult, output_path: Path) -> Path:
        output_path = output_path.with_suffix(self.file_extension)
        content = self.export_to_string(result)
        output_path.write_text(content, encoding="utf-8")
        return output_path

    def export_to_string(self, result: ProcessingResult) -> str:
        if result.ssml_output:
            return result.ssml_output

        # Gerar SSML a partir dos segmentos
        parts = ['<?xml version="1.0" encoding="UTF-8"?>']
        parts.append('<speak version="1.1" xml:lang="pt-BR">')

        for seg in result.segments:
            if seg.ssml_markup:
                parts.append(f"  <p>{seg.ssml_markup}</p>")
            else:
                parts.append(f"  <p>{seg.text}</p>")

        parts.append("</speak>")
        return "\n".join(parts)
