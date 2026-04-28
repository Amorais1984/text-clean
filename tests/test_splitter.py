"""Testes para o Divisor de Texto."""

import pytest
from voxtext.text_splitter import split_text_at_sentences, TextChunk


class TestTextSplitter:
    """Testes da função split_text_at_sentences."""

    def test_empty_text(self):
        chunks = split_text_at_sentences("", 5000)
        assert chunks == []

    def test_text_under_limit(self):
        text = "Texto curto."
        chunks = split_text_at_sentences(text, 5000)
        assert len(chunks) == 1
        assert chunks[0].text == "Texto curto."
        assert chunks[0].index == 1

    def test_split_at_period(self):
        # Criar texto com sentenças que ultrapassam o limite
        text = "Primeira sentença completa. Segunda sentença completa. Terceira sentença completa."
        # Limite que force a divisão
        chunks = split_text_at_sentences(text, 30)
        assert len(chunks) > 1
        # Cada chunk deve terminar com ponto
        for chunk in chunks:
            assert chunk.text.rstrip().endswith(".")

    def test_preserves_all_content(self):
        text = "Sentença um. Sentença dois. Sentença três. Sentença quatro."
        chunks = split_text_at_sentences(text, 30)
        # Reunir todas as partes e verificar que nenhum conteúdo foi perdido
        all_text = " ".join(c.text for c in chunks)
        for word in ["um", "dois", "três", "quatro"]:
            assert word in all_text

    def test_chunk_indices(self):
        text = "Frase A. Frase B. Frase C. Frase D."
        chunks = split_text_at_sentences(text, 20)
        # Índices devem ser sequenciais começando em 1
        for i, chunk in enumerate(chunks):
            assert chunk.index == i + 1

    def test_char_count_matches(self):
        text = "Uma frase aqui. Outra frase ali."
        chunks = split_text_at_sentences(text, 5000)
        for chunk in chunks:
            assert chunk.char_count == len(chunk.text)

    def test_word_count_matches(self):
        text = "Uma frase aqui. Outra frase ali."
        chunks = split_text_at_sentences(text, 5000)
        for chunk in chunks:
            assert chunk.word_count == len(chunk.text.split())

    def test_respects_max_chars(self):
        # Construir texto longo
        sentences = [f"Esta é a sentença número {i}." for i in range(50)]
        text = " ".join(sentences)
        max_chars = 200

        chunks = split_text_at_sentences(text, max_chars)
        for chunk in chunks:
            # Cada chunk deve estar dentro do limite (com tolerância para
            # o caso de uma sentença individual ultrapassar)
            assert chunk.char_count <= max_chars or "." not in chunk.text[:-1]

    def test_large_text_multiple_chunks(self):
        text = ". ".join([f"Parágrafo {i} com conteúdo relevante" for i in range(100)]) + "."
        chunks = split_text_at_sentences(text, 500)
        assert len(chunks) > 1

    def test_no_period_falls_back_to_space(self):
        # Texto sem ponto final — deve cortar no espaço
        text = "Uma frase muito longa sem pontuação que precisa ser dividida em partes menores"
        chunks = split_text_at_sentences(text, 30)
        assert len(chunks) > 1
