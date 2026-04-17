import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.mock_data import get_historical_df

st.set_page_config(page_title="Analytique · Cantine+", page_icon="📈", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FAFAFA; }
    h1, h2, h3 { color: #2E7D32 !important; }
    [data-testid="stMetric"] {
        background: white; border-radius: 16px;
        padding: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📈 Analytique")
    st.divider()
    df_full = get_historical_df()
    cantines = ["Toutes"] + sorted(df_full["cantine"].unique().tolist())
    cantine_sel = st.selectbox("🏫 Cantine", cantines)
    meteos = ["Toutes"] + sorted(df_full["meteo"].unique().tolist())
    meteo_sel = st.selectbox("🌤️ Météo", meteos)

df = df_full.copy()
df["date"] = pd.to_datetime(df["date"])
if cantine_sel != "Toutes":
    df = df[df["cantine"] == cantine_sel]
if meteo_sel != "Toutes":
    df = df[df["meteo"] == meteo_sel]

st.markdown("# 📈 Analyse des données")
st.markdown(f"*{cantine_sel} · {len(df)} repas analysés*")
st.divider()

# ── Onglets ───────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🍽️ Popularité", "🗑️ Gaspillage", "🌿 CO₂ & Coûts", "📊 Comparatifs"])

# ── Onglet 1 : Popularité ─────────────────────────────────────
with tab1:
    st.markdown("### 🍽️ Plats les plus et moins appréciés")

    col1, col2 = st.columns(2)
    with col1:
        top_plats = (
            df.groupby("plat")["taux_participation"].mean()
            .sort_values(ascending=False).head(8).reset_index()
        )
        top_plats.columns = ["Plat", "Participation (%)"]
        fig = px.bar(
            top_plats, x="Participation (%)", y="Plat", orientation="h",
            color="Participation (%)",
            color_continuous_scale=["#C8E6C9", "#4CAF50", "#1B5E20"],
            title="Top 8 plats – Taux de participation",
        )
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                          coloraxis_showscale=False, height=380, margin=dict(t=40))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        worst_plats = (
            df.groupby("plat")["taux_participation"].mean()
            .sort_values().head(8).reset_index()
        )
        worst_plats.columns = ["Plat", "Participation (%)"]
        fig2 = px.bar(
            worst_plats, x="Participation (%)", y="Plat", orientation="h",
            color="Participation (%)",
            color_continuous_scale=["#FFCDD2", "#F44336", "#B71C1C"],
            title="Flop 8 plats – Taux de participation",
        )
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           coloraxis_showscale=False, height=380, margin=dict(t=40))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### 📊 Score de popularité par catégorie")
    col_e, col_d = st.columns(2)
    with col_e:
        pop_entrees = (
            df.groupby("entree")["taux_participation"].mean()
            .sort_values(ascending=False).head(6).reset_index()
        )
        fig_e = px.bar(pop_entrees, x="entree", y="taux_participation",
                       color_discrete_sequence=["#81C784"],
                       labels={"entree": "Entrée", "taux_participation": "Participation (%)"},
                       title="Entrées – popularité")
        fig_e.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=280, margin=dict(t=40))
        st.plotly_chart(fig_e, use_container_width=True)

    with col_d:
        pop_desserts = (
            df.groupby("dessert")["taux_participation"].mean()
            .sort_values(ascending=False).head(6).reset_index()
        )
        fig_d = px.bar(pop_desserts, x="dessert", y="taux_participation",
                       color_discrete_sequence=["#FFB74D"],
                       labels={"dessert": "Dessert", "taux_participation": "Participation (%)"},
                       title="Desserts – popularité")
        fig_d.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=280, margin=dict(t=40))
        st.plotly_chart(fig_d, use_container_width=True)

# ── Onglet 2 : Gaspillage ─────────────────────────────────────
with tab2:
    st.markdown("### 🗑️ Analyse du gaspillage")

    col1, col2 = st.columns([2, 1])
    with col1:
        df_jour = df.groupby("jour_semaine")["taux_gaspillage"].mean().reset_index()
        ordre = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        labels_fr = {"Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi",
                     "Thursday": "Jeudi", "Friday": "Vendredi"}
        df_jour["jour_semaine"] = df_jour["jour_semaine"].map(labels_fr)
        df_jour = df_jour.dropna()
        fig_jour = px.bar(
            df_jour, x="jour_semaine", y="taux_gaspillage",
            color="taux_gaspillage",
            color_continuous_scale=["#A5D6A7", "#F44336"],
            labels={"taux_gaspillage": "Gaspillage (%)", "jour_semaine": "Jour"},
            title="Gaspillage moyen par jour de la semaine",
        )
        fig_jour.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                               coloraxis_showscale=False, height=320, margin=dict(t=40))
        st.plotly_chart(fig_jour, use_container_width=True)

    with col2:
        df_meteo = df.groupby("meteo")["taux_gaspillage"].mean().reset_index()
        fig_m = px.pie(
            df_meteo, values="taux_gaspillage", names="meteo",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title="Gaspillage par météo", hole=0.4,
        )
        fig_m.update_layout(height=320, margin=dict(t=40), paper_bgcolor="white")
        st.plotly_chart(fig_m, use_container_width=True)

    st.markdown("### 🥩 Gaspillage par plat principal")
    waste_plat = (
        df.groupby("plat")["taux_gaspillage"].mean()
        .sort_values(ascending=False).reset_index()
    )
    waste_plat.columns = ["Plat", "Taux de gaspillage (%)"]
    fig_wp = px.bar(
        waste_plat, x="Plat", y="Taux de gaspillage (%)",
        color="Taux de gaspillage (%)",
        color_continuous_scale=["#C8E6C9", "#F44336"],
    )
    fig_wp.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                         coloraxis_showscale=False, height=340,
                         xaxis_tickangle=-35, margin=dict(t=10))
    st.plotly_chart(fig_wp, use_container_width=True)

    st.markdown("### 📊 Prévision vs Réel (convives)")
    df_sample = df.tail(30).copy()
    fig_pv = go.Figure()
    fig_pv.add_trace(go.Bar(x=df_sample["date"].astype(str),
                            y=df_sample["nb_convives_prevus"],
                            name="Prévus", marker_color="#81C784"))
    fig_pv.add_trace(go.Bar(x=df_sample["date"].astype(str),
                            y=df_sample["nb_convives_reels"],
                            name="Réels", marker_color="#4CAF50"))
    fig_pv.update_layout(barmode="group", plot_bgcolor="white", paper_bgcolor="white",
                         height=300, margin=dict(t=10), xaxis_tickangle=-45)
    st.plotly_chart(fig_pv, use_container_width=True)

