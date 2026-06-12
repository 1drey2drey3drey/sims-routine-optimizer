# 🎮 Sims Routine Optimizer
## Otimização de Rotina Diária com Computação Evolutiva

---

### Slide 1: Capa e Equipe

* **Título:** Sims Routine Optimizer  
* **Subtítulo:** Otimização de rotina de 24 horas usando Algoritmo Genético (AG) e Enxame de Partículas (PSO)
* **Equipe CC5MA:**
  * Andrey Lourival Andrade Garcia
  * Everton de Oliveira da Silva
  * Filipe César Maciel Sucupira
  * Igor Cecim Vilhena
* **Instituição:** CESUPA — Semestre 01/2026 — Disciplina: Inteligência Artificial e Computacional  
* **Professor:** Daniel Leal Souza  

---

### Slide 2: Descrição do Problema e Motivação

* **Objetivo:** Encontrar a agenda diária de 24 horas ideal (dividida em 48 blocos de 30 minutos) que maximiza o bem-estar (felicidade) de um Sim, equilibrando suas necessidades biológicas e sociais.
* **Entradas (Configuração do Sim):**
  * **Perfil do Sim:** Nome e intensidade (`[0.0, 1.0]`) de 9 traços de personalidade (*Workaholic*, *Introvertido*, *Extrovertido*, *Criativo*, *Preguiçoso*, *Ativo*, *Gastronômico* (ex-gourmet), *Sociável* e *Solitário*).
  * **Parâmetros dos Algoritmos:** Semente aleatória, tamanho da população/enxame, número de gerações/iterações, taxas de crossover/mutação.
* **Complexidade:** Com 20 atividades possíveis e 48 blocos diários, o espaço de busca possui **20⁴⁸ combinações possíveis** (aproximadamente 2.81 × 10⁶²), inviabilizando busca exaustiva (força bruta).

---

### Slide 3: Modelagem e Espaço de Busca

* **Representação (Cromossomo / Partícula):**
  * Vetor unidimensional de 48 genes (bloco de 30 min = 24 h).
  * Cada elemento do vetor armazena o identificador de uma das 20 atividades disponíveis (ex: `dormir`, `trabalhar`, `comer_refeicao`).
* **Filtro de Reparo de Consistência (Crítico):**
  * As atividades possuem durações contíguas mínimas (ex: `trabalho` exige 16 blocos contíguos de 30 min/8h, `dormir` exige blocos contíguos mínimos).
  * Um operador de reparo varre a sequência e reconstrói blocos quebrados ou inconsistentes para manter a rotina estruturalmente viável.
* **Função de Aptidão (Fitness):**
  * $\text{Fitness} = \text{Felicidade Acumulada} + \text{Bônus de Variedade} - \text{Penalidades} + (10 \times \text{Felicidade Média})$
  * A felicidade é calculada com base no impacto das necessidades ponderado pelos traços de personalidade.
  * Penalidades severas são aplicadas por privação de necessidades básicas (fome e energia < -50) ou inconsistências de cronograma.
  * O termo de Felicidade Média Diária garante alinhamento estrito entre a otimização de fitness e o bem-estar do Sim.

---

### Slide 4: Motor de Otimização 1 — Algoritmo Genético (AG)

* **Representação:** População de 80 cronogramas diários (indivíduos).
* **Seleção:** Torneio binário estocástico com tamanho $k=3$ para equilibrar pressão seletiva e manter diversidade genética.
* **Crossover (Recombinação):** Crossover de um ponto, trocando fatias temporais de agendas entre dois pais, seguido do filtro de reparo de consistência.
* **Mutação:** Mutação por substituição aleatória de blocos de atividades no cromossomo, seguida de reparo subsequente para manter a consistência da agenda.
* **Elitismo:** Preservação direta dos 2 melhores indivíduos de cada geração para a população seguinte.

---

### Slide 5: Motor de Otimização 2 — Enxame de Partículas (PSO)

* **Abordagem de Inteligência Coletiva:**
  * Mapeamento do cronograma diário (vetor discreto de atividades) para posições e velocidades em um espaço multidimensional.
  * Cada partícula mantém memória do seu melhor resultado individual histórico (*pbest*) e do melhor resultado global obtido por todo o enxame (*gbest*).
