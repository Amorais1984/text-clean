"""Testes para o módulo de limpeza (Cleaner)."""

import pytest
from voxtext.pipeline.cleaner import CleanerStage
from voxtext.models.document import Document
from voxtext.config.settings import Settings


@pytest.fixture
def cleaner():
    return CleanerStage(Settings())


class TestCleanerStage:
    def test_normalize_whitespace(self, cleaner):
        doc = Document(raw_text="Texto   com    muitos   espaços.")
        result = cleaner.process(doc)
        assert "  " not in result.cleaned_text
        assert "Texto com muitos espaços." in result.cleaned_text

    def test_remove_page_numbers(self, cleaner):
        doc = Document(raw_text="Conteúdo aqui.\n\n42\n\nMais conteúdo.")
        result = cleaner.process(doc)
        assert "\n42\n" not in result.cleaned_text

    def test_collapse_blank_lines(self, cleaner):
        doc = Document(raw_text="Linha 1\n\n\n\n\nLinha 2")
        result = cleaner.process(doc)
        assert "\n\n\n" not in result.cleaned_text

    def test_empty_text(self, cleaner):
        doc = Document(raw_text="   ")
        result = cleaner.process(doc)
        assert result.cleaned_text == ""

    def test_reconstruct_paragraphs(self, cleaner):
        doc = Document(raw_text="Esta é uma frase que\ncontinua na próxima linha.")
        result = cleaner.process(doc)
        assert "frase que continua" in result.cleaned_text


class TestNormalizerStage:
    """Testes para normalização linguística."""

    @pytest.fixture
    def normalizer(self):
        from voxtext.pipeline.normalizer import NormalizerStage
        return NormalizerStage(Settings())

    def test_number_to_words(self, normalizer):
        doc = Document(cleaned_text="Tenho 42 itens.")
        result = normalizer.process(doc)
        assert "quarenta e dois" in result.cleaned_text

    def test_currency_brl(self, normalizer):
        doc = Document(cleaned_text="O preço é R$ 1.500,00.")
        result = normalizer.process(doc)
        assert "mil e quinhentos reais" in result.cleaned_text

    def test_percentage(self, normalizer):
        doc = Document(cleaned_text="Aumento de 15%.")
        result = normalizer.process(doc)
        assert "quinze por cento" in result.cleaned_text

    def test_time(self, normalizer):
        doc = Document(cleaned_text="Reunião às 14:30.")
        result = normalizer.process(doc)
        assert "quatorze horas e trinta minutos" in result.cleaned_text

    def test_date(self, normalizer):
        doc = Document(cleaned_text="Data: 28/04/2026.")
        result = normalizer.process(doc)
        assert "vinte e oito de abril" in result.cleaned_text

    def test_ordinal(self, normalizer):
        doc = Document(cleaned_text="O 1º lugar.")
        result = normalizer.process(doc)
        assert "primeiro" in result.cleaned_text


class TestSemanticEngine:
    """Testes para reestruturação semântica."""

    @pytest.fixture
    def engine(self):
        from voxtext.pipeline.semantic_engine import SemanticEngineStage
        return SemanticEngineStage(Settings())

    def test_list_to_narrative(self, engine):
        doc = Document(cleaned_text="Componentes:\n- CPU\n- RAM\n- SSD")
        result = engine.process(doc)
        assert "CPU" in result.cleaned_text
        assert "RAM" in result.cleaned_text
        assert "SSD" in result.cleaned_text
        assert "-" not in result.cleaned_text

    def test_numbered_list(self, engine):
        doc = Document(cleaned_text="Passos:\n1) Abrir\n2) Editar\n3) Salvar")
        result = engine.process(doc)
        assert "1)" not in result.cleaned_text


class TestTTSOptimizer:
    """Testes para otimização TTS."""

    @pytest.fixture
    def optimizer(self):
        from voxtext.pipeline.tts_optimizer import TTSOptimizerStage
        return TTSOptimizerStage(Settings())

    def test_generates_segments(self, optimizer):
        doc = Document(cleaned_text="Primeiro parágrafo.\n\nSegundo parágrafo.")
        result = optimizer.process(doc)
        assert len(result.segments) == 2

    def test_generates_ssml(self, optimizer):
        doc = Document(cleaned_text="Uma frase com vírgula, e ponto.")
        result = optimizer.process(doc)
        assert len(result.segments) > 0
        assert "break" in result.segments[0].ssml_markup


class TestPipeline:
    """Testes de integração do pipeline completo."""

    def test_full_pipeline_txt(self, tmp_path):
        from voxtext.app import VoxTextApp

        # Criar arquivo de teste
        test_file = tmp_path / "test.txt"
        test_file.write_text(
            "Título do Documento\n\n"
            "Este é o conteúdo principal. Tem 42 itens.\n\n"
            "Componentes:\n- CPU\n- RAM\n- SSD\n\n"
            "O preço é R$ 1.500,00.",
            encoding="utf-8",
        )

        app = VoxTextApp()
        result = app.process_file(test_file)

        assert result.processed_text
        assert result.stats.segment_count > 0
        assert result.stats.processing_time_seconds > 0
        assert len(result.errors) == 0

    def test_export_txt(self, tmp_path):
        from voxtext.app import VoxTextApp

        test_file = tmp_path / "test.txt"
        test_file.write_text("Texto de teste simples.", encoding="utf-8")

        app = VoxTextApp()
        app.process_file(test_file)

        output = tmp_path / "output.txt"
        exported = app.export_result("txt", output)
        assert exported.exists()
        assert exported.read_text(encoding="utf-8").strip()

    def test_export_json(self, tmp_path):
        import json
        from voxtext.app import VoxTextApp

        test_file = tmp_path / "test.txt"
        test_file.write_text("Texto de teste.", encoding="utf-8")

        app = VoxTextApp()
        app.process_file(test_file)

        output = tmp_path / "output.json"
        exported = app.export_result("json", output)
        data = json.loads(exported.read_text(encoding="utf-8"))
        assert "segments" in data
        assert "metadata" in data

    def test_export_ssml(self, tmp_path):
        from voxtext.app import VoxTextApp

        test_file = tmp_path / "test.txt"
        test_file.write_text("Texto de teste.", encoding="utf-8")

        app = VoxTextApp()
        app.process_file(test_file)

        output = tmp_path / "output.ssml"
        exported = app.export_result("ssml", output)
        content = exported.read_text(encoding="utf-8")
        assert "<speak" in content
