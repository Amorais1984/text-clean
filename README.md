# VoxText Engine

> Pré-processador avançado de texto para TTS — converte conteúdo bruto em texto estruturado, fluido e pronto para síntese de voz.

---

## 📌 Visão Geral

O **VoxText Engine** é um sistema especializado em pré-processamento linguístico e estrutural, projetado para preparar textos para motores de Text-to-Speech (TTS).

Diferente de soluções convencionais, o foco **não é gerar áudio**, mas sim entregar uma camada intermediária de alta qualidade, resolvendo problemas comuns como:

- Texto mal formatado (PDFs, OCR)
- Falta de fluidez para leitura em voz
- Ambiguidade semântica
- Ausência de marcações SSML

O resultado é um texto natural, inteligível e otimizado para fala, independente da engine utilizada.

---

## 🧠 Arquitetura

O sistema opera como um **pipeline modular** de processamento, dividido em estágios desacoplados:

```
📂 Input (PDF/TXT)
 ↓
Parser ─────────── Extração de conteúdo com layout awareness
 ↓
Cleaner ────────── Remoção de ruído estrutural
 ↓
Semantic Engine ── Adaptação para linguagem falada
 ↓
Normalizer ─────── Expansão linguística PT-BR
 ↓
TTS Optimizer ──── Inserção de pausas e SSML
 ↓
Segmenter ──────── Quebra inteligente em blocos
 ↓
💾 Export (TXT/JSON/SSML)

Pós-processamento opcional:
 ↓
✂️ Text Splitter ── Divisão por limite de caracteres
```

Cada estágio é uma classe independente (`PipelineStage` ABC), testável isoladamente e extensível sem alterar o pipeline existente.

---

## ✨ Funcionalidades

### 📥 Importação de Conteúdo
- **PDF** — extração via `pdfplumber` com detecção de colunas
- **TXT** — detecção automática de encoding via `chardet`
- Preparado para expansão (DOCX, HTML)

### 🧹 Limpeza Estrutural
- Remoção de cabeçalhos e rodapés repetidos (heurística de frequência)
- Eliminação de numeração de páginas (múltiplos formatos)
- Remoção de artefatos de OCR
- Normalização Unicode (NFC) e caracteres de controle
- Reconstrução automática de parágrafos quebrados por formatação PDF
- Reconstrução de palavras hifenizadas entre linhas

### 🔄 Reestruturação Semântica
- Conversão de listas (bullet, numerada, letras) em narrativa sequencial
- Detecção e preservação de headings
- Exemplo: `- CPU / - RAM / - SSD` → *"Os principais itens são: CPU, RAM e SSD."*

### 🗣️ Normalização Linguística (PT-BR)
| Tipo | Entrada | Saída |
|------|---------|-------|
| Números | `123` | `cento e vinte e três` |
| Datas | `28/04/2026` | `vinte e oito de abril de dois mil e vinte e seis` |
| Moedas | `R$ 1.500,00` | `mil e quinhentos reais` |
| Percentuais | `15%` | `quinze por cento` |
| Horários | `14:30` | `quatorze horas e trinta minutos` |
| Ordinais | `1º` | `primeiro` |
| Abreviações | `Dr.`, `Sr.`, `pág.` | `Doutor`, `Senhor`, `página` |
| Unidades | `kg`, `km/h` | `quilogramas`, `quilômetros por hora` |

- Dicionário extenso com 80+ abreviações PT-BR
- Matching seguro via regex com word boundaries
- Abreviações customizáveis pelo usuário

### ⏸️ Otimização para TTS
- Inserção de pausas via SSML calibradas por modo de otimização:
  - vírgula → 175–375ms | ponto → 350–750ms | seção → 560–1200ms
- Geração de SSML completo com `<speak>`, `<break>`, `<p>`
- Compatível com Azure TTS, Google TTS, ElevenLabs e qualquer engine SSML

### ✂️ Segmentação Inteligente
- Blocos de 200–500 caracteres (configurável)
- Respeita fronteiras de sentença (nunca corta no meio)
- Ideal para streaming ou processamento incremental

### ✂️ Divisor de Texto por Limite de Caracteres
- Divide o texto processado em partes de **tamanho máximo configurável**
- **Corte inteligente**: sempre no último ponto final (`.`) antes do limite
- Hierarquia de fallback: `.` → `!` `?` → `;` → espaço
- Preservação integral de sentenças
- **Diálogo dedicado** com:
  - Campo para definir limite de caracteres
  - Preview navegável de cada parte (◀ ▶)
  - Contagem de caracteres e palavras por parte
  - Exportação em lote como arquivos individuais (`parte_001.txt`, `parte_002.txt`, ...)

### 💾 Exportação
| Formato | Descrição |
|---------|-----------|
| **TXT** | Texto limpo sem marcações, UTF-8 |
| **JSON** | Estrutura completa com metadados, segmentos e estatísticas |
| **SSML** | Documento XML com `<speak>`, `<break>`, `<p>` |
| **Lote** | Partes divididas como arquivos TXT individuais |

