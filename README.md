VoxText Engine

Pré-processador avançado de texto para TTS — converte conteúdo bruto em texto estruturado, fluido e pronto para síntese de voz.

📌 Visão Geral

O VoxText Engine é um sistema especializado em pré-processamento linguístico e estrutural, projetado para preparar textos para motores de Text-to-Speech (TTS).

Diferente de soluções convencionais, o foco não é gerar áudio, mas sim entregar uma camada intermediária de alta qualidade, resolvendo problemas comuns como:

Texto mal formatado (PDFs, OCR)
Falta de fluidez para leitura em voz
Ambiguidade semântica
Ausência de marcações SSML

O resultado é um texto natural, inteligível e otimizado para fala, independente da engine utilizada.

🧠 Arquitetura Conceitual

O sistema opera como um pipeline modular de processamento, dividido em estágios bem definidos:

Parsing → Extração de conteúdo (PDF/TXT)
Cleaning → Remoção de ruído estrutural
Semantic Restructuring → Adaptação para linguagem falada
Normalization (PT-BR) → Expansão linguística
TTS Optimization → Inserção de pausas e SSML
Segmentation → Quebra inteligente em blocos

Essa abordagem permite extensibilidade, testes isolados e evolução incremental.

✨ Funcionalidades
📥 Entrada de Dados
Importação de arquivos PDF (com detecção de colunas)
Suporte a TXT
Preparado para expansão (HTML, DOCX)
🧹 Limpeza Estrutural
Remoção de:
Cabeçalhos e rodapés repetidos
Numeração de páginas
Artefatos de OCR
Reconstrução automática de parágrafos
🔄 Reestruturação Semântica
Conversão de listas em narrativa contínua
Ajuste de pontuação para fala
Redução de ambiguidade sintática
🗣️ Normalização Linguística (PT-BR)
Números → “123” → “cento e vinte e três”
Datas → “12/05/2024” → forma falada
Moedas → “R$ 50,00”
Percentuais, horários e abreviações
⏸️ Otimização para TTS
Inserção de pausas via SSML
Ajuste de ritmo e cadência
Preparação para engines como:
Azure TTS
Google TTS
ElevenLabs
✂️ Segmentação Inteligente
Blocos de 200 a 500 caracteres
Respeito a fronteiras semânticas
Ideal para streaming ou processamento incremental
💾 Exportação
Texto limpo (.txt)
Estrutura completa (.json)
SSML pronto para TTS
🎛️ Modos de Otimização
Modo	Característica	Uso Ideal
Acadêmico	Formal, pausas mais longas	Aulas, artigos
Natural	Equilíbrio entre fluidez e clareza	Uso geral (padrão)
Compacto	Mais direto, menos pausas	Conteúdo dinâmico
🚀 Instalação
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
▶️ Execução
python run.py
🧪 Testes
pytest tests/ -v
📁 Estrutura do Projeto
text-clean/
├── run.py
├── voxtext/
│   ├── app.py                  # Orquestrador principal
│   ├── pipeline/
│   │   ├── parser.py           # Extração (PDF/TXT)
│   │   ├── cleaner.py          # Limpeza estrutural
│   │   ├── semantic_engine.py  # Reestruturação semântica
│   │   ├── normalizer.py       # Normalização PT-BR
│   │   ├── tts_optimizer.py    # SSML + pausas
│   │   └── segmenter.py        # Segmentação inteligente
│   ├── exporters/              # Exportadores (TXT, JSON, SSML)
│   ├── config/                 # Configurações e regras
│   ├── models/                 # Estruturas de dados
│   └── gui/                    # Interface Tkinter
└── tests/
🖥️ Interface

O projeto inclui uma interface gráfica simples utilizando Tkinter, permitindo:

Importar arquivos
Selecionar modo de otimização
Visualizar saída processada
Exportar resultados
🔧 Roadmap
 Suporte a DOCX e HTML
 API REST (FastAPI)
 CLI avançada
 Plugins de normalização por idioma
 Integração opcional com engines TTS
 Dashboard de análise de qualidade do texto
🤝 Contribuição

Contribuições são bem-vindas. Para colaborar:

Fork do projeto
Crie uma branch (feature/nova-feature)
Commit (git commit -m 'feat: nova feature')
Push (git push origin feature/nova-feature)
Abra um Pull Request
📜 Licença

Distribuído sob licença MIT.

⚖️ Opinião Técnica

Esse tipo de projeto tem um diferencial estratégico forte: ele atua exatamente na camada que a maioria ignora — o pré-processamento de linguagem para TTS, que é onde ocorre a maior perda de qualidade perceptiva.

Se evoluído corretamente (principalmente com API e suporte multilíngue), isso deixa de ser apenas uma ferramenta e passa a ser um componente reutilizável de alto valor em pipelines de IA e voz.