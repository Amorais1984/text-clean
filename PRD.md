PRD — Sistema de Organização de Texto para TTS (Sem Geração de Áudio)

1. Visão Geral do Produto
1.1 Nome do Produto

VoxText Engine

1.2 Proposta de Valor

Transformar textos brutos em versões estruturalmente e linguisticamente otimizadas para síntese de fala, prontas para consumo por qualquer motor de TTS.

1.3 Problema

Motores de TTS recebem texto inadequado porque:

estrutura textual é visual (não auditiva)
PDFs são semanticamente pobres
linguagem escrita ≠ linguagem falada
ausência de marcações de prosódia
1.4 Solução

Um sistema que:

extrai conteúdo corretamente
reorganiza a estrutura semântica
adapta linguagem para fala
aplica marcações SSML
divide texto em partes controladas
exporta texto pronto para TTS
2. Objetivos do Produto
2.1 Objetivo Principal

Produzir texto otimizado para escuta, independente do motor de TTS utilizado posteriormente.

2.2 Objetivos Secundários
padronizar entrada para pipelines de voz
reduzir necessidade de edição manual
aumentar naturalidade percebida
servir como middleware para sistemas TTS
3. Público-Alvo
Primário
desenvolvedores de sistemas TTS
criadores de conteúdo educacional
empresas de acessibilidade
Secundário
estudantes
produtores de audiobooks
edtechs
4. Funcionalidades (Core Features)
4.1 Importação de Conteúdo
Suporte:
PDF (prioritário) — com pdfplumber
TXT — com detecção automática de encoding (chardet)
DOCX (fase futura)
HTML (fase futura)
4.2 Extração Inteligente de Texto
Funções:
remoção de cabeçalhos/rodapés repetidos (heurística de frequência)
eliminação de numeração de páginas (múltiplos formatos)
reconstrução de palavras hifenizadas entre linhas
detecção de colunas
Estratégia:
análise de repetição de padrões (Counter com threshold 50%)
heurísticas de layout via pdfplumber
4.3 Limpeza Estrutural
normalização Unicode (NFC)
remoção de caracteres de controle
normalização de espaços e tabs
remoção de artefatos de OCR
reconstrução de parágrafos quebrados por formatação PDF
colapso de linhas em branco excessivas
4.4 Reestruturação Semântica
Transformações:
listas (bullet, numerada, letras) → narrativa sequencial
blocos longos → segmentação respeitando sentenças
Exemplo:
Entrada:
- CPU
- RAM
- SSD

Saída:
"Os principais componentes são: CPU, RAM e SSD."
4.5 Normalização Linguística (PT-BR)
Conversões implementadas:
números → por extenso (até 999.999, implementação nativa sem dependência externa)
datas → forma falada (28/04/2026 → "vinte e oito de abril de dois mil e vinte e seis")
moedas → leitura natural (R$ 1.500,00 → "mil e quinhentos reais"; US$ suportado)
abreviações → expansão configurável (dicionário extenso PT-BR com 80+ entradas)
percentuais → forma falada (15% → "quinze por cento")
ordinais → por extenso (1º → "primeiro")
horários → forma falada (14:30 → "quatorze horas e trinta minutos")
unidades de medida → por extenso (kg → "quilogramas", km/h → "quilômetros por hora")
Matching seguro:
regex com word boundaries para evitar substituições parciais
ordenação por comprimento decrescente para priorizar matches mais longos
4.6 Otimização para TTS
Inserção de pausas SSML calibradas por modo:
vírgula → pausa curta (175–375ms conforme modo)
ponto → pausa média (350–750ms conforme modo)
seção → pausa longa (560–1200ms conforme modo)
ponto e vírgula / dois pontos → pausa curta
Saída:
texto enriquecido com marcações
SSML completo com <speak>, <break>, <p>

Exemplo:

<speak>
Introdução.
<break time="500ms"/>
Agora o conteúdo principal.
</speak>
4.7 Segmentação Inteligente
Regras:
blocos de 200–500 caracteres (configurável via Settings)
nunca quebra no meio de uma sentença
respeita limites de sentença via regex
mantém coerência semântica
4.8 Divisão de Texto por Limite de Caracteres ✂️ [NOVO]
Funcionalidade:
divisão do texto processado em partes de tamanho máximo configurável
corte sempre no último ponto final (.) antes do limite
preservação integral de sentenças — nunca corta no meio de uma frase
Algoritmo de corte (prioridade):
1. último ponto final (.) antes do limite
2. último ! ou ? se não houver ponto
3. último ; como fallback
4. último espaço em último caso
Interface:
diálogo dedicado (✂️ Dividir) com campo para limite de caracteres
preview navegável de cada parte (◀ ▶) com contagem de caracteres e palavras
exportação de todas as partes como arquivos individuais (parte_001.txt, parte_002.txt, ...)
informações do texto original (total de caracteres e palavras)
Acesso:
botão ✂️ Dividir na toolbar (habilitado após processamento)
menu Processar → Dividir Texto
atalho de teclado Ctrl+D
4.9 Exportação
Formatos:
TXT limpo (texto sem marcações, UTF-8)
JSON estruturado (metadados + segmentos + stats)
SSML (documento XML completo com <speak>, <break>, <p>)
Exportação em lote (partes divididas como arquivos individuais)
Markdown (fase futura)
4.10 Interface de Usuário
Funcionalidades implementadas:
upload de arquivo (PDF, TXT) via diálogo ou Ctrl+O
visualização split-view:
texto original (esquerda, somente leitura)
texto processado (direita, editável)
edição manual do texto processado
syntax highlighting para tags SSML (cores Catppuccin Mocha)
numeração de linhas
estatísticas em tempo real (caracteres, palavras, linhas)
exportação via diálogo com seleção de formato
divisão de texto com preview e exportação em lote [NOVO]
barra de progresso durante processamento
processamento em thread separada (GUI não trava)
Tema:
ttkbootstrap "darkly" (dark mode)
cores Catppuccin Mocha nos editores
4.11 Editor Avançado

Permitir:

ajuste de pausas (SSML)
edição de estrutura
marcação de ênfase
4.12 Modos de Otimização
Acadêmico — mais pausas (+50%), mais formal
Natural — equilibrado (padrão)
Compacto — mais direto, menos pausas (-30%)

Cada modo ajusta automaticamente todas as durações de pausa SSML.
5. Arquitetura do Sistema
5.1 Pipeline
Entrada
 ↓
Parser (PDF/TXT)
 ↓
Cleaner
 ↓
Semantic Engine
 ↓
Normalizer (PT-BR)
 ↓
TTS Optimizer (SSML)
 ↓
Segmenter
 ↓
Exporter (TXT/JSON/SSML)

Pós-processamento opcional:
 ↓
Text Splitter (divisão por limite de caracteres) [NOVO]
5.2 Componentes
Parser
leitura de arquivos (PDF via pdfplumber, TXT via chardet)
detecção de cabeçalhos/rodapés, reconstrução de hifenização
Cleaner
normalização Unicode, remoção de ruído, reconstrução de parágrafos
Semantic Engine
conversão de listas para narrativa, detecção de headings
Normalizer
normalização linguística PT-BR (números, datas, moedas, abreviações, horários, ordinais, percentuais)
TTS Optimizer
inserção de pausas SSML calibradas por modo de otimização
Segmenter
divisão em blocos de 200-500 chars respeitando sentenças
Text Splitter [NOVO]
divisão do texto final em partes de tamanho configurável
corte sempre em ponto final para preservar sentenças
Exporter
geração de saída em TXT, JSON e SSML
exportação em lote de partes divididas
5.3 Tecnologias
Backend
Python 3.10+
NLP
Normalização nativa PT-BR (sem dependência de spaCy para MVP)
num2words (disponível como dependência, mas normalização de números implementada nativamente)
PDF
pdfplumber (extração com layout awareness)
chardet (detecção de encoding)
Interface
Tkinter + ttkbootstrap (tema darkly)
Padrão Arquitetural
Pipeline (Chain of Responsibility) — estágios desacoplados e extensíveis
PipelineStage ABC + Pipeline runner com callbacks de progresso
6. Requisitos Funcionais
importar arquivos (PDF, TXT)
extrair texto corretamente (com remoção de cabeçalhos/rodapés e hifenização)
limpar ruído (Unicode, OCR, espaços, parágrafos)
reorganizar estrutura (listas → narrativa)
normalizar linguagem (números, datas, moedas, abreviações, horários, ordinais, percentuais)
inserir pausas SSML (calibradas por modo)
segmentar texto (200-500 chars)
dividir texto em partes configuráveis (corte em ponto final) [NOVO]
exportar em múltiplos formatos (TXT, JSON, SSML)
exportar partes divididas como arquivos individuais [NOVO]
7. Requisitos Não Funcionais
Performance
processamento de 100 páginas em < 10s (meta inicial)
Modularidade
pipeline desacoplado (cada estágio é independente e testável)
Extensibilidade
suporte a novos formatos (DOCX, HTML) via ParserFactory
novos estágios adicionáveis sem alterar o pipeline existente
Usabilidade
interface clara com split-view e tema dark
atalhos de teclado (Ctrl+O, F5, Ctrl+S, Ctrl+D)
feedback de progresso durante processamento
Testabilidade
suite de testes automatizados (29 testes cobrindo todos os módulos)
8. Métricas de Sucesso
redução de edição manual (%)
tempo de processamento
qualidade percebida do texto (avaliação humana)
adoção por desenvolvedores
9. Roadmap
Fase 1 — MVP ✅ CONCLUÍDA
importação PDF e TXT
extração inteligente (cabeçalhos, rodapés, hifenização)
limpeza estrutural completa
exportação TXT
Fase 2 ✅ CONCLUÍDA
normalização linguística PT-BR completa
segmentação inteligente
reestruturação semântica (listas → narrativa)
Fase 3 ✅ CONCLUÍDA
SSML com pausas calibradas
3 modos de otimização (Acadêmico, Natural, Compacto)
exportação JSON e SSML
GUI completa com split-view, editor e tema dark
Fase 3.1 ✅ CONCLUÍDA [NOVO]
divisor de texto por limite de caracteres
corte inteligente em ponto final
diálogo dedicado com preview e navegação
exportação em lote de partes individuais
Fase 4
editor avançado de SSML (drag & drop de pausas)
importação DOCX
Fase 5
aprendizado adaptativo
importação HTML
API REST
10. Riscos
ambiguidade linguística
PDFs mal estruturados
excesso de heurísticas rígidas
variação de estilos de texto
11. Diferencial Estratégico

O produto deixa de ser um "gerador de áudio" e passa a ser:

👉 Infraestrutura linguística para TTS

Isso permite:

integração com qualquer motor
uso como API
posicionamento B2B forte
12. Expansões Futuras
API REST para integração
suporte multilíngue
plugins para editores
integração com pipelines de IA
divisão avançada com controle por sentenças, parágrafos ou seções
Conclusão

Essa versão do produto é mais sólida do ponto de vista técnico e comercial.

Você está criando:

um pré-processador inteligente de linguagem
com potencial de virar padrão dentro de pipelines de voz

---

Status de Implementação: Fases 1, 2, 3 e 3.1 concluídas.
29 testes automatizados passando.
GUI desktop funcional com tema dark e todas as funcionalidades operacionais.