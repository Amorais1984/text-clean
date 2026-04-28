"""
Divisor de Texto Inteligente.

Divide texto processado em partes de tamanho máximo configurável,
cortando sempre em um ponto final para preservar sentenças completas.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TextChunk:
    """Uma parte do texto dividido."""
    index: int
    text: str
    char_count: int
    word_count: int


def split_text_at_sentences(
    text: str,
    max_chars: int = 5000,
) -> list[TextChunk]:
    """
    Divide texto em partes de no máximo `max_chars` caracteres,
    cortando sempre no último ponto final (.) antes do limite.

    Se não houver ponto final antes do limite, tenta cortar em
    outros sinais de pontuação (! ? ;). Se nenhum for encontrado,
    corta no último espaço.

    Args:
        text: Texto completo a ser dividido.
        max_chars: Número máximo de caracteres por parte.

    Returns:
        Lista de TextChunk com as partes do texto.
    """
    if not text or not text.strip():
        return []

    if len(text) <= max_chars:
        return [TextChunk(
            index=1,
            text=text.strip(),
            char_count=len(text.strip()),
            word_count=len(text.strip().split()),
        )]

    chunks: list[TextChunk] = []
    remaining = text.strip()
    index = 1

    while remaining:
        if len(remaining) <= max_chars:
            # O que sobrou cabe em uma parte
            chunks.append(TextChunk(
                index=index,
                text=remaining.strip(),
                char_count=len(remaining.strip()),
                word_count=len(remaining.strip().split()),
            ))
            break

        # Pegar a janela de max_chars
        window = remaining[:max_chars]

        # Tentar encontrar o último ponto final na janela
        cut_pos = _find_last_sentence_end(window)

        if cut_pos == -1:
            # Sem pontuação → cortar no último espaço
            cut_pos = window.rfind(" ")
            if cut_pos == -1:
                # Sem espaço → corte forçado no limite
                cut_pos = max_chars

        # O cut_pos é o índice do caractere de corte (inclusive)
        chunk_text = remaining[:cut_pos + 1].strip()

        if chunk_text:
            chunks.append(TextChunk(
                index=index,
                text=chunk_text,
                char_count=len(chunk_text),
                word_count=len(chunk_text.split()),
            ))
            index += 1

        # Avançar o restante
        remaining = remaining[cut_pos + 1:].strip()

    return chunks


def _find_last_sentence_end(text: str) -> int:
    """
    Encontra a posição do último finalizador de sentença no texto.

    Prioridade: ponto final (.) > exclamação (!) > interrogação (?) > ponto e vírgula (;)

    Retorna -1 se nenhum for encontrado.
    """
    # Procurar de trás para frente o último ponto final
    # Ignorar pontos que fazem parte de abreviações (ex: "Dr.", "Sr.")
    last_period = -1
    for i in range(len(text) - 1, -1, -1):
        ch = text[i]
        if ch == ".":
            # Verificar se é fim de sentença (seguido de espaço, newline ou fim)
            next_pos = i + 1
            if next_pos >= len(text) or text[next_pos] in (" ", "\n", "\r"):
                # Verificar se NÃO é abreviação (palavra curta antes do ponto)
                word_start = i - 1
                while word_start >= 0 and text[word_start].isalpha():
                    word_start -= 1
                word_before = text[word_start + 1:i]
                # Se a palavra antes do ponto tem 1-3 chars, pode ser abreviação
                # Mas ainda é um ponto válido para corte
                last_period = i
                break

    if last_period != -1:
        return last_period

    # Fallback: ! ou ?
    for ch in ("!", "?"):
        pos = text.rfind(ch)
        if pos != -1:
            return pos

    # Fallback: ;
    pos = text.rfind(";")
    if pos != -1:
        return pos

    return -1
