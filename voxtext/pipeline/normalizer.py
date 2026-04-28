"""
Estágio de Normalização Linguística para PT-BR.

Converte números, datas, moedas, abreviações e outros elementos
para sua forma por extenso, melhorando a naturalidade da fala.
"""

from __future__ import annotations

import re

from voxtext.pipeline.base import PipelineStage
from voxtext.models.document import Document
from voxtext.config.abbreviations import ABBREVIATIONS, UNITS


class NormalizerStage(PipelineStage):
    """Estágio 4: Normalização linguística do texto para PT-BR."""

    # Mapeamento de números por extenso (0–19)
    _ONES = [
        "zero", "um", "dois", "três", "quatro", "cinco", "seis",
        "sete", "oito", "nove", "dez", "onze", "doze", "treze",
        "quatorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove",
    ]
    _TENS = [
        "", "", "vinte", "trinta", "quarenta", "cinquenta",
        "sessenta", "setenta", "oitenta", "noventa",
    ]
    _HUNDREDS = [
        "", "cento", "duzentos", "trezentos", "quatrocentos", "quinhentos",
        "seiscentos", "setecentos", "oitocentos", "novecentos",
    ]
    _MONTHS = [
        "", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
    ]
    _ORDINALS_M = {
        1: "primeiro", 2: "segundo", 3: "terceiro", 4: "quarto",
        5: "quinto", 6: "sexto", 7: "sétimo", 8: "oitavo",
        9: "nono", 10: "décimo",
    }

    def process(self, document: Document) -> Document:
        text = document.cleaned_text or document.raw_text
        if not text.strip():
            return document

        count = 0

        if self.settings.expand_currencies:
            text, n = self._normalize_currencies(text)
            count += n
        if self.settings.expand_percentages:
            text, n = self._normalize_percentages(text)
            count += n
        if self.settings.expand_ordinals:
            text, n = self._normalize_ordinals(text)
            count += n
        if self.settings.expand_times:
            text, n = self._normalize_times(text)
            count += n
        if self.settings.expand_dates:
            text, n = self._normalize_dates(text)
            count += n
        if self.settings.expand_numbers:
            text, n = self._normalize_numbers(text)
            count += n
        if self.settings.expand_abbreviations:
            text, n = self._normalize_abbreviations(text)
            count += n

        document.cleaned_text = text
        document.metadata["normalizations_applied"] = count
        self.logger.info("Normalizações aplicadas: %d", count)
        return document

    # ── Moedas ──────────────────────────────────────────────
    def _normalize_currencies(self, text: str) -> tuple[str, int]:
        count = 0

        def _replace_brl(m: re.Match) -> str:
            nonlocal count
            count += 1
            integer_part = m.group(1).replace(".", "")
            decimal_part = m.group(2) if m.group(2) else ""
            value = int(integer_part)
            result = self._number_to_words(value)

            if value == 1:
                result += " real"
            else:
                result += " reais"

            if decimal_part:
                cents = int(decimal_part)
                if cents > 0:
                    result += f" e {self._number_to_words(cents)}"
                    result += " centavo" if cents == 1 else " centavos"
            return result

        text = re.sub(
            r"R\$\s*([\d.]+)(?:,(\d{2}))?",
            _replace_brl, text
        )

        def _replace_usd(m: re.Match) -> str:
            nonlocal count
            count += 1
            integer_part = m.group(1).replace(",", "")
            value = int(integer_part)
            result = self._number_to_words(value)
            result += " dólar" if value == 1 else " dólares"
            return result

        text = re.sub(r"US?\$\s*([\d,]+)", _replace_usd, text)
        return text, count

    # ── Percentuais ─────────────────────────────────────────
    def _normalize_percentages(self, text: str) -> tuple[str, int]:
        count = 0

        def _replace(m: re.Match) -> str:
            nonlocal count
            count += 1
            num_str = m.group(1).replace(",", ".")
            num = float(num_str)
            if num == int(num):
                return f"{self._number_to_words(int(num))} por cento"
            integer = int(num)
            decimal = round((num - integer) * 10)
            return f"{self._number_to_words(integer)} vírgula {self._number_to_words(decimal)} por cento"

        text = re.sub(r"(\d+(?:,\d+)?)\s*%", _replace, text)
        return text, count

    # ── Ordinais ────────────────────────────────────────────
    def _normalize_ordinals(self, text: str) -> tuple[str, int]:
        count = 0

        def _replace(m: re.Match) -> str:
            nonlocal count
            count += 1
            num = int(m.group(1))
            return self._ORDINALS_M.get(num, f"{self._number_to_words(num)}º")

        text = re.sub(r"(\d+)[ºª°]", _replace, text)
        return text, count

    # ── Horários ────────────────────────────────────────────
    def _normalize_times(self, text: str) -> tuple[str, int]:
        count = 0

        def _replace(m: re.Match) -> str:
            nonlocal count
            count += 1
            hours = int(m.group(1))
            minutes = int(m.group(2))
            h_word = self._number_to_words(hours)
            if minutes == 0:
                return f"{h_word} horas"
            m_word = self._number_to_words(minutes)
            return f"{h_word} horas e {m_word} minutos"

        text = re.sub(r"\b(\d{1,2}):(\d{2})\b", _replace, text)
        return text, count

    # ── Datas ───────────────────────────────────────────────
    def _normalize_dates(self, text: str) -> tuple[str, int]:
        count = 0

        def _replace(m: re.Match) -> str:
            nonlocal count
            count += 1
            day = int(m.group(1))
            month = int(m.group(2))
            year = int(m.group(3))
            d = self._number_to_words(day)
            mo = self._MONTHS[month] if 1 <= month <= 12 else str(month)
            y = self._number_to_words(year)
            return f"{d} de {mo} de {y}"

        text = re.sub(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", _replace, text)
        return text, count

    # ── Números genéricos ───────────────────────────────────
    def _normalize_numbers(self, text: str) -> tuple[str, int]:
        count = 0

        def _replace(m: re.Match) -> str:
            nonlocal count
            num_str = m.group(0)
            # Ignorar números que já fazem parte de outras estruturas
            try:
                num = int(num_str)
            except ValueError:
                return num_str
            if num > 999999:
                return num_str
            count += 1
            return self._number_to_words(num)

        text = re.sub(r"\b\d{1,6}\b", _replace, text)
        return text, count

    # ── Abreviações ─────────────────────────────────────────
    def _normalize_abbreviations(self, text: str) -> tuple[str, int]:
        count = 0
        all_abbrevs = {**ABBREVIATIONS, **self.settings.custom_abbreviations}

        # Ordenar por comprimento decrescente para evitar matches parciais
        sorted_abbrevs = sorted(all_abbrevs.items(), key=lambda x: len(x[0]), reverse=True)

        for abbrev, expansion in sorted_abbrevs:
            # Usar regex com escape para match seguro
            escaped = re.escape(abbrev)
            # Para abreviações com ponto, o ponto já é escapado
            # Adicionar word boundary quando apropriado
            if abbrev.endswith(".") or abbrev.endswith("/"):
                pattern = r"(?<!\w)" + escaped
            else:
                pattern = r"\b" + escaped + r"\b"

            new_text = re.sub(pattern, expansion, text)
            if new_text != text:
                count += 1
                text = new_text

        return text, count

    # ── Conversão de número para palavras (PT-BR) ──────────
    def _number_to_words(self, n: int) -> str:
        if n < 0:
            return "menos " + self._number_to_words(-n)
        if n < 20:
            return self._ONES[n]
        if n < 100:
            tens = self._TENS[n // 10]
            ones = n % 10
            return f"{tens} e {self._ONES[ones]}" if ones else tens
        if n == 100:
            return "cem"
        if n < 1000:
            h = self._HUNDREDS[n // 100]
            remainder = n % 100
            if remainder == 0:
                return h
            return f"{h} e {self._number_to_words(remainder)}"
        if n < 1000000:
            thousands = n // 1000
            remainder = n % 1000
            if thousands == 1:
                t_word = "mil"
            else:
                t_word = f"{self._number_to_words(thousands)} mil"
            if remainder == 0:
                return t_word
            # Em português: "mil e quinhentos", "mil e duzentos" (centenas exatas)
            # Mas: "mil quinhentos e vinte e três" (centenas + dezenas)
            if remainder < 100 or remainder % 100 == 0:
                connector = " e "
            else:
                connector = " "
            return f"{t_word}{connector}{self._number_to_words(remainder)}"

        return str(n)
