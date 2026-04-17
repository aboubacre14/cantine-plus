import streamlit as st
import sys, os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.mock_data import get_student_profile, get_current_week_menu, BADGES_ELEVE, POPULARITE

st.set_page_config(page_title="Espace Élève · Cantine+", page_icon="👦", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #FFF9C4 0%, #E8F5E9 50%, #E3F2FD 100%); }
    h1 { color: #FF6F00 !important; font-size: 2.2rem !important; }
    h2, h3 { color: #2E7D32 !important; }
    .stButton > button {
        border-radius: 20px; font-size: 1.1rem; font-weight: 700;
        border: none; padding: 0.7rem 1.5rem; transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background: #FFF9C4; color: #FF6F00 !important; font-weight: 700;
    }
    .emoji-btn { font-size: 3rem; cursor: pointer; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────
if "vote_today" not in st.session_state:
    st.session_state.vote_today = None
if "feedback_eleve" not in st.session_state:
    st.session_state.feedback_eleve = None
if "points_eleve" not in st.session_state:
    st.session_state.points_eleve = 340
if "serie" not in st.session_state:
    st.session_state.serie = 5

profile = get_student_profile()
menu_df = get_current_week_menu()
today = datetime.today()
today_wd = min(today.weekday(), 4)
repas = menu_df.iloc[today_wd]

with st.sidebar:
    st.markdown("## 👦 Espace Élève")
    st.divider()
    st.markdown(f"**Bonjour {profile['prenom']} !** 🌟")
    st.markdown(f"Classe : **{profile['classe']}**")
    st.divider()
    st.markdown(f"⭐ **{st.session_state.points_eleve} points**")
    st.progress(min(st.session_state.points_eleve / 500, 1.0))
    st.caption(f"Niveau : **{profile['niveau']}** · Prochain : Légende (500 pts)")
    st.divider()
    st.markdown(f"🔥 Série : **{st.session_state.serie} jours**")
    st.markdown(f"🏆 Record : **{profile['meilleure_serie']} jours**")

# ── Header ────────────────────────────────────────────────────
st.markdown("# 👦 Ta Mission du Jour !")
st.markdown(f"**{today.strftime('%A %d %B').capitalize()}** — Cantine en vue, héros ! 🦸")
st.divider()

tab1, tab2, tab3 = st.tabs(["🎯 Mission du jour", "🏅 Mes badges", "📊 Mon historique"])

# ═══════════════════════════════════════════════════════════════
# TAB 1 – MISSION DU JOUR
# ═══════════════════════════════════════════════════════════════
with tab1:
    col_repas, col_vote = st.columns([3, 2])

    with col_repas:
        st.markdown("### 🍽️ Le repas du jour")
        plat = repas["plat"]
        pop = POPULARITE.get(plat, 0.65)

        st.markdown(f"""
        <div style='background:white; border-radius:24px; padding:1.8rem;
                    box-shadow:0 6px 20px rgba(0,0,0,0.10); border-top:6px solid #FF6F00;'>
            <div style='font-size:3rem; margin-bottom:0.8rem'>🍽️</div>
            <div style='display:flex; justify-content:space-between; padding:0.4rem 0; border-bottom:1px solid #f5f5f5'>
                <span style='color:#888'>🥗 Entrée</span>
                <span style='font-weight:600; color:#333'>{repas['entree']}</span>
            </div>
            <div style='display:flex; justify-content:space-between; padding:0.5rem 0.3rem;
                        background:#FFF9C4; border-radius:8px; margin:0.3rem 0'>
                <span style='color:#888'>🍽️ Plat principal</span>
                <span style='font-weight:700; color:#FF6F00; font-size:1.05rem'>{plat}</span>
            </div>
            <div style='display:flex; justify-content:space-between; padding:0.4rem 0; border-bottom:1px solid #f5f5f5'>
                <span style='color:#888'>🥦 Accompagnement</span>
                <span style='font-weight:600; color:#333'>{repas['accompagnement']}</span>
            </div>
            <div style='display:flex; justify-content:space-between; padding:0.4rem 0'>
                <span style='color:#888'>🍮 Dessert</span>
                <span style='font-weight:600; color:#333'>{repas['dessert']}</span>
            </div>
            <hr style='border-color:#FFF9C4; margin:1rem 0'>
            <div style='display:flex; gap:0.6rem; justify-content:center; flex-wrap:wrap'>
                <span style='background:#E8F5E9; border-radius:20px; padding:0.3rem 0.8rem;
                             color:#2E7D32; font-size:0.85rem; font-weight:600'>
                    🌿 CO₂ : {repas['co2_estime']} kg
                </span>
                <span style='background:#FFF9C4; border-radius:20px; padding:0.3rem 0.8rem;
                             color:#FF6F00; font-size:0.85rem; font-weight:600'>
                    ⭐ {round(pop * 100)}%
                </span>
                <span style='background:#E3F2FD; border-radius:20px; padding:0.3rem 0.8rem;
                             color:#1565C0; font-size:0.85rem; font-weight:600'>
                    💰 {repas['cout_estime']} €
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_vote:
        st.markdown("### 🗳️ Ton vote")

        if st.session_state.vote_today is None:
            st.markdown("""
            <div style='background:white; border-radius:20px; padding:1.5rem;
                        box-shadow:0 4px 12px rgba(0,0,0,0.08); text-align:center;'>
                <p style='color:#555; font-weight:600; font-size:1rem'>Tu aimes ce repas ?</p>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("😍\n\nJ'adore !", use_container_width=True):
                    st.session_state.vote_today = "adore"
                    st.session_state.points_eleve += 10
                    st.rerun()
            with c2:
                if st.button("😐\n\nBof...", use_container_width=True):
                    st.session_state.vote_today = "bof"
                    st.session_state.points_eleve += 5
                    st.rerun()

            c3, c4 = st.columns(2)
            with c3:
                if st.button("🥦\n\nJe vais goûter !", use_container_width=True):
                    st.session_state.vote_today = "gouter"
                    st.session_state.points_eleve += 15
                    st.rerun()
            with c4:
                if st.button("😣\n\nPas pour moi", use_container_width=True):
                    st.session_state.vote_today = "non"
                    st.session_state.points_eleve += 5
                    st.rerun()
        else:
            vote_display = {
                "adore": ("😍", "Tu adores ce repas !", "#FFF9C4", "#FF6F00"),
                "bof": ("😐", "D'accord, bof aujourd'hui...", "#F5F5F5", "#757575"),
                "gouter": ("🥦", "Héros ! Tu vas goûter !", "#E8F5E9", "#2E7D32"),
                "non": ("😣", "Ok, noté pour l'IA.", "#FFEBEE", "#C62828"),
            }
            icon, text, bg, color = vote_display[st.session_state.vote_today]
            st.markdown(f"""
            <div style='background:{bg}; border-radius:20px; padding:1.5rem;
                        text-align:center; box-shadow:0 4px 12px rgba(0,0,0,0.08);'>
                <div style='font-size:4rem'>{icon}</div>
                <b style='color:{color}; font-size:1rem'>{text}</b><br>
                <small style='color:#888'>+5 points gagnés !</small>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔄 Changer mon vote"):
                st.session_state.vote_today = None
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Feedback quantité
        st.markdown("### 🍽️ Après le repas")
        if st.session_state.feedback_eleve is None:
            st.caption("Combien tu as mangé ?")
            fa, fb, fc = st.columns(3)
            with fa:
                if st.button("🌟\n\nTout !", use_container_width=True):
                    st.session_state.feedback_eleve = "tout"
                    st.session_state.points_eleve += 20
                    st.session_state.serie += 1
                    st.rerun()
            with fb:
                if st.button("🥣\n\nLa moitié", use_container_width=True):
                    st.session_state.feedback_eleve = "moitie"
                    st.session_state.points_eleve += 10
                    st.rerun()
            with fc:
                if st.button("🙈\n\nPeu", use_container_width=True):
                    st.session_state.feedback_eleve = "peu"
                    st.session_state.points_eleve += 5
                    st.rerun()
        else:
            fb_display = {
                "tout": ("🌟", "Super héros ! +20 points !", "#FFF9C4", "#FF6F00"),
                "moitie": ("🥣", "Bien joué ! +10 points !", "#E8F5E9", "#2E7D32"),
                "peu": ("🙈", "Pas grave ! +5 points quand même !", "#E3F2FD", "#1565C0"),
            }
            icon, text, bg, color = fb_display[st.session_state.feedback_eleve]
            st.markdown(f"""
            <div style='background:{bg}; border-radius:16px; padding:1rem;
                        text-align:center;'>
                <span style='font-size:2.5rem'>{icon}</span><br>
                <b style='color:{color}'>{text}</b>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # Points & progression
    st.markdown("### ⭐ Tes points")
    col_pts, col_serie, col_mission = st.columns(3)

    with col_pts:
        pct = min(st.session_state.points_eleve / 500, 1.0)
        st.markdown(f"""
        <div style='background:white; border-radius:16px; padding:1.2rem;
                    box-shadow:0 2px 8px rgba(0,0,0,0.08); text-align:center;'>
            <div style='font-size:2.5rem'>⭐</div>
            <h2 style='color:#FF6F00; margin:0.3rem 0'>{st.session_state.points_eleve}</h2>
            <p style='color:#888; margin:0'>points accumulés</p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(pct)
        st.caption(f"Prochain niveau : Légende ({500 - st.session_state.points_eleve} pts restants)")

    with col_serie:
        st.markdown(f"""
        <div style='background:white; border-radius:16px; padding:1.2rem;
                    box-shadow:0 2px 8px rgba(0,0,0,0.08); text-align:center;'>
            <div style='font-size:2.5rem'>🔥</div>
            <h2 style='color:#F44336; margin:0.3rem 0'>{st.session_state.serie}</h2>
            <p style='color:#888; margin:0'>jours de suite</p>
            <small style='color:#aaa'>Record : {profile["meilleure_serie"]} jours</small>
        </div>
        """, unsafe_allow_html=True)

    with col_mission:
        mission_done = st.session_state.vote_today is not None and st.session_state.feedback_eleve is not None
        m_icon = "✅" if mission_done else "🎯"
        m_text = "Mission accomplie !" if mission_done else "Mission en cours..."
        m_color = "#2E7D32" if mission_done else "#FF6F00"
        m_bg = "#E8F5E9" if mission_done else "#FFF9C4"
        st.markdown(f"""
        <div style='background:{m_bg}; border-radius:16px; padding:1.2rem;
                    box-shadow:0 2px 8px rgba(0,0,0,0.08); text-align:center;'>
            <div style='font-size:2.5rem'>{m_icon}</div>
            <h3 style='color:{m_color}; margin:0.3rem 0'>{m_text}</h3>
            <p style='color:#888; margin:0; font-size:0.85rem'>
                {"Vote + feedback complétés" if mission_done else "Vote et feedback à faire"}
            </p>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 2 – BADGES
# ═══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🏅 Ma collection de badges")
    st.caption("Accomplis des missions pour débloquer de nouveaux badges !")

    badges_obtenus = profile["badges"]

    cols = st.columns(3)
    for i, badge in enumerate(BADGES_ELEVE):
        obtenu = badge["nom"] in badges_obtenus
        col = cols[i % 3]
        with col:
            bg = "#FFF9C4" if obtenu else "#F5F5F5"
            opacity = "1" if obtenu else "0.4"
            lock = "" if obtenu else "🔒 "
            st.markdown(f"""
            <div style='background:{bg}; border-radius:20px; padding:1.5rem;
                        box-shadow:0 2px 8px rgba(0,0,0,0.08); text-align:center;
                        margin-bottom:1rem; opacity:{opacity};
                        border:{"3px solid #FF6F00" if obtenu else "2px dashed #ccc"};'>
                <div style='font-size:3rem'>{badge["emoji"]}</div>
                <b style='color:#333; font-size:1rem'>{lock}{badge["nom"]}</b><br>
                <small style='color:#888'>{badge["condition"]}</small><br>
                {"<span style='color:#FF6F00; font-weight:700; font-size:0.9rem'>✅ Obtenu !</span>" if obtenu else "<span style='color:#aaa; font-size:0.85rem'>À débloquer</span>"}
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.markdown(f"### 🏆 Score général")
    nb_badges = len(badges_obtenus)
    st.markdown(f"""
    <div style='background:white; border-radius:16px; padding:1.5rem;
                box-shadow:0 2px 8px rgba(0,0,0,0.08); text-align:center;'>
        <span style='font-size:4rem'>🦸</span>
        <h2 style='color:#FF6F00'>{nb_badges} badge{"s" if nb_badges > 1 else ""} obtenu{"s" if nb_badges > 1 else ""}</h2>
        <p style='color:#555'>{profile["repas_notes"]} repas notés · {st.session_state.points_eleve} points</p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 3 – HISTORIQUE
# ═══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 📊 Mon historique de la semaine")

    historique = [
        {"jour": "Lundi",    "plat": "Lasagnes bolognaise",       "vote": "😍", "quantite": "🌟 Tout",   "points": 30},
        {"jour": "Mardi",    "plat": "Escalope de dinde",          "vote": "😊", "quantite": "🥣 Moitié", "points": 15},
        {"jour": "Mercredi", "plat": "Poisson pané",               "vote": "😐", "quantite": "🙈 Peu",    "points": 10},
        {"jour": "Jeudi",    "plat": "Hachis parmentier",          "vote": "😍", "quantite": "🌟 Tout",   "points": 30},
        {"jour": "Vendredi", "plat": "Gratin de courgettes",       "vote": "😕", "quantite": "🙈 Peu",    "points": 10},
    ]

    for item in historique:
        total_pts = item["points"]
        st.markdown(f"""
        <div style='background:white; border-radius:14px; padding:0.9rem 1.2rem;
                    box-shadow:0 2px 6px rgba(0,0,0,0.07); margin-bottom:0.5rem;
                    display:flex; justify-content:space-between; align-items:center;'>
            <div>
                <b style='color:#FF6F00'>{item["jour"]}</b>
                <span style='color:#555; font-size:0.95rem'> — {item["plat"]}</span>
            </div>
            <div style='display:flex; gap:1rem; align-items:center'>
                <span style='font-size:1.4rem'>{item["vote"]}</span>
                <span style='color:#888; font-size:0.85rem'>{item["quantite"]}</span>
                <span style='background:#FFF9C4; border-radius:10px; padding:0.2rem 0.6rem;
                             color:#FF6F00; font-weight:700; font-size:0.85rem'>
                    +{total_pts} pts
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    total_sem = sum(h["points"] for h in historique)
    st.markdown(f"""
    <div style='background:#FFF9C4; border-radius:16px; padding:1rem; text-align:center;'>
        <b style='color:#FF6F00; font-size:1.1rem'>🏆 Total cette semaine : +{total_sem} points</b>
    </div>
    """, unsafe_allow_html=True)
