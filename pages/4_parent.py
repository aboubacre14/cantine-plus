import streamlit as st
import sys, os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.mock_data import (
    get_parent_profile, get_two_weeks_menu, get_current_week_menu,
    ALLERGENES, PLATS, POPULARITE, CO2_PAR_PLAT,
)

st.set_page_config(page_title="Espace Parent · Cantine+", page_icon="👨‍👩‍👧", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F8F4FF; }
    h1, h2, h3 { color: #6A1B9A !important; }
    .stButton > button {
        border-radius: 14px; font-weight: 600; border: none;
        padding: 0.5rem 1.2rem; transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] { background: #EDE7F6; color: #6A1B9A !important; }
    [data-testid="stMetric"] {
        background: white; border-radius: 16px;
        padding: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────
if "presence_today" not in st.session_state:
    st.session_state.presence_today = "present"
if "votes" not in st.session_state:
    st.session_state.votes = {}
if "allergies_sel" not in st.session_state:
    st.session_state.allergies_sel = ["Gluten", "Arachides"]
if "regime_sel" not in st.session_state:
    st.session_state.regime_sel = "Standard"
if "feedback_sent" not in st.session_state:
    st.session_state.feedback_sent = False

profile = get_parent_profile()
weeks = get_two_weeks_menu()
today = datetime.today()

with st.sidebar:
    st.markdown("## 👨‍👩‍👧 Espace Parent")
    st.divider()
    st.markdown(f"**Bonjour {profile['parent_prenom']} !**")
    st.markdown(f"Enfant : **{profile['enfant_prenom']}** · {profile['classe']}")
    st.markdown(f"Cantine : {profile['cantine']}")
    st.divider()
    st.markdown(f"⭐ Points : **{profile['points']}**")
    st.markdown(f"📅 Repas ce mois : **{profile['nb_repas_mois']}**")

st.markdown("# 👨‍👩‍👧 Espace Parent")
st.markdown(f"*Bienvenue, {profile['parent_prenom']} – Suivi de {profile['enfant_prenom']}*")
st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Tableau de bord",
    "📅 Menu & Votes",
    "✅ Présence",
    "🥗 Préférences",
    "⭐ Feedback",
])

# ═══════════════════════════════════════════════════════════════
# TAB 1 – TABLEAU DE BORD
# ═══════════════════════════════════════════════════════════════
with tab1:
    col_profil, col_repas = st.columns([1, 2])

    with col_profil:
        st.markdown(f"""
        <div style='background:white; border-radius:20px; padding:1.5rem;
                    box-shadow:0 4px 16px rgba(106,27,154,0.12); text-align:center;'>
            <div style='font-size:4rem'>👧</div>
            <h2 style='color:#6A1B9A; margin:0.3rem 0'>{profile['enfant_prenom']}</h2>
            <p style='color:#888; margin:0'>{profile['classe']}</p>
            <p style='color:#888; font-size:0.85rem'>{profile['cantine']}</p>
            <hr style='border-color:#EDE7F6; margin:1rem 0'>
            <div style='display:flex; justify-content:space-around'>
                <div>
                    <b style='color:#6A1B9A; font-size:1.3rem'>{profile['points']}</b><br>
                    <small style='color:#888'>Points</small>
                </div>
                <div>
                    <b style='color:#6A1B9A; font-size:1.3rem'>{profile['nb_repas_mois']}</b><br>
                    <small style='color:#888'>Repas/mois</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Badges
        st.markdown("**🏅 Badges obtenus**")
        badges_map = {"Héros anti-gaspi": "🦸", "Explorateur": "🧭",
                      "Champion vert": "🌿", "Super goûteur": "⭐"}
        for badge in profile["badges_obtenus"]:
            emoji = badges_map.get(badge, "🏅")
            st.markdown(f"""
            <div style='background:#EDE7F6; border-radius:10px; padding:0.5rem 0.8rem;
                        margin-bottom:0.4rem; display:flex; align-items:center; gap:0.5rem'>
                <span style='font-size:1.3rem'>{emoji}</span>
                <span style='color:#6A1B9A; font-weight:500; font-size:0.9rem'>{badge}</span>
            </div>
            """, unsafe_allow_html=True)

    with col_repas:
        # Statut présence du jour
        presence_label = "✅ Présent(e) à la cantine" if st.session_state.presence_today == "present" else "❌ Absent(e) aujourd'hui"
        presence_color = "#E8F5E9" if st.session_state.presence_today == "present" else "#FFEBEE"
        presence_text_color = "#2E7D32" if st.session_state.presence_today == "present" else "#C62828"

        st.markdown(f"""
        <div style='background:{presence_color}; border-radius:14px; padding:1rem 1.2rem;
                    border-left:5px solid {presence_text_color}; margin-bottom:1rem;'>
            <b style='color:{presence_text_color}; font-size:1.1rem'>{presence_label}</b><br>
            <small style='color:#666'>{today.strftime("%A %d %B %Y").capitalize()}</small>
        </div>
        """, unsafe_allow_html=True)

        # Prochain repas
        menu_df = get_current_week_menu()
        today_wd = today.weekday()
        jours_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
        if today_wd < 5:
            repas_idx = today_wd
        else:
            repas_idx = 0
        repas = menu_df.iloc[repas_idx]
        plat = repas["plat"]
        pop = POPULARITE.get(plat, 0.65)
        waste_risk = round((1 - pop) * 35, 1)

        risk_color = "#4CAF50" if waste_risk < 12 else ("#FF9800" if waste_risk < 20 else "#F44336")
        risk_label = "Faible" if waste_risk < 12 else ("Moyen" if waste_risk < 20 else "Élevé")
        risk_icon = "🟢" if waste_risk < 12 else ("🟡" if waste_risk < 20 else "🔴")

        st.markdown("**🍽️ Prochain repas**")
        st.markdown(f"""
        <div style='background:white; border-radius:16px; padding:1.2rem;
                    box-shadow:0 2px 8px rgba(0,0,0,0.08); margin-bottom:1rem;'>
            <div style='display:flex; justify-content:space-between; align-items:start'>
                <div>
                    <b style='color:#6A1B9A'>🥗 Entrée</b> &nbsp; <span style='color:#555'>{repas['entree']}</span><br>
                    <b style='color:#6A1B9A'>🍽️ Plat</b> &nbsp;&nbsp;&nbsp; <span style='color:#555'>{plat}</span><br>
                    <b style='color:#6A1B9A'>🥦 Accomp.</b> <span style='color:#555'>{repas['accompagnement']}</span><br>
                    <b style='color:#6A1B9A'>🍮 Dessert</b> <span style='color:#555'>{repas['dessert']}</span>
                </div>
                <div style='text-align:right'>
                    <div style='background:{risk_color}22; border-radius:10px; padding:0.5rem 0.8rem'>
                        <b style='color:{risk_color}; font-size:0.85rem'>IA Risque gaspillage</b><br>
                        <span style='font-size:1.4rem'>{risk_icon}</span>
                        <b style='color:{risk_color}'>{risk_label}</b><br>
                        <small style='color:#888'>{waste_risk}%</small>
                    </div>
                    <div style='margin-top:0.5rem; font-size:0.8rem; color:#888'>
                        🌿 CO₂ : <b>{repas['co2_estime']} kg</b><br>
                        💰 Coût : <b>{repas['cout_estime']} €</b>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # KPIs rapides
        k1, k2, k3 = st.columns(3)
        k1.metric("🍽️ Repas ce mois", profile["nb_repas_mois"])
        k2.metric("⭐ Points accumulés", profile["points"])
        k3.metric("🏅 Badges", len(profile["badges_obtenus"]))

        # Allergies rappel
        if profile["allergies"]:
            st.markdown(f"""
            <div style='background:#FFF3E0; border-radius:12px; padding:0.8rem 1rem; margin-top:0.5rem;
                        border-left:4px solid #FF9800;'>
                <b style='color:#E65100'>⚠️ Allergies déclarées</b> :
                {", ".join(profile["allergies"])}
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 2 – MENU & VOTES
# ═══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 📅 Menu prévisionnel – 2 semaines")
    st.caption("Cliquez sur 👍 ou 👎 pour exprimer vos préférences. L'IA adapte les menus selon les votes collectifs.")

    for w_idx, week in enumerate(weeks):
        monday_date = week[0]["date"]
        st.markdown(f"#### 📆 Semaine {w_idx + 1} — du {week[0]['date_str']} au {week[4]['date_str']}")

        cols = st.columns(5)
        for day, col in zip(week, cols):
            plat = day["plat"]
            pop = day["popularite"]
            co2 = day["co2"]
            risque = day["risque"]

            if day["est_passe"]:
                border = "#BDBDBD"
                bg = "#F5F5F5"
            elif day["est_aujourd_hui"]:
                border = "#6A1B9A"
                bg = "#F3E5F5"
            else:
                border = "#4CAF50"
                bg = "white"

            vote_key = f"{w_idx}_{day['date_str']}"
            vote_actuel = st.session_state.votes.get(vote_key, None)

            risk_icon = "🟢" if risque < 12 else ("🟡" if risque < 20 else "🔴")

            with col:
                header = "📍 " if day["est_aujourd_hui"] else ("✓ " if day["est_passe"] else "")
                st.markdown(f"""
                <div style='background:{bg}; border-radius:14px; padding:0.9rem;
                            box-shadow:0 2px 6px rgba(0,0,0,0.07);
                            border-top:4px solid {border}; min-height:240px;'>
                    <b style='color:#6A1B9A'>{header}{day['jour']}</b><br>
                    <small style='color:#888'>{day['date_str']}</small><br><br>
                    <small><b>🥗</b> {day['entree'][:20]}</small><br>
                    <small><b>🍽️</b> {plat[:20]}</small><br>
                    <small><b>🥦</b> {day['accompagnement'][:18]}</small><br>
                    <small><b>🍮</b> {day['dessert'][:18]}</small><br>
                    <hr style='margin:0.5rem 0; border-color:#EDE7F6'>
                    <small>{risk_icon} Risque: {risque}%</small><br>
                    <small>🌿 {co2} kg CO₂</small><br>
                    <small>⭐ Pop: {pop}%</small>
                </div>
                """, unsafe_allow_html=True)

                if not day["est_passe"]:
                    c1, c2 = st.columns(2)
                    with c1:
                        label_p = "👍✓" if vote_actuel == "pour" else "👍"
                        if st.button(label_p, key=f"pour_{vote_key}", use_container_width=True):
                            st.session_state.votes[vote_key] = "pour"
                            st.rerun()
                    with c2:
                        label_c = "👎✓" if vote_actuel == "contre" else "👎"
                        if st.button(label_c, key=f"contre_{vote_key}", use_container_width=True):
                            st.session_state.votes[vote_key] = "contre"
                            st.rerun()

        st.divider()

    votes_pour = sum(1 for v in st.session_state.votes.values() if v == "pour")
    votes_contre = sum(1 for v in st.session_state.votes.values() if v == "contre")
    if st.session_state.votes:
        st.info(f"📊 Vos votes : **{votes_pour} 👍 favorables** · **{votes_contre} 👎 défavorables** — Merci, l'IA prend en compte vos retours !")

# ═══════════════════════════════════════════════════════════════
# TAB 3 – PRÉSENCE & RÉSERVATION
# ═══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### ✅ Présence & Réservation")

    col_pres, col_info = st.columns([1, 1])

    with col_pres:
        st.markdown(f"""
        <div style='background:white; border-radius:20px; padding:1.5rem;
                    box-shadow:0 4px 16px rgba(0,0,0,0.08); text-align:center;'>
            <h3 style='color:#6A1B9A'>Aujourd'hui · {today.strftime("%d/%m/%Y")}</h3>
            <p style='color:#555'>{profile['enfant_prenom']} sera-t-il/elle à la cantine ?</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Présent(e)\nà la cantine", use_container_width=True, type="primary"):
                st.session_state.presence_today = "present"
                st.success("Présence confirmée ! Merci.")
        with c2:
            if st.button("❌ Absent(e)\naujourd'hui", use_container_width=True):
                st.session_state.presence_today = "absent"
                st.info("Absence enregistrée.")

        status_color = "#4CAF50" if st.session_state.presence_today == "present" else "#F44336"
        status_text = "✅ PRÉSENT(E)" if st.session_state.presence_today == "present" else "❌ ABSENT(E)"
        st.markdown(f"""
        <div style='background:{status_color}22; border-radius:12px; padding:1rem;
                    border:2px solid {status_color}; text-align:center; margin-top:1rem;'>
            <b style='color:{status_color}; font-size:1.2rem'>{status_text}</b>
        </div>
        """, unsafe_allow_html=True)

    with col_info:
        st.markdown("""
        <div style='background:#E8F5E9; border-radius:16px; padding:1.5rem;
                    border-left:5px solid #4CAF50;'>
            <h4 style='color:#2E7D32; margin-top:0'>🌱 Votre réponse aide à réduire le gaspillage</h4>
            <p style='color:#555; font-size:0.9rem'>
                En déclarant la présence ou l'absence de votre enfant, vous permettez à la cantine
                de préparer les bonnes quantités et d'éviter les surplus alimentaires.
            </p>
            <hr style='border-color:#C8E6C9'>
            <b style='color:#2E7D32'>📅 Date limite de déclaration</b><br>
            <p style='color:#555; font-size:0.9rem'>Chaque jour avant <b>8h00</b> pour le repas du midi.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("#### 📅 Planifier la semaine")
        jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
        presences = {}
        for jour in jours_semaine:
            presences[jour] = st.checkbox(f"{jour}", value=True, key=f"pres_{jour}")

        if st.button("💾 Enregistrer la semaine", type="primary"):
            nb_jours = sum(presences.values())
            st.success(f"✅ Planning enregistré : {profile['enfant_prenom']} sera présent(e) {nb_jours} jour(s) cette semaine.")

# ═══════════════════════════════════════════════════════════════
# TAB 4 – PRÉFÉRENCES & ALLERGIES
# ═══════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 🥗 Préférences alimentaires & Allergies")
    st.info("💡 Les menus s'adaptent selon les préférences collectives grâce à l'IA.")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### ⚠️ Allergies déclarées")
        allergies_new = st.multiselect(
            "Sélectionnez les allergènes :",
            ALLERGENES,
            default=st.session_state.allergies_sel,
            key="allergies_widget"
        )

        st.markdown("#### 🥦 Régime alimentaire")
        regime_new = st.radio(
            "Type de régime :",
            ["Standard", "Végétarien", "Végétalien", "Sans porc", "Sans gluten", "Autre"],
            index=["Standard", "Végétarien", "Végétalien", "Sans porc", "Sans gluten", "Autre"]
                .index(st.session_state.regime_sel),
        )

    with col_b:
        st.markdown("#### 👍 Aliments aimés")
        _opts_aimes = PLATS["plats"] + PLATS["entrees"] + PLATS["desserts"]
        aliments_aimes = st.multiselect(
            "Sélectionner les plats appréciés :",
            _opts_aimes,
            default=[a for a in profile["aliments_aimes"] if a in _opts_aimes],
            key="aimes_widget",
        )

        st.markdown("#### 👎 Aliments non aimés")
        _opts_non_aimes = PLATS["plats"] + PLATS["entrees"] + PLATS["accompagnements"]
        aliments_non_aimes = st.multiselect(
            "Sélectionner les plats non appréciés :",
            _opts_non_aimes,
            default=[a for a in profile["aliments_non_aimes"] if a in _opts_non_aimes],
            key="non_aimes_widget",
        )

    st.divider()

    if st.button("💾 Enregistrer mes préférences", type="primary"):
        st.session_state.allergies_sel = allergies_new
        st.session_state.regime_sel = regime_new
        st.success("✅ Préférences enregistrées ! L'IA les prendra en compte pour les prochains menus.")
        if allergies_new:
            st.warning(f"⚠️ Allergies transmises à la cantine : {', '.join(allergies_new)}")

# ═══════════════════════════════════════════════════════════════
# TAB 5 – FEEDBACK POST-REPAS
# ═══════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### ⭐ Feedback post-repas")
    st.caption("Votre retour améliore les menus futurs et aide l'IA à mieux prédire le gaspillage.")

    if st.session_state.feedback_sent:
        st.success("✅ Merci pour votre retour ! Il sera pris en compte pour améliorer les menus.")
        st.markdown("### 📊 Historique de vos feedbacks")
        feedbacks_exemples = [
            {"date": "Hier", "plat": "Lasagnes bolognaise", "note": "😍", "quantite": "Tout mangé"},
            {"date": "Lundi", "plat": "Poisson pané", "note": "😐", "quantite": "À moitié"},
            {"date": "Vendredi", "plat": "Gratin de courgettes", "note": "😕", "quantite": "Presque rien"},
        ]
        for fb in feedbacks_exemples:
            st.markdown(f"""
            <div style='background:white; border-radius:12px; padding:0.8rem 1rem;
                        box-shadow:0 1px 4px rgba(0,0,0,0.07); margin-bottom:0.5rem;
                        display:flex; gap:1rem; align-items:center;'>
                <span style='font-size:1.5rem'>{fb['note']}</span>
                <div>
                    <b style='color:#6A1B9A'>{fb['plat']}</b><br>
                    <small style='color:#888'>{fb['date']} · {fb['quantite']}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("📝 Donner un nouveau feedback"):
            st.session_state.feedback_sent = False
            st.rerun()
        st.stop()

    # Repas du jour
    menu_df = get_current_week_menu()
    repas = menu_df.iloc[min(today.weekday(), 4)]

    st.markdown(f"""
    <div style='background:white; border-radius:16px; padding:1.2rem;
                box-shadow:0 2px 8px rgba(0,0,0,0.08); margin-bottom:1.5rem;'>
        <b style='color:#6A1B9A'>🍽️ Repas évalué</b><br>
        <span style='color:#555'>
            {repas['entree']} · <b>{repas['plat']}</b> · {repas['accompagnement']} · {repas['dessert']}
        </span>
    </div>
    """, unsafe_allow_html=True)

    col_note, col_qty = st.columns(2)

    with col_note:
        st.markdown("#### 😊 Notation globale")
        note_emoji = st.radio(
            "Comment était le repas ?",
            ["😍 Excellent", "😊 Bien", "😐 Moyen", "😕 Pas très bon", "😣 Mauvais"],
            horizontal=False,
        )

    with col_qty:
        st.markdown("#### 🍽️ Quantité consommée")
        quantite = st.radio(
            "Combien a-t-il/elle mangé ?",
            ["🍽️ Tout mangé", "🥣 À moitié", "🙈 Presque rien", "🚫 Rien du tout"],
            horizontal=False,
        )

    commentaire = st.text_area(
        "💬 Commentaire (facultatif)",
        placeholder=f"Ex : {profile['enfant_prenom']} a adoré le plat principal mais n'aime pas les haricots...",
        max_chars=300,
    )

    st.markdown("""
    <div style='background:#E8F5E9; border-radius:12px; padding:0.8rem 1rem; margin-bottom:1rem;'>
        <small style='color:#2E7D32'>💡 <b>Votre retour compte !</b> Il aide l'IA à mieux planifier les menus et à réduire le gaspillage alimentaire.</small>
    </div>
    """, unsafe_allow_html=True)

    if st.button("📤 Envoyer mon feedback", type="primary"):
        st.session_state.feedback_sent = True
        st.balloons()
        st.rerun()
