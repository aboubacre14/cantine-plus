import streamlit as st

st.set_page_config(
    page_title="Cantine+",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS global (appliqué à toutes les pages) ───────────────────
st.markdown("""
<style>
    :root {
        --green:  #2C8A4A;
        --orange: #F47B20;
        --white:  #FFFFFF;
        --soft:   #E5F4EA;
        --muted:  #6B7280;
    }
    .stApp { background-color: var(--white); }

    [data-testid="stSidebar"] {
        background-color: var(--green) !important;
    }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.2) !important; }

    /* Liens de navigation sidebar */
    [data-testid="stSidebarNavLink"] {
        border-radius: 8px !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        color: rgba(255,255,255,0.85) !important;
        padding: 0.4rem 0.8rem !important;
    }
    [data-testid="stSidebarNavLink"]:hover {
        background: rgba(255,255,255,0.15) !important;
        color: white !important;
    }
    [data-testid="stSidebarNavLink"][aria-selected="true"] {
        background: rgba(255,255,255,0.2) !important;
        color: white !important;
        font-weight: 700 !important;
    }
    /* Labels de section */
    [data-testid="stSidebarNavSeparatorLabel"] {
        color: rgba(255,255,255,0.55) !important;
        font-size: 0.7rem !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
    }

    h1 { color: var(--green) !important; font-weight: 800 !important; }
    h2, h3 { color: var(--green) !important; font-weight: 700 !important; }

    [data-testid="stMetric"] {
        background: var(--white); border-radius: 14px;
        padding: 1rem 1.2rem;
        box-shadow: 0 1px 6px rgba(0,0,0,0.07);
        border-left: 4px solid var(--green);
    }
    [data-testid="stMetricLabel"] { font-size: 0.82rem; color: var(--muted); }
    [data-testid="stMetricValue"] { color: var(--green); font-weight: 700; }

    .stButton > button {
        background: var(--orange) !important;
        color: white !important; border: none;
        border-radius: 10px; padding: 0.5rem 1.4rem;
        font-weight: 600; transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.88; }

    .stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0; font-weight: 500; }
    .stTabs [aria-selected="true"] {
        background: var(--soft) !important;
        color: var(--green) !important; font-weight: 700;
    }

    .mod-card {
        background: var(--white); border-radius: 14px;
        padding: 1.2rem 1.4rem 0.8rem 1.4rem;
        box-shadow: 0 1px 6px rgba(0,0,0,0.07);
        border-top: 4px solid var(--green); margin-bottom: 0.4rem;
        transition: box-shadow 0.2s, transform 0.15s;
    }
    .mod-card:hover {
        box-shadow: 0 6px 18px rgba(44,138,74,0.15);
        transform: translateY(-2px);
    }
    .mod-card h3 { margin-top:0; font-size:1rem; color:var(--green); }
    .mod-card p  { color:var(--muted); font-size:0.86rem; margin-bottom:0.2rem; }

    .mod-card-link [data-testid="stPageLink"] a {
        display:block; width:100%; text-align:center;
        background:var(--soft); border-radius:8px;
        padding:0.42rem 0; font-weight:600; font-size:0.85rem;
        color:var(--green) !important; text-decoration:none;
        border:1.5px solid var(--green); transition:background 0.2s, color 0.2s;
    }
    .mod-card-link [data-testid="stPageLink"] a:hover {
        background:var(--green); color:white !important;
    }

    hr { border-color: var(--soft) !important; }
    .stDataFrame { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Navigation avec titres accentués ──────────────────────────
pg = st.navigation({
    "École": [
        st.Page("pages/0_Accueil.py",          title="Accueil",           icon="🏠", default=True),
        st.Page("pages/1_Dashboard.py",         title="Dashboard",         icon="📊"),
        st.Page("pages/2_Analytique.py",        title="Analytique",        icon="📈"),
        st.Page("pages/3_Menus.py",             title="Menus",             icon="🍽️"),
        st.Page("pages/4_Espace_Parent.py",     title="Espace Parent",     icon="👨‍👩‍👧"),
        st.Page("pages/5_Espace_Eleve.py",      title="Espace Élève",      icon="👦"),
    ],
    "Entreprise": [
        st.Page("pages/6_Espace_Entreprise.py", title="Espace Entreprise", icon="💼"),
    ],
    "Solidaire & IA": [
        st.Page("pages/7_Repas_Solidaires.py",  title="Repas Solidaires",  icon="♻️"),
        st.Page("pages/8_IA_Coach.py",          title="IA Coach Enfant",   icon="⚡"),
    ],
})
pg.run()
