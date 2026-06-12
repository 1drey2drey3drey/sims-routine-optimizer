# 🎮 Sims Routine Optimizer

> Otimização de rotina diária inspirada em *The Sims* usando **Algoritmo Genético**.

**Disciplina:** Inteligência Artificial e Computacional (0700M8)  
**Professor:** Daniel Leal Souza — CESUPA, Semestre 01/2026  
**Equipe:** Andrey Lourival Andrade Garcia | Everton de Oliveira da Silva  | Filipe César Maciel Sucupira  | Igor Cecim Vilhena

---

## 📌 Problema

Dado um Sim com **traços de personalidade** (workaholic, introvertido, extrovertido, criativo, preguiçoso, ativo, gastronômico, sociável, solitário), encontrar a **rotina diária de 24 horas** que **maximiza a felicidade** do personagem, equilibrando as 8 necessidades do jogo:

| Necessidade | Peso |
|-------------|------|
| Fome        | 20%  |
| Energia     | 20%  |
| Diversão    | 15%  |
| Social      | 15%  |
| Higiene     | 10%  |
| Banheiro    | 10%  |
| Conforto    |  5%  |
| Ambiente    |  5%  |

**Público-alvo:** estudantes e entusiastas de jogos de simulação de vida que queiram entender como algoritmos evolutivos podem otimizar decisões de planejamento diário.

---

## 🧬 Algoritmo Genético

| Componente | Detalhe |
|---|---|
| **Cromossomo** | Lista de 48 genes (blocos de 30 min = 24 h) |
| **Gene** | Nome de uma atividade (ex: `"dormir"`, `"videogame"`) |
| **Seleção** | Torneio binário (k=3) |
| **Crossover** | Um ponto com reparo de consistência |
| **Mutação** | Substituição de bloco/gene (com reparo de consistência) |
| **Elitismo** | Preserva os N melhores por geração |
| **Critério de parada** | Número fixo de gerações (Justificado pela previsibilidade de tempo de execução e estabilidade da convergência observada empiricamente antes do limite) |

**Por que AG?** O espaço de busca é combinatorial e exponencial: com 20 atividades e 48 blocos, há mais de 20⁴⁸ combinações possíveis. Busca exaustiva é inviável. O AG explora esse espaço eficientemente por seleção natural, recombinação e mutação, convergindo para soluções de alta qualidade em poucas centenas de gerações.

### Parâmetros padrão

| Parâmetro | Valor | Justificativa |
|---|---|---|
| População | 80 | Diversidade suficiente sem custo excessivo |
| Gerações  | 150 | Convergência antes de 150 gerações na maioria dos casos |
| Crossover | 85% | Alta recombinação promove exploração |
| Mutação   | 12% | Aplicada por cromossomo (com reparo) — evita destruição excessiva de boas soluções |
| Elitismo  | 2 | Preserva melhores sem perder diversidade |

---

## 🚀 Instalação e Execução

### Pré-requisitos

- Python 3.10+

### Instalação

```bash
git clone https://github.com/1drey2drey3drey/sims-routine-optimizer.git
cd sims-routine-optimizer
pip install -r requirements.txt
```

### Executar o dashboard web

```bash
streamlit run app.py
```

Acesse: `http://localhost:8501`

### Executar os testes

```bash
python tests/test_runs.py
```

Os resultados são salvos automaticamente em `results/test_results.json` e a curva de convergência em `results/convergence_chart.png`.

---

## 📁 Estrutura do projeto

