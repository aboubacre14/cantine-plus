import streamlit as st
import plotly.express as px
import pandas as pd
import sys, os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.mock_data import get_historical_df, get_current_week_menu, PLATS, POPULARITE, CO2_PAR_PLAT, COUT_PAR_REPAS

st.set_page_config(page_title="Menus · Cantine+", page_icon="🍽️", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FAFAFA; }
    h1, h2, h3 { color: #2E7D32 !important; }
    .stButton > button {
        background: #4CAF50; color: white; border: none;
        border-radius: 12px; font-weight: 600;
    }
    .menu-card {
        background: white; border-radius: 16px; padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        border-left: 4px solid #4CAF50; margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🍽️ Menus")
    st.divider()
    semaines = [f"Semaine {i}" for i in range(1, 5)]
    sem_sel = st.selectbox("📅 Semaine", semaines)
    st.divider()
    st.markdown("**Filtres**")
    show_co2 = st.checkbox("Afficher CO₂", value=True)
    show_cout = st.checkbox("Afficher coût", value=True)
    show_pop = st.checkbox("Afficher popularité", value=True)

st.markdown("# 🍽️ Gestion des Menus")
st.markdown("*Planification multi-semaines avec scores IA*")
st.divider()

# ── Menu semaine courante ─────────────────────────────────────
st.markdown("### 📅 Menu de la semaine en cours")
menu_df = get_current_week_menu()
jours = menu_df["jour"].tolist()

cols = st.columns(5)
for i, (col, row) in enumerate(zip(cols, menu_df.itertuples())):
    plat = row.plat
    pop = POPULARITE.get(plat, 0.65)
    co2 = CO2_PAR_PLAT.get(plat, 2.5)
    cout = COUT_PAR_REPAS.get(plat, 3.80)

    # Couleur badge popularité
    if pop >= 0.8:
        badge_color = "#4CAF50"; badge_label = "🟢 Populaire"
    elif pop >= 0.6:
        badge_color = "#FF9800"; badge_label = "🟡 Moyen"
    else:
        badge_color = "#F44336"; badge_label = "🔴 Risqué"

    waste_risk = round((1 - pop) * 35, 1)

    with col:
        st.markdown(f"""
        <div style='background:white; border-radius:14px; padding:1rem;
                    box-shadow:0 2px 8px rgba(0,0,0,0.08);
                    border-top: 4px solid {badge_color};'>
            <b style='color:#2E7D32; font-size:1rem'>{row.jour}</b><br>
            <small style='color:#888'>{row.date}</small><br><br>
            <b>🥗 Entrée</b><br><small>{row.entree}</small><br>
            <b>🍽️ Plat</b><br><small>{plat}</small><br>
            <b>🥦 Accomp.</b><br><small>{row.accompagnement}</small><br>
            <b>🍮 Dessert</b><br><small>{row.dessert}</small><br>
            <hr style='margin:0.5rem 0; border-color:#E8F5E9'>
            <small>{badge_label}</small><br>
            {"<small>🌿 CO₂ : <b>" + str(co2) + " kg</b></small><br>" if show_co2 else ""}
            {"<small>💰 Coût : <b>" + str(cout) + " €</b></small><br>" if show_cout else ""}
            {"<small>⭐ Pop. : <b>" + str(round(pop*100)) + "%</b></small>" if show_pop else ""}
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Règles métiers ────────────────────────────────────────────
st.markdown("### ⚖️ Règles métiers appliquées")
df_hist = get_historical_df()
df_hist["date"] = pd.to_datetime(df_hist["date"])
today = pd.Timestamp.today().normalize()

col_r1, col_r2 = st.columns(2)
with col_r1:
    st.markdown("""
    <div style='background:#E8F5E9; border-radius:12px; padding:1rem;'>
        <b style='color:#2E7D32'>📋 Règle 1 – Non-répétition des plats</b><br>
        <span style='font-size:0.9rem; color:#555'>
        Un plat ne doit pas réapparaître avant <b>7 jours</b>.<br>
        Un menu entier ne doit pas réapparaître avant <b>30 jours</b>.
        </span>
    </div>
    """, unsafe_allow_html=True)

with col_r2:
    recent = df_hist[df_hist["date"] >= today - timedelta(days=7)]
    plats_recents = recent["plat"].unique().tolist()
    st.markdown(f"""
    <div style='background:#FFF3E0; border-radius:12px; padding:1rem;'>
        <b style='color:#E65100'>⚠️ Plats à éviter cette semaine</b><br>
        <span style='font-size:0.9rem; color:#555'>
        {", ".join(plats_recents[:5]) if plats_recents else "Aucun · planification libre"}
        </span>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── Éditeur de menu ───────────────────────────────────────────
st.markdown("### ✏️ Modifier un menu")
with st.expander("Ouvrir l'éditeur de menu", expanded=False):
    col_j, col_c = st.columns([1, 2])
    with col_j:
        jour_edit = st.selectbox("Jour", ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"])
    with col_c:
        cantine_edit = st.selectbox("Cantine", ["Cantine A – Centre-ville", "Cantine B – Nord", "Cantine C – Sud"])

    col1, col2 = st.columns(2)
    with col1:
        entree_edit = st.selectbox("Entrée", PLATS["entrees"])
        plat_edit = st.selectbox("Plat principal", PLATS["plats"])
    with col2:
        accomp_edit = st.selectbox("Accompagnement", PLATS["accompagnements"])
        dessert_edit = st.selectbox("Dessert", PLATS["desserts"])

    # Calcul scores IA
    pop_edit = (
        POPULARITE.get(entree_edit, 0.65)
        + POPULARITE.get(plat_edit, 0.65)
        + POPULARITE.get(accomp_edit, 0.65)
        + POPULARITE.get(dessert_edit, 0.65)
    ) / 4
    co2_edit = CO2_PAR_PLAT.get(plat_edit, 2.5)
    cout_edit = COUT_PAR_REPAS.get(plat_edit, 3.80)
    waste_edit = round((1 - pop_edit) * 35, 1)

    st.markdown("#### 🤖 Scores IA estimés")
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("⭐ Popularité", f"{round(pop_edit*100)}%")
    s2.metric("🗑️ Risque gaspillage", f"{waste_edit}%")
    s3.metric("🌿 CO₂ estimé", f"{co2_edit} kg")
    s4.metric("💰 Coût estimé", f"{cout_edit} €")

    if waste_edit > 20:
        st.warning(f"⚠️ Risque de gaspillage élevé ({waste_edit}%) — envisagez un plat plus populaire.")
    else:
        st.success(f"✅ Menu bien équilibré – faible risque de gaspillage ({waste_edit}%)")

    if st.button("💾 Enregistrer ce menu"):
        st.success(f"Menu du {jour_edit} enregistré pour {cantine_edit} !")

st.divider()

# ── Vue planning multi-semaines ───────────────────────────────
st.markdown("### 📆 Planning sur 4 semaines")
today = datetime.today()
monday = today - timedelta(days=today.weekday())

planning_rows = []
for week_offset in range(4):
    for day_offset in range(5):
        date_day = monday + timedelta(weeks=week_offset, days=day_offset)
        jours_fr = ["Lun", "Mar", "Mer", "Jeu", "Ven"]
        plat_idx = (week_offset * 5 + day_offset) % len(PLATS["plats"])
        plat = PLATS["plats"][plat_idx]
        pop = POPULARITE.get(plat, 0.65)
        planning_rows.append({
            "Semaine": f"S{week_offset+1}",
            "Jour": jours_fr[day_offset],
            "Date": date_day.strftime("%d/%m"),
            "Plat": plat,
            "Popularité (%)": round(pop * 100),
            "Risque gaspillage (%)": round((1 - pop) * 35, 1),
            "CO₂ (kg)": CO2_PAR_PLAT.get(plat, 2.5),
            "Coût (€)": COUT_PAR_REPAS.get(plat, 3.80),
        })

planning_df = pd.DataFrame(planning_rows)

def highlight_risk(val):
    if isinstance(val, float) and val > 20:
        return "background-color: #FFEBEE; color: #C62828"
    if isinstance(val, float) and val < 12:
        return "background-color: #E8F5E9; color: #1B5E20"
    return ""

st.dataframe(
    planning_df.style.map(highlight_risk, subset=["Risque gaspillage (%)"]),
    use_container_width=True,
    hide_index=True,
)

# ── Repas solidaires ──────────────────────────────────────────
st.divider()
st.markdown("### ♻️ Repas solidaires du jour")
st.markdown("*Invendus disponibles à prix réduit – inspiré Too Good To Go*")

col_s1, col_s2, col_s3 = st.columns(3)
repas_solidaires = [
    {"nom": "Poulet rôti + Riz", "quantite": 8, "prix": 2.50, "heure": "13h30–14h00"},
    {"nom": "Lasagnes bolognaise", "quantite": 5, "prix": 2.00, "heure": "13h45–14h15"},
    {"nom": "Gratin de courgettes", "quantite": 12, "prix": 1.50, "heure": "13h30–14h00"},
]
for col, repas in zip([col_s1, col_s2, col_s3], repas_solidaires):
    with col:
        st.markdown(f"""
        <div style='background:white; border-radius:14px; padding:1rem;
                    box-shadow:0 2px 8px rgba(0,0,0,0.08); border-top:3px solid #4CAF50;'>
            <b>♻️ {repas["nom"]}</b><br>
            <span style='color:#888; font-size:0.85rem'>
                📦 {repas["quantite"]} portions restantes<br>
                🕐 Retrait : {repas["heure"]}<br>
                💰 Prix : <b style='color:#4CAF50'>{repas["prix"]} €</b>
            </span>
        </div>
        """, unsafe_allow_html=True)
        st.button(f"Réserver", key=f"res_{repas['nom']}")
