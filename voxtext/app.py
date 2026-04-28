"""
Classe principal do VoxText Engine.

Orquestra o pipeline de processamento, os exportadores e a interface gráfica.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable

from voxtext.config.settings import Settings, ProcessingMode
from voxtext.models.document import Document, ProcessingResult
from voxtext.pipeline.base import Pipeline
from voxtext.pipeline.parser import ParserStage
from voxtext.pipeline.cleaner import CleanerStage
from voxtext.pipeline.semantic_engine import SemanticEngineStage
from voxtext.pipeline.normalizer import NormalizerStage
from voxtext.pipeline.tts_optimizer import TTSOptimizerStage
from voxtext.pipeline.segmenter import SegmenterStage
from voxtext.exporters.txt_exporter import TxtExporter
from voxtext.exporters.json_exporter import JsonExporter
from voxtext.exporters.ssml_exporter import SsmlExporter
from voxtext.text_splitter import split_text_at_sentences, TextChunk

logger = logging.getLogger(__name__)


class VoxTextApp:
    """Classe principal que orquestra todo o sistema VoxText."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.last_result: ProcessingResult | None = None
        self.last_chunks: list[TextChunk] = []

        # Exportadores disponíveis
        self._exporters = {
            "txt": TxtExporter(),
            "json": JsonExporter(),
            "ssml": SsmlExporter(),
        }

    def load_file(self, path: Path) -> str:
        """
        Carrega e extrai texto de um arquivo.

        Args:
            path: Caminho do arquivo.

        Returns:
            Texto bruto extraído.
        """
        document = Document(source_path=path)
        parser = ParserStage(self.settings)
        document = parser.process(document)
        return document.raw_text

    def process_file(
        self,
        path: Path,
        on_progress: Callable[[str, float], None] | None = None,
    ) -> ProcessingResult:
        """
        Processa um arquivo pelo pipeline completo.

        Args:
            path: Caminho do arquivo.
            on_progress: Callback de progresso (stage_name, percentage).

        Returns:
            Resultado do processamento.
        """
        document = Document(source_path=path)

        stages = [
            ParserStage(self.settings),
            CleanerStage(self.settings),
            SemanticEngineStage(self.settings),
            NormalizerStage(self.settings),
            TTSOptimizerStage(self.settings),
            SegmenterStage(self.settings),
        ]

        pipeline = Pipeline(stages=stages, on_progress=on_progress)
        self.last_result = pipeline.run(document)
        return self.last_result

    def export_result(self, format_name: str, output_path: Path) -> Path:
        """
        Exporta o último resultado processado.

        Args:
            format_name: Nome do formato ('txt', 'json', 'ssml').
            output_path: Caminho do arquivo de saída.

        Returns:
            Caminho do arquivo gerado.
        """
        if not self.last_result:
            raise RuntimeError("Nenhum resultado disponível. Processe um arquivo primeiro.")

        exporter = self._exporters.get(format_name)
        if not exporter:
            raise ValueError(f"Formato desconhecido: {format_name}. "
                             f"Disponíveis: {list(self._exporters.keys())}")

        return exporter.export(self.last_result, output_path)

    def set_processing_mode(self, mode: str) -> None:
        """Define o modo de processamento."""
        mode_map = {
            "academic": ProcessingMode.ACADEMIC,
            "natural": ProcessingMode.NATURAL,
            "compact": ProcessingMode.COMPACT,
        }
        self.settings.processing_mode = mode_map.get(mode, ProcessingMode.NATURAL)
        logger.info("Modo alterado para: %s", self.settings.get_mode_display_name())

    def get_export_preview(self, format_name: str) -> str:
        """Retorna preview do resultado em determinado formato."""
        if not self.last_result:
            return ""
        exporter = self._exporters.get(format_name)
        if not exporter:
            return ""
        return exporter.export_to_string(self.last_result)

    def split_text(self, text: str, max_chars: int) -> list[TextChunk]:
        """
        Divide o texto em partes de no máximo max_chars caracteres,
        cortando sempre no último ponto final.

        Args:
            text: Texto a ser dividido.
            max_chars: Limite máximo de caracteres por parte.

        Returns:
            Lista de TextChunk com as partes.
        """
        self.last_chunks = split_text_at_sentences(text, max_chars)
        logger.info("Texto dividido em %d partes (limite: %d chars)",
                     len(self.last_chunks), max_chars)
        return self.last_chunks

    def export_chunks(self, chunks: list[TextChunk], output_dir: Path) -> list[Path]:
        """
        Exporta cada chunk como um arquivo TXT individual.

        Args:
            chunks: Lista de TextChunk.
            output_dir: Diretório de saída.

        Returns:
            Lista de caminhos dos arquivos criados.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        exported: list[Path] = []

        for chunk in chunks:
            filename = f"parte_{chunk.index:03d}.txt"
            filepath = output_dir / filename
            filepath.write_text(chunk.text, encoding="utf-8")
            exported.append(filepath)

        logger.info("Exportados %d arquivos em %s", len(exported), output_dir)
        return exported

