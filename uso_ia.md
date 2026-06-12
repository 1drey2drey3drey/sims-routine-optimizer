# Declaração de Uso de Inteligência Artificial

**Projeto:** Sims Routine Optimizer  
**Disciplina:** Inteligência Artificial e Computacional (0700M8) — CESUPA 01/2026  
**Equipe:** Andrey Lourival Andrade Garcia | Everton de Oliveira da Silva | Filipe César Maciel Sucupira | Igor Cecim Vilhena

---

## Ferramentas utilizadas

| Ferramenta | Finalidade |
|------------|-----------|
| Claude (Anthropic) | Apoio na estruturação do código, revisão da lógica do AG, geração de documentação e testes |

## Principais usos

1. **Estruturação da arquitetura do projeto** — A IA sugeriu a separação em módulos (`activities.py`, `fitness.py`, `genetic_algorithm.py`, `pso.py`, `sim.py`, `export.py`) e o fluxo entre eles.
2. **Implementação dos motores heurísticos (AG e PSO)** — A IA auxiliou na codificação dos operadores genéticos (crossover de um ponto, mutação por bloco, torneio de seleção), na modelagem de velocidade/posição das partículas no PSO, e nas respectivas lógicas de reparo de consistência.
3. **Função de aptidão** — A IA ajudou a formular as penalidades por necessidades críticas e o bônus de diversidade de categorias.
4. **Interface Streamlit** — A IA auxiliou na construção dos gráficos Plotly (Gantt, curva de convergência, radar comparativo).
5. **Documentação** — README, slides.md, docstrings e este arquivo foram gerados com apoio da IA e revisados pela equipe.
6. **Suite de testes** — O script `tests/test_runs.py` comparando AG e PSO estatisticamente foi gerado com apoio da IA e validado manualmente.

## Revisão humana

- Todos os parâmetros de busca do AG e do PSO foram discutidos e ajustados pela equipe com base em execuções reais.
- A modelagem de atividades e necessidades (pesos, deltas, penalidades) foi revisada e calibrada manualmente.
- Os resultados dos testes comparativos foram analisados criticamente pelos integrantes.
- Nenhum código foi submetido sem leitura e compreensão pela equipe.

## Responsabilidade

A equipe assume total responsabilidade pelo conteúdo deste trabalho. O uso de IA foi instrumental e supervisionado; todas as decisões de projeto, implementação e análise são de autoria da equipe.
