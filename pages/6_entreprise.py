import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.mock_data import (
    get_enterprise_kpis, get_enterprise_menu, get_enterprise_top_plats,
    get_gaspillage_prevision, PLATS, CO2_PAR_PLAT, COUT_PAR_REPAS, POPULARITE,
)

st.set_page_config(page_title="Espace Entreprise · Cantine+", page_icon="💼", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F8F9FA; }
    h1 { color: #263238 !important; }
    h2, h3 { color: #37474F !important; }
    .stButton > button {
        border-radius: 10px; font-weight: 600; border: none;
        padding: 0.5rem 1.2rem; transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background: #E8F5E9; color: #2E7D32 !important; font-weight: 600;
    }
    [data-testid="stMetric"] {
        background: white; border-radius: 12px;
        padding: 1rem; box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        border-left: 4px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────
if "resa_semaine" not in st.session_state:
    st.session_state.resa_semaine = {}
if "vote_entreprise" not in st.session_state:
    st.session_state.vote_entreprise = {}
if "notation_envoyee" not in st.session_state:
    st.session_state.notation_envoyee = False

kpis = get_enterprise_kpis()
menu_weeks = get_enterprise_menu()
today = datetime.today()

with st.sidebar:
    st.markdown("## 💼 Espace Entreprise")
    st.divider()
    st.markdown("**Utilisateur :** Jean Martin")
    st.markdown("**Service :** Informatique")
    st.markdown("**Site :** Paris – Tour A")
    st.divider()
    vue = st.radio("Vue", ["👨‍💼 Mon espace", "📊 Dashboard RH"])

st.markdown("# 💼 Espace Entreprise")
st.markdown("*Restauration collective – Tableau de bord professionnel*")
st.divider()

# ═══════════════════════════════════════════════════════════════
# VUE SALARIÉ
# ═══════════════════════════════════════════════════════════════
if vue == "👨‍💼 Mon espace":
    st.markdown("## 👨‍💼 Mon espace salarié")

    tab_menu, tab_resa, tab_feedback = st.tabs([
        "🍽️ Menu prévisionnel",
        "✅ Mes réservations",
        "⭐ Notation post-repas",
    ])

    # ─── Onglet menu ──────────────────────────────────────────
    with tab_menu:
        st.markdown("### 📅 Menu sur 4 semaines")
        st.caption("Consultez et votez pour les menus à venir. L'IA adapte les propositions selon les votes collectifs.")

        for week in menu_weeks:
            with st.expander(f"📆 {week['semaine']} — {week['jours'][0]['date']} au {week['jours'][4]['date']}", expanded=(week == menu_weeks[0])):
                cols = st.columns(5)
                for day, col in zip(week["jours"], cols):
                    co2 = day["co2"]
                    co2_color = "#4CAF50" if co2 < 2 else ("#FF9800" if co2 < 4 else "#F44336")
                    vote_key = f"ent_{week['semaine']}_{day['jour']}"
                    vote_actuel = st.session_state.vote_entreprise.get(vote_key)
                    with col:
                        st.markdown(f"""
                        <div style='background:white; border-radius:12px; padding:0.9rem;
                                    box-shadow:0 2px 6px rgba(0,0,0,0.07);
                                    border-top:3px solid #4CAF50; min-height:220px;'>
                            <b style='color:#37474F'>{day['jour']}</b><br>
                            <small style='color:#888'>{day['date']}</small><br><hr style='margin:0.4rem 0'>
                            <small><b>Entrée</b><br>{day['entree'][:22]}</small><br>
                            <small><b style='color:#4CAF50'>Plat</b><br>{day['plat'][:22]}</small><br>
                            <small><b>Dessert</b><br>{day['dessert'][:22]}</small><br>
                            <hr style='margin:0.4rem 0; border-color:#f0f0f0'>
                            <small style='color:{co2_color}'>🌿 {co2} kg CO₂</small><br>
                            <small style='color:#607D8B'>💰 {day["cout"]} €</small><br>
                            <small style='color:#888'>⭐ {day["popularite"]}% pop.</small>
                        </div>
                        """, unsafe_allow_html=True)

                        c1, c2 = st.columns(2)
                        with c1:
                            lbl = "👍✓" if vote_actuel == "pour" else "👍"
                            if st.button(lbl, key=f"vp_{vote_key}", use_container_width=True):
                                st.session_state.vote_entreprise[vote_key] = "pour"
                                st.rerun()
                        with c2:
                            lbl = "👎✓" if vote_actuel == "contre" else "👎"
                            if st.button(lbl, key=f"vc_{vote_key}", use_container_width=True):
                                st.session_state.vote_entreprise[vote_key] = "contre"
                                st.rerun()

        votes_p = sum(1 for v in st.session_state.vote_entreprise.values() if v == "pour")
        votes_c = sum(1 for v in st.session_state.vote_entreprise.values() if v == "contre")
        if st.session_state.vote_entreprise:
            st.info(f"📊 Vos votes : **{votes_p} 👍** favorables · **{votes_c} 👎** défavorables")

    # ─── Onglet réservations ──────────────────────────────────
    with tab_resa:
        st.markdown("### ✅ Mes réservations – Semaine en cours")
        st.caption("Réservez avant 9h le matin. Choisissez votre portion pour aider à réduire le gaspillage.")

        week_current = menu_weeks[0]
        jours_semaine = week_current["jours"]

        for day in jours_semaine:
            resa_key = f"resa_{day['jour']}"
            portion_key = f"portion_{day['jour']}"
            resa_actuelle = st.session_state.resa_semaine.get(resa_key, False)

            plat = day["plat"]
            co2 = day["co2"]
            co2_color = "#4CAF50" if co2 < 2 else ("#FF9800" if co2 < 4 else "#F44336")

            with st.container():
                col_jour, col_plat, col_portion, col_action = st.columns([1, 3, 2, 1])

                with col_jour:
                    st.markdown(f"**{day['jour']}**")
                    st.caption(day["date"])

                with col_plat:
                    st.markdown(f"**{plat}**")
                    st.caption(f"Entrée : {day['entree']} · Dessert : {day['dessert']}")
                    st.markdown(
                        f"<small style='color:{co2_color}'>🌿 CO₂ : {co2} kg</small> &nbsp; "
                        f"<small style='color:#607D8B'>💰 {day['cout']} €</small>",
                        unsafe_allow_html=True
                    )

                with col_portion:
                    portion = st.selectbox(
                        "Portion",
                        ["🥗 Petite", "🍽️ Normale", "💪 Grande"],
                        key=portion_key,
                        disabled=not resa_actuelle,
                        label_visibility="collapsed",
                    )

                with col_action:
                    if resa_actuelle:
                        if st.button("❌ Annuler", key=f"ann_{day['jour']}", use_container_width=True):
                            st.session_state.resa_semaine[resa_key] = False
                            st.rerun()
                    else:
                        if st.button("✅ Réserver", key=f"res_{day['jour']}", use_container_width=True, type="primary"):
                            st.session_state.resa_semaine[resa_key] = True
                            st.rerun()

                if resa_actuelle:
                    st.markdown(
                        f"<small style='color:#4CAF50'>✅ Réservé · {portion}</small>",
                        unsafe_allow_html=True
                    )

            st.divider()

        nb_resa = sum(1 for v in st.session_state.resa_semaine.values() if v)
        st.markdown(f"""
        <div style='background:#E8F5E9; border-radius:12px; padding:1rem;
                    border-left:5px solid #4CAF50;'>
            <b style='color:#2E7D32'>🌱 {nb_resa} repas réservé(s) cette semaine</b><br>
            <small style='color:#555'>Vos réservations permettent à la cantine de réduire le gaspillage alimentaire. Merci !</small>
        </div>
        """, unsafe_allow_html=True)

    # ─── Onglet feedback ──────────────────────────────────────
    with tab_feedback:
        st.markdown("### ⭐ Notation post-repas")
        st.caption("Votre avis améliore les propositions futures.")

        if st.session_state.notation_envoyee:
            st.success("✅ Merci pour votre note ! Elle a été prise en compte.")
            if st.button("📝 Noter un autre repas"):
                st.session_state.notation_envoyee = False
                st.rerun()
        else:
            col_f1, col_f2 = st.columns(2)

            with col_f1:
                plat_a_noter = st.selectbox("Plat à noter", PLATS["plats"])
                note = st.slider("⭐ Note globale", 1, 5, 4)
                etoiles = "⭐" * note + "☆" * (5 - note)
                st.markdown(f"**{etoiles}** ({note}/5)")

            with col_f2:
                portion_consommee = st.radio(
                    "Portion consommée",
                    ["🍽️ Tout mangé", "🥣 Environ la moitié", "🙈 Peu ou rien"],
                )
                qualite = st.radio(
                    "Qualité perçue",
                    ["Excellente", "Bonne", "Moyenne", "Insuffisante"],
                )
                commentaire = st.text_area(
                    "Commentaire (optionnel)",
                    placeholder="Ex : Plat trop salé, mais l'accompagnement était très bon...",
                    max_chars=200,
                )

            co2_plat = CO2_PAR_PLAT.get(plat_a_noter, 2.5)
            co2_color = "#4CAF50" if co2_plat < 2 else ("#FF9800" if co2_plat < 4 else "#F44336")
            st.markdown(f"""
            <div style='background:#F8F9FA; border-radius:12px; padding:0.8rem;
                        border-left:4px solid {co2_color}; margin-bottom:1rem;'>
                <small style='color:#555'>
                    🌿 Empreinte carbone de <b>{plat_a_noter}</b> :
                    <b style='color:{co2_color}'>{co2_plat} kg CO₂</b> par portion
                </small>
            </div>
            """, unsafe_allow_html=True)

            if st.button("📤 Envoyer ma notation", type="primary"):
                st.session_state.notation_envoyee = True
                st.rerun()

# ═══════════════════════════════════════════════════════════════
# VUE DASHBOARD RH / GESTIONNAIRE
# ═══════════════════════════════════════════════════════════════
else:
    st.markdown("## 📊 Dashboard Gestionnaire Entreprise")

    # ─── KPIs ──────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(
        "✅ Taux de réservation",
        f"{kpis['reservations_taux']}%",
        f"{kpis['reservations_delta']:+.1f}% vs mois préc."
    )
    k2.metric(
        "⭐ Satisfaction",
        f"{kpis['satisfaction_note']}/5",
        f"{kpis['satisfaction_delta']:+.1f} vs mois préc."
    )
    k3.metric(
        "🌿 CO₂ / repas",
        f"{kpis['co2_par_repas']} kg",
        f"{kpis['co2_delta']:+.1f} kg vs mois préc."
    )
    k4.metric(
        "♻️ Réduction gaspillage",
        f"{kpis['reduction_gaspillage']}%",
        f"+{kpis['reduction_delta']}% vs mois préc."
    )

    st.divider()

    # ─── Top plats ─────────────────────────────────────────────
    col_top, col_prev = st.columns([3, 2])

    with col_top:
        st.markdown("### 🏆 Top 10 plats – Satisfaction salariés")
        df_top = get_enterprise_top_plats()
        fig_top = px.bar(
            df_top, x="Satisfaction (%)", y="Plat", orientation="h",
            color="Satisfaction (%)",
            color_continuous_scale=["#C8E6C9", "#4CAF50", "#1B5E20"],
            text="Satisfaction (%)",
        )
        fig_top.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_top.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            coloraxis_showscale=False, height=400,
            margin=dict(t=20, b=10), font=dict(size=12),
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig_top, use_container_width=True)

    with col_prev:
        st.markdown("### 📅 Prévision gaspillage par jour")
        df_prev = get_gaspillage_prevision()
        fig_prev = go.Figure()
        fig_prev.add_trace(go.Bar(
            x=df_prev["Jour"], y=df_prev["Gaspillage prévu (%)"],
            name="Prévu", marker_color="#90CAF9",
        ))
        fig_prev.add_trace(go.Scatter(
            x=df_prev["Jour"], y=df_prev["Gaspillage réel (%)"],
            name="Réel", line=dict(color="#F44336", width=2.5),
            mode="lines+markers", marker=dict(size=8),
        ))
        fig_prev.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            height=400, margin=dict(t=20, b=10),
            legend=dict(orientation="h", y=-0.15),
            yaxis=dict(title="Gaspillage (%)", range=[0, 25]),
        )
        st.plotly_chart(fig_prev, use_container_width=True)

    st.divider()

    # ─── Graphiques secondaires ────────────────────────────────
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("### 🥧 Répartition des portions")
        fig_portions = px.pie(
            values=[22, 55, 23],
            names=["🥗 Petite", "🍽️ Normale", "💪 Grande"],
            color_discrete_sequence=["#81C784", "#4CAF50", "#1B5E20"],
            hole=0.45,
        )
        fig_portions.update_layout(
            height=280, paper_bgcolor="white",
            margin=dict(t=10, b=10), showlegend=True,
        )
        st.plotly_chart(fig_portions, use_container_width=True)

    with col_b:
        st.markdown("### 🌿 CO₂ par plat")
        df_co2 = pd.DataFrame([
            {"Plat": p, "CO₂ (kg)": CO2_PAR_PLAT.get(p, 2.5)}
            for p in PLATS["plats"]
        ]).sort_values("CO₂ (kg)", ascending=False).head(8)
        fig_co2 = px.bar(
            df_co2, x="Plat", y="CO₂ (kg)",
            color="CO₂ (kg)",
            color_continuous_scale=["#C8E6C9", "#F44336"],
        )
        fig_co2.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            coloraxis_showscale=False, height=280,
            margin=dict(t=10, b=10), xaxis_tickangle=-35,
        )
        st.plotly_chart(fig_co2, use_container_width=True)

    with col_c:
        st.markdown("### 📆 Réservations / semaine")
        semaines = [f"S{i}" for i in range(1, 9)]
        reservations = [720, 745, 710, 760, 780, 800, 820, 876]
        fig_resa = px.line(
            x=semaines, y=reservations,
            labels={"x": "Semaine", "y": "Réservations"},
            color_discrete_sequence=["#4CAF50"],
            markers=True,
        )
        fig_resa.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            height=280, margin=dict(t=10, b=10),
        )
        st.plotly_chart(fig_resa, use_container_width=True)

    st.divider()

    # ─── Table top plats ───────────────────────────────────────
    st.markdown("### 📋 Tableau de bord complet")
    df_top_full = get_enterprise_top_plats()
    df_top_full["CO₂ Impact"] = df_top_full["CO₂ (kg)"].apply(
        lambda x: "🟢 Faible" if x < 2 else ("🟡 Moyen" if x < 4 else "🔴 Élevé")
    )
    st.dataframe(
        df_top_full.style.background_gradient(subset=["Satisfaction (%)"], cmap="Greens"),
        use_container_width=True,
        hide_index=True,
    )
