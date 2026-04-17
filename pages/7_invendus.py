import streamlit as st
import pandas as pd
import sys, os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.mock_data import get_repas_solidaires, get_historique_invendus, PLATS, CANTINES, COUT_PAR_REPAS

st.set_page_config(page_title="Repas Solidaires · Cantine+", page_icon="♻️", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F1F8E9; }
    h1, h2, h3 { color: #1B5E20 !important; }
    .stButton > button {
        border-radius: 14px; font-weight: 600; border: none; transition: all 0.2s;
    }
    [data-testid="stMetric"] {
        background: white; border-radius: 16px;
        padding: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        border-left: 4px solid #4CAF50;
    }
    .stTabs [aria-selected="true"] { background: #C8E6C9; color: #1B5E20 !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────
if "reservations_solidaires" not in st.session_state:
    st.session_state.reservations_solidaires = {}
if "invendu_soumis" not in st.session_state:
    st.session_state.invendu_soumis = False
if "invendus_declares" not in st.session_state:
    st.session_state.invendus_declares = []

repas_dispo = get_repas_solidaires()
historique = get_historique_invendus()
today = datetime.today()

with st.sidebar:
    st.markdown("## ♻️ Repas Solidaires")
    st.divider()
    nb_dispo = sum(1 for r in repas_dispo if r["disponible"])
    st.metric("Repas disponibles", nb_dispo)
    st.metric("Portions déclarées", historique["quantite_declaree"].sum())
    st.metric("Portions collectées", historique["quantite_collectee"].sum())
    st.divider()
    profil = st.radio("Je suis :", ["👩‍🍳 Personnel cantine", "👨‍👩‍👧 Parent / Citoyen", "🤝 Bénéficiaire"])

st.markdown("# ♻️ Repas Solidaires")
st.markdown("*Réduire le gaspillage · Partager avec sa communauté · Inspiré de Too Good To Go*")
st.divider()

tab1, tab2, tab3 = st.tabs([
    "🍱 Repas disponibles",
    "📢 Déclarer des invendus",
    "📊 Historique & Bilan",
])

# ═══════════════════════════════════════════════════════════════
# TAB 1 – REPAS DISPONIBLES
# ═══════════════════════════════════════════════════════════════
with tab1:
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("🍱 Repas disponibles", nb_dispo)
    k2.metric("💰 Économies max.", f"{sum(r['prix_normal'] - r['prix_reduit'] for r in repas_dispo):.2f} €")
    k3.metric("📦 Portions totales", sum(r["quantite"] for r in repas_dispo))
    k4.metric("🌿 CO₂ économisé", f"{sum(r['co2'] * r['quantite'] for r in repas_dispo):.1f} kg")

    st.divider()
    st.markdown("### 🍱 Repas disponibles aujourd'hui")
    st.caption(f"Mise à jour : {today.strftime('%H:%M')} — Ces repas sont proposés à prix réduit pour éviter le gaspillage.")

    cols = st.columns(2)
    for i, repas in enumerate(repas_dispo):
        col = cols[i % 2]
        resa_key = repas["id"]
        deja_reserve = st.session_state.reservations_solidaires.get(resa_key, False)

        co2_color = "#4CAF50" if repas["co2"] < 2 else ("#FF9800" if repas["co2"] < 4 else "#F44336")
        border_color = "#4CAF50" if repas["disponible"] else "#BDBDBD"
        qty_pct = max(0, repas["quantite"]) / 15

        with col:
            st.markdown(f"""
            <div style='background:white; border-radius:20px; padding:1.5rem;
                        box-shadow:0 4px 12px rgba(0,0,0,0.09);
                        border-top:5px solid {border_color}; margin-bottom:1rem;'>
                <div style='display:flex; justify-content:space-between; align-items:start;'>
                    <div>
                        <h3 style='color:#1B5E20; margin:0'>♻️ {repas["nom"]}</h3>
                        <p style='color:#888; margin:0.2rem 0; font-size:0.85rem'>
                            📍 {repas["cantine"]}
                        </p>
                    </div>
                    <div style='text-align:right;'>
                        <span style='font-size:1.5rem; font-weight:800; color:#4CAF50'>{repas["prix_reduit"]} €</span><br>
                        <small style='text-decoration:line-through; color:#aaa'>{repas["prix_normal"]} €</small>
                    </div>
                </div>
                <hr style='border-color:#E8F5E9; margin:0.8rem 0'>
                <div style='display:flex; gap:0.8rem; flex-wrap:wrap; margin-bottom:0.8rem'>
                    <span style='background:#E8F5E9; border-radius:20px; padding:0.2rem 0.7rem;
                                 color:#2E7D32; font-size:0.8rem'>
                        📦 {repas["quantite"]} portions
                    </span>
                    <span style='background:#FFF9C4; border-radius:20px; padding:0.2rem 0.7rem;
                                 color:#F57F17; font-size:0.8rem'>
                        🕐 {repas["heure_retrait"]}
                    </span>
                    <span style='background:#E3F2FD; border-radius:20px; padding:0.2rem 0.7rem;
                                 color:#1565C0; font-size:0.8rem'>
                        🔥 ~{repas["calories"]} kcal
                    </span>
                    <span style='background:#F1F8E9; border-radius:20px; padding:0.2rem 0.7rem;
                                 color:{co2_color}; font-size:0.8rem'>
                        🌿 {repas["co2"]} kg CO₂
                    </span>
                </div>
                <div style='background:#F5F5F5; border-radius:8px; height:6px; margin-bottom:0.5rem'>
                    <div style='background:#4CAF50; height:6px; border-radius:8px;
                                width:{min(qty_pct*100, 100):.0f}%'></div>
                </div>
                <small style='color:#888'>{repas["quantite"]} portions restantes</small>
            </div>
            """, unsafe_allow_html=True)

            if deja_reserve:
                st.markdown(f"""
                <div style='background:#E8F5E9; border-radius:12px; padding:0.8rem;
                            text-align:center; border:2px solid #4CAF50;'>
                    <b style='color:#2E7D32'>✅ Réservé !</b><br>
                    <small style='color:#555'>Présentez votre QR code au retrait</small>
                </div>
                """, unsafe_allow_html=True)

                # Mock QR Code (representation texte)
                st.markdown(f"""
                <div style='background:white; border-radius:12px; padding:1rem;
                            text-align:center; margin-top:0.5rem;
                            box-shadow:0 2px 6px rgba(0,0,0,0.07);'>
                    <div style='font-family:monospace; font-size:0.75rem; color:#333;
                                background:#f8f8f8; padding:0.8rem; border-radius:8px;
                                letter-spacing:2px; display:inline-block;'>
                        ██████ ██ ██████<br>
                        ██  ██ ░░ ██  ██<br>
                        ██████ ██ ██████<br>
                        ░░ ██ ░░ ██ ░░ ██<br>
                        ██████ ░░ ██████
                    </div><br>
                    <small style='color:#888; font-family:monospace'>{repas["id"]}-{today.strftime("%d%m%Y")}</small>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"❌ Annuler", key=f"ann_{resa_key}", use_container_width=True):
                    st.session_state.reservations_solidaires[resa_key] = False
                    st.rerun()
            else:
                if st.button(f"🛒 Réserver ce repas", key=f"res_{resa_key}",
                             use_container_width=True, type="primary"):
                    st.session_state.reservations_solidaires[resa_key] = True
                    st.rerun()

    nb_mes_resas = sum(1 for v in st.session_state.reservations_solidaires.values() if v)
    if nb_mes_resas:
        st.success(f"✅ {nb_mes_resas} repas solidaire(s) réservé(s). Présentez votre QR code au retrait !")

    st.divider()
    st.markdown("""
    <div style='background:#E8F5E9; border-radius:16px; padding:1.2rem;
                border-left:5px solid #4CAF50;'>
        <b style='color:#1B5E20'>🌱 Impact collectif</b><br>
        <p style='color:#555; font-size:0.9rem; margin:0.5rem 0 0 0'>
            Chaque repas solidaire collecté évite l'équivalent de <b>0.5 à 5 kg de CO₂</b> et permet
            à quelqu'un de manger un repas complet à prix solidaire.
            Merci de participer à la réduction du gaspillage alimentaire !
        </p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 2 – DÉCLARER DES INVENDUS (PERSONNEL)
# ═══════════════════════════════════════════════════════════════
with tab2:
    if profil != "👩‍🍳 Personnel cantine":
        st.info("🔐 Cette section est réservée au personnel de cantine. Connectez-vous en tant que personnel.")
        st.stop()

    st.markdown("### 📢 Déclarer des repas invendus")
    st.caption("Publiez les repas non servis pour les rendre disponibles en mode solidaire.")

    if st.session_state.invendu_soumis:
        last = st.session_state.invendus_declares[-1] if st.session_state.invendus_declares else {}
        st.success(f"✅ Invendu déclaré : **{last.get('plat', '')}** — {last.get('quantite', '')} portions à {last.get('prix', '')} €")
        st.markdown("""
        <div style='background:white; border-radius:12px; padding:1rem;
                    box-shadow:0 2px 6px rgba(0,0,0,0.07);'>
            <b style='color:#1B5E20'>📤 Publication automatique</b><br>
            <small style='color:#555'>Ce repas est maintenant visible dans la section "Repas disponibles".</small>
        </div>
        """, unsafe_allow_html=True)
        if st.button("➕ Déclarer un autre invendu"):
            st.session_state.invendu_soumis = False
            st.rerun()
    else:
        col_f1, col_f2 = st.columns(2)

        with col_f1:
            cantine_dec = st.selectbox("🏫 Cantine", CANTINES)
            plat_dec = st.selectbox("🍽️ Plat invendu", PLATS["plats"])
            entree_dec = st.selectbox("🥗 Entrée associée (optionnel)", ["Aucune"] + PLATS["entrees"])
            dessert_dec = st.selectbox("🍮 Dessert associé (optionnel)", ["Aucun"] + PLATS["desserts"])

        with col_f2:
            quantite_dec = st.number_input("📦 Quantité (portions)", min_value=1, max_value=200, value=10)
            prix_normal = COUT_PAR_REPAS.get(plat_dec, 3.80)
            reduction_pct = st.slider("💰 Réduction (%)", min_value=20, max_value=80, value=65, step=5)
            prix_reduit = round(prix_normal * (1 - reduction_pct / 100), 2)
            st.markdown(f"""
            <div style='background:#E8F5E9; border-radius:10px; padding:0.8rem;'>
                Prix normal : <s>{prix_normal} €</s> → Prix solidaire : <b style='color:#4CAF50'>{prix_reduit} €</b>
            </div>
            """, unsafe_allow_html=True)
            heure_debut = st.time_input("🕐 Début retrait", value=datetime.strptime("13:30", "%H:%M").time())
            heure_fin = st.time_input("🕑 Fin retrait", value=datetime.strptime("14:00", "%H:%M").time())

        st.divider()

        if st.button("📤 Publier dans Repas Solidaires", type="primary"):
            st.session_state.invendus_declares.append({
                "cantine": cantine_dec,
                "plat": plat_dec,
                "quantite": quantite_dec,
                "prix": prix_reduit,
                "heure": f"{heure_debut.strftime('%Hh%M')} – {heure_fin.strftime('%Hh%M')}",
                "date": today.strftime("%d/%m/%Y"),
            })
            st.session_state.invendu_soumis = True
            st.rerun()

# ═══════════════════════════════════════════════════════════════
# TAB 3 – HISTORIQUE & BILAN
# ═══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 📊 Bilan des repas solidaires – 14 derniers jours")

    total_dec = historique["quantite_declaree"].sum()
    total_col = historique["quantite_collectee"].sum()
    taux_col = round(total_col / total_dec * 100, 1) if total_dec > 0 else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📢 Portions déclarées", total_dec)
    k2.metric("🤝 Portions collectées", total_col)
    k3.metric("♻️ Taux de collecte", f"{taux_col}%")
    k4.metric("💰 Valeur redistribuée", f"{total_col * 1.5:.0f} €")

    st.divider()

    st.markdown("#### 📋 Historique détaillé")

    def color_statut(val):
        if val == "Collecté":
            return "background-color: #E8F5E9; color: #2E7D32"
        elif val == "Partiel":
            return "background-color: #FFF9C4; color: #F57F17"
        return "background-color: #FFEBEE; color: #C62828"

    st.dataframe(
        historique.style.map(color_statut, subset=["statut"]),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    col_imp1, col_imp2 = st.columns(2)
    with col_imp1:
        st.markdown("""
        <div style='background:white; border-radius:16px; padding:1.2rem;
                    box-shadow:0 2px 8px rgba(0,0,0,0.07);'>
            <h4 style='color:#1B5E20; margin-top:0'>🌿 Impact environnemental</h4>
            <p style='color:#555; font-size:0.9rem'>
                En 14 jours, les repas solidaires ont permis d'éviter l'équivalent de
                <b style='color:#4CAF50'>≈ 185 kg de CO₂</b> et
                <b style='color:#4CAF50'>≈ 62 kg de déchets alimentaires</b>.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_imp2:
        st.markdown("""
        <div style='background:white; border-radius:16px; padding:1.2rem;
                    box-shadow:0 2px 8px rgba(0,0,0,0.07);'>
            <h4 style='color:#1B5E20; margin-top:0'>🤝 Impact social</h4>
            <p style='color:#555; font-size:0.9rem'>
                <b style='color:#4CAF50'>≈ 234 repas</b> redistribués à prix solidaire,
                soit environ <b style='color:#4CAF50'>351 € d'économies</b>
                pour les bénéficiaires de la communauté locale.
            </p>
        </div>
        """, unsafe_allow_html=True)