* **Atualização de Posição e Velocidade:**
  * As partículas se deslocam pelo espaço de busca ajustando suas posições em direção à melhor solução histórica pessoal e do grupo.
  * Convergência tipicamente rápida e excelente explotação de ótimos locais.

---

### Slide 6: Parâmetros Configurados (AG e PSO)

| Parâmetro | Valor Padrão (AG) | Valor Padrão (PSO) | Justificativa Técnica |
|---|---|---|---|
| **Tamanho da População / Enxame** | 80 indivíduos | 80 partículas | Diversidade de busca com ótimo tempo de processamento (~1.0s). |
| **Gerações / Iterações** | 150 gerações | 150 iterações | Limite estável; convergência observada empiricamente antes de 120 passos. |
| **Taxa de Crossover** | 85% | N/A | Alta recombinação promove exploração estruturada do espaço. |
| **Taxa de Mutação** | 12% | N/A | Introduz diversidade para escapar de ótimos locais sem destruir o progresso. |
| **Elitismo** | 2 indivíduos | N/A | Preserva as melhores soluções obtidas sem perda de material genético. |
| **Fatores Inercial e Cognitivos** | N/A | w=0.7, c1=1.5, c2=1.5 | Equilíbrio clássico para convergência de enxame. |
| **Semente Aleatória** | 42 | 42 | Garante reprodutibilidade científica de todas as rodadas. |

---

### Slide 7: Validação Estatística e Resultados (5 Sementes)

Resultados consolidados em 5 execuções independentes (sementes `42, 7, 123, 999, 2024`) para 4 perfis distintos frente ao baseline aleatório:

| Perfil | Fitness AG (Média ± DP) | Fitness PSO (Média ± DP) | Fitness Baseline (Média) | Felicidade Média (AG / PSO) | Vencedor Geral |
|---|---|---|---|---|---|
| **Workaholic** | 1304.14 ± 25.70 | 1305.28 ± 9.02 | 0.00 | 63.7% / 63.6% | **PSO** |
| **Social** | 1819.04 ± 45.80 | 1802.37 ± 63.91 | 0.00 | 62.9% / 63.6% | **AG** |
| **Criativo** | 1333.76 ± 18.46 | 1338.19 ± 10.35 | 0.00 | 64.0% / 64.1% | **PSO** |
| **Equilibrado** | 1470.23 ± 21.24 | 1487.77 ± 14.74 | 0.00 | 64.3% / 63.3% | **PSO** |

* **Saídas da Otimização:**
  * Rotina diária detalhada em gráfico de Gantt e tabela interativa.
  * Estado final das 8 necessidades HUD (escala -100 a +100) e gráfico radar.
  * Curvas de convergência da busca (unificada e individual por perfil).
  * Arquivos de exportação prontos em formato CSV e Relatórios HTML.

---

### Slide 8: Arquitetura Modular e Conclusões

* **Estrutura de Código Desacoplada (Nova Organização):**
  * `app.py`: Dashboard Streamlit principal na raiz do repositório.
  * `src/`: Pasta contendo a lógica de negócio encapsulada como pacote Python.
    * `src/genetic_algorithm.py` / `src/pso.py`: Motores evolutivos/heurísticos de busca.
    * `src/fitness.py`: Motor de simulação biológica e cálculo de aptidão.
    * `src/activities.py` / `src/sim.py`: Modelos de atividades e dados dos Sims.
    * `src/export.py`: Funções de formatação e exportação CSV/HTML.
  * `tests/test_runs.py`: Suite de validação científica automatizada.
* **Conclusões:**
  * Tanto o AG quanto o PSO superam drasticamente a rotina aleatória baseline.
  * O PSO demonstra excelente convergência para perfis com objetivos individuais de alta intensidade (como *Workaholic* e *Criativo*).
  * O AG apresenta maior estabilidade e menor desvio padrão para rotinas com dinâmicas sociais mais densas (como o perfil *Social*).
  * O sistema atende plenamente aos requisitos, gerando agendas consistentes de forma instantânea.