```
sims-routine-optimizer/
├── app.py                  # Interface Streamlit (dashboard principal)
├── relatorio_tecnico.html  # Relatório Técnico acadêmico (PDF imprimível)
├── slides.md               # Slides de apresentação acadêmica (Markdown)
├── requirements.txt
├── uso_ia.md               # Declaração de uso de IA
├── src/                    # Código-fonte principal
│   ├── __init__.py         # Pacote Python
│   ├── activities.py       # Catálogo de 20 atividades
│   ├── sim.py              # Modelo do Sim (traços e necessidades)
│   ├── fitness.py          # Função de aptidão
│   ├── genetic_algorithm.py # Motor do AG
│   ├── pso.py              # Motor do PSO
│   └── export.py           # Exportação CSV e HTML
├── tests/
│   └── test_runs.py        # 5 execuções × 4 perfis com sementes distintas
└── results/
    ├── test_results.json   # Resultados dos testes (pré-gerados)
    ├── convergence_chart.png # Curvas de convergência geradas (2x2 unificado)
    ├── convergence_workaholic.png # Curva de convergência isolada (Workaholic)
    ├── convergence_social.png     # Curva de convergência isolada (Social)
    ├── convergence_criativo.png   # Curva de convergência isolada (Criativo)
    └── convergence_equilibrado.png # Curva de convergência isolada (Equilibrado)
```

---

## 📊 Resultados dos testes

5 execuções independentes × 4 perfis de Sim, com sementes distintas (`42, 7, 123, 999, 2024`). Comparação entre AG, PSO e rotina aleatória (baseline):

| Perfil | Fitness AG (Média ± DP) | Fitness PSO (Média ± DP) | Fitness Baseline (Média) | Felicidade Média (AG / PSO) | Vencedor |
|---|---|---|---|---|---|
| **Workaholic**  | 1304.14 ± 25.70 | 1305.28 ± 9.02 | 0.00  | 63.7% / 63.6% | **PSO** |
| **Social**      | 1819.04 ± 45.80 | 1802.37 ± 63.91 | 0.00  | 62.9% / 63.6% | **AG** |
| **Criativo**    | 1333.76 ± 18.46 | 1338.19 ± 10.35 | 0.00  | 64.0% / 64.1% | **PSO** |
| **Equilibrado** | 1470.23 ± 21.24 | 1487.77 ± 14.74 | 0.00  | 64.3% / 63.3% | **PSO** |

> **Entendendo as métricas:**
> - **Fitness (Média)**: É a função objetivo otimizada pelo algoritmo. Corresponde à utilidade das atividades ao longo dos 48 blocos diários modificada por traços de personalidade, acrescida dos bônus de diversidade/equilíbrio/moodlets, deduzida das penalidades biológicas, e **acrescida diretamente de 10 vezes a Felicidade Média Diária (escala 0-1000)**. Isso garante correlação direta e estrita com o bem-estar geral do Sim.
> - **Felicidade Média**: É uma métrica clínica normalizada no intervalo de `[0, 100]` que indica a média dos níveis de satisfação das 8 necessidades do Sim ao longo de todos os 48 blocos do dia.
>
> Tempo médio de execução: ~1.0s por execução (150 gerações, população 80).

Resultados completos em [`results/test_results.json`](results/test_results.json), gráfico de convergência unificado gerado em [`results/convergence_chart.png`](results/convergence_chart.png) e gráficos isolados gerados em `results/convergence_{perfil}.png`.

---

## 📥 Exportação (Bônus — Alternativa 1)

O dashboard permite exportar a rotina otimizada em:
- **CSV** — tabela de horários para uso em planilhas
- **Relatório HTML** — visualização completa com gráfico de necessidades

---

## ⚠️ Limitações

- O modelo de necessidades é simplificado; não replica 100% a mecânica do jogo
- Atividades multi-bloco são tratadas como atômicas pelo cromossomo
- O AG pode convergir para ótimos locais em execuções com poucas gerações
- O estado inicial das necessidades do Sim é fixo em 0 nos testes automatizados

---

## 🔮 Melhorias Futuras

- Adicionar restrições de horário (ex: trabalho apenas entre 8h–18h)
- Suporte a necessidades com estado inicial personalizado via interface
- Implementar PSO como segunda metaheurística para comparação (Alternativa 3)
- Persistência de rotinas favoritas em banco de dados local

---

## 🤖 Uso de IA

Ver arquivo [`uso_ia.md`](uso_ia.md).

---

## 📚 Referências

- Mitchell, M. (1998). *An Introduction to Genetic Algorithms*. MIT Press.
- Holland, J. H. (1992). *Adaptation in Natural and Artificial Systems*. MIT Press.
- The Sims Wiki — Needs mechanics: https://sims.fandom.com/wiki/Needs
