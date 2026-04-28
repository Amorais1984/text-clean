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
from voxtext.ai.providers import create_provider
from voxtext.ai.corrector import AICorrector, CorrectionResult

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

    def export_chunks(
        self,
        chunks: list[TextChunk],
        output_dir: Path,
        format_name: str = "txt",
    ) -> list[Path]:
        """
        Exporta cada chunk como um arquivo individual no formato escolhido.

        Args:
            chunks: Lista de TextChunk.
            output_dir: Diretório de saída.
            format_name: Formato de exportação ('txt', 'json', 'ssml').

        Returns:
            Lista de caminhos dos arquivos criados.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        exported: list[Path] = []

        ext_map = {"txt": ".txt", "json": ".json", "ssml": ".ssml"}
        ext = ext_map.get(format_name, ".txt")
        exporter = self._exporters.get(format_name)

        for chunk in chunks:
            filename = f"parte_{chunk.index:03d}{ext}"
            filepath = output_dir / filename

            if exporter and format_name != "txt":
                # Criar um mini ProcessingResult para este chunk
                from voxtext.models.document import Segment, SegmentType, ProcessingStats
                mini_result = ProcessingResult(
                    original_text=chunk.text,
                    processed_text=chunk.text,
                    segments=[Segment(
                        text=chunk.text,
                        segment_type=SegmentType.PARAGRAPH,
                        index=0,
                        ssml_markup=chunk.text,
                    )],
                    stats=ProcessingStats(
                        original_char_count=chunk.char_count,
                        processed_char_count=chunk.char_count,
                        segment_count=1,
                    ),
                    processing_mode=self.settings.processing_mode.value,
                )
                content = exporter.export_to_string(mini_result)
                filepath.write_text(content, encoding="utf-8")
            else:
                filepath.write_text(chunk.text, encoding="utf-8")

            exported.append(filepath)

        logger.info("Exportados %d arquivos (%s) em %s", len(exported), format_name, output_dir)
        return exported

    def correct_with_ai(
        self,
        text: str,
        provider_name: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> CorrectionResult:
        """
        Corrige o texto usando IA (Ollama ou Gemini).

        Args:
            text: Texto a ser corrigido.
            provider_name: 'ollama' ou 'gemini' (override de settings).
            model: Nome do modelo (override).
            api_key: API key para Gemini (override).
            base_url: URL do Ollama (override).
            on_progress: Callback (chunk_atual, total_chunks).

        Returns:
            CorrectionResult com o texto corrigido.
        """
        prov = provider_name or self.settings.ai_provider

        if prov == "ollama":
            mdl = model or self.settings.ollama_model
            url = base_url or self.settings.ollama_url
            provider = create_provider("ollama", model=mdl, base_url=url)
        else:
            mdl = model or self.settings.gemini_model
            key = api_key or self.settings.gemini_api_key
            provider = create_provider("gemini", model=mdl, api_key=key)

        corrector = AICorrector(
            provider=provider,
            max_chunk_size=self.settings.ai_max_chunk_size,
        )

        result = corrector.correct(text, on_progress=on_progress)
        logger.info(
            "Correção IA (%s/%s): %d chunks, %d tokens, sucesso=%s",
            result.provider, result.model,
            result.chunks_processed, result.total_tokens,
            result.success,
        )
        return result
