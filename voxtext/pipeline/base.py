"""
Base do pipeline de processamento.

Define a classe abstrata PipelineStage e o orquestrador Pipeline,
que executa os estágios sequencialmente com callbacks de progresso.
"""

from __future__ import annotations

import time
import logging
from abc import ABC, abstractmethod
from typing import Callable

from voxtext.models.document import Document, ProcessingResult, ProcessingStats
from voxtext.config.settings import Settings

logger = logging.getLogger(__name__)


class PipelineStage(ABC):
    """Classe base abstrata para todos os estágios do pipeline."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    def name(self) -> str:
        """Nome amigável do estágio."""
        return self.__class__.__name__.replace("Stage", "")

    @abstractmethod
    def process(self, document: Document) -> Document:
        """
        Processa o documento e retorna uma versão atualizada.

        Args:
            document: Documento a ser processado.

        Returns:
            Documento com as transformações deste estágio aplicadas.
        """
        ...


class Pipeline:
    """
    Orquestrador do pipeline de processamento.

    Executa uma sequência de PipelineStage sobre um Document,
    emitindo callbacks de progresso para a GUI.
    """

    def __init__(
        self,
        stages: list[PipelineStage],
        on_progress: Callable[[str, float], None] | None = None,
    ) -> None:
        """
        Args:
            stages: Lista ordenada de estágios a executar.
            on_progress: Callback (stage_name, progress_pct) para atualizar a GUI.
        """
        self.stages = stages
        self.on_progress = on_progress or (lambda name, pct: None)

    def run(self, document: Document) -> ProcessingResult:
        """
        Executa todos os estágios do pipeline sequencialmente.

        Args:
            document: Documento inicial (com raw_text ou source_path).

        Returns:
            ProcessingResult com texto processado, segmentos e estatísticas.
        """
        start_time = time.time()
        original_text = document.raw_text
        total_stages = len(self.stages)
        errors: list[str] = []
        warnings: list[str] = []

        logger.info("Pipeline iniciado com %d estágios", total_stages)

        for i, stage in enumerate(self.stages):
            stage_name = stage.name
            progress = (i / total_stages) * 100
            self.on_progress(stage_name, progress)
            logger.info("Executando estágio: %s (%.0f%%)", stage_name, progress)

            try:
                document = stage.process(document)
            except Exception as e:
                error_msg = f"Erro no estágio '{stage_name}': {e}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)
                # Continua com o próximo estágio quando possível
                continue

        self.on_progress("Concluído", 100.0)
        elapsed = time.time() - start_time
        logger.info("Pipeline concluído em %.2fs", elapsed)

        # Montar o texto processado a partir dos segmentos
        processed_text = document.cleaned_text
        if document.segments:
            processed_text = "\n\n".join(seg.text for seg in document.segments)

        # Montar o SSML a partir dos segmentos
        ssml_parts = [seg.ssml_markup for seg in document.segments if seg.ssml_markup]
        ssml_output = ""
        if ssml_parts:
            ssml_output = "<speak>\n" + "\n".join(ssml_parts) + "\n</speak>"

        stats = ProcessingStats(
            original_char_count=len(original_text),
            processed_char_count=len(processed_text),
            segment_count=len(document.segments),
            pages_processed=document.page_count,
            processing_time_seconds=elapsed,
        )

        return ProcessingResult(
            original_text=original_text,
            processed_text=processed_text,
            segments=document.segments,
            ssml_output=ssml_output,
            stats=stats,
            processing_mode=document.metadata.get("processing_mode", "natural"),
            errors=errors,
            warnings=warnings,
        )
