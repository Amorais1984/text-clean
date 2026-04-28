"""
Dicionário de abreviações e unidades para português brasileiro.

Usado pelo Normalizer para expandir abreviações comuns em texto por extenso,
melhorando a naturalidade da leitura por motores TTS.
"""

# Abreviações comuns em português brasileiro
ABBREVIATIONS: dict[str, str] = {
    # Títulos e tratamentos
    "Dr.": "Doutor",
    "Dra.": "Doutora",
    "Sr.": "Senhor",
    "Sra.": "Senhora",
    "Srta.": "Senhorita",
    "Prof.": "Professor",
    "Profa.": "Professora",
    "Eng.": "Engenheiro",
    "Adv.": "Advogado",

    # Endereços
    "Av.": "Avenida",
    "R.": "Rua",
    "Pça.": "Praça",
    "Al.": "Alameda",
    "Trav.": "Travessa",
    "Rod.": "Rodovia",
    "Cj.": "Conjunto",
    "Ed.": "Edifício",
    "Apt.": "Apartamento",
    "Apto.": "Apartamento",

    # Referências textuais
    "pág.": "página",
    "págs.": "páginas",
    "p.": "página",
    "pp.": "páginas",
    "cap.": "capítulo",
    "fig.": "figura",
    "figs.": "figuras",
    "tab.": "tabela",
    "tabs.": "tabelas",
    "vol.": "volume",
    "vols.": "volumes",
    "ed.": "edição",
    "n.": "número",
    "nº": "número",
    "nºs": "números",
    "obs.": "observação",
    "ex.": "exemplo",
    "ref.": "referência",

    # Organizações e termos jurídicos
    "Ltda.": "Limitada",
    "S.A.": "Sociedade Anônima",
    "Cia.": "Companhia",
    "Inc.": "Incorporada",
    "Gov.": "Governo",
    "Min.": "Ministério",
    "Depto.": "Departamento",
    "Dept.": "Departamento",
    "Sec.": "Secretaria",

    # Tempo
    "seg.": "segunda-feira",
    "ter.": "terça-feira",
    "qua.": "quarta-feira",
    "qui.": "quinta-feira",
    "sex.": "sexta-feira",
    "sáb.": "sábado",
    "dom.": "domingo",
    "jan.": "janeiro",
    "fev.": "fevereiro",
    "mar.": "março",
    "abr.": "abril",
    "mai.": "maio",
    "jun.": "junho",
    "jul.": "julho",
    "ago.": "agosto",
    "set.": "setembro",
    "out.": "outubro",
    "nov.": "novembro",
    "dez.": "dezembro",


    # Diversos
    "etc.": "etcétera",
    "aprox.": "aproximadamente",
    "máx.": "máximo",
    "mín.": "mínimo",
    "qtd.": "quantidade",
    "qtde.": "quantidade",
    "tel.": "telefone",
    "cel.": "celular",
    "c/": "com",
    "s/": "sem",
    "p/": "para",
}


# Unidades de medida
UNITS: dict[str, str] = {
    # Comprimento
    "mm": "milímetros",
    "cm": "centímetros",
    "m": "metros",
    "km": "quilômetros",
    "mi": "milhas",
    "in": "polegadas",
    "ft": "pés",
    "yd": "jardas",

    # Massa
    "mg": "miligramas",
    "g": "gramas",
    "kg": "quilogramas",
    "t": "toneladas",
    "lb": "libras",
    "oz": "onças",

    # Volume
    "ml": "mililitros",
    "l": "litros",
    "L": "litros",

    # Área
    "m²": "metros quadrados",
    "km²": "quilômetros quadrados",
    "ha": "hectares",

    # Velocidade
    "km/h": "quilômetros por hora",
    "m/s": "metros por segundo",
    "mph": "milhas por hora",

    # Temperatura
    "°C": "graus Celsius",
    "°F": "graus Fahrenheit",
    "K": "Kelvin",

    # Informática
    "B": "bytes",
    "KB": "quilobytes",
    "MB": "megabytes",
    "GB": "gigabytes",
    "TB": "terabytes",
    "Hz": "hertz",
    "MHz": "megahertz",
    "GHz": "gigahertz",

    # Elétrica
    "V": "volts",
    "W": "watts",
    "kW": "quilowatts",
    "A": "ampères",
    "mA": "miliampères",
    "Ω": "ohms",
}


# Símbolos matemáticos e especiais
SYMBOLS: dict[str, str] = {
    "%": "por cento",
    "‰": "por mil",
    "+": "mais",
    "-": "menos",
    "×": "vezes",
    "÷": "dividido por",
    "=": "igual a",
    "≠": "diferente de",
    "<": "menor que",
    ">": "maior que",
    "≤": "menor ou igual a",
    "≥": "maior ou igual a",
    "±": "mais ou menos",
    "√": "raiz quadrada de",
    "∞": "infinito",
    "&": "e",
    "@": "arroba",
    "§": "parágrafo",
    "©": "copyright",
    "®": "marca registrada",
    "™": "trademark",
}
