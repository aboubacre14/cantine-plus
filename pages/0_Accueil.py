import streamlit as st

# ── Hero ───────────────────────────────────────────────────────
import os

logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo.png")

col_logo, col_title = st.columns([1, 8])
with col_logo:
    if os.path.exists(logo_path):
        st.image(logo_path, width=64)
    else:
        st.markdown("""
        <div style='background:#2C8A4A; border-radius:14px; width:56px; height:56px;
                    display:flex; align-items:center; justify-content:center;
                    font-size:1.8rem; margin-top:0.1rem'>
            🍽️
        </div>""", unsafe_allow_html=True)
with col_title:
    st.markdown("""
    <div style='padding-top:0.3rem'>
        <span style='font-size:2rem; font-weight:800; color:#2C8A4A'>cantine</span><span style='font-size:2rem; font-weight:800; color:#F47B20'> +</span><br>
        <span style='color:#6B7280; font-size:0.88rem'>
            Plateforme intelligente de réduction du gaspillage alimentaire
        </span>
    </div>""", unsafe_allow_html=True)

st.divider()

# ── Cartes modules ─────────────────────────────────────────────
CARDS = [
    ("pages/1_Dashboard.py",         "📊", "Dashboard",         "KPIs, taux de gaspillage, participation et recommandations IA."),
    ("pages/2_Analytique.py",        "📈", "Analytique",         "Tendances, popularité des plats, empreinte CO₂ et économies."),
    ("pages/3_Menus.py",             "🍽️", "Menus",             "Planification multi-semaines, scores popularité et risque gaspi."),
    ("pages/4_Espace_Parent.py",     "👨‍👩‍👧", "Espace Parent",  "Profil enfant, menu prévisionnel, votes, présences et feedback."),
    ("pages/5_Espace_Eleve.py",      "👦", "Espace Élève",       "Vote emoji, gamification, badges héros anti-gaspi."),
    ("pages/6_Espace_Entreprise.py", "💼", "Espace Entreprise",  "Réservation, notation et dashboard RH pour les salariés."),
    ("pages/7_Repas_Solidaires.py",  "♻️", "Repas Solidaires",   "Invendus à prix réduit, déclaration personnel, QR code retrait."),
    ("pages/8_IA_Coach.py",          "⚡", "IA Coach Enfant",    "Détecte les aliments et génère un message audio style Sonic."),
]

rows = [CARDS[:3], CARDS[3:6], CARDS[6:]]
for row in rows:
    cols = st.columns(len(row))
    for col, (page, icon, label, desc) in zip(cols, row):
        with col:
            st.markdown(f"""
            <div class='mod-card'>
                <h3>{icon} {label}</h3>
                <p>{desc}</p>
            </div>""", unsafe_allow_html=True)
            st.markdown("<div class='mod-card-link'>", unsafe_allow_html=True)
            st.page_link(page, label="Accéder →", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

st.divider()

# ── Recommandations IA ─────────────────────────────────────────
st.markdown("### Recommandations IA du jour")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div style='background:#E5F4EA;border-radius:12px;padding:1rem;
                border-left:4px solid #2C8A4A'>
        <b style='color:#2C8A4A'>Risque gaspillage</b><br>
        <span style='font-size:1.4rem;font-weight:700;color:#2C8A4A'>12.4%</span>
        <span style='color:#6B7280;font-size:0.82rem'> · Faible — menu bien noté</span>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""
    <div style='background:#FFF4EC;border-radius:12px;padding:1rem;
                border-left:4px solid #F47B20'>
        <b style='color:#F47B20'>Popularité</b><br>
        <span style='font-size:1.4rem;font-weight:700;color:#F47B20'>78/100</span>
        <span style='color:#6B7280;font-size:0.82rem'> · Lasagnes bolognaise en tête</span>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown("""
    <div style='background:#F5F5F5;border-radius:12px;padding:1rem;
                border-left:4px solid #9E9E9E'>
        <b style='color:#424242'>Optimisation</b><br>
        <span style='font-size:0.88rem;color:#6B7280'>
            Réduire les portions de haricots verts (−8%)
        </span>
    </div>""", unsafe_allow_html=True)
