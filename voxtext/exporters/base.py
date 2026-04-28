"""Classe base abstrata para exportadores."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from voxtext.models.document import ProcessingResult


class Exporter(ABC):
    """Classe base para todos os exportadores de resultado."""

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Nome do formato de exportação."""
        ...

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Extensão do arquivo de saída."""
        ...

    @abstractmethod
    def export(self, result: ProcessingResult, output_path: Path) -> Path:
        """
        Exporta o resultado para um arquivo.

        Args:
            result: Resultado do processamento.
            output_path: Caminho do arquivo de saída.

        Returns:
            Caminho do arquivo gerado.
        """
        ...

    def export_to_string(self, result: ProcessingResult) -> str:
        """Exporta o resultado como string (para preview na GUI)."""
        ...
