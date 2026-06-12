
"""
export.py
Funções de exportação: CSV, HTML.
"""

import csv
import io
from typing import List, Dict
from .activities import ACTIVITIES, TOTAL_BLOCKS


def schedule_to_list(routine: List[str]) -> List[Dict]:
    """Converte cromossomo em lista de dicionários com horários."""
    schedule = []
    i = 0
    while i < len(routine):
        act_name = routine[i]
        if act_name is None or act_name == "vazio":
            i += 1
            continue
        act = ACTIVITIES.get(act_name)
        if act is None:
            i += 1
            continue
        n_blocks = min(act.duration_blocks, len(routine) - i)
        start_min = i * 30
        end_min   = (i + n_blocks) * 30
        sh = f"{(start_min // 60):02d}:{(start_min % 60):02d}"
        eh = f"{(end_min   // 60) % 24:02d}:{(end_min   % 60):02d}"
        schedule.append({
            "horario_inicio": sh,
            "horario_fim":    eh,
            "duracao_min":    n_blocks * 30,
            "atividade":      act.name,
            "emoji":          act.emoji,
            "categoria":      act.category,
            "descricao":      act.description,
        })
        i += n_blocks
    return schedule


def to_csv_bytes(routine: List[str], sim_name: str, fitness: float) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Sim", "Fitness", "Início", "Fim", "Duração(min)",
                     "Atividade", "Emoji", "Categoria", "Descrição"])
    for row in schedule_to_list(routine):
        writer.writerow([
            sim_name, f"{fitness:.2f}",
            row["horario_inicio"], row["horario_fim"], row["duracao_min"],
            row["atividade"], row["emoji"], row["categoria"], row["descricao"],
        ])
    return output.getvalue().encode("utf-8")


def to_html_report(
    routine: List[str],
    sim_name: str,
    fitness: float,
    info: Dict,
    history: Dict,
) -> str:
    schedule = schedule_to_list(routine)
    rows = "".join(
        f"<tr><td>{r['emoji']}</td><td>{r['horario_inicio']}–{r['horario_fim']}</td>"
        f"<td>{r['atividade']}</td><td>{r['categoria']}</td>"
        f"<td>{r['duracao_min']} min</td></tr>"
        for r in schedule
    )
    needs_rows = "".join(
        f"<tr><td>{n}</td><td>{v:+.1f}</td></tr>"
        for n, v in info["final_needs"].items()
    )
    moodlets_html = ""
    if info.get("activated_moodlets"):
        moodlets_html = "<h3>Moodlets Ativados</h3><ul>" + "".join(
            f"<li>✨ {m}</li>" for m in info["activated_moodlets"]
        ) + "</ul>"
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><title>Rotina {sim_name}</title>
<style>body{{font-family:monospace;background:#0d0b1e;color:#c8c4e0;padding:2rem}}
h1{{color:#00C896}} h3{{color:#F5A623}}
table{{border-collapse:collapse;width:100%;margin:1rem 0}}
th,td{{border:1px solid #2a2060;padding:6px 10px}}
th{{background:#1a1033;color:#8ecfc2}}</style></head>
<body>
<h1>🎮 Sims Routine Optimizer — {sim_name}</h1>
<p>Fitness AG: <strong style="color:#00C896">{fitness:.2f}</strong> &nbsp;|&nbsp;
   Felicidade Média: <strong style="color:#4FC3F7">{info['final_happiness']:.1f}/100</strong> &nbsp;|&nbsp;
   Moodlet Bônus: <strong style="color:#E879F9">+{info.get('moodlet_bonus',0):.1f}</strong></p>
{moodlets_html}
<h3>Rotina Diária</h3>
<table><tr><th>Emoji</th><th>Horário</th><th>Atividade</th><th>Categoria</th><th>Duração</th></tr>
{rows}</table>
<h3>Estado Final das Necessidades</h3>
<table><tr><th>Necessidade</th><th>Valor Final</th></tr>{needs_rows}</table>
</body></html>"""