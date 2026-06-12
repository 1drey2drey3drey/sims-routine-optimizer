
"""
genetic_algorithm.py
Motor do Algoritmo Genético para otimização de rotina diária.

Representação cromossômica:
  - Cromossomo: lista de 48 genes (blocos de 30min)
  - Gene: nome de uma atividade (str) ou None
  - Restrição: atividades de duração D ocupam D blocos consecutivos iguais

Operadores:
  - Seleção: torneio (k=3)
  - Crossover: crossover de dois pontos com reparo de consistência
  - Mutação: substituição de segmento aleatório + troca de atividade
  - Elitismo: preserva os N melhores a cada geração
"""

import random
from typing import List, Tuple, Dict, Optional, Callable
from dataclasses import dataclass, field
from .activities import ACTIVITIES, TOTAL_BLOCKS
from .fitness import evaluate


@dataclass
class GAConfig:
    population_size: int = 80
    generations: int = 150
    crossover_rate: float = 0.85
    mutation_rate: float = 0.12
    tournament_size: int = 3
    elitism: int = 2
    seed: Optional[int] = None


Chromosome = List[str]


# ── Representação / Decodificação ─────────────────────────────────────────────

def _activity_names() -> List[str]:
    return list(ACTIVITIES.keys())


def random_chromosome(rng: random.Random) -> Chromosome:
    """
    Gera um cromossomo aleatório válido de 48 blocos.
    Ordem biológica mínima: garante pelo menos 1 bloco de sono e 1 de comida.
    """
    acts = _activity_names()
    chrom: Chromosome = [None] * TOTAL_BLOCKS
    i = 0
    while i < TOTAL_BLOCKS:
        act_name = rng.choice(acts)
        act = ACTIVITIES[act_name]
        blocks = min(act.duration_blocks, TOTAL_BLOCKS - i)
        for j in range(blocks):
            chrom[i + j] = act_name
        i += blocks
    return chrom


def repair(chrom: Chromosome, rng: random.Random) -> Chromosome:
    """Garante que atividades multi-bloco sejam contíguas e consistentes."""
    result = []
    i = 0
    while i < len(chrom):
        act_name = chrom[i]
        if act_name is None:
            result.append(None)
            i += 1
            continue
        act = ACTIVITIES.get(act_name)
        if act is None:
            result.append(None)
            i += 1
            continue
        blocks = min(act.duration_blocks, len(chrom) - i)
        result.extend([act_name] * blocks)
        i += blocks
    while len(result) < TOTAL_BLOCKS:
        result.append("lanche_rapido")
    return result[:TOTAL_BLOCKS]


# ── Seleção ───────────────────────────────────────────────────────────────────

def tournament_selection(
    population: List[Chromosome],
    fitnesses: List[float],
    k: int,
    rng: random.Random,
) -> Chromosome:
    candidates = rng.choices(range(len(population)), k=k)
    best = max(candidates, key=lambda idx: fitnesses[idx])
    return population[best][:]


# ── Crossover ─────────────────────────────────────────────────────────────────

def two_point_crossover(
    parent1: Chromosome,
    parent2: Chromosome,
    rng: random.Random,
) -> Tuple[Chromosome, Chromosome]:
    """Crossover de dois pontos — mais adequado para cromossomos longos (48 genes)."""
    pts = sorted(rng.sample(range(1, TOTAL_BLOCKS), 2))
    p, q = pts[0], pts[1]
    child1 = repair(parent1[:p] + parent2[p:q] + parent1[q:], rng)
    child2 = repair(parent2[:p] + parent1[p:q] + parent2[q:], rng)
    return child1, child2


# ── Mutação ───────────────────────────────────────────────────────────────────

