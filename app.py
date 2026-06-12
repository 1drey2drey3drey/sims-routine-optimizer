"""
app.py  —  Sims Routine Optimizer
Interface web principal com Streamlit.
Dashboard redesenhado com tema The Sims + mapa isométrico.
"""

import sys
import os

# 1. Configuração do path de execução do Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 2. Importações do projeto e de bibliotecas externas
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time
import json

from src.sim import Sim
from src.genetic_algorithm import run_ga, random_baseline, GAConfig
from src.pso import run_pso, PSOConfig
from src.activities import ACTIVITIES, NEED_KEYS
from src.export import to_csv_bytes, to_html_report, schedule_to_list

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sims Routine Optimizer",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS global ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Silkscreen:wght@400;700&family=Inter:wght@400;500;600&display=swap');

  /* Reset geral */
  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
  }

  /* Fundo degradê noturno Sims */
  .stApp {
    background: linear-gradient(160deg, #0d0b1e 0%, #1a1033 55%, #0e1f2e 100%);
  }

  /* ── Pixel border mixin ─────────────────────────────────────────── */
  .pixel-card {
    background: rgba(20, 16, 40, 0.85);
    border: 2px solid #00C896;
    border-radius: 0px;
    box-shadow: 4px 4px 0px #007a5e, inset 0 0 20px rgba(0,200,150,0.04);
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    image-rendering: pixelated;
  }

  .pixel-card-amber {
    background: rgba(20, 16, 40, 0.85);
    border: 2px solid #F5A623;
    border-radius: 0px;
    box-shadow: 4px 4px 0px #9a6610;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
  }

  .pixel-card-blue {
    background: rgba(14, 28, 46, 0.9);
    border: 2px solid #4FC3F7;
    border-radius: 0px;
    box-shadow: 4px 4px 0px #1a6e99;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
  }

  /* ── Header ─────────────────────────────────────────────────────── */
  .sims-hero {
    text-align: center;
    padding: 1.8rem 0 1.2rem;
  }
  .sims-hero-title {
    font-family: 'Silkscreen', monospace;
    font-size: 2.6rem;
    font-weight: 700;
    color: #00C896;
    text-shadow: 3px 3px 0px #007a5e, 0 0 30px rgba(0,200,150,0.4);
    letter-spacing: 0.05em;
    margin: 0;
    line-height: 1.15;
  }
  .sims-hero-sub {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    color: #8ecfc2;
    margin-top: 0.5rem;
    letter-spacing: 0.03em;
  }
  .plumbob-icon {
    font-size: 3.5rem;
    filter: drop-shadow(0 0 10px rgba(0,200,150,0.7));
    display: block;
    margin-bottom: 0.4rem;
  }

  /* ── Stat cards topo ─────────────────────────────────────────────── */
  .stat-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 1rem 0; }
  .stat-card {
    background: rgba(20, 16, 40, 0.9);
    border: 2px solid #2a2060;
    border-radius: 0px;
    padding: 1rem 0.8rem;
    text-align: center;
    position: relative;
    overflow: hidden;
  }
  .stat-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
  }
  .stat-card.green::before { background: #00C896; }
  .stat-card.amber::before { background: #F5A623; }
  .stat-card.blue::before  { background: #4FC3F7; }
  .stat-card.pink::before  { background: #E879F9; }

  .stat-label {
    font-family: 'Silkscreen', monospace;
    font-size: 0.55rem;
    color: #8ecfc2;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin: 0 0 6px;
  }
  .stat-value {
    font-family: 'Silkscreen', monospace;
    font-size: 1.7rem;
    color: #F0EDE8;
    margin: 0;
    line-height: 1.1;
  }
  .stat-value.green { color: #00C896; }
  .stat-value.amber { color: #F5A623; }
  .stat-value.blue  { color: #4FC3F7; }
  .stat-value.pink  { color: #E879F9; }
  .stat-sub {
    font-size: 0.7rem;
    color: #5a5575;
    margin-top: 4px;
  }

  /* ── Barras de necessidades estilo HUD ───────────────────────────── */
  .need-bar-container { margin: 6px 0; }
  .need-bar-label {
    font-family: 'Silkscreen', monospace;
    font-size: 0.6rem;
    color: #8ecfc2;
    display: flex;
    justify-content: space-between;
    margin-bottom: 3px;
  }
  .need-bar-track {
    background: #0d0b1e;
    border: 1px solid #2a2060;
    height: 10px;
    width: 100%;
    position: relative;
  }
  .need-bar-fill {
    height: 100%;
    transition: width 0.3s ease;
    image-rendering: pixelated;
  }

  /* ── Card title pixel ────────────────────────────────────────────── */
  .pixel-section-title {
    font-family: 'Silkscreen', monospace;
    font-size: 0.7rem;
    color: #00C896;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 0 0 0.8rem;
    padding-bottom: 6px;
    border-bottom: 1px solid #00C89620;
  }
  .pixel-card-blue .pixel-section-title {
    color: #4FC3F7;
    border-bottom: 1px solid #4FC3F720;
  }
  .pixel-card-amber .pixel-section-title {
    color: #F5A623;
    border-bottom: 1px solid #F5A62320;
  }

  /* ── Sidebar ─────────────────────────────────────────────────────── */
  .sidebar-section-title {
    font-family: 'Silkscreen', monospace;
    font-size: 0.62rem;
    color: #F5A623;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 1.5rem 0 0.5rem;
    padding-bottom: 4px;
    border-bottom: 1px solid rgba(245, 166, 35, 0.25);
  }

  /* Customização completa do Sidebar Streamlit */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0a22 0%, #060411 100%) !important;
    border-right: 2px solid #2a2060;
  }

  [data-testid="stSidebar"] div[data-testid="stWidgetLabel"] p {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.78rem !important;
    color: #8ecfc2 !important;
    font-weight: 500 !important;
  }

  [data-testid="stSidebar"] .stCaption {
    color: #5a5575 !important;
    font-size: 0.7rem !important;
  }

  /* Sliders customizados */
  [data-testid="stSidebar"] div[data-testid="stSlider"] [data-baseweb="slider-track"] > div {
    background: #00C896 !important;
  }
  [data-testid="stSidebar"] div[data-testid="stSlider"] [data-baseweb="slider-track"] {
    background: #2a2060 !important;
  }
  [data-testid="stSidebar"] div[data-testid="stSlider"] [data-baseweb="slider-thumb"] {
    background-color: #00C896 !important;
    border: 2px solid #0d0b1e !important;
    border-radius: 0px !important;
    box-shadow: 2px 2px 0px #007a5e !important;
    width: 14px !important;
    height: 14px !important;
  }

  /* Inputs de texto e numéricos */
  [data-testid="stSidebar"] input {
    background-color: #0d0b1e !important;
    color: #c8c4e0 !important;
    border: 1px solid #2a2060 !important;
    border-radius: 0px !important;
    font-family: 'Inter', sans-serif !important;
  }
  [data-testid="stSidebar"] input:focus {
    border-color: #00C896 !important;
    box-shadow: 0 0 5px rgba(0, 200, 150, 0.4) !important;
  }

  /* Radio Buttons */
  [data-testid="stSidebar"] [data-testid="stRadio"] label {
    color: #c8c4e0 !important;
    font-size: 0.8rem !important;
  }
  [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
    background-color: rgba(20, 16, 40, 0.5) !important;
    border: 1px solid #2a2060 !important;
    padding: 0.5rem !important;
    border-radius: 0px !important;
  }
  [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] {
    padding: 0.3rem 0.5rem !important;
  }

  /* Expander avançado */
  [data-testid="stSidebar"] [data-testid="stExpander"] {
    background-color: rgba(42, 32, 96, 0.2) !important;
    border: 1px solid #2a2060 !important;
    border-radius: 0px !important;
    margin-bottom: 0.5rem !important;
  }
  [data-testid="stSidebar"] [data-testid="stExpanderDetails"] {
    background-color: rgba(13, 11, 30, 0.4) !important;
  }

  /* Botões na sidebar */
  [data-testid="stSidebar"] .stButton > button {
    font-family: 'Silkscreen', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.05em !important;
    background: rgba(42, 32, 96, 0.4) !important;
    color: #8ecfc2 !important;
    border: 1px solid #2a2060 !important;
    border-radius: 0px !important;
    box-shadow: 2px 2px 0px #1a1040 !important;
    text-transform: uppercase !important;
  }
  [data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(0, 200, 150, 0.15) !important;
    border-color: #00C896 !important;
    color: #00C896 !important;
    box-shadow: 2px 2px 0px #007a5e !important;
  }
  [data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #00C896 !important;
    color: #0d0b1e !important;
    border: none !important;
    box-shadow: 3px 3px 0px #007a5e !important;
  }
  [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background: #00e6ad !important;
    box-shadow: 2px 2px 0px #007a5e !important;
  }

  /* ── Moodlet badges ──────────────────────────────────────────────── */
  .moodlet {
    display: inline-block;
    font-family: 'Silkscreen', monospace;
    font-size: 0.55rem;
    padding: 3px 8px;
    margin: 2px;
    border-radius: 0px;
  }
  .moodlet-green { background: #00C89620; border: 1px solid #00C896; color: #00C896; }
  .moodlet-amber { background: #F5A62320; border: 1px solid #F5A623; color: #F5A623; }
  .moodlet-red   { background: #FF4D6D20; border: 1px solid #FF4D6D; color: #FF4D6D; }
  .moodlet-blue  { background: #4FC3F720; border: 1px solid #4FC3F7; color: #4FC3F7; }

  /* ── Tabela com estilo pixel ─────────────────────────────────────── */
  .pixel-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
  .pixel-table th {
    font-family: 'Silkscreen', monospace;
    font-size: 0.58rem;
    color: #8ecfc2;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    border-bottom: 2px solid #00C896;
    padding: 6px 8px;
    text-align: left;
  }
  .pixel-table td {
    color: #c8c4e0;
    border-bottom: 1px solid #2a2060;
    padding: 7px 8px;
  }
  .pixel-table tr:hover td { background: rgba(0,200,150,0.04); }

  /* Mapa isométrico */
  .iso-map-wrapper {
    width: 100%;
    overflow: hidden;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 220px;
    background: rgba(13, 11, 30, 0.6);
    border: 2px solid #2a2060;
    margin-bottom: 1rem;
    position: relative;
  }

  /* Comparação */
  .cmp-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
  .cmp-card {
    padding: 1.2rem;
    border-radius: 0px;
  }
  .cmp-card-ag {
    background: rgba(0, 60, 40, 0.3);
    border: 2px solid #00C896;
    box-shadow: 4px 4px 0px #007a5e;
  }
  .cmp-card-al {
    background: rgba(60, 40, 0, 0.3);
    border: 2px solid #F5A623;
    box-shadow: 4px 4px 0px #9a6610;
  }
  .cmp-card-title {
    font-family: 'Silkscreen', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0 0 0.7rem;
  }
  .cmp-card-ag .cmp-card-title { color: #00C896; }
  .cmp-card-al .cmp-card-title { color: #F5A623; }
  .cmp-big {
    font-family: 'Silkscreen', monospace;
    font-size: 2.2rem;
    margin: 0 0 0.5rem;
  }
  .cmp-card-ag .cmp-big { color: #00C896; }
  .cmp-card-al .cmp-big { color: #F5A623; }
  .cmp-row {
    display: flex; justify-content: space-between;
    font-size: 0.78rem; color: #8ecfc2; margin-top: 4px;
  }

  /* Botão de otimizar */
  .stButton > button[kind="primary"] {
    font-family: 'Silkscreen', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.08em !important;
    background: #00C896 !important;
    color: #0d0b1e !important;
    border: none !important;
    border-radius: 0px !important;
    box-shadow: 3px 3px 0px #007a5e !important;
    text-transform: uppercase !important;
  }
  .stButton > button[kind="primary"]:hover {
    background: #00e6ad !important;
    box-shadow: 2px 2px 0px #007a5e !important;
    transform: translate(1px, 1px);
  }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    background: rgba(13, 11, 30, 0.8);
    border-bottom: 2px solid #2a2060;
    gap: 0;
  }
  .stTabs [data-baseweb="tab"] {
    font-family: 'Silkscreen', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.06em;
    color: #5a5575;
    border-radius: 0px;
    padding: 0.6rem 1rem;
  }
  .stTabs [aria-selected="true"] {
    color: #00C896 !important;
    border-bottom: 2px solid #00C896 !important;
    background: rgba(0, 200, 150, 0.08) !important;
  }

  /* Divider */
  hr { border-color: #2a2060 !important; }

  /* Texto geral streamlit */
  .stMarkdown p { color: #c8c4e0; }
  .stMarkdown h3 { font-family: 'Silkscreen', monospace; font-size: 0.85rem; color: #F5A623; }

  /* Expander */
  .streamlit-expanderHeader {
    font-family: 'Silkscreen', monospace;
    font-size: 0.65rem !important;
    color: #8ecfc2 !important;
  }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="sims-hero">
  <h1 class="sims-hero-title">SIMS ROUTINE OPTIMIZER</h1>
  <p class="sims-hero-sub">Otimização de rotina diária de 24h via Algoritmo Genético e Enxame de Partículas</p>
</div>
""", unsafe_allow_html=True)

st.divider()


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <p style="font-family:'Silkscreen',monospace;font-size:1rem;color:#00C896;
       text-shadow:2px 2px 0px #007a5e;margin:0 0 0.3rem;">
      CRIAR SIM
    </p>
    <p style="font-size:0.75rem;color:#8ecfc2;margin:0 0 1rem;">
      Configure o perfil do seu Sim para que o algoritmo otimize a rotina de 24h.
    </p>
    """, unsafe_allow_html=True)

    sim_name = st.text_input("Nome do Sim", value="Alex", label_visibility="visible")

    st.markdown('<p class="sidebar-section-title">TRAÇOS DE PERSONALIDADE</p>', unsafe_allow_html=True)
    st.caption("Os traços influenciam os pesos das atividades na função de avaliação de felicidade.")

    _defaults = {
        "sl_workaholic":   0.5,
        "sl_introvertido": 0.3,
        "sl_extrovertido": 0.3,
        "sl_criativo":     0.3,
        "sl_preguicoso":   0.1,
        "sl_ativo":        0.3,
        "sl_gastronomico": 0.0,
        "sl_sociavel":     0.3,
        "sl_solitario":    0.0,
    }
    for k, v in _defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if st.button("Gerar Traços Aleatórios", use_container_width=True):
        import random as _rnd
        _opts = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        for k in _defaults:
            st.session_state[k] = _rnd.choice(_opts)

    workaholic   = st.slider("Workaholic",   0.0, 1.0, step=0.1, key="sl_workaholic",
                              help="Aumenta a satisfação com atividades de trabalho e freelance.")
    introvertido = st.slider("Introvertido",  0.0, 1.0, step=0.1, key="sl_introvertido",
                              help="Prefere lazer solo; reduz o ganho de atividades sociais.")
    extrovertido = st.slider("Extrovertido",  0.0, 1.0, step=0.1, key="sl_extrovertido",
                              help="Aumenta a satisfação de interações sociais e saídas.")
    criativo     = st.slider("Criativo",      0.0, 1.0, step=0.1, key="sl_criativo",
                              help="Beneficia-se mais de pintura, música e jogos.")
    preguicoso   = st.slider("Preguiçoso",    0.0, 1.0, step=0.1, key="sl_preguicoso",
                              help="Concede bônus em atividades básicas e penalidade no trabalho.")
    ativo        = st.slider("Ativo",         0.0, 1.0, step=0.1, key="sl_ativo",
                              help="Aumenta a satisfação com exercícios e cuidados pessoais.")
    gastronomico = st.slider("Gastronômico",   0.0, 1.0, step=0.1, key="sl_gastronomico",
                              help="Aprecia alimentação de qualidade; bônus em refeições completas.")
    sociavel     = st.slider("Sociável",      0.0, 1.0, step=0.1, key="sl_sociavel",
                              help="Amplifica os benefícios de atividades sociais em grupo.")
    solitario    = st.slider("Solitário",     0.0, 1.0, step=0.1, key="sl_solitario",
                              help="Penaliza atividades sociais e valoriza atividades individuais.")

    st.markdown('<p class="sidebar-section-title">MODO DE OTIMIZAÇÃO</p>', unsafe_allow_html=True)
    run_mode = st.radio(
        "Algoritmo",
        ["AG (Algoritmo Genético)", "PSO (Enxame de Partículas)", "AG vs PSO (Comparação)"],
        index=0,
        help="Selecione a abordagem heurística para otimização da rotina.",
    )

    st.markdown('<p class="sidebar-section-title">PARÂMETROS DE OTIMIZAÇÃO</p>', unsafe_allow_html=True)
    st.caption("Parâmetros de controle para os algoritmos de busca.")

    with st.expander("Configurar parâmetros avançados"):
        pop_size    = st.slider("Tamanho da população / enxame", 20, 200, 80, 10,
                                 help="Número de soluções candidatas por iteração.")
        generations = st.slider("Gerações / Iterações",         50, 500, 150, 25,
                                 help="Número total de passos evolutivos de busca.")
        cx_rate     = st.slider("Taxa de crossover",    0.5, 1.0, 0.85, 0.05,
                                 help="Probabilidade de cruzamento entre indivíduos (apenas AG).")
        mut_rate    = st.slider("Taxa de mutação",      0.01, 0.5, 0.12, 0.01,
                                 help="Probabilidade de mutação em genes individuais (apenas AG).")
        elitism     = st.slider("Elitismo",             1, 10, 2,
                                 help="Número de melhores soluções preservadas a cada geração (apenas AG).")
        seed        = st.number_input("Semente aleatória", value=42, step=1,
                                       help="Semente para reprodutibilidade dos resultados.")

    st.markdown("---")
    run_btn = st.button("OTIMIZAR ROTINA", use_container_width=True, type="primary")

    # Info sobre o AG
    st.markdown("""
    <div style="margin-top:1rem;padding:0.8rem;background:rgba(0,200,150,0.06);
         border-left:3px solid #00C896;font-size:0.72rem;color:#8ecfc2;line-height:1.6;">
      <strong style="color:#00C896;font-family:'Silkscreen',monospace;font-size:0.6rem;">
        COMO FUNCIONA
      </strong><br>
      O AG representa cada rotina como um <em>cromossomo de 48 genes</em>
      (blocos de 30 min = 24h). A <em>função de aptidão</em> avalia felicidade,
      penalidades por necessidades críticas e diversidade de atividades.
      Seleção por torneio (k=3), crossover de 1 ponto com reparo e elitismo
      garantem convergência para rotinas de alta qualidade.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ESTADO DA SESSÃO
# ─────────────────────────────────────────────────────────────────────────────
for key in ("result", "result2", "baseline", "sim", "run_mode"):
    if key not in st.session_state:
        st.session_state[key] = None


# ─────────────────────────────────────────────────────────────────────────────
# EXECUÇÃO DO AG
# ─────────────────────────────────────────────────────────────────────────────
if run_btn:
    sim_traits = {
        "workaholic":   workaholic,
        "introvertido": introvertido,
        "extrovertido": extrovertido,
        "criativo":     criativo,
        "preguicoso":   preguicoso,
        "ativo":        ativo,
        "gastronomico": gastronomico,
        "sociavel":     sociavel,
        "solitario":    solitario,
    }
    sim = Sim(name=sim_name, traits=sim_traits)
    st.session_state.sim = sim

    ga_config = GAConfig(
        population_size=pop_size, generations=generations,
        crossover_rate=cx_rate, mutation_rate=mut_rate,
        elitism=elitism, seed=int(seed),
    )
    pso_config = PSOConfig(
        swarm_size=pop_size, iterations=generations,
        w=0.7, c1=1.5, c2=1.5, seed=int(seed),
    )

    progress_bar = st.progress(0, text="Inicializando...")
    status_text  = st.empty()

    def make_cb(label, total):
        def cb(step, best_fit):
            pct = min(step / total, 1.0)
            progress_bar.progress(pct,
                text=f"{label} — passo {step}/{total} | melhor fitness: {best_fit:.1f}")
        return cb

    t0 = time.time()
    result2 = None

    if "PSO" in run_mode and "vs" not in run_mode:
        result = run_pso(sim_traits, pso_config,
                         progress_callback=make_cb("PSO", generations))
    elif "vs" in run_mode:
        progress_bar.progress(0, text="Executando AG...")
        result  = run_ga(sim_traits, ga_config,
                         progress_callback=make_cb("AG", generations))
        progress_bar.progress(0, text="Executando PSO...")
        result2 = run_pso(sim_traits, pso_config,
                          progress_callback=make_cb("PSO", generations))
    else:
        result = run_ga(sim_traits, ga_config,
                        progress_callback=make_cb("AG", generations))

    elapsed  = time.time() - t0
    baseline = random_baseline(sim_traits, seed=int(seed))

    progress_bar.progress(1.0, text="Otimização concluída!")
    status_text.empty()

    st.session_state.result   = result
    st.session_state.result2  = result2
    st.session_state.baseline = baseline
    st.session_state.elapsed  = elapsed
    st.session_state.run_mode = run_mode
    st.session_state.generations_used = generations


# ─────────────────────────────────────────────────────────────────────────────
# HELPER PLOTLY
# ─────────────────────────────────────────────────────────────────────────────
def _plotly_defaults(fig, height=360):
    fig.update_layout(
        plot_bgcolor="#0d0b1e",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c8c4e0", family="Inter, sans-serif", size=11),
        height=height,
        margin=dict(l=10, r=16, t=36, b=36),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# RESULTADOS
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.result is not None:
    result      = st.session_state.result
    baseline    = st.session_state.baseline
    result2     = st.session_state.result2
    run_mode    = st.session_state.get("run_mode", "AG (Algoritmo Genético)")
    sim         = st.session_state.sim
    elapsed     = st.session_state.get("elapsed", 0)
    gens_used   = st.session_state.get("generations_used", generations)
    # Determinar qual resultado mostrar nas stat cards (se for Comparação, mostramos o melhor)
    best_result = result
    best_algo_label = "AG"
    if result2 is not None and result2["best_fitness"] > result["best_fitness"]:
        best_result = result2
        best_algo_label = "PSO"

    info        = best_result["best_info"]
    history     = best_result["history"]

    improvement = (
        (best_result["best_info"]["final_happiness"] - baseline["best_info"]["final_happiness"])
        / max(baseline["best_info"]["final_happiness"], 1) * 100
    )

    label_suffix = f" ({best_algo_label})" if result2 is not None else ""

    # ── Stat cards ────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="stat-card green">
          <p class="stat-label">Fitness{label_suffix}</p>
          <p class="stat-value green">{best_result['best_fitness']:.0f}</p>
          <p class="stat-sub">pontuação de aptidão</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-card amber">
          <p class="stat-label">Melhoria de Felicidade{label_suffix}</p>
          <p class="stat-value amber">{improvement:+.0f}%</p>
          <p class="stat-sub">sobre a baseline aleatória</p>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-card blue">
          <p class="stat-label">Felicidade Média{label_suffix}</p>
          <p class="stat-value blue">{info['final_happiness']:.1f}<span style="font-size:1rem">/100</span></p>
          <p class="stat-sub">média das necessidades do dia</p>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="stat-card pink">
          <p class="stat-label">Tempo de Execução</p>
          <p class="stat-value pink">{elapsed:.1f}s</p>
          <p class="stat-sub">{gens_used} gerações evoluídas</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Rotina Otimizada",
        "Evolução",
        "Necessidades",
        "Comparação Baseline",
        "AG vs PSO",
        "Testes de Desempenho",
    ])

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 1 — ROTINA OTIMIZADA
    # ═══════════════════════════════════════════════════════════════════════════
    with tab1:
        schedule = schedule_to_list(result["best_routine"])

        st.markdown(f"""
        <div class="pixel-card">
          <p class="pixel-section-title">Rotina de 24h — {sim.name}</p>
          <p style="font-size:0.8rem;color:#8ecfc2;margin:0 0 0.8rem;">
            O algoritmo encontrou a sequência de atividades que <strong style="color:#00C896">
            maximiza a felicidade</strong> de <strong style="color:#F0EDE8">{sim.name}</strong>
            com base nos traços de personalidade configurados.
            Cada bloco representa <strong>30 minutos</strong> da rotina diária.
          </p>
        </div>
        """, unsafe_allow_html=True)

        # Gantt Chart
        cat_colors = {
            "basico":   "#4FC3F7",
            "trabalho": "#FF4D6D",
            "lazer":    "#00C896",
            "social":   "#F5A623",
            "cuidado":  "#E879F9",
        }

        fig_gantt = go.Figure()
        legend_seen = set()
        for row in schedule:
            h_start    = int(row["horario_inicio"].split(":")[0]) + int(row["horario_inicio"].split(":")[1]) / 60
            h_end      = int(row["horario_fim"].split(":")[0])    + int(row["horario_fim"].split(":")[1])    / 60
            if h_end == 0: h_end = 24
            duration_h = h_end - h_start
            color      = cat_colors.get(row["categoria"], "#5a5575")
            label      = f"{row['emoji']} {row['atividade']}" if duration_h >= 1.0 else row["emoji"]
            legend_name = f"{row['emoji']} {row['atividade']}"
            show_leg    = legend_name not in legend_seen
            if show_leg: legend_seen.add(legend_name)

            fig_gantt.add_trace(go.Bar(
                x=[duration_h], base=[h_start],
                y=[row["categoria"].capitalize()],
                orientation="h",
                name=legend_name,
                showlegend=show_leg,
                marker=dict(color=color, line=dict(color="#0d0b1e", width=1.5), opacity=0.88),
                hovertemplate=(
                    f"<b>{row['emoji']} {row['atividade']}</b><br>"
                    f"🕐 {row['horario_inicio']} – {row['horario_fim']}<br>"
                    f"⏱ {row['duracao_min']} min<br>"
                    f"{row['descricao']}<extra></extra>"
                ),
                text=label, textposition="inside", insidetextanchor="middle",
                textfont=dict(color="white", size=11, family="Inter, sans-serif"),
            ))

        fig_gantt.update_layout(
            barmode="stack", bargap=0.3,
            xaxis=dict(
                title="Hora do dia", range=[0, 24],
                tickmode="linear", tick0=0, dtick=2,
                gridcolor="#2a2060", color="#c8c4e0",
                tickfont=dict(size=11, color="#8ecfc2"),
            ),
            yaxis=dict(
                gridcolor="#2a2060", color="#c8c4e0",
                tickfont=dict(size=12, color="#c8c4e0"),
            ),
            legend=dict(
                title=dict(text="Atividades", font=dict(color="#8ecfc2", size=11)),
                bgcolor="#1a1033", bordercolor="#2a2060", borderwidth=1,
                font=dict(color="#c8c4e0", size=10),
            ),
        )
        _plotly_defaults(fig_gantt, height=380)

        st.markdown('<div class="pixel-card-blue">'
                    '<p class="pixel-section-title">Gráfico de Gantt — distribuição da rotina</p>',
                    unsafe_allow_html=True)
        st.plotly_chart(fig_gantt, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Tabela detalhada
        st.markdown('<div class="pixel-card">'
                    '<p class="pixel-section-title">Tabela detalhada de atividades</p>',
                    unsafe_allow_html=True)
        df_schedule = pd.DataFrame(schedule)
        df_schedule.columns = ["Início", "Fim", "Duração (min)",
                                "Atividade", "Emoji", "Categoria", "Descrição"]
        st.dataframe(
            df_schedule[["Emoji", "Início", "Fim", "Duração (min)", "Atividade", "Categoria", "Descrição"]],
            use_container_width=True, hide_index=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Moodlets ativados
        activated_moodlets = info.get("activated_moodlets", [])
        if activated_moodlets:
            st.markdown('<div class="pixel-card">'
                        '<p class="pixel-section-title">✨ Moodlets Ativados</p>',
                        unsafe_allow_html=True)
            moodlet_html = "".join(
                f'<span class="moodlet moodlet-green">✨ {m}</span>'
                for m in activated_moodlets
            )
            st.markdown(
                f'<p style="font-size:0.8rem;color:#8ecfc2;margin-bottom:0.5rem;">'
                f'O AG encontrou sequências de atividades que ativam <strong style="color:#00C896">'
                f'{len(activated_moodlets)} moodlet(s)</strong>, gerando bônus extra de felicidade '
                f'(<strong>+{info.get("moodlet_bonus",0):.1f} pts</strong>).</p>'
                f'{moodlet_html}',
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

        # Exportação
        st.markdown('<div class="pixel-card-amber">'
                    '<p class="pixel-section-title">Exportar rotina</p>',
                    unsafe_allow_html=True)
        col_csv, col_html = st.columns(2)
        with col_csv:
            st.download_button(
                "Baixar CSV",
                data=to_csv_bytes(result["best_routine"], sim.name, result["best_fitness"]),
                file_name=f"rotina_{sim.name}.csv", mime="text/csv",
                use_container_width=True,
            )
        with col_html:
            st.download_button(
                "Baixar Relatório HTML",
                data=to_html_report(
                    result["best_routine"], sim.name,
                    result["best_fitness"], info, history,
                ).encode("utf-8"),
                file_name=f"relatorio_{sim.name}.html", mime="text/html",
                use_container_width=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)


    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 2 — EVOLUÇÃO
    # ═══════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("""
        <div class="pixel-card">
          <p class="pixel-section-title">Curva de Convergência</p>
          <p style="font-size:0.8rem;color:#8ecfc2;margin:0;">
            A curva mostra como a <strong style="color:#F5A623">melhor aptidão</strong>,
            a <strong style="color:#E879F9">aptidão média</strong> e a
            <strong style="color:#FF4D6D">pior aptidão</strong> da população evoluem
            a cada geração. A convergência indica que o algoritmo encontrou uma solução estável.
          </p>
        </div>
        """, unsafe_allow_html=True)

        gens = list(range(1, len(history["best"]) + 1))

        fig_conv = go.Figure()
        fig_conv.add_trace(go.Scatter(
            x=gens, y=history["best"], name="Melhor",
            line=dict(color="#F5A623", width=2.5),
            fill="tozeroy", fillcolor="rgba(245,166,35,0.06)",
        ))
        fig_conv.add_trace(go.Scatter(
            x=gens, y=history["mean"], name="Média",
            line=dict(color="#E879F9", width=1.8, dash="dash"),
        ))
        fig_conv.add_trace(go.Scatter(
            x=gens, y=history["worst"], name="Pior",
            line=dict(color="#FF4D6D", width=1.2, dash="dot"),
        ))
        fig_conv.update_layout(
            xaxis=dict(title="Geração", gridcolor="#2a2060", color="#c8c4e0",
                       tickfont=dict(color="#8ecfc2")),
            yaxis=dict(title="Fitness", gridcolor="#2a2060", color="#c8c4e0",
                       tickfont=dict(color="#8ecfc2")),
            legend=dict(bgcolor="#1a1033", bordercolor="#2a2060", borderwidth=1,
                        font=dict(color="#c8c4e0")),
        )
        _plotly_defaults(fig_conv, height=360)

        st.markdown('<div class="pixel-card-blue">', unsafe_allow_html=True)
        st.plotly_chart(fig_conv, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Parâmetros
        st.markdown('<div class="pixel-card">'
                    '<p class="pixel-section-title">Parâmetros utilizados nesta execução</p>',
                    unsafe_allow_html=True)
        
        cfg = result["config"]

        # Identifica dinamicamente se estamos lendo de um AG ou de um PSO
        is_pso = hasattr(cfg, "swarm_size")

        tamanho_pop = str(cfg.swarm_size) if is_pso else str(cfg.population_size)
        num_geracoes = str(cfg.iterations) if is_pso else str(cfg.generations)
        
        # Parâmetros exclusivos do AG que não existem no PSO
        taxa_cx = f"{cfg.crossover_rate:.0%}" if not is_pso else "N/A (Exclusivo do AG)"
        taxa_mut = f"{cfg.mutation_rate:.0%}" if not is_pso else "N/A (Exclusivo do AG)"
        elitismo_val = str(cfg.elitism) if not is_pso else "N/A (Exclusivo do AG)"
        selecao_tipo = "Torneio binário (k=3)" if not is_pso else "Atualização de velocidade e posição"

        params_data = [
            {"Parâmetro": "Algoritmo Ativo", "Valor": "Enxame de Partículas (PSO)" if is_pso else "Algoritmo Genético (AG)", "Justificativa": "Modo selecionado na barra lateral"},
            {"Parâmetro": "Representação", "Valor": "Cromossomo de 48 genes (1 gene = 1 bloco de 30 min)" if not is_pso else "Partícula de 48 dimensões", "Justificativa": "Cobre exatamente 24h do dia"},
            {"Parâmetro": "Tamanho da população / Enxame", "Valor": tamanho_pop, "Justificativa": "Diversidade suficiente sem custo computacional excessivo"},
            {"Parâmetro": "Gerações / Iterações", "Valor": num_geracoes, "Justificativa": "Número fixo; convergência observada antes deste limite"},
            {"Parâmetro": "Taxa de crossover", "Valor": taxa_cx, "Justificativa": "Alta recombinação promove exploração do espaço de busca"},
            {"Parâmetro": "Taxa de mutação", "Valor": taxa_mut, "Justificativa": "Mutação por cromossomo (substituição de 1 bloco aleatório)"},
            {"Parâmetro": "Elitismo", "Valor": elitismo_val, "Justificativa": "Preserva os melhores indivíduos sem modificação"},
            {"Parâmetro": "Seleção / Atualização", "Valor": selecao_tipo, "Justificativa": "Equilíbrio entre exploração e explotação do espaço de busca"},
        ]
        st.dataframe(pd.DataFrame(params_data), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)


    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 3 — NECESSIDADES
    # ═══════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("""
        <div class="pixel-card">
          <p class="pixel-section-title">Estado Final das Necessidades</p>
          <p style="font-size:0.8rem;color:#8ecfc2;margin:0;">
            Cada necessidade é modelada em uma escala de <strong>−100 a +100</strong>,
            começando em 0. Valores acima de +30 indicam estado ótimo; abaixo de −50
            geram <strong style="color:#FF4D6D">penalidades</strong> na função de aptidão.
            Os pesos determinam a contribuição de cada necessidade na felicidade geral.
          </p>
        </div>
        """, unsafe_allow_html=True)

        need_emojis = {
            "hunger": "", "energy": "", "fun": "", "social": "",
            "hygiene": "", "bladder": "", "comfort": "", "environment": "",
        }
        need_weights_display = {
            "hunger": "20%", "energy": "20%", "fun": "15%", "social": "15%",
            "hygiene": "10%", "bladder": "10%", "comfort": "5%", "environment": "5%",
        }

        col_left, col_right = st.columns([3, 2])
        with col_left:
            st.markdown('<div class="pixel-card-blue"><p class="pixel-section-title">Barras de necessidades (HUD)</p>', unsafe_allow_html=True)

            for need in NEED_KEYS:
                val = info["final_needs"].get(need, 0)
                pct = (val + 100) / 200 * 100
                if val > 30:
                    color, status = "#00C896", "ÓTIMO"
                elif val > 0:
                    color, status = "#F5A623", "BOM"
                elif val > -30:
                    color, status = "#FF8C42", "ATENÇÃO"
                else:
                    color, status = "#FF4D6D", "CRÍTICO"

                st.markdown(f"""
                <div class="need-bar-container">
                  <div class="need-bar-label">
                    <span>{need.upper()} <span style="color:#3a3060"> ({need_weights_display.get(need,"")})</span></span>
                    <span style="color:{color}">{status} {val:+.0f}</span>
                  </div>
                  <div class="need-bar-track">
                    <div class="need-bar-fill" style="width:{pct:.1f}%;background:{color};"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            # Radar
            needs_vals_radar = [(info["final_needs"].get(n, 0) + 100) / 2 for n in NEED_KEYS]
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=needs_vals_radar,
                theta=[n.capitalize() for n in NEED_KEYS],
                fill="toself",
                name=sim.name,
                line_color="#00C896",
                fillcolor="rgba(0,200,150,0.15)",
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor="#2a2060",
                                    color="#8ecfc2", tickfont=dict(color="#8ecfc2", size=9)),
                    angularaxis=dict(gridcolor="#2a2060", color="#c8c4e0",
                                     tickfont=dict(color="#c8c4e0", size=10)),
                    bgcolor="#0d0b1e",
                ),
                legend=dict(bgcolor="#1a1033", bordercolor="#2a2060", borderwidth=1,
                            font=dict(color="#c8c4e0")),
            )
            _plotly_defaults(fig_radar, height=340)

            st.markdown('<div class="pixel-card">'
                        '<p class="pixel-section-title">Radar das necessidades</p>',
                        unsafe_allow_html=True)
            st.plotly_chart(fig_radar, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Traços
            st.markdown('<div class="pixel-card-amber">'
                        '<p class="pixel-section-title">Traços de personalidade</p>',
                        unsafe_allow_html=True)
            traits_df = pd.DataFrame([
                {"Traço": t.capitalize(), "Intensidade": v}
                for t, v in sim.traits.items() if v > 0
            ])
            if not traits_df.empty:
                fig_traits = px.bar(
                    traits_df, x="Intensidade", y="Traço", orientation="h",
                    color="Intensidade",
                    color_continuous_scale=[[0,"#2a2060"],[0.5,"#F5A623"],[1,"#FF4D6D"]],
                    range_x=[0, 1],
                )
                fig_traits.update_layout(
                    xaxis=dict(gridcolor="#2a2060", color="#c8c4e0", tickfont=dict(color="#8ecfc2")),
                    yaxis=dict(gridcolor="#2a2060", color="#c8c4e0", tickfont=dict(color="#c8c4e0")),
                    coloraxis_showscale=False,
                )
                _plotly_defaults(fig_traits, height=220)
                st.plotly_chart(fig_traits, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)


    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 4 — COMPARAÇÃO
    # ═══════════════════════════════════════════════════════════════════════════
    with tab4:
        # Usar o nome do algoritmo dinamicamente se estiver em comparação ou PSO
        algo_title = f"{best_algo_label} vs. Baseline Aleatório"
        st.markdown(f"""
        <div class="pixel-card">
          <p class="pixel-section-title">{algo_title}</p>
          <p style="font-size:0.8rem;color:#8ecfc2;margin:0;">
            O algoritmo otimizador selecionado (<strong style="color:#00C896">{best_algo_label}</strong>) é comparado com uma
            <strong style="color:#F5A623">rotina aleatória</strong> gerada com a mesma semente.
            Esta comparação valida que o algoritmo agrega valor real frente a uma solução sem otimização.
          </p>
        </div>
        """, unsafe_allow_html=True)

        cats_opt = info["categories_used"]
        cats_bl = baseline["best_info"]["categories_used"]

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div class="cmp-card cmp-card-ag">
              <p class="cmp-card-title">Otimizador ({best_algo_label})</p>
              <p class="cmp-big">{info['final_happiness']:.1f} <span style="font-size:1.1rem;opacity:0.75">/ 100</span></p>
              <div class="cmp-row"><span>Categorias usadas</span><span>{len(cats_opt)}</span></div>
              <div class="cmp-row"><span>Penalidades</span><span>{info['penalties']:.0f}</span></div>
              <div class="cmp-row"><span>Bônus diversidade</span><span>+{info['diversity_bonus']}</span></div>
              <div class="cmp-row"><span>Moodlet Bônus</span><span>+{info['moodlet_bonus']:.1f}</span></div>
              <p style="font-size:0.7rem;color:#3a6050;margin-top:8px;">{' · '.join(cats_opt)}</p>
            </div>
            """, unsafe_allow_html=True)

        with col_b:
            st.markdown(f"""
            <div class="cmp-card cmp-card-al">
              <p class="cmp-card-title">Rotina Aleatória (baseline)</p>
              <p class="cmp-big">{baseline['best_info']['final_happiness']:.1f} <span style="font-size:1.1rem;opacity:0.75">/ 100</span></p>
              <div class="cmp-row"><span>Categorias usadas</span><span>{len(cats_bl)}</span></div>
              <div class="cmp-row"><span>Penalidades</span><span>{baseline['best_info']['penalties']:.0f}</span></div>
              <div class="cmp-row"><span>Bônus diversidade</span><span>+{baseline['best_info']['diversity_bonus']}</span></div>
              <div class="cmp-row"><span>Moodlet Bônus</span><span>+{baseline['best_info']['moodlet_bonus']:.1f}</span></div>
              <p style="font-size:0.7rem;color:#604a20;margin-top:8px;">{' · '.join(cats_bl)}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── NOVO: Gráfico de Gantt Comparativo ──
        st.markdown('<div class="pixel-card-blue">'
                    '<p class="pixel-section-title">Comparação de Linha do Tempo: Otimizada vs. Baseline</p>'
                    '<p style="font-size:0.8rem;color:#8ecfc2;margin:0 0 1rem;">'
                    'Compare diretamente a distribuição de atividades ao longo das 24 horas '
                    'entre a rotina otimizada e o baseline aleatório. Passe o mouse sobre as barras para ver os detalhes.'
                    '</p>', unsafe_allow_html=True)

        cat_colors = {
            "basico":   "#4FC3F7",
            "trabalho": "#FF4D6D",
            "lazer":    "#00C896",
            "social":   "#F5A623",
            "cuidado":  "#E879F9",
        }

        fig_gantt_cmp = go.Figure()
        
        # 1. Adicionar rotina otimizada
        schedule_opt = schedule_to_list(best_result["best_routine"])
        y_label_opt = f"Otimizada ({best_algo_label})"
        
        for row in schedule_opt:
            h_start    = int(row["horario_inicio"].split(":")[0]) + int(row["horario_inicio"].split(":")[1]) / 60
            h_end      = int(row["horario_fim"].split(":")[0])    + int(row["horario_fim"].split(":")[1])    / 60
            if h_end == 0: h_end = 24
            duration_h = h_end - h_start
            color      = cat_colors.get(row["categoria"], "#5a5575")
            label      = f"{row['emoji']} {row['atividade']}" if duration_h >= 1.2 else row["emoji"]

            fig_gantt_cmp.add_trace(go.Bar(
                x=[duration_h], base=[h_start],
                y=[y_label_opt],
                orientation="h",
                showlegend=False,
                marker=dict(color=color, line=dict(color="#0d0b1e", width=1.5), opacity=0.9),
                hovertemplate=(
                    f"<b>{row['emoji']} {row['atividade']}</b> ({best_algo_label})<br>"
                    f"🕐 {row['horario_inicio']} – {row['horario_fim']}<br>"
                    f"⏱ {row['duracao_min']} min<br>"
                    f"{row['descricao']}<extra></extra>"
                ),
                text=label, textposition="inside", insidetextanchor="middle",
                textfont=dict(color="white", size=10, family="Inter, sans-serif"),
            ))

        # 2. Adicionar rotina baseline aleatória
        schedule_bl = schedule_to_list(baseline["best_routine"])
        y_label_bl = "Baseline Aleatório"
        
        for row in schedule_bl:
            h_start    = int(row["horario_inicio"].split(":")[0]) + int(row["horario_inicio"].split(":")[1]) / 60
            h_end      = int(row["horario_fim"].split(":")[0])    + int(row["horario_fim"].split(":")[1])    / 60
            if h_end == 0: h_end = 24
            duration_h = h_end - h_start
            color      = cat_colors.get(row["categoria"], "#5a5575")
            label      = f"{row['emoji']} {row['atividade']}" if duration_h >= 1.2 else row["emoji"]

            fig_gantt_cmp.add_trace(go.Bar(
                x=[duration_h], base=[h_start],
                y=[y_label_bl],
                orientation="h",
                showlegend=False,
                marker=dict(color=color, line=dict(color="#0d0b1e", width=1.5), opacity=0.8),
                hovertemplate=(
                    f"<b>{row['emoji']} {row['atividade']}</b> (Baseline)<br>"
                    f"🕐 {row['horario_inicio']} – {row['horario_fim']}<br>"
                    f"⏱ {row['duracao_min']} min<br>"
                    f"{row['descricao']}<extra></extra>"
                ),
                text=label, textposition="inside", insidetextanchor="middle",
                textfont=dict(color="white", size=10, family="Inter, sans-serif"),
            ))

        fig_gantt_cmp.update_layout(
            barmode="stack", bargap=0.4,
            xaxis=dict(
                title="Hora do dia", range=[0, 24],
                tickmode="linear", tick0=0, dtick=2,
                gridcolor="#2a2060", color="#c8c4e0",
                tickfont=dict(size=11, color="#8ecfc2"),
            ),
            yaxis=dict(
                gridcolor="#2a2060", color="#c8c4e0",
                tickfont=dict(size=11, color="#c8c4e0"),
            ),
        )
        _plotly_defaults(fig_gantt_cmp, height=260)
        st.plotly_chart(fig_gantt_cmp, use_container_width=True)
        st.markdown('</div><br>', unsafe_allow_html=True)

        # Radar comparativo
        needs_opt_r  = [(info["final_needs"].get(n, 0)   + 100) / 2 for n in NEED_KEYS]
        needs_base_r = [(baseline["best_info"]["final_needs"].get(n, 0) + 100) / 2 for n in NEED_KEYS]
        labels_rad   = [n.capitalize() for n in NEED_KEYS]

        fig_radar2 = go.Figure()
        fig_radar2.add_trace(go.Scatterpolar(
            r=needs_opt_r, theta=labels_rad, fill="toself",
            name=best_algo_label, line_color="#00C896", fillcolor="rgba(0,200,150,0.15)",
        ))
        fig_radar2.add_trace(go.Scatterpolar(
            r=needs_base_r, theta=labels_rad, fill="toself",
            name="Aleatório", line_color="#F5A623", fillcolor="rgba(245,166,35,0.10)",
        ))
        fig_radar2.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="#2a2060",
                                color="#8ecfc2", tickfont=dict(color="#8ecfc2", size=9)),
                angularaxis=dict(gridcolor="#2a2060", color="#c8c4e0",
                                 tickfont=dict(color="#c8c4e0", size=11)),
                bgcolor="#0d0b1e",
            ),
            legend=dict(bgcolor="#1a1033", bordercolor="#2a2060", borderwidth=1,
                        font=dict(color="#c8c4e0")),
        )
        _plotly_defaults(fig_radar2, height=400)

        st.markdown('<div class="pixel-card-blue">'
                    f'<p class="pixel-section-title">Radar de necessidades: {best_algo_label} vs. Aleatório</p>',
                    unsafe_allow_html=True)
        st.plotly_chart(fig_radar2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if improvement > 0:
            st.success(f"O {best_algo_label} gerou uma rotina com felicidade {improvement:.1f}% maior que a solução aleatória baseline.")
        else:
            st.warning(f"O {best_algo_label} não superou o baseline nesta execução. Tente aumentar o número de gerações.")


    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 5 — AG vs PSO (COMPARAÇÃO TÉCNICA AVANÇADA)
    # ═══════════════════════════════════════════════════════════════════════════
    with tab5:
        st.markdown("""
        <div class="pixel-card">
          <p class="pixel-section-title">Comparação Técnica: AG vs PSO</p>
          <p style="font-size:0.8rem;color:#8ecfc2;margin:0;">
            Para ver a comparação ao vivo, selecione <strong style="color:#E879F9">
            AG vs PSO (Comparação)</strong> na sidebar e clique em Otimizar. Esta aba exibe
            as curvas de convergência lado a lado, métricas comparativas e análise
            do custo computacional para uma comparação científica e de desempenho.
          </p>
        </div>
        """, unsafe_allow_html=True)

        if result2 is not None:
            r1, r2 = result, result2
            alg1 = r1.get("algorithm", "AG")
            alg2 = r2.get("algorithm", "PSO")
            h1, h2 = r1["history"], r2["history"]
            gens = list(range(1, len(h1["best"]) + 1))

            # ── Cards comparativos ────────────────────────────────────────────
            col_a, col_b = st.columns(2)
            imp1 = (r1["best_info"]["final_happiness"] - baseline["best_info"]["final_happiness"]) / max(baseline["best_info"]["final_happiness"], 1) * 100
            imp2 = (r2["best_info"]["final_happiness"] - baseline["best_info"]["final_happiness"]) / max(baseline["best_info"]["final_happiness"], 1) * 100

            with col_a:
                moodlets1 = r1["best_info"].get("activated_moodlets", [])
                st.markdown(f"""
                <div class="cmp-card cmp-card-ag">
                  <p class="cmp-card-title">{alg1} — Algoritmo Genético</p>
                  <p class="cmp-big">{r1['best_fitness']:.1f}</p>
                  <div class="cmp-row"><span>Felicidade Média</span><span>{r1['best_info']['final_happiness']:.1f}/100</span></div>
                  <div class="cmp-row"><span>Melhoria de Felicidade</span><span>{imp1:+.1f}%</span></div>
                  <div class="cmp-row"><span>Penalidades</span><span>{r1['best_info']['penalties']:.0f}</span></div>
                  <div class="cmp-row"><span>Moodlet Bônus</span><span>+{r1['best_info'].get('moodlet_bonus',0):.1f}</span></div>
                  <div class="cmp-row"><span>Avaliações de fitness</span><span>{r1.get('evals_count','N/A')}</span></div>
                  <p style="font-size:0.7rem;color:#3a6050;margin-top:8px;">
                    {' · '.join(moodlets1) if moodlets1 else 'Nenhum moodlet'}</p>
                </div>
                """, unsafe_allow_html=True)

            with col_b:
                moodlets2 = r2["best_info"].get("activated_moodlets", [])
                st.markdown(f"""
                <div class="cmp-card cmp-card-al">
                  <p class="cmp-card-title">{alg2} — Enxame de Partículas</p>
                  <p class="cmp-big">{r2['best_fitness']:.1f}</p>
                  <div class="cmp-row"><span>Felicidade Média</span><span>{r2['best_info']['final_happiness']:.1f}/100</span></div>
                  <div class="cmp-row"><span>Melhoria de Felicidade</span><span>{imp2:+.1f}%</span></div>
                  <div class="cmp-row"><span>Penalidades</span><span>{r2['best_info']['penalties']:.0f}</span></div>
                  <div class="cmp-row"><span>Moodlet Bônus</span><span>+{r2['best_info'].get('moodlet_bonus',0):.1f}</span></div>
                  <div class="cmp-row"><span>Avaliações de fitness</span><span>{r2.get('evals_count','N/A')}</span></div>
                  <p style="font-size:0.7rem;color:#604a20;margin-top:8px;">
                    {' · '.join(moodlets2) if moodlets2 else 'Nenhum moodlet'}</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Curvas de convergência sobrepostas ───────────────────────────
            fig_cmp = go.Figure()
            fig_cmp.add_trace(go.Scatter(
                x=gens, y=h1["best"], name=f"{alg1} — Melhor",
                line=dict(color="#00C896", width=2.5),
                fill="tozeroy", fillcolor="rgba(0,200,150,0.05)",
            ))
            fig_cmp.add_trace(go.Scatter(
                x=gens, y=h1["mean"], name=f"{alg1} — Média",
                line=dict(color="#00C896", width=1.5, dash="dash"),
            ))
            fig_cmp.add_trace(go.Scatter(
                x=gens, y=h2["best"], name=f"{alg2} — Melhor",
                line=dict(color="#F5A623", width=2.5),
                fill="tozeroy", fillcolor="rgba(245,166,35,0.05)",
            ))
            fig_cmp.add_trace(go.Scatter(
                x=gens, y=h2["mean"], name=f"{alg2} — Média",
                line=dict(color="#F5A623", width=1.5, dash="dash"),
            ))
            # Linha do baseline
            fig_cmp.add_hline(
                y=baseline["best_fitness"],
                line_dash="dot", line_color="#FF4D6D", line_width=1.5,
                annotation_text="Baseline aleatório",
                annotation_font_color="#FF4D6D",
            )
            fig_cmp.update_layout(
                xaxis=dict(title="Geração / Iteração", gridcolor="#2a2060",
                           color="#c8c4e0", tickfont=dict(color="#8ecfc2")),
                yaxis=dict(title="Fitness", gridcolor="#2a2060",
                           color="#c8c4e0", tickfont=dict(color="#8ecfc2")),
                legend=dict(bgcolor="#1a1033", bordercolor="#2a2060", borderwidth=1,
                            font=dict(color="#c8c4e0")),
            )
            _plotly_defaults(fig_cmp, height=400)

            st.markdown('<div class="pixel-card-blue">'
                        '<p class="pixel-section-title">Curvas de Convergência: AG vs PSO vs Baseline</p>',
                        unsafe_allow_html=True)
            st.plotly_chart(fig_cmp, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # ── Tabela de métricas comparativas ─────────────────────────────
            winner = alg1 if r1["best_fitness"] >= r2["best_fitness"] else alg2
            metrics_df = pd.DataFrame([
                {"Métrica": "Melhor Fitness", alg1: f"{r1['best_fitness']:.2f}",
                 alg2: f"{r2['best_fitness']:.2f}", "Aleatório": f"{baseline['best_fitness']:.2f}"},
                {"Métrica": "Felicidade Média (/100)", alg1: f"{r1['best_info']['final_happiness']:.1f}",
                 alg2: f"{r2['best_info']['final_happiness']:.1f}", "Aleatório": f"{baseline['best_info']['final_happiness']:.1f}"},
                {"Métrica": "Melhoria de Felicidade vs Baseline", alg1: f"{imp1:+.1f}%",
                 alg2: f"{imp2:+.1f}%", "Aleatório": "0%"},
                {"Métrica": "Penalidades", alg1: f"{r1['best_info']['penalties']:.0f}",
                 alg2: f"{r2['best_info']['penalties']:.0f}", "Aleatório": f"{baseline['best_info']['penalties']:.0f}"},
                {"Métrica": "Moodlet Bônus", alg1: f"+{r1['best_info'].get('moodlet_bonus',0):.1f}",
                 alg2: f"+{r2['best_info'].get('moodlet_bonus',0):.1f}", "Aleatório": "-"},
                {"Métrica": "Avaliações de Fitness", alg1: str(r1.get("evals_count", "N/A")),
                 alg2: str(r2.get("evals_count", "N/A")), "Aleatório": "1"},
                {"Métrica": "Fitness final do pior (pior da pop.)",
                 alg1: f"{h1['worst'][-1]:.2f}", alg2: f"{h2['worst'][-1]:.2f}", "Aleatório": "-"},
            ])

            st.markdown('<div class="pixel-card">'
                        '<p class="pixel-section-title">Tabela Comparativa de Métricas</p>',
                        unsafe_allow_html=True)
            st.dataframe(metrics_df, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if r1["best_fitness"] > r2["best_fitness"]:
                diff = r1["best_fitness"] - r2["best_fitness"]
                st.success(f"O **AG** superou o PSO em **{diff:.1f} pontos** de fitness nesta execução.")
            elif r2["best_fitness"] > r1["best_fitness"]:
                diff = r2["best_fitness"] - r1["best_fitness"]
                st.success(f"O **PSO** superou o AG em **{diff:.1f} pontos** de fitness nesta execução.")
            else:
                st.info("AG e PSO obtiveram fitness idêntico nesta execução.")

            # ── Análise qualitativa ──────────────────────────────────────────
            st.markdown("""
            <div class="pixel-card-amber">
              <p class="pixel-section-title">Análise Comparativa — AG vs PSO</p>
              <div style="font-size:0.8rem;color:#c8a060;line-height:1.7;">
                <p><strong style="color:#00C896">AG (Algoritmo Genético):</strong>
                   usa representação cromossômica, seleção por torneio e crossover de dois pontos.
                   Tende a convergir mais lentamente mas com maior diversidade genética,
                   sendo eficaz em escapar de ótimos locais via mutação.</p>
                <p><strong style="color:#F5A623">PSO (Enxame de Partículas):</strong>
                   cada partícula mantém memória do próprio melhor (pbest) e do melhor global (gbest).
                   Convergência tipicamente mais rápida nas primeiras iterações,
                   mas pode estagnar prematuramente sem mecanismo de diversificação.</p>
                <p><strong style="color:#E879F9">Análise de custo computacional:</strong>
                   ambos avaliam o mesmo número de soluções por geração/iteração.
                   O PSO tem overhead ligeiramente maior por manter velocidades e pbest de cada partícula.</p>
              </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown("""
            <div class="pixel-card-amber">
              <p class="pixel-section-title">Modo de comparação não selecionado</p>
              <p style="font-size:0.8rem;color:#c8a060;">
                Para ver a comparação AG vs PSO, selecione
                <strong>AG vs PSO (Comparação)</strong> na sidebar e clique em
                <strong>Otimizar Rotina</strong>.
              </p>
            </div>
            """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 6 — RESULTADOS DOS TESTES
    # ═══════════════════════════════════════════════════════════════════════════
    with tab6:
        st.markdown("""
        <div class="pixel-card">
          <p class="pixel-section-title">Suíte de Testes — 5 Sementes × 4 Perfis (AG vs PSO)</p>
          <p style="font-size:0.8rem;color:#8ecfc2;margin:0;">
            Validação estatística com <strong>5 execuções independentes</strong> (sementes 42, 7, 123, 999, 2024)
            para cada um dos 4 perfis. Compara AG, PSO e Baseline aleatório para uma comparação científica e de desempenho.
          </p>
        </div>
        """, unsafe_allow_html=True)

        json_path = os.path.join(os.path.dirname(__file__), "results", "test_results.json")

        if os.path.exists(json_path):
            with open(json_path, encoding="utf-8") as f:
                test_data = json.load(f)

            rows = []
            for profile, r in test_data.items():
                rows.append({
                    "Perfil":              profile.capitalize(),
                    "AG média ± dp":       f"{r.get('mean_ga', 0):.2f} ± {r.get('std_ga', 0):.2f}",
                    "PSO média ± dp":      f"{r.get('mean_pso', r.get('mean_ga', 0)):.2f} ± {r.get('std_pso', r.get('std_ga', 0)):.2f}",
                    "Baseline média":      f"{r.get('mean_base', 0):.2f}",
                    "AG melhoria":         f"{r.get('mean_ga_improvement_pct', r.get('mean_improvement_pct', 0)):+.1f}%",
                    "PSO melhoria":        f"{r.get('mean_pso_improvement_pct', r.get('mean_improvement_pct', 0)):+.1f}%",
                    "AG tempo (s)":        f"{r.get('mean_ga_time_s', r.get('mean_time_s', 0)):.2f}",
                    "PSO tempo (s)":       f"{r.get('mean_pso_time_s', r.get('mean_time_s', 0)):.2f}",
                })

            st.markdown('<div class="pixel-card">'
                        '<p class="pixel-section-title">Tabela AG vs PSO vs Baseline</p>',
                        unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Barras agrupadas
            profiles = list(test_data.keys())
            ag_vals  = [test_data[p].get("mean_ga", 0)   for p in profiles]
            pso_vals = [test_data[p].get("mean_pso", test_data[p].get("mean_ga", 0)) for p in profiles]
            bl_vals  = [test_data[p].get("mean_base", 0) for p in profiles]

            fig_test = go.Figure()
            fig_test.add_trace(go.Bar(name="AG",  x=profiles, y=ag_vals,
                marker_color="#00C896", marker_line_color="#007a5e", marker_line_width=1.5))
            fig_test.add_trace(go.Bar(name="PSO", x=profiles, y=pso_vals,
                marker_color="#F5A623", marker_line_color="#9a6610", marker_line_width=1.5))
            fig_test.add_trace(go.Bar(name="Aleatório", x=profiles, y=bl_vals,
                marker_color="#FF4D6D", opacity=0.6,
                marker_line_color="#99001a", marker_line_width=1.5))
            fig_test.update_layout(
                barmode="group",
                xaxis=dict(gridcolor="#2a2060", color="#c8c4e0", tickfont=dict(color="#8ecfc2")),
                yaxis=dict(title="Fitness médio", gridcolor="#2a2060", color="#c8c4e0",
                           tickfont=dict(color="#8ecfc2")),
                legend=dict(bgcolor="#1a1033", bordercolor="#2a2060", borderwidth=1,
                            font=dict(color="#c8c4e0")),
            )
            _plotly_defaults(fig_test, height=320)

            st.markdown('<div class="pixel-card-blue">'
                        '<p class="pixel-section-title">Fitness médio: AG vs PSO vs Aleatório</p>',
                        unsafe_allow_html=True)
            st.plotly_chart(fig_test, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            chart_path = os.path.join(os.path.dirname(__file__), "results", "convergence_chart.png")
            if os.path.exists(chart_path):
                st.markdown('<div class="pixel-card">'
                            '<p class="pixel-section-title">Curvas de convergência AG vs PSO — média de 5 sementes</p>',
                            unsafe_allow_html=True)
                st.image(chart_path, width='stretch')
                st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.markdown("""
            <div class="pixel-card-amber">
              <p class="pixel-section-title">Resultados não encontrados</p>
              <p style="font-size:0.8rem;color:#c8a060;">
                Execute a suíte de testes para gerar os resultados (AG + PSO) antes da apresentação.
              </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Executar Suíte de Testes (AG + PSO)", use_container_width=True):
                with st.spinner("Executando 40 execuções (5 sementes × 4 perfis × 2 algoritmos)..."):
                    try:
                        import sys as _sys
                        _sys.path.insert(0, os.path.dirname(__file__))
                        from tests.test_runs import run_tests
                        run_tests()
                        st.success("Testes concluídos!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as err:
                        st.error(f"Erro: {err}")




else:
    col_info, col_acts = st.columns([3, 2])

    with col_info:
        st.markdown("""
        <div class="pixel-card-blue">
          <p class="pixel-section-title">Como usar este otimizador</p>
          <div style="font-size:0.82rem;color:#b3e5fc;line-height:1.8;">
            <p><strong style="color:#00C896;font-family:'Silkscreen',monospace;font-size:0.65rem;">
              1 · CRIAR SEU SIM
            </strong><br>
            Configure o nome e os traços de personalidade na barra lateral.
            Traços influenciam diretamente quais atividades rendem mais felicidade.</p>
            <p><strong style="color:#F5A623;font-family:'Silkscreen',monospace;font-size:0.65rem;">
              2 · CONFIGURAR PARÂMETROS
            </strong><br>
            Ajuste os parâmetros evolutivos ou use os valores padrão (população de 80,
            150 gerações). Valores maiores = melhor exploração, mais tempo.</p>
            <p><strong style="color:#E879F9;font-family:'Silkscreen',monospace;font-size:0.65rem;">
              3 · OTIMIZAR
            </strong><br>
            Clique em "Otimizar Rotina". O algoritmo gerará uma rotina completa de 24h.</p>
            <p><strong style="color:#4FC3F7;font-family:'Silkscreen',monospace;font-size:0.65rem;">
              4 · ANALISAR
            </strong><br>
            Explore as abas: veja a rotina em Gantt, a curva de convergência,
            o estado das necessidades e a comparação com a baseline aleatória.</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="pixel-card">
          <p class="pixel-section-title">Funcionamento do Algoritmo Genético</p>
          <div style="font-size:0.8rem;color:#8ecfc2;line-height:1.7;">
            <p>O espaço de busca possui mais de <strong style="color:#00C896">20⁴⁸</strong>
            combinações possíveis (20 atividades × 48 blocos). Busca exaustiva é inviável —
            o AG encontra soluções de alta qualidade de forma eficiente em dezenas de gerações.</p>
            <p><strong>Representação:</strong> cromossomo de 48 genes (blocos de 30 min)<br>
            <strong>Seleção:</strong> torneio binário k=3<br>
            <strong>Crossover:</strong> um ponto com reparo de consistência<br>
            <strong>Mutação:</strong> substituição de um bloco aleatório<br>
            <strong>Fitness:</strong> felicidade ponderada − penalidades + bônus diversidade</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="pixel-card-amber">
          <p class="pixel-section-title">Funcionamento do Enxame de Partículas (PSO)</p>
          <div style="font-size:0.8rem;color:#c8a060;line-height:1.7;">
            <p>Inspirado na inteligência coletiva de bandos de aves. Em vez de evolução genética,
            o PSO move uma população de soluções (partículas) ajustando suas "velocidades"
            em direção aos melhores históricos individuais e do grupo.</p>
            <p><strong>Representação:</strong> partícula (vetor de 48 blocos de atividades)<br>
            <strong>Velocidade:</strong> probabilidade de alteração de cada gene/bloco<br>
            <strong>Atração Cognitiva (c1):</strong> atração em direção ao próprio melhor histórico (pbest)<br>
            <strong>Atração Social (c2):</strong> atração em direção ao melhor global do enxame (gbest)<br>
            <strong>Reparo:</strong> filtro de consistência discreto após atualização de posição</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_acts:
        st.markdown("""
        <div class="pixel-card-blue">
          <p class="pixel-section-title">Atividades disponíveis (20)</p>
        """, unsafe_allow_html=True)
        acts_data = [
            {
                "": a.emoji,
                "Atividade": a.name,
                "Cat.": a.category.capitalize(),
                "Duração": f"{a.duration_blocks * 30} min",
            }
            for a in ACTIVITIES.values()
        ]
        st.dataframe(pd.DataFrame(acts_data), width='stretch', hide_index=True, height=460)
        st.markdown('</div>', unsafe_allow_html=True)