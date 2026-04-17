import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.mock_data import get_historical_df, get_current_week_kpis, get_current_week_menu

st.set_page_config(page_title="Dashboard · Cantine+", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FAFAFA; }
    [data-testid="stMetric"] {
        background: white; border-radius: 16px;
        padding: 1rem 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    h1, h2, h3 { color: #2E7D32 !important; }
    .stButton > button {
        background: #4CAF50; color: white; border: none;
        border-radius: 12px; font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar filtres ───────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Dashboard")
    st.divider()
    df_full = get_historical_df()
    cantines = ["Toutes"] + sorted(df_full["cantine"].unique().tolist())
    cantine_sel = st.selectbox("🏫 Cantine", cantines)
    st.divider()
    periode = st.selectbox("📅 Période", ["30 derniers jours", "60 derniers jours", "6 mois"])
    jours_map = {"30 derniers jours": 30, "60 derniers jours": 60, "6 mois": 180}
    nb_jours = jours_map[periode]

# ── Filtrage données ──────────────────────────────────────────
df = df_full.copy()
df["date"] = pd.to_datetime(df["date"])
cutoff = df["date"].max() - pd.Timedelta(days=nb_jours)
df = df[df["date"] >= cutoff]
if cantine_sel != "Toutes":
    df = df[df["cantine"] == cantine_sel]

# ── Header ────────────────────────────────────────────────────
st.markdown("# 📊 Vue d'ensemble")
st.markdown(f"*{cantine_sel} · {periode}*")
st.divider()

# ── KPIs ──────────────────────────────────────────────────────
kpis = get_current_week_kpis()
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("🗑️ Taux de gaspillage", f"{df['taux_gaspillage'].mean():.1f}%",
          f"{kpis['waste_delta']:+.1f}% vs mois préc.")
c2.metric("👥 Taux de participation", f"{df['taux_participation'].mean():.1f}%",
          f"{kpis['participation_delta']:+.1f}% vs mois préc.")
c3.metric("💰 Coût moyen/repas", f"{df['cout_repas'].mean():.2f} €")
c4.metric("🌿 CO₂ moyen/repas", f"{df['co2_kg'].mean():.2f} kg")
c5.metric("♻️ Repas solidaires", str(kpis["repas_solidaires"]))

st.divider()

# ── Graphiques principaux ─────────────────────────────────────
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown("### 📉 Évolution du gaspillage et de la participation")
    df_daily = df.groupby("date")[["taux_gaspillage", "taux_participation"]].mean().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_daily["date"], y=df_daily["taux_gaspillage"],
        name="Gaspillage (%)", line=dict(color="#F44336", width=2),
        fill="tozeroy", fillcolor="rgba(244,67,54,0.08)"
    ))
    fig.add_trace(go.Scatter(
        x=df_daily["date"], y=df_daily["taux_participation"],
        name="Participation (%)", line=dict(color="#4CAF50", width=2),
        yaxis="y2"
    ))
    fig.update_layout(
        yaxis=dict(title="Gaspillage (%)", color="#F44336"),
        yaxis2=dict(title="Participation (%)", overlaying="y", side="right", color="#4CAF50"),
        legend=dict(orientation="h", y=-0.2),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=20, b=40),
        height=320,
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("### 🥧 Répartition par cantine")
    df_cantine = df_full.groupby("cantine")["taux_gaspillage"].mean().reset_index()
    fig_pie = px.pie(
        df_cantine, values="taux_gaspillage", names="cantine",
        color_discrete_sequence=["#4CAF50", "#81C784", "#C8E6C9"],
        hole=0.45,
    )
    fig_pie.update_layout(
        showlegend=True, margin=dict(t=10, b=10),
        height=320, plot_bgcolor="white", paper_bgcolor="white"
    )
    fig_pie.update_traces(textinfo="percent+label")
    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# ── Coût & CO2 ────────────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### 💰 Coût hebdomadaire estimé")
    df_week = df.copy()
    df_week["semaine"] = df_week["date"].dt.to_period("W").astype(str)
    df_cost = df_week.groupby("semaine").apply(
        lambda x: (x["cout_repas"] * x["nb_convives_reels"]).sum()
    ).reset_index(name="cout_total")
    fig_cost = px.bar(
        df_cost.tail(12), x="semaine", y="cout_total",
        color_discrete_sequence=["#FF9800"],
        labels={"cout_total": "Coût (€)", "semaine": "Semaine"},
    )
    fig_cost.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=10), height=280,
        xaxis_tickangle=-45,
    )
    st.plotly_chart(fig_cost, use_container_width=True)

with col_b:
    st.markdown("### 🌿 Empreinte CO₂ par semaine")
    df_co2 = df_week.groupby("semaine").apply(
        lambda x: (x["co2_kg"] * x["nb_convives_reels"]).sum()
    ).reset_index(name="co2_total")
    fig_co2 = px.area(
        df_co2.tail(12), x="semaine", y="co2_total",
        color_discrete_sequence=["#4CAF50"],
        labels={"co2_total": "CO₂ total (kg)", "semaine": "Semaine"},
    )
    fig_co2.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=10), height=280,
        xaxis_tickangle=-45,
    )
    st.plotly_chart(fig_co2, use_container_width=True)

st.divider()

# ── Menu de la semaine ────────────────────────────────────────
st.markdown("### 🍽️ Menu de la semaine en cours")
menu_df = get_current_week_menu()
menu_df.columns = ["Jour", "Date", "Entrée", "Plat", "Accompagnement", "Dessert", "Coût (€)", "CO₂ (kg)"]

def color_row(row):
    return ["background-color: #F1F8E9" if i % 2 == 0 else "" for i in range(len(row))]

st.dataframe(
    menu_df.style.apply(color_row, axis=1),
    use_container_width=True,
    hide_index=True,
)

# ── IA Recommandations ────────────────────────────────────────
st.divider()
st.markdown("### 🤖 Recommandations IA")
col_ia1, col_ia2, col_ia3 = st.columns(3)
avg_waste = df["taux_gaspillage"].mean()
avg_part = df["taux_participation"].mean()

with col_ia1:
    niveau = "🟢 Faible" if avg_waste < 15 else ("🟡 Moyen" if avg_waste < 25 else "🔴 Élevé")
    st.info(f"**Score risque gaspillage** · {niveau}\nMoyenne : {avg_waste:.1f}%")
with col_ia2:
    top_plat = df.groupby("plat")["taux_participation"].mean().idxmax()
    st.success(f"**Plat le plus populaire**\n{top_plat}")
with col_ia3:
    worst_plat = df.groupby("plat")["taux_gaspillage"].mean().idxmax()
    st.warning(f"**Suggestion d'optimisation**\nRéduire les portions de : {worst_plat}")
