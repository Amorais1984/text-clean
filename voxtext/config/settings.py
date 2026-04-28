"""
Configurações globais do VoxText Engine.

Define modos de processamento (Acadêmico, Natural, Compacto) e seus
respectivos parâmetros de pausa, segmentação e formalidade.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ProcessingMode(Enum):
    """Modos de otimização para diferentes contextos de uso."""
    ACADEMIC = "academic"    # Mais pausas, mais formal
    NATURAL = "natural"      # Equilibrado (padrão)
    COMPACT = "compact"      # Mais direto, menos pausas


@dataclass
class PauseDurations:
    """Durações de pausa em milissegundos para marcações SSML."""
    comma: int = 250        # Pausa após vírgula
    period: int = 500       # Pausa após ponto final
    section: int = 800      # Pausa entre seções
    paragraph: int = 600    # Pausa entre parágrafos
    list_item: int = 300    # Pausa entre itens de lista


# Presets de pausa por modo de processamento
PAUSE_PRESETS: dict[ProcessingMode, PauseDurations] = {
    ProcessingMode.ACADEMIC: PauseDurations(
        comma=375, period=750, section=1200, paragraph=900, list_item=450
    ),
    ProcessingMode.NATURAL: PauseDurations(
        comma=250, period=500, section=800, paragraph=600, list_item=300
    ),
    ProcessingMode.COMPACT: PauseDurations(
        comma=175, period=350, section=560, paragraph=420, list_item=210
    ),
}


@dataclass
class Settings:
    """Configurações globais da aplicação."""

    # Modo de processamento
    processing_mode: ProcessingMode = ProcessingMode.NATURAL

    # Segmentação
    min_segment_length: int = 200   # Caracteres mínimos por segmento
    max_segment_length: int = 500   # Caracteres máximos por segmento

    # Normalização
    expand_numbers: bool = True
    expand_dates: bool = True
    expand_currencies: bool = True
    expand_abbreviations: bool = True
    expand_percentages: bool = True
    expand_ordinals: bool = True
    expand_times: bool = True

    # Exportação
    default_export_format: str = "txt"
    include_ssml: bool = True

    # PDF
    detect_columns: bool = True
    remove_headers_footers: bool = True
    reconstruct_hyphenated: bool = True

    # Customizações do usuário
    custom_abbreviations: dict[str, str] = field(default_factory=dict)

    # IA / LLM
    ai_enabled: bool = False
    ai_provider: str = "ollama"                     # "ollama" ou "gemini"
    ollama_model: str = "llama3.2"
    ollama_url: str = "http://localhost:11434"
    gemini_model: str = "gemini-2.5-flash"
    gemini_api_key: str = ""
    ai_max_chunk_size: int = 3000                   # Chars por chunk para IA

    @property
    def pause_durations(self) -> PauseDurations:
        """Retorna as durações de pausa para o modo atual."""
        return PAUSE_PRESETS[self.processing_mode]

    def get_mode_display_name(self) -> str:
        """Nome amigável do modo de processamento."""
        names = {
            ProcessingMode.ACADEMIC: "Acadêmico",
            ProcessingMode.NATURAL: "Natural",
            ProcessingMode.COMPACT: "Compacto",
        }
        return names.get(self.processing_mode, "Natural")
