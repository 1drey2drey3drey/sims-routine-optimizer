
"""
tests/test_runs.py
Suite de testes: 5 execuções independentes com sementes distintas.
Compara AG vs PSO vs Baseline Aleatório — Pontuação Extra (Comparação Técnica Avançada).

Uso:
    python tests/test_runs.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import json
import time
import statistics
from src.genetic_algorithm import run_ga, random_baseline, GAConfig
from src.pso import run_pso, PSOConfig
from src.sim import Sim

SEEDS    = [42, 7, 123, 999, 2024]
PROFILES = ["workaholic", "social", "criativo", "equilibrado"]


def run_tests():
    print("=" * 70)
    print("SUITE DE TESTES — Sims Routine Optimizer  (AG vs PSO vs Aleatório)")
    print("=" * 70)

    all_results = {}

    for profile in PROFILES:
        sim = Sim.from_profile(f"Sim_{profile}", profile)
        print(f"\n> Perfil: {profile.upper()} | {sim}")
        print("-" * 60)

        ga_fitnesses   = []
        pso_fitnesses  = []
        base_fitnesses = []
        ga_happiness   = []
        pso_happiness  = []
        base_happiness = []
        ga_times       = []
        pso_times      = []

        ga_history_best_all  = []
        ga_history_mean_all  = []
        pso_history_best_all = []
        pso_history_mean_all = []

        for seed in SEEDS:
            ga_config = GAConfig(
                population_size=80, generations=150,
                crossover_rate=0.85, mutation_rate=0.12,
                tournament_size=3, elitism=2, seed=seed,
            )
            pso_config = PSOConfig(
                swarm_size=80, iterations=150,
                w=0.7, c1=1.5, c2=1.5, seed=seed,
            )

            # AG
            t0 = time.time()
            ga_result = run_ga(sim.traits, ga_config)
            ga_elapsed = time.time() - t0

            # PSO
            t0 = time.time()
            pso_result = run_pso(sim.traits, pso_config)
            pso_elapsed = time.time() - t0

            # Baseline
            base = random_baseline(sim.traits, seed=seed)

            ga_fitnesses.append(ga_result["best_fitness"])
            ga_happiness.append(ga_result["best_info"]["final_happiness"])
            ga_times.append(ga_elapsed)
            ga_history_best_all.append(ga_result["history"]["best"])
            ga_history_mean_all.append(ga_result["history"]["mean"])

            pso_fitnesses.append(pso_result["best_fitness"])
            pso_happiness.append(pso_result["best_info"]["final_happiness"])
            pso_times.append(pso_elapsed)
            pso_history_best_all.append(pso_result["history"]["best"])
            pso_history_mean_all.append(pso_result["history"]["mean"])

            base_fitnesses.append(base["best_fitness"])
            base_happiness.append(base["best_info"]["final_happiness"])

            winner = "AG" if ga_result["best_fitness"] >= pso_result["best_fitness"] else "PSO"
            print(
                f"  Semente {seed:>4} | "
                f"AG={ga_result['best_fitness']:>8.2f} ({ga_elapsed:.2f}s)  "
                f"PSO={pso_result['best_fitness']:>8.2f} ({pso_elapsed:.2f}s)  "
                f"Base={base['best_fitness']:>8.2f}  "
                f"Vencedor: {winner}"
            )

        # Estatísticas
        def stats(vals):
            return statistics.mean(vals), (statistics.stdev(vals) if len(vals) > 1 else 0)

        mean_ga,  std_ga  = stats(ga_fitnesses)
        mean_pso, std_pso = stats(pso_fitnesses)
        mean_base, _      = stats(base_fitnesses)
        mean_ga_happy, _  = stats(ga_happiness)
        mean_pso_happy, _ = stats(pso_happiness)
        mean_base_happy, _ = stats(base_happiness)
        mean_ga_time, _   = stats(ga_times)
        mean_pso_time, _  = stats(pso_times)

        # Melhoria calculada com base na Felicidade Média (escala de 0-100)
        improv_ga  = (mean_ga_happy  - mean_base_happy) / max(mean_base_happy, 1) * 100
        improv_pso = (mean_pso_happy - mean_base_happy) / max(mean_base_happy, 1) * 100

        n_gens = len(ga_history_best_all[0])
        avg_ga_best  = [statistics.mean([h[g] for h in ga_history_best_all])  for g in range(n_gens)]
        avg_ga_mean  = [statistics.mean([h[g] for h in ga_history_mean_all])  for g in range(n_gens)]
        avg_pso_best = [statistics.mean([h[g] for h in pso_history_best_all]) for g in range(n_gens)]
        avg_pso_mean = [statistics.mean([h[g] for h in pso_history_mean_all]) for g in range(n_gens)]

        print(f"\n  RESUMO {'-' * 47}")
        print(f"  AG   — média: {mean_ga:.2f} ± {std_ga:.2f}  "
              f"felicidade média: {mean_ga_happy:.1f}  "
              f"melhoria (feliz): {improv_ga:+.1f}%  tempo: {mean_ga_time:.2f}s")
        print(f"  PSO  — média: {mean_pso:.2f} ± {std_pso:.2f}  "
              f"felicidade média: {mean_pso_happy:.1f}  "
              f"melhoria (feliz): {improv_pso:+.1f}%  tempo: {mean_pso_time:.2f}s")
        print(f"  Base — média: {mean_base:.2f}")

        all_results[profile] = {
            # AG
            "ga_fitnesses":       ga_fitnesses,
            "mean_ga":            mean_ga,
            "std_ga":             std_ga,
            "mean_ga_time_s":     mean_ga_time,
            "mean_ga_happiness":  mean_ga_happy,
            "mean_ga_improvement_pct": improv_ga,
            "avg_ga_history_best":  avg_ga_best,
            "avg_ga_history_mean":  avg_ga_mean,
            # PSO
            "pso_fitnesses":      pso_fitnesses,
            "mean_pso":           mean_pso,
            "std_pso":            std_pso,
            "mean_pso_time_s":    mean_pso_time,
            "mean_pso_happiness": mean_pso_happy,
            "mean_pso_improvement_pct": improv_pso,
            "avg_pso_history_best": avg_pso_best,
            "avg_pso_history_mean": avg_pso_mean,
            # Baseline
            "baseline_fitnesses": base_fitnesses,
            "mean_base":          mean_base,
            "mean_base_happiness": mean_base_happy,
            # Legado (mantido para compatibilidade com app.py)
            "mean_improvement_pct": improv_ga,
            "mean_happiness":       mean_ga_happy,
            "mean_time_s":          mean_ga_time,
        }

    # Salva JSON
    os.makedirs("results", exist_ok=True)
    out_path = "results/test_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] Resultados salvos em {out_path}")

    # Gera gráficos de convergência (AG vs PSO por perfil)
    try:
        import matplotlib.pyplot as plt
        import matplotlib.gridspec as gridspec

        fig = plt.figure(figsize=(16, 10))
        fig.patch.set_facecolor("#0d0b1e")
        gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

        for idx, profile in enumerate(PROFILES):
            r    = all_results[profile]
            gens = list(range(1, len(r["avg_ga_history_best"]) + 1))
            ax   = fig.add_subplot(gs[idx // 2, idx % 2])
            ax.set_facecolor("#0d0b1e")

            ax.plot(gens, r["avg_ga_history_best"],  label="AG — Melhor",   color="#00C896", linewidth=2.2)
            ax.plot(gens, r["avg_ga_history_mean"],  label="AG — Média",    color="#00C896", linewidth=1.2, linestyle="--", alpha=0.6)
            ax.plot(gens, r["avg_pso_history_best"], label="PSO — Melhor",  color="#F5A623", linewidth=2.2)
            ax.plot(gens, r["avg_pso_history_mean"], label="PSO — Média",   color="#F5A623", linewidth=1.2, linestyle="--", alpha=0.6)

            ax.set_title(f"Perfil: {profile.capitalize()}", color="#c8c4e0", fontsize=11)
            ax.set_xlabel("Geração / Iteração", color="#8ecfc2", fontsize=9)
            ax.set_ylabel("Fitness", color="#8ecfc2", fontsize=9)
            ax.tick_params(colors="#8ecfc2")
            ax.spines[:].set_color("#2a2060")
            ax.grid(True, linestyle=":", alpha=0.3, color="#3a3060")
            ax.legend(fontsize=8, facecolor="#1a1033", edgecolor="#2a2060",
                      labelcolor="#c8c4e0")

            # Anotação com médias finais
            ax.annotate(
                f"AG: {r['mean_ga']:.0f} | PSO: {r['mean_pso']:.0f}",
                xy=(0.98, 0.05), xycoords="axes fraction",
                ha="right", fontsize=8, color="#8ecfc2",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#1a1033", edgecolor="#2a2060"),
            )

            # --- Gerar gráfico isolado para este perfil ---
            fig_iso = plt.figure(figsize=(8, 5))
            fig_iso.patch.set_facecolor("#0d0b1e")
            ax_iso = fig_iso.add_subplot(111)
            ax_iso.set_facecolor("#0d0b1e")

            ax_iso.plot(gens, r["avg_ga_history_best"],  label="AG — Melhor",   color="#00C896", linewidth=2.2)
            ax_iso.plot(gens, r["avg_ga_history_mean"],  label="AG — Média",    color="#00C896", linewidth=1.2, linestyle="--", alpha=0.6)
            ax_iso.plot(gens, r["avg_pso_history_best"], label="PSO — Melhor",  color="#F5A623", linewidth=2.2)
            ax_iso.plot(gens, r["avg_pso_history_mean"], label="PSO — Média",   color="#F5A623", linewidth=1.2, linestyle="--", alpha=0.6)

            ax_iso.set_title(f"Convergência AG vs PSO: Perfil {profile.capitalize()} (Média de 5 Sementes)", color="#00C896", fontsize=11, fontweight="bold")
            ax_iso.set_xlabel("Geração / Iteração", color="#8ecfc2", fontsize=9)
            ax_iso.set_ylabel("Fitness", color="#8ecfc2", fontsize=9)
            ax_iso.tick_params(colors="#8ecfc2")
            ax_iso.spines[:].set_color("#2a2060")
            ax_iso.grid(True, linestyle=":", alpha=0.3, color="#3a3060")
            ax_iso.legend(fontsize=9, facecolor="#1a1033", edgecolor="#2a2060", labelcolor="#c8c4e0")

            ax_iso.annotate(
                f"AG Média Final: {r['mean_ga']:.1f}\nPSO Média Final: {r['mean_pso']:.1f}",
                xy=(0.98, 0.05), xycoords="axes fraction",
                ha="right", fontsize=9, color="#8ecfc2",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#1a1033", edgecolor="#2a2060"),
            )

            iso_path = f"results/convergence_{profile}.png"
            plt.savefig(iso_path, dpi=150, facecolor=fig_iso.get_facecolor())
            plt.close(fig_iso)
            print(f"[OK] Gráfico de convergência isolado salvo em {iso_path}")

        fig.suptitle("Convergência AG vs PSO — Média de 5 Sementes", 
                     color="#00C896", fontsize=14, fontweight="bold")

        chart_path = "results/convergence_chart.png"
        plt.savefig(chart_path, dpi=150, facecolor=fig.get_facecolor())
        plt.close()
        print(f"[OK] Gráfico de convergência unificado AG vs PSO salvo em {chart_path}")
    except Exception as e:
        print(f"[WARN] Erro ao gerar gráfico: {e}")

    # Resumo geral comparativo
    print("\n" + "=" * 70)
    print("RESUMO GERAL — AG vs PSO vs Aleatório")
    print("=" * 70)
    print(f"  {'Perfil':<15} | {'AG média':>10} | {'PSO média':>10} | {'Base média':>10} | {'Vencedor':>8}")
    print(f"  {'-'*15}-+-{'-'*10}-+-{'-'*10}-+-{'-'*10}-+-{'-'*8}")
    for profile, r in all_results.items():
        winner = "AG" if r["mean_ga"] >= r["mean_pso"] else "PSO"
        print(f"  {profile:<15} | {r['mean_ga']:>10.2f} | {r['mean_pso']:>10.2f} | {r['mean_base']:>10.2f} | {winner:>8}")


if __name__ == "__main__":
    run_tests()