### 🎛️ Modos de Otimização

| Modo | Característica | Pausas | Uso Ideal |
|------|----------------|--------|-----------|
| **Acadêmico** | Formal, pausas longas | +50% | Aulas, artigos |
| **Natural** | Equilíbrio (padrão) | Base | Uso geral |
| **Compacto** | Direto, menos pausas | -30% | Conteúdo dinâmico |

---

## 🖥️ Interface Gráfica

A interface utiliza **Tkinter + ttkbootstrap** com tema dark (`darkly`):

- **Split-view**: texto original (esquerda) | texto processado (direita, editável)
- **Syntax highlighting** para tags SSML (cores Catppuccin Mocha)
- **Numeração de linhas** e estatísticas em tempo real
- **Barra de progresso** durante processamento
- **Processamento em thread** separada (GUI não trava)
- **Diálogo de divisão** com preview e navegação entre partes

### Atalhos de Teclado

| Atalho | Ação |
|--------|------|
| `Ctrl+O` | Importar arquivo |
| `F5` | Processar |
| `Ctrl+S` | Exportar |
| `Ctrl+D` | Dividir texto |

---

## 🚀 Instalação

```bash
# Clone o repositório
git clone https://github.com/Amorais1984/text-clean.git

# Acesse a pasta
cd text-clean

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac

# Instale as dependências
pip install -r requirements.txt
```

## ▶️ Execução

```bash
python run.py
```

## 🧪 Testes

```bash
python -m pytest tests/ -v
```

> 29 testes automatizados cobrindo todos os módulos: Cleaner, Normalizer, Semantic Engine, TTS Optimizer, Pipeline de integração, Text Splitter e Exportadores.

---

## 📁 Estrutura do Projeto

```
text-clean/
├── run.py                      # Entry point
├── pyproject.toml              # Metadados e dependências
├── requirements.txt            # Dependências (pip)
├── PRD.md                      # Product Requirements Document
├── voxtext/
│   ├── app.py                  # Orquestrador principal
│   ├── text_splitter.py        # Divisor de texto por limite de chars
│   ├── pipeline/
│   │   ├── base.py             # PipelineStage ABC + Pipeline runner
│   │   ├── parser.py           # Extração (PDF/TXT)
│   │   ├── cleaner.py          # Limpeza estrutural
│   │   ├── semantic_engine.py  # Reestruturação semântica
│   │   ├── normalizer.py       # Normalização PT-BR
│   │   ├── tts_optimizer.py    # SSML + pausas
│   │   └── segmenter.py        # Segmentação inteligente
│   ├── exporters/
│   │   ├── txt_exporter.py     # Exportação TXT
│   │   ├── json_exporter.py    # Exportação JSON
│   │   └── ssml_exporter.py    # Exportação SSML
│   ├── config/
│   │   ├── settings.py         # Modos e configurações
│   │   └── abbreviations.py    # Dicionário PT-BR (80+ entradas)
│   ├── models/
│   │   └── document.py         # Dataclasses (Document, Segment, etc.)
│   └── gui/
│       ├── main_window.py      # Janela principal (split-view)
│       ├── editor_panel.py     # Editor com syntax highlight
│       ├── toolbar.py          # Barra de ferramentas
│       └── dialogs.py          # Diálogos (Export, Split, About)
└── tests/
    ├── test_pipeline.py        # 19 testes (pipeline + módulos)
    └── test_splitter.py        # 10 testes (divisor de texto)
```

---

## 🔧 Roadmap

- [x] Importação PDF e TXT
- [x] Extração inteligente (cabeçalhos, rodapés, hifenização)
- [x] Limpeza estrutural completa
- [x] Reestruturação semântica (listas → narrativa)
- [x] Normalização linguística PT-BR completa
- [x] Segmentação inteligente
- [x] SSML com pausas calibradas por modo
- [x] 3 modos de otimização
- [x] Exportação TXT, JSON, SSML
- [x] GUI completa com split-view e tema dark
- [x] Divisor de texto por limite de caracteres
- [ ] Suporte a DOCX e HTML
- [ ] API REST (FastAPI)
- [ ] CLI avançada
- [ ] Plugins de normalização por idioma
- [ ] Integração opcional com engines TTS
- [ ] Dashboard de análise de qualidade

---

## 🤝 Contribuição

Contribuições são bem-vindas. Para colaborar:

1. Fork do projeto
2. Crie uma branch (`feature/nova-feature`)
3. Commit (`git commit -m 'feat: nova feature'`)
4. Push (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📜 Licença

Distribuído sob licença MIT.

---

## ⚖️ Diferencial Estratégico

Esse projeto atua na camada que a maioria ignora — o **pré-processamento de linguagem para TTS**, onde ocorre a maior perda de qualidade perceptiva.

Se evoluído corretamente (principalmente com API e suporte multilíngue), isso deixa de ser apenas uma ferramenta e passa a ser um **componente reutilizável de alto valor** em pipelines de IA e voz.