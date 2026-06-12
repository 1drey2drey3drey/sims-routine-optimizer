
"""
fitness.py
Função de aptidão (fitness) para avaliar uma rotina diária do Sim.

Melhorias implementadas (v3 — Sims-fiel):
  1. Decaimento passivo de necessidades (Need Decay) a cada bloco
  2. Penalidade contextual: atividades fora de hora custam fitness
  3. Sistema de moodlets: sequências temáticas de atividades geram bônus
  4. Penalidade por hora inadequada (ex: dormir de manhã perde bônus noturno)
  5. Penalidade por necessidades críticas mais gradual e realista
  6. Bônus por Sim bem balanceado (todas as necessidades acima de 0 no final)
"""

from typing import List, Dict, Tuple
from copy import deepcopy
from .activities import (
    ACTIVITIES, NEED_KEYS, NEED_WEIGHTS, TOTAL_BLOCKS,
    NEED_DECAY, MOODLETS
)

CRITICAL_THRESHOLD = -50   # necessidade crítica
URGENT_THRESHOLD   = -30   # começa a piorar o humor

def _get_moodlet_bonus(tags_used_sequence: List[set]) -> Tuple[float, List[str]]:
    """
    Verifica se alguma combinação de tags presentes na rotina
    ativa moodlets. Retorna bônus total e lista de moodlets ativados.
    """
    all_tags = set()
    for tag_set in tags_used_sequence:
        all_tags.update(tag_set)
    
    bonus = 0.0
    activated = []
    for required_tags, name, value in MOODLETS:
        if required_tags.issubset(all_tags):
            bonus += value
            activated.append(name)
    return bonus, activated