def mutate(chrom: Chromosome, mutation_rate: float, rng: random.Random) -> Chromosome:
    """
    Duas formas de mutação (escolhidas aleatoriamente):
      1. Substituição de segmento: troca uma atividade por outra diferente
      2. Inversão de segmento: inverte uma sub-sequência do cromossomo
    """
    if rng.random() >= mutation_rate:
        return chrom[:]

    chrom = chrom[:]
    mutation_type = rng.choice(["replace", "swap"])

    if mutation_type == "replace":
        i = rng.randint(0, TOTAL_BLOCKS - 1)
        new_act = rng.choice(_activity_names())
        act = ACTIVITIES[new_act]
        blocks = min(act.duration_blocks, TOTAL_BLOCKS - i)
        for j in range(blocks):
            chrom[i + j] = new_act
    else:
        # Swap de dois segmentos aleatórios
        i = rng.randint(0, TOTAL_BLOCKS - 2)
        j = rng.randint(i + 1, TOTAL_BLOCKS - 1)
        chrom[i], chrom[j] = chrom[j], chrom[i]

    return repair(chrom, rng)


# ── Motor principal ───────────────────────────────────────────────────────────

def run_ga(
    sim_traits: Dict[str, float],
    config: GAConfig,
    progress_callback: Optional[Callable[[int, float], None]] = None,
) -> Dict:
    """
    Executa o AG e retorna o melhor cromossomo encontrado.
    """
    rng = random.Random(config.seed)

    population = [random_chromosome(rng) for _ in range(config.population_size)]

    def eval_population(pop):
        fs, is_ = [], []
        for chrom in pop:
            f, info = evaluate(chrom, sim_traits)
            fs.append(f)
            is_.append(info)
        return fs, is_

    fitnesses, infos = eval_population(population)

    history = {"best": [], "mean": [], "worst": []}
    best_overall_fitness = -1
    best_overall_chrom   = None
    best_overall_info    = None
    evals_count          = len(population)

    for gen in range(config.generations):
        sorted_idx = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)
        new_population = [population[i][:] for i in sorted_idx[:config.elitism]]

        while len(new_population) < config.population_size:
            p1 = tournament_selection(population, fitnesses, config.tournament_size, rng)
            p2 = tournament_selection(population, fitnesses, config.tournament_size, rng)

            if rng.random() < config.crossover_rate:
                c1, c2 = two_point_crossover(p1, p2, rng)
            else:
                c1, c2 = p1[:], p2[:]

            c1 = mutate(c1, config.mutation_rate, rng)
            c2 = mutate(c2, config.mutation_rate, rng)
            new_population.extend([c1, c2])

        population = new_population[:config.population_size]
        fitnesses, infos = eval_population(population)
        evals_count += len(population)

        best_idx  = max(range(len(fitnesses)), key=lambda i: fitnesses[i])
        gen_best  = fitnesses[best_idx]
        gen_mean  = sum(fitnesses) / len(fitnesses)
        gen_worst = min(fitnesses)

        history["best"].append(gen_best)
        history["mean"].append(gen_mean)
        history["worst"].append(gen_worst)

        if gen_best > best_overall_fitness:
            best_overall_fitness = gen_best
            best_overall_chrom   = population[best_idx][:]
            best_overall_info    = infos[best_idx]

        if progress_callback:
            progress_callback(gen + 1, gen_best)

    return {
        "best_routine":  best_overall_chrom,
        "best_fitness":  best_overall_fitness,
        "best_info":     best_overall_info,
        "history":       history,
        "config":        config,
        "evals_count":   evals_count,
        "algorithm":     "GA",
    }


# ── Baseline: rotina aleatória (comparação) ───────────────────────────────────

def random_baseline(sim_traits: Dict[str, float], seed: int = 0) -> Dict:
    """Gera uma rotina aleatória sem AG (baseline para comparação)."""
    rng = random.Random(seed)
    chrom = random_chromosome(rng)
    fitness, info = evaluate(chrom, sim_traits)
    return {
        "best_routine": chrom,
        "best_fitness": fitness,
        "best_info":    info,
        "algorithm":    "Random",
    }