# ── Onglet 3 : CO2 & Coûts ────────────────────────────────────
with tab3:
    st.markdown("### 🌿 Empreinte carbone & Économies")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("CO₂ moyen / repas", f"{df['co2_kg'].mean():.2f} kg")
    c2.metric("CO₂ total estimé", f"{(df['co2_kg'] * df['nb_convives_reels']).sum() / 1000:.1f} t")
    c3.metric("Coût moyen / repas", f"{df['cout_repas'].mean():.2f} €")
    c4.metric("Coût total estimé", f"{(df['cout_repas'] * df['nb_convives_reels']).sum():,.0f} €")

    col1, col2 = st.columns(2)
    with col1:
        co2_plat = df.groupby("plat")["co2_kg"].mean().sort_values(ascending=False).reset_index()
        fig_co2 = px.bar(
            co2_plat, x="plat", y="co2_kg",
            color="co2_kg",
            color_continuous_scale=["#C8E6C9", "#1B5E20"],
            labels={"co2_kg": "CO₂ (kg)", "plat": "Plat"},
            title="Empreinte CO₂ par plat",
        )
        fig_co2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                              coloraxis_showscale=False, height=340,
                              xaxis_tickangle=-35, margin=dict(t=40))
        st.plotly_chart(fig_co2, use_container_width=True)

    with col2:
        cout_plat = df.groupby("plat")["cout_repas"].mean().sort_values(ascending=False).reset_index()
        fig_cout = px.bar(
            cout_plat, x="plat", y="cout_repas",
            color="cout_repas",
            color_continuous_scale=["#FFF9C4", "#FF9800"],
            labels={"cout_repas": "Coût (€)", "plat": "Plat"},
            title="Coût moyen par plat",
        )
        fig_cout.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                               coloraxis_showscale=False, height=340,
                               xaxis_tickangle=-35, margin=dict(t=40))
        st.plotly_chart(fig_cout, use_container_width=True)

    st.markdown("### 💰 Économies réalisées grâce à la réduction du gaspillage")
    df["date"] = pd.to_datetime(df["date"])
    df["mois"] = df["date"].dt.to_period("M").astype(str)
    df["cout_gaspille"] = df["cout_repas"] * df["nb_convives_reels"] * (df["taux_gaspillage"] / 100)
    df_econ = df.groupby("mois")["cout_gaspille"].sum().reset_index()
    df_econ.columns = ["Mois", "Coût gaspillé (€)"]
    fig_econ = px.area(df_econ, x="Mois", y="Coût gaspillé (€)",
                       color_discrete_sequence=["#F44336"],
                       title="Coût mensuel dû au gaspillage")
    fig_econ.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           height=300, margin=dict(t=40), xaxis_tickangle=-20)
    st.plotly_chart(fig_econ, use_container_width=True)

# ── Onglet 4 : Comparatifs ────────────────────────────────────
with tab4:
    st.markdown("### 📊 Comparatif entre cantines")
    comp = df_full.groupby("cantine")[["taux_gaspillage", "taux_participation", "co2_kg", "cout_repas"]].mean().reset_index()
    comp.columns = ["Cantine", "Gaspillage (%)", "Participation (%)", "CO₂ (kg)", "Coût (€)"]

    fig_comp = px.bar(
        comp.melt(id_vars="Cantine"),
        x="variable", y="value", color="Cantine",
        barmode="group",
        color_discrete_sequence=["#4CAF50", "#81C784", "#C8E6C9"],
        labels={"variable": "Indicateur", "value": "Valeur"},
    )
    fig_comp.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           height=380, margin=dict(t=20))
    st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("### 📅 Corrélation popularité ↔ gaspillage")
    fig_scatter = px.scatter(
        df, x="popularite_score", y="taux_gaspillage",
        color="cantine", size="nb_convives_reels",
        color_discrete_sequence=["#4CAF50", "#FF9800", "#2196F3"],
        labels={"popularite_score": "Score popularité", "taux_gaspillage": "Gaspillage (%)"},
    )
    fig_scatter.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                              height=360, margin=dict(t=20))
    st.plotly_chart(fig_scatter, use_container_width=True)
