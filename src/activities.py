
"""
activities.py
Catálogo de atividades disponíveis para o Sim.
Cada atividade tem duração (em blocos de 30min), impacto nas necessidades
e custo energético.

Necessidades modeladas (escala -100 a +100, iniciando em 0):
  hunger, energy, fun, social, hygiene, bladder, comfort, environment

Lógica Sims:
  - Necessidades decaem naturalmente ao longo do tempo (decay passivo)
  - Atividades incoerentes com estado atual do Sim são penalizadas
  - Traços amplificam/reduzem impacto de categorias específicas
  - Moodlets concedem bônus temporários baseados em sequências de atividades
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Activity:
    name: str
    emoji: str
    duration_blocks: int          # 1 bloco = 30 minutos
    needs_delta: Dict[str, float] # impacto em cada necessidade por bloco
    category: str                 # trabalho, lazer, social, basico, cuidado
    description: str = ""
    # Necessidade mínima que o Sim deve ter para executar (ex: não dormir sem energy baixa)
    requires_need_below: Optional[Dict[str, float]] = None
    # Necessidade máxima que o Sim deve ter para executar (ex: não comer se hunger > 70)
    requires_need_above: Optional[Dict[str, float]] = None
    # Tags para detecção de moodlets
    tags: List[str] = field(default_factory=list)

    def total_happiness(self, sim_traits: Dict[str, float]) -> float:
        """
        Calcula a felicidade total da atividade levando em conta os traços do Sim.
        Traços amplificam ou reduzem o impacto de certas atividades.
        A lógica replica o sistema de traços do The Sims 3/4.
        """
        base = sum(self.needs_delta.values())
        bonus = 0.0
        trait_map = {
            # Traços positivos por categoria
            "workaholic":   {"trabalho": 0.5, "lazer": -0.1},
            "introvertido": {"social": -0.5, "lazer": 0.3, "basico": 0.1},
            "extrovertido": {"social": 0.5, "lazer": 0.1},
            "criativo":     {"lazer": 0.4, "trabalho": 0.1},
            "preguicoso":   {"basico": 0.3, "trabalho": -0.5, "cuidado": -0.2},
            "ativo":        {"cuidado": 0.5, "lazer": 0.1, "basico": -0.1},
            "gastronomico": {"basico": 0.4},   # ama comida
            "sociavel":     {"social": 0.4, "lazer": 0.1},
            "solitario":    {"social": -0.6, "basico": 0.2, "lazer": 0.2},
        }
        for trait, cat_mods in trait_map.items():
            if sim_traits.get(trait, 0) > 0:
                mod = cat_mods.get(self.category, 0)
                bonus += mod * sim_traits[trait]
        return base * (1 + bonus)

    def context_penalty(self, current_needs: Dict[str, float]) -> float:
        """
        Penalidade contextual: actividades fora de hora custam felicidade.
        Ex: dormir com energy=90 é desperdício; trabalhar com hunger=-70 é sofrimento.
        """
        penalty = 0.0
        if self.requires_need_below:
            for need, threshold in self.requires_need_below.items():
                val = current_needs.get(need, 0)
                if val > threshold:
                    # Muito acima do threshold → atividade é desnecessária agora
                    penalty += (val - threshold) * 0.05
        if self.requires_need_above:
            for need, threshold in self.requires_need_above.items():
                val = current_needs.get(need, 0)
                if val < threshold:
                    # Muito abaixo → Sim não tem condições
                    penalty += (threshold - val) * 0.08
        return penalty


# ---------------------------------------------------------------------------
# Catálogo completo de atividades — inspirado em The Sims 4
# ---------------------------------------------------------------------------

ACTIVITIES: Dict[str, Activity] = {

    # ── BÁSICO ──────────────────────────────────────────────────────────────
    "dormir": Activity(
        name="Dormir", emoji="😴", duration_blocks=16, category="basico",
        needs_delta={"energy": 8.0, "comfort": 2.5, "bladder": -1.0, "fun": 0.3},
        description="Recupera energia essencial para o dia.",
        requires_need_below={"energy": 20.0},  # só faz sentido com energy baixa
        tags=["rest", "night"],
    ),
    "soneca": Activity(
        name="Soneca no sofá", emoji="💤", duration_blocks=4, category="basico",
        needs_delta={"energy": 3.5, "comfort": 1.5, "bladder": -0.5},
        description="Recarrega levemente sem comprometer a noite.",
        requires_need_below={"energy": 10.0},
        tags=["rest"],
    ),
    "comer_refeicao": Activity(
        name="Cozinhar refeição", emoji="🍳", duration_blocks=2, category="basico",
        needs_delta={"hunger": 8.0, "comfort": 1.5, "fun": 1.5, "environment": 0.5},
        description="Prepara e come uma refeição completa.",
        requires_need_below={"hunger": 40.0},
        tags=["food", "cooking"],
    ),
    "lanche_rapido": Activity(
        name="Lanche rápido", emoji="🥪", duration_blocks=1, category="basico",
        needs_delta={"hunger": 3.5, "comfort": -0.5},
        description="Come algo rápido entre atividades.",
        requires_need_below={"hunger": 20.0},
        tags=["food"],
    ),
    "banheiro": Activity(
        name="Usar banheiro", emoji="🚽", duration_blocks=1, category="basico",
        needs_delta={"bladder": 10.0, "hygiene": 1.5, "comfort": 0.5},
        description="Necessidade básica urgente.",
        requires_need_below={"bladder": -20.0},  # só quando bladder está baixa
        tags=["hygiene", "urgent"],
    ),
    "banho": Activity(
        name="Banho relaxante", emoji="🚿", duration_blocks=2, category="cuidado",
        needs_delta={"hygiene": 10.0, "comfort": 3.0, "fun": 1.0, "energy": 1.0},
        description="Higiene completa e revigorante.",
        tags=["hygiene", "self_care"],
    ),

    # ── TRABALHO / ESTUDO ────────────────────────────────────────────────────
    "trabalho": Activity(
        name="Trabalhar (turno completo)", emoji="💼", duration_blocks=16, category="trabalho",
        needs_delta={"hunger": -2.5, "energy": -3.5, "bladder": -2.5,
                     "comfort": -1.5, "fun": -1.5, "social": 1.5},
        description="Turno de trabalho completo (8h).",
        requires_need_above={"energy": -30.0},  # precisa de energia mínima
        tags=["career", "grind"],
    ),
    "estudar": Activity(
        name="Estudar", emoji="📚", duration_blocks=4, category="trabalho",
        needs_delta={"energy": -2.5, "fun": -1.5, "hunger": -1.5,
                     "comfort": -1.0, "social": 0.5},
        description="Sessão de estudos de 2 horas.",
        requires_need_above={"energy": -20.0},
        tags=["career", "skill"],
    ),
    "freelance": Activity(
        name="Trabalho freelance", emoji="💻", duration_blocks=4, category="trabalho",
        needs_delta={"energy": -1.5, "fun": 1.0, "hunger": -1.0,
                     "comfort": -0.5, "social": -0.5},
        description="Trabalho extra em casa com mais autonomia.",
        tags=["career", "skill"],
    ),

    # ── LAZER ────────────────────────────────────────────────────────────────
    "videogame": Activity(
        name="Jogar videogame", emoji="🎮", duration_blocks=4, category="lazer",
        needs_delta={"fun": 8.0, "energy": -1.5, "social": 1.0,
                     "comfort": 1.0, "bladder": -1.0},
        description="Joga videogame por 2 horas.",
        tags=["entertainment", "indoor"],
    ),
    "ler": Activity(
        name="Ler livro", emoji="📖", duration_blocks=2, category="lazer",
        needs_delta={"fun": 3.5, "energy": -0.5, "comfort": 2.0, "environment": 1.0},
        description="Leitura relaxante e enriquecedora.",
        tags=["entertainment", "indoor", "quiet"],
    ),
    "assistir_tv": Activity(
        name="Maratonar série", emoji="📺", duration_blocks=4, category="lazer",
        needs_delta={"fun": 4.5, "comfort": 2.5, "energy": -0.5,
                     "social": 0.5, "bladder": -1.0},
        description="Maratona de série ou filme.",
        tags=["entertainment", "indoor"],
    ),
    "pintar": Activity(
        name="Pintar / criar arte", emoji="🎨", duration_blocks=4, category="lazer",
        needs_delta={"fun": 7.0, "energy": -1.5, "comfort": 0.5,
                     "environment": 1.5},
        description="Atividade criativa que eleva o humor.",
        tags=["creative", "skill"],
    ),
    "musica": Activity(
        name="Tocar instrumento", emoji="🎸", duration_blocks=2, category="lazer",
        needs_delta={"fun": 5.5, "energy": -1.0, "social": 1.0},
        description="Prática musical.",
        tags=["creative", "skill"],
    ),
    "jardinagem_hobby": Activity(
        name="Jardinagem (hobby)", emoji="🌻", duration_blocks=2, category="lazer",
        needs_delta={"fun": 4.0, "environment": 5.0, "energy": -1.0,
                     "comfort": 1.0},
        description="Cuidar das plantas por prazer.",
        tags=["outdoor", "relaxing"],
    ),

    # ── SOCIAL ───────────────────────────────────────────────────────────────
    "conversar": Activity(
        name="Conversar com amigos", emoji="💬", duration_blocks=4, category="social",
        needs_delta={"social": 9.0, "fun": 3.5, "energy": -0.5,
                     "comfort": 1.0},
        description="Bate-papo com amigos ou família.",
        tags=["social", "relationship"],
    ),
    "sair_jantar": Activity(
        name="Jantar fora", emoji="🍽️", duration_blocks=4, category="social",
        needs_delta={"social": 7.0, "fun": 4.5, "hunger": 6.0,
                     "comfort": 1.5, "energy": -1.0},
        description="Jantar fora com alguém especial.",
        tags=["social", "food", "outing"],
    ),
    "festa": Activity(
        name="Festa / Balada", emoji="🎉", duration_blocks=6, category="social",
        needs_delta={"social": 11.0, "fun": 9.0, "energy": -5.0,
                     "hunger": -2.5, "bladder": -2.5, "hygiene": -1.5},
        description="Noite de festa (3 horas).",
        requires_need_above={"energy": 10.0},  # precisa de energia para curtir
        tags=["social", "outing", "intense"],
    ),
    "namorar": Activity(
        name="Tempo com parceiro(a)", emoji="❤️", duration_blocks=4, category="social",
        needs_delta={"social": 8.0, "fun": 6.0, "comfort": 3.0,
                     "energy": -0.5},
        description="Momento de qualidade com o parceiro.",
        tags=["social", "romance", "relationship"],
    ),

    # ── CUIDADO ──────────────────────────────────────────────────────────────
    "exercitar": Activity(
        name="Malhar / exercitar", emoji="🏃", duration_blocks=4, category="cuidado",
        needs_delta={"fun": 4.0, "energy": -4.0, "hygiene": -3.0,
                     "hunger": -2.5, "comfort": -1.5},
        description="Academia ou treino em casa.",
        requires_need_above={"energy": -10.0},
        tags=["fitness", "skill"],
    ),
    "meditar": Activity(
        name="Meditar", emoji="🧘", duration_blocks=2, category="cuidado",
        needs_delta={"fun": 2.5, "energy": 2.5, "comfort": 3.5,
                     "social": 0.5},
        description="Sessão de meditação para equilíbrio mental.",
        tags=["relaxing", "wellness", "quiet"],
    ),
    "cuidar_jardim": Activity(
        name="Cuidar do jardim", emoji="🌱", duration_blocks=2, category="cuidado",
        needs_delta={"fun": 3.0, "environment": 6.0, "energy": -1.5,
                     "comfort": 0.5},
        description="Jardinagem terapêutica.",
        tags=["outdoor", "relaxing", "environment"],
    ),
}

# Necessidades com limite mínimo (não podem descer abaixo de -100)
NEED_KEYS = ["hunger", "energy", "fun", "social", "hygiene",
             "bladder", "comfort", "environment"]

TOTAL_BLOCKS = 48  # 24h × 2 blocos/hora

# Peso de cada necessidade na felicidade geral
NEED_WEIGHTS = {
    "hunger":      0.20,
    "energy":      0.20,
    "fun":         0.15,
    "social":      0.15,
    "hygiene":     0.10,
    "bladder":     0.10,
    "comfort":     0.05,
    "environment": 0.05,
}

# Decaimento passivo por bloco (30min) — necessidades caem naturalmente
# Baseado na lógica de motives decay dos Sims 3/4
NEED_DECAY = {
    "hunger":      -1.5,   # sempre com fome ao longo do dia
    "energy":      -0.8,   # cansa gradualmente
    "fun":         -0.6,   # tédio aparece com o tempo
    "social":      -0.5,   # solidão cresce devagar
    "hygiene":     -0.4,   # fica sujo ao longo do dia
    "bladder":     -1.2,   # urgência cresce rápido
    "comfort":     -0.3,   # desconforto acumula
    "environment": -0.1,   # ambiente piora suavemente
}

# Sistema de moodlets — bônus de felicidade por sequências de atividades
# Formato: (tags_requeridas_em_sequência, nome_moodlet, bônus_fitness)
MOODLETS = [
    ({"fitness", "hygiene"},     "Corpo em Forma",      15.0),
    ({"food", "social"},         "Jantar Especial",     12.0),
    ({"creative", "quiet"},      "Foco Criativo",       10.0),
    ({"rest", "career"},         "Descansado e Produtivo", 14.0),
    ({"social", "outing"},       "Vida Social Ativa",   11.0),
    ({"romance", "food"},        "Noite Romântica",     16.0),
    ({"wellness", "quiet"},      "Zen Total",           10.0),
    ({"entertainment", "social"},"Noite Divertida",      9.0),
]
