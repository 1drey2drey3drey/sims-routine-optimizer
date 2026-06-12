
"""
pso.py
Otimização por Enxame de Partículas (PSO) para rotina diária do Sim.

Adaptação discreta para espaço de busca combinatório:
  - Cada partícula representa uma rotina (cromossomo de 48 blocos)
  - "Velocidade" é representada como probabilidade de substituir cada gene
  - Melhor posição pessoal (pbest) e melhor global (gbest) guiam a busca
  - Atualização discreta: gene é substituído pelo pbest ou gbest com
    probabilidade proporcional à velocidade (sigmoid)

Referência: Kennedy & Eberhart (1997) adaptado para espaços discretos.
"""

import random
import math
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from .activities import ACTIVITIES, TOTAL_BLOCKS
from .fitness import evaluate
from .genetic_algorithm import repair, random_chromosome, Chromosome


@dataclass
class PSOConfig:
    swarm_size: int = 80
    iterations: int = 150
    w: float = 0.7       # inércia
    c1: float = 1.5      # coeficiente cognitivo (atração para pbest)
    c2: float = 1.5      # coeficiente social (atração para gbest)
    seed: Optional[int] = None


def _sigmoid(x: float) -> float:
    """Função sigmóide para mapear velocidade em probabilidade [0,1]."""
    return 1.0 / (1.0 + math.exp(-x))


def _activity_names() -> List[str]:
    return list(ACTIVITIES.keys())


def _discrete_velocity_update(
    vel: List[float],
    pos: Chromosome,
    pbest: Chromosome,
    gbest: Chromosome,
    w: float,
    c1: float,
    c2: float,
    rng: random.Random,
) -> List[float]:
    """
    Atualiza a velocidade discreta de cada gene.
    vel[i] = w*vel[i] + c1*r1*(pbest[i]≠pos[i]) + c2*r2*(gbest[i]≠pos[i])
    """
    new_vel = []
    for i in range(TOTAL_BLOCKS):
        r1, r2 = rng.random(), rng.random()
        cognitive = c1 * r1 * (1.0 if pbest[i] != pos[i] else 0.0)
        social    = c2 * r2 * (1.0 if gbest[i] != pos[i] else 0.0)
        v = w * vel[i] + cognitive + social
        # Clamp para evitar overflow no sigmoid
        v = max(-6.0, min(6.0, v))
        new_vel.append(v)
    return new_vel


def _discrete_position_update(
    pos: Chromosome,
    vel: List[float],
    pbest: Chromosome,
    gbest: Chromosome,
    rng: random.Random,
) -> Chromosome:
    """
    Atualiza posição com base na velocidade discreta.
    Com probabilidade sigmoid(vel[i]), o gene i é substituído pelo
    pbest[i] ou gbest[i] (escolhido aleatoriamente).
    """
    new_pos = pos[:]
    acts = _activity_names()
    for i in range(TOTAL_BLOCKS):
        prob = _sigmoid(vel[i])
        if rng.random() < prob:
            # Escolhe entre pbest, gbest ou aleatório
            choice = rng.random()
            if choice < 0.45:
                new_pos[i] = pbest[i]
            elif choice < 0.90:
                new_pos[i] = gbest[i]
            else:
                new_pos[i] = rng.choice(acts)  # exploração aleatória
    return repair(new_pos, rng)


def run_pso(
    sim_traits: Dict[str, float],
    config: PSOConfig,
    progress_callback: Optional[Callable[[int, float], None]] = None,
) -> Dict:
    """
    Executa o PSO e retorna a melhor rotina encontrada.
    """
    rng = random.Random(config.seed)

    # Inicialização do enxame
    swarm    = [random_chromosome(rng) for _ in range(config.swarm_size)]
    velocities = [[rng.uniform(-1, 1) for _ in range(TOTAL_BLOCKS)]
                  for _ in range(config.swarm_size)]

    # Avalia fitness inicial
    fitnesses = []
    infos     = []
    for p in swarm:
        f, info = evaluate(p, sim_traits)
        fitnesses.append(f)
        infos.append(info)

    # Inicializa pbest e gbest
    pbest          = [p[:] for p in swarm]
    pbest_fitness  = fitnesses[:]

    gbest_idx      = max(range(config.swarm_size), key=lambda i: fitnesses[i])
    gbest          = swarm[gbest_idx][:]
    gbest_fitness  = fitnesses[gbest_idx]
    gbest_info     = infos[gbest_idx]

    history    = {"best": [], "mean": [], "worst": []}
    evals_count = config.swarm_size

    for it in range(config.iterations):
        for idx in range(config.swarm_size):
            # Atualiza velocidade
            velocities[idx] = _discrete_velocity_update(
                velocities[idx], swarm[idx],
                pbest[idx], gbest,
                config.w, config.c1, config.c2, rng,
            )
            # Atualiza posição
            swarm[idx] = _discrete_position_update(
                swarm[idx], velocities[idx],
                pbest[idx], gbest, rng,
            )
            # Avalia
            f, info = evaluate(swarm[idx], sim_traits)
            fitnesses[idx] = f
            infos[idx]     = info
            evals_count   += 1

            # Atualiza pbest
            if f > pbest_fitness[idx]:
                pbest[idx]         = swarm[idx][:]
                pbest_fitness[idx] = f

            # Atualiza gbest
            if f > gbest_fitness:
                gbest         = swarm[idx][:]
                gbest_fitness = f
                gbest_info    = info

        history["best"].append(gbest_fitness)
        history["mean"].append(sum(fitnesses) / len(fitnesses))
        history["worst"].append(min(fitnesses))

        if progress_callback:
            progress_callback(it + 1, gbest_fitness)

    return {
        "best_routine": gbest,
        "best_fitness": gbest_fitness,
        "best_info":    gbest_info,
        "history":      history,
        "config":       config,
        "evals_count":  evals_count,
        "algorithm":    "PSO",
    }