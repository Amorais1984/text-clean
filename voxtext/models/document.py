"""
Modelos de dados centrais do VoxText Engine.

Define as estruturas usadas ao longo de todo o pipeline de processamento:
Document (entrada), Segment (bloco processado) e ProcessingResult (saída final).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class SegmentType(Enum):
    """Tipos de segmentos textuais detectados."""
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    LIST = "list"
    TABLE = "table"
    CAPTION = "caption"
    UNKNOWN = "unknown"


@dataclass
class Segment:
    """Um bloco semântico de texto processado."""
    text: str
    segment_type: SegmentType = SegmentType.PARAGRAPH
    index: int = 0
    ssml_markup: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def char_count(self) -> int:
        """Número de caracteres do segmento."""
        return len(self.text)

    @property
    def word_count(self) -> int:
        """Número estimado de palavras."""
        return len(self.text.split())


@dataclass
class Document:
    """Representação de um documento ao longo do pipeline."""
    source_path: Path | None = None
    raw_text: str = ""
    cleaned_text: str = ""
    segments: list[Segment] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def source_format(self) -> str:
        """Extensão do arquivo de origem (e.g., 'pdf', 'txt')."""
        if self.source_path:
            return self.source_path.suffix.lstrip(".").lower()
        return "unknown"

    @property
    def page_count(self) -> int:
        """Número de páginas (se disponível nos metadados)."""
        return self.metadata.get("page_count", 0)

    @property
    def total_chars(self) -> int:
        """Total de caracteres do texto limpo."""
        return len(self.cleaned_text) if self.cleaned_text else len(self.raw_text)


@dataclass
class ProcessingStats:
    """Estatísticas do processamento."""
    original_char_count: int = 0
    processed_char_count: int = 0
    segment_count: int = 0
    pages_processed: int = 0
    processing_time_seconds: float = 0.0
    normalizations_applied: int = 0
    lists_converted: int = 0
    abbreviations_expanded: int = 0

    @property
    def compression_ratio(self) -> float:
        """Razão entre texto processado e original."""
        if self.original_char_count == 0:
            return 0.0
        return self.processed_char_count / self.original_char_count


@dataclass
class ProcessingResult:
    """Resultado final do processamento do pipeline."""
    original_text: str = ""
    processed_text: str = ""
    segments: list[Segment] = field(default_factory=list)
    ssml_output: str = ""
    stats: ProcessingStats = field(default_factory=ProcessingStats)
    processing_mode: str = "natural"
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