def evaluate(
    routine: List[str],
    sim_traits: Dict[str, float],
    initial_needs: Dict[str, float] = None
) -> Tuple[float, Dict]:
    """
    Avalia a aptidão de uma rotina com lógica Sims-fiel.

    Args:
        routine: Lista de nomes de atividades (len == TOTAL_BLOCKS).
        sim_traits: Dicionário de traços do Sim.
        initial_needs: Estado inicial das necessidades. Se None, começa em 0.

    Returns:
        (fitness_score, info_dict)
        fitness_score: valor não-negativo; maior = melhor rotina.
        info_dict: dados detalhados para análise.
    """
    needs = {
        k: (initial_needs[k] if initial_needs and k in initial_needs else 0.0)
        for k in NEED_KEYS
    }
    total_happiness = 0.0
    penalties = 0.0
    activity_log: List[Tuple[int, str, float]] = []
    block_happiness_values = []  # Para cálculo da felicidade média do dia

    i = 0
    activities_used = set()
    tags_sequence = []   # sequência de tag-sets das atividades executadas

    while i < len(routine):
        act_name = routine[i]

        if act_name is None or act_name == "vazio":
            # Bloco vazio: apenas decay passivo
            for need_key in NEED_KEYS:
                decay = NEED_DECAY.get(need_key, 0)
                needs[need_key] = max(-100, min(100, needs[need_key] + decay))
            happy_inst = sum(
                NEED_WEIGHTS[k] * (needs[k] + 100) / 200 * 100
                for k in NEED_KEYS
            )
            block_happiness_values.append(happy_inst)
            i += 1
            continue

        act = ACTIVITIES.get(act_name)
        if act is None:
            i += 1
            continue

        activities_used.add(act_name)
        n_blocks = min(act.duration_blocks, len(routine) - i)

        # Penalidade contextual (fora de hora / sem condições)
        ctx_penalty = act.context_penalty(needs)
        penalties += ctx_penalty

        block_happiness = 0.0
        for block_idx in range(n_blocks):
            # 1. Decay passivo neste bloco
            for need_key in NEED_KEYS:
                decay = NEED_DECAY.get(need_key, 0)
                needs[need_key] = max(-100, min(100, needs[need_key] + decay))

            # 2. Aplica deltas da atividade
            for need_key, delta in act.needs_delta.items():
                needs[need_key] = max(-100, min(100, needs[need_key] + delta))

            # 3. Penalidade por necessidade urgente durante execução (penalização mais rigorosa, mas mantendo gradiente)
            for need in ["hunger", "bladder", "energy"]:
                if needs[need] < URGENT_THRESHOLD:
                    deficit = URGENT_THRESHOLD - needs[need]
                    w = NEED_WEIGHTS.get(need, 0.1)
                    penalties += deficit * w * 8

            # Reduz a felicidade obtida da atividade se o Sim estiver com necessidades básicas negligenciadas
            well_being_mult = 1.0
            for need in ["hunger", "energy", "hygiene", "bladder"]:
                if needs[need] < 0:
                    well_being_mult -= (abs(needs[need]) / 100) * 0.40
            well_being_mult = max(0.1, well_being_mult)

            block_happiness += act.total_happiness(sim_traits) * well_being_mult
            happy_inst = sum(
                NEED_WEIGHTS[k] * (needs[k] + 100) / 200 * 100
                for k in NEED_KEYS
            )
            block_happiness_values.append(happy_inst)

        total_happiness += block_happiness
        activity_log.append((i, act_name, block_happiness))

        if act.tags:
            tags_sequence.append(set(act.tags))

        i += n_blocks

    # ── Penalidades de necessidades críticas (final do dia) ──────────────────
    for need in NEED_KEYS:
        if needs[need] < CRITICAL_THRESHOLD:
            deficit = CRITICAL_THRESHOLD - needs[need]
            w = NEED_WEIGHTS.get(need, 0.05)
            penalties += deficit * w * 10

    # ── Penalidades estruturais (rotina impossível de viver) ─────────────────
    if "dormir" not in activities_used and "soneca" not in activities_used:
        penalties += 100  # sem dormir é biologicamente impossível

    if not any(a in activities_used for a in
               ("comer_refeicao", "lanche_rapido", "sair_jantar")):
        penalties += 75   # sem comer é biologicamente impossível

    if "banheiro" not in activities_used:
        penalties += 40

    if "banho" not in activities_used:
        penalties += 20   # higiene mínima esperada

    # ── Bônus por diversidade de categorias ──────────────────────────────────
    categories_used = {ACTIVITIES[a].category for a in activities_used if a in ACTIVITIES}
    diversity_bonus = len(categories_used) * 8

    # ── Bônus por Sim equilibrado (todas necessidades >= 0 no final) ─────────
    balanced_bonus = 0.0
    for need in NEED_KEYS:
        if needs[need] >= 0:
            balanced_bonus += NEED_WEIGHTS.get(need, 0.05) * 20

    # ── Sistema de Moodlets ───────────────────────────────────────────────────
    moodlet_bonus, activated_moodlets = _get_moodlet_bonus(tags_sequence)

    # Felicidade média diária das necessidades (escala 0–100)
    final_happiness = sum(block_happiness_values) / len(block_happiness_values) if block_happiness_values else 0.0

    # ── Fitness final ─────────────────────────────────────────────────────────
    raw_fitness = total_happiness + diversity_bonus + balanced_bonus + moodlet_bonus - penalties
    # Adicionamos a Felicidade Média Diária diretamente no fitness final como o componente principal.
    # Como final_happiness está na escala 0-100, multiplicamos por 10.0 para dar o peso correto (escala 0-1000).
    # Isso alinha o fitness perfeitamente com a felicidade média e evita o colapso para 0.0.
    fitness = max(0.0, raw_fitness + (final_happiness * 10.0))

    info = {
        "final_needs":       dict(needs),
        "final_happiness":   round(final_happiness, 2),
        "penalties":         round(penalties, 2),
        "diversity_bonus":   round(diversity_bonus, 2),
        "balanced_bonus":    round(balanced_bonus, 2),
        "moodlet_bonus":     round(moodlet_bonus, 2),
        "activated_moodlets": activated_moodlets,
        "activities_used":   list(activities_used),
        "categories_used":   list(categories_used),
        "activity_log":      activity_log,
    }

    return fitness, info
