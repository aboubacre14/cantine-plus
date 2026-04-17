import streamlit as st

st.set_page_config(
    page_title="Cantine+ | SmartCanteen",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    :root { --green: #4CAF50; --green-light: #E8F5E9; --beige: #F5F0E8; --gray: #F5F5F5; }
    .stApp { background-color: #FAFAFA; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1B5E20 0%, #2E7D32 50%, #388E3C 100%);
    }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] .stSelectbox label { color: rgba(255,255,255,0.8) !important; }
    [data-testid="stMetric"] {
        background: white; border-radius: 16px;
        padding: 1rem 1.2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #4CAF50;
    }
    [data-testid="stMetricLabel"] { font-size: 0.82rem; color: #666; }
    [data-testid="stMetricValue"] { color: #2E7D32; font-weight: 700; }
    h1 { color: #2E7D32 !important; }
    h2, h3 { color: #388E3C !important; }
    .stButton > button {
        background: #4CAF50; color: white; border: none;
        border-radius: 12px; padding: 0.5rem 1.5rem;
        font-weight: 600; transition: background 0.2s;
    }
    .stButton > button:hover { background: #388E3C; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0; font-weight: 500; }
    .stTabs [aria-selected="true"] { background: #E8F5E9; color: #2E7D32 !important; }
    .stDataFrame { border-radius: 12px; overflow: hidden; }
    hr { border-color: #E8F5E9; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🥗 Cantine+")
    st.markdown("*SmartCanteen – IA Anti-Gaspillage*")
    st.divider()

    st.markdown("### 🏫 École")
    st.page_link("app.py",               label="🏠 Accueil")
    st.page_link("pages/1_dashboard.py", label="📊 Dashboard Cantine")
    st.page_link("pages/2_analytics.py", label="📈 Analytique")
    st.page_link("pages/3_menus.py",     label="🍽️ Gestion Menus")
    st.page_link("pages/4_parent.py",    label="👨‍👩‍👧 Espace Parent")
    st.page_link("pages/5_eleve.py",     label="👦 Espace Élève")

    st.divider()
    st.markdown("### 🏢 Entreprise")
    st.page_link("pages/6_entreprise.py", label="💼 Espace Entreprise")

    st.divider()
    st.markdown("### ♻️ Solidaire & IA")
    st.page_link("pages/7_invendus.py", label="♻️ Repas Solidaires")
    st.page_link("pages/8_ia_coach.py", label="🤖 IA Coach Enfant")

    st.divider()
    st.markdown(
        "<small style='opacity:0.7'>Données simulées · 3 cantines · Rennes</small>",
        unsafe_allow_html=True,
    )

# ── Hero ──────────────────────────────────────────────────────
st.markdown("# 🥗 SmartCanteen – IA Anti-Gaspillage")
st.markdown("#### Plateforme intelligente de réduction du gaspillage alimentaire")
st.divider()

# ── Modules cards ─────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='background:white; border-radius:16px; padding:1.5rem;
                box-shadow:0 2px 8px rgba(0,0,0,0.08); border-top:4px solid #4CAF50;'>
        <h3 style='color:#2E7D32; margin-top:0'>📊 Dashboard Cantine</h3>
        <p style='color:#555; font-size:0.9rem;'>
            Vue d'ensemble : KPIs, taux de gaspillage, participation et recommandations IA.
        </p>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background:white; border-radius:16px; padding:1.5rem;
                box-shadow:0 2px 8px rgba(0,0,0,0.08); border-top:4px solid #FF9800;'>
        <h3 style='color:#E65100; margin-top:0'>📈 Analytique</h3>
        <p style='color:#555; font-size:0.9rem;'>
            Analyse des tendances, popularité des plats, empreinte CO₂ et économies réalisées.
        </p>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='background:white; border-radius:16px; padding:1.5rem;
                box-shadow:0 2px 8px rgba(0,0,0,0.08); border-top:4px solid #2196F3;'>
        <h3 style='color:#1565C0; margin-top:0'>🍽️ Gestion Menus</h3>
        <p style='color:#555; font-size:0.9rem;'>
            Planification multi-semaines avec scores de popularité et risque de gaspillage.
        </p>
    </div>""", unsafe_allow_html=True)

st.divider()

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown("""
    <div style='background:white; border-radius:16px; padding:1.5rem;
                box-shadow:0 2px 8px rgba(0,0,0,0.08); border-top:4px solid #9C27B0;'>
        <h3 style='color:#6A1B9A; margin-top:0'>👨‍👩‍👧 Espace Parent</h3>
        <p style='color:#555; font-size:0.9rem;'>
            Profil enfant, menu prévisionnel, votes, présence, préférences et feedback repas.
        </p>
    </div>""", unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div style='background:white; border-radius:16px; padding:1.5rem;
                box-shadow:0 2px 8px rgba(0,0,0,0.08); border-top:4px solid #FF5722;'>
        <h3 style='color:#BF360C; margin-top:0'>👦 Espace Élève</h3>
        <p style='color:#555; font-size:0.9rem;'>
            Vote emoji, gamification, badges "Héros anti-gaspi" et feedback quotidien.
        </p>
    </div>""", unsafe_allow_html=True)

with col6:
    st.markdown("""
    <div style='background:white; border-radius:16px; padding:1.5rem;
                box-shadow:0 2px 8px rgba(0,0,0,0.08); border-top:4px solid #607D8B;'>
        <h3 style='color:#37474F; margin-top:0'>💼 Espace Entreprise</h3>
        <p style='color:#555; font-size:0.9rem;'>
            Réservation, vote, choix de portion et dashboard analytique pour les salariés.
        </p>
    </div>""", unsafe_allow_html=True)

st.divider()

col7, col8 = st.columns(2)

with col7:
    st.markdown("""
    <div style='background:white; border-radius:16px; padding:1.5rem;
                box-shadow:0 2px 8px rgba(0,0,0,0.08); border-top:4px solid #4CAF50;'>
        <h3 style='color:#2E7D32; margin-top:0'>♻️ Repas Solidaires</h3>
        <p style='color:#555; font-size:0.9rem;'>
            Invendus à prix réduit, déclaration du personnel, QR code de retrait – inspiré Too Good To Go.
        </p>
    </div>""", unsafe_allow_html=True)

with col8:
    st.markdown("""
    <div style='background:white; border-radius:16px; padding:1.5rem;
                box-shadow:0 2px 8px rgba(0,0,0,0.08); border-top:4px solid #00BCD4;'>
        <h3 style='color:#006064; margin-top:0'>🤖 IA Coach Enfant</h3>
        <p style='color:#555; font-size:0.9rem;'>
            Analyse le plateau de l'élève et génère un script TTS motivant adapté aux enfants.
        </p>
    </div>""", unsafe_allow_html=True)

st.divider()

st.markdown("### 🤖 Recommandations IA du jour")
col_ia1, col_ia2, col_ia3 = st.columns(3)
with col_ia1:
    st.info("**Score risque gaspillage** · Faible (12.4%)\nMenu bien noté cette semaine")
with col_ia2:
    st.success("**Indice de popularité** · 78/100\nLasagnes bolognaise en tête")
with col_ia3:
    st.warning("**Suggestion d'optimisation**\nRéduire les portions de haricots verts (−8%)")
