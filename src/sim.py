
"""
sim.py
Modelo do Sim: traços de personalidade e estado das necessidades.
Traços inspirados no sistema de traços do The Sims 3/4.
"""

from dataclasses import dataclass, field
from typing import Dict
from .activities import NEED_KEYS, NEED_WEIGHTS


@dataclass
class Sim:
    name: str
    traits: Dict[str, float] = field(default_factory=dict)
    initial_needs: Dict[str, float] = field(default_factory=lambda: {
        k: 0.0 for k in NEED_KEYS
    })

    @classmethod
    def from_profile(cls, name: str, profile: str) -> "Sim":
        """Cria um Sim pré-configurado com base em perfis prontos."""
        profiles = {
            "workaholic": {
                "workaholic": 1.0, "introvertido": 0.3, "preguicoso": 0.0,
                "extrovertido": 0.0, "criativo": 0.2, "ativo": 0.1,
                "gastronomico": 0.0, "sociavel": 0.0, "solitario": 0.2,
            },
            "social": {
                "extrovertido": 1.0, "introvertido": 0.0, "criativo": 0.3,
                "workaholic": 0.2, "preguicoso": 0.1, "ativo": 0.3,
                "gastronomico": 0.3, "sociavel": 1.0, "solitario": 0.0,
            },
            "criativo": {
                "criativo": 1.0, "introvertido": 0.5, "ativo": 0.2,
                "workaholic": 0.3, "extrovertido": 0.2, "preguicoso": 0.1,
                "gastronomico": 0.2, "sociavel": 0.1, "solitario": 0.3,
            },
            "equilibrado": {
                "workaholic": 0.3, "extrovertido": 0.3, "criativo": 0.3,
                "introvertido": 0.2, "ativo": 0.3, "preguicoso": 0.1,
                "gastronomico": 0.2, "sociavel": 0.3, "solitario": 0.0,
            },
        }
        return cls(name=name, traits=profiles.get(profile, profiles["equilibrado"]))

    def happiness_score(self, needs: Dict[str, float]) -> float:
        score = 0.0
        for need, weight in NEED_WEIGHTS.items():
            val = needs.get(need, 0.0)
            normalized = (val + 100) / 200
            score += weight * normalized
        return round(score * 100, 2)

    def __str__(self):
        traits_str = ", ".join(
            f"{t}({v:.1f})" for t, v in self.traits.items() if v > 0
        )
        return f"Sim({self.name} | traços: {traits_str})"
