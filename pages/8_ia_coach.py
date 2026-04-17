"""
IA Coach Enfant – Analyse un plateau de cantine et génère un script TTS motivant.
Basé sur le prompt pédagogique du formateur Keskia.
"""

import streamlit as st
import json
import sys, os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.mock_data import (
    generate_ia_coach_analysis, FOOD_CATEGORIES, PLATS,
)

st.set_page_config(page_title="IA Coach Enfant · Cantine+", page_icon="🤖", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #E0F7FA 0%, #E8EAF6 100%); }
    h1 { color: #006064 !important; }
    h2, h3 { color: #00838F !important; }
    .stButton > button {
        border-radius: 14px; font-weight: 700; border: none;
        padding: 0.6rem 1.5rem; transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background: #E0F7FA; color: #006064 !important; font-weight: 700;
    }
    .tts-script-box {
        background: linear-gradient(135deg, #006064, #00838F);
        border-radius: 20px; padding: 2rem;
        color: white; font-size: 1.15rem;
        line-height: 1.8; font-weight: 500;
        box-shadow: 0 8px 24px rgba(0,96,100,0.25);
    }
    .json-box {
        background: #1E2A30; border-radius: 14px;
        padding: 1.2rem; font-family: monospace;
        font-size: 0.82rem; color: #E0F7FA; overflow-x: auto;
    }
    [data-testid="stMetric"] {
        background: white; border-radius: 14px;
        padding: 0.8rem; box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        border-left: 4px solid #00838F;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────
if "analyse_result" not in st.session_state:
    st.session_state.analyse_result = None
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

with st.sidebar:
    st.markdown("## 🤖 IA Coach Enfant")
    st.divider()
    st.markdown("""
    **Comment ça marche ?**

    1. 📸 Uploadez une photo du plateau **ou** sélectionnez les aliments manuellement
    2. 🤖 L'IA analyse le contenu nutritionnel
    3. 📝 Un script TTS motivant est généré pour encourager l'enfant à manger
    4. 📋 Copiez le JSON pour l'intégrer à votre système TTS

    ---
    **Public cible :** Enfants 4–11 ans
    **Format sortie :** JSON strict
    **Longueur script :** 35–90 mots
    """)
    st.divider()
    st.markdown("**🔧 Paramètres**")
    age_groupe = st.radio("Tranche d'âge", ["4–6 ans (maternelle)", "6–9 ans (primaire)", "9–11 ans (CM)"])
    langue = st.selectbox("Langue", ["Français"])
    st.divider()
    if st.button("🗑️ Réinitialiser", use_container_width=True):
        st.session_state.analyse_result = None
        st.session_state.uploaded_image = None
        st.rerun()

# ── Header ────────────────────────────────────────────────────
st.markdown("# 🤖 IA Coach Enfant")
st.markdown("*Génère un script audio motivant et bienveillant pour encourager l'enfant à manger*")
st.divider()

tab1, tab2, tab3 = st.tabs(["📸 Analyse plateau", "📋 Résultat JSON & Script", "📚 Guide pédagogique"])

# ═══════════════════════════════════════════════════════════════
# TAB 1 – ANALYSE DU PLATEAU
# ═══════════════════════════════════════════════════════════════
with tab1:
    col_photo, col_select = st.columns([1, 1])

    with col_photo:
        st.markdown("### 📸 Photo du plateau")
        st.caption("Uploadez une photo du plateau de cantine pour une analyse automatique.")

        uploaded = st.file_uploader(
            "Choisir une image",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
        )

        if uploaded:
            st.session_state.uploaded_image = uploaded
            st.image(uploaded, caption="Plateau analysé", use_column_width=True)
            st.markdown("""
            <div style='background:#E0F7FA; border-radius:12px; padding:0.8rem;
                        border-left:4px solid #00838F; margin-top:0.5rem;'>
                <small style='color:#006064'>
                    📸 Image uploadée — <b>Sélectionnez les aliments détectés</b> ci-contre
                    pour générer le script TTS adapté.
                </small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background:white; border-radius:16px; padding:2rem;
                        text-align:center; border:3px dashed #B2EBF2;
                        box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
                <div style='font-size:4rem'>📷</div>
                <p style='color:#888; margin:0.5rem 0'>
                    Glissez-déposez une photo de plateau<br>ou cliquez pour choisir un fichier
                </p>
                <small style='color:#aaa'>JPG, PNG, WEBP — Max 10 Mo</small>
            </div>
            """, unsafe_allow_html=True)

    with col_select:
        st.markdown("### 🥗 Aliments détectés / sélectionnés")
        st.caption("Sélectionnez les aliments visibles sur le plateau pour générer le script.")

        all_foods = (
            PLATS["entrees"]
            + PLATS["plats"]
            + PLATS["accompagnements"]
            + PLATS["desserts"]
            + ["Brocoli", "Épinards", "Petits pois", "Jambon", "Pain", "Fromage", "Pomme", "Banane", "Orange"]
        )

        st.markdown("**🥩 Protéines**")
        sel_proteines = st.multiselect(
            "Protéines",
            [f for f in FOOD_CATEGORIES["protéines"] if f in all_foods or f in FOOD_CATEGORIES["protéines"]],
            label_visibility="collapsed",
            key="sel_prot",
        )

        st.markdown("**🥦 Légumes**")
        sel_legumes = st.multiselect(
            "Légumes",
            FOOD_CATEGORIES["légumes"],
            label_visibility="collapsed",
            key="sel_leg",
        )

        st.markdown("**🍝 Féculents**")
        sel_feculents = st.multiselect(
            "Féculents",
            FOOD_CATEGORIES["féculents"],
            label_visibility="collapsed",
            key="sel_fec",
        )

        st.markdown("**🍎 Fruits & Desserts**")
        sel_fruits = st.multiselect(
            "Fruits & desserts",
            FOOD_CATEGORIES["fruits"] + FOOD_CATEGORIES["desserts"],
            label_visibility="collapsed",
            key="sel_fruits",
        )

        sel_autres = st.multiselect(
            "**🥛 Autres** (pain, fromage, lait...)",
            FOOD_CATEGORIES["produits_laitiers"] + ["Pain", "Beurre", "Eau"],
            key="sel_autres",
        )

        all_selected = sel_proteines + sel_legumes + sel_feculents + sel_fruits + sel_autres

        if all_selected:
            st.markdown(f"""
            <div style='background:#E0F7FA; border-radius:10px; padding:0.6rem 1rem; margin-top:0.5rem;'>
                <small style='color:#006064'>
                    <b>{len(all_selected)} aliment(s) sélectionné(s) :</b>
                    {", ".join(all_selected[:5])}{"..." if len(all_selected) > 5 else ""}
                </small>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Bouton analyse
        can_analyse = len(all_selected) > 0
        if not can_analyse:
            st.caption("⚠️ Sélectionnez au moins un aliment pour générer le script.")

        if st.button(
            "🤖 Analyser et générer le script TTS",
            type="primary",
            use_container_width=True,
            disabled=not can_analyse,
        ):
            with st.spinner("🤖 L'IA analyse le plateau et génère le script..."):
                import time
                time.sleep(1.2)
                result = generate_ia_coach_analysis(all_selected)
                st.session_state.analyse_result = result
            st.success("✅ Analyse terminée ! Consultez l'onglet **📋 Résultat JSON & Script**")
            st.balloons()

    # ─── Exemple rapide ───────────────────────────────────────
    st.divider()
    st.markdown("### ⚡ Exemples rapides")
    col_ex1, col_ex2, col_ex3, col_ex4 = st.columns(4)
    exemples = [
        ("🍗 Plat protéiné", ["Poulet rôti", "Riz", "Haricots verts"]),
        ("🥗 Repas équilibré", ["Lasagnes bolognaise", "Salade verte", "Fruits frais de saison"]),
        ("🥦 Légumes-stars", ["Gratin de courgettes", "Carottes glacées", "Compote de pommes"]),
        ("🐟 Menu poisson", ["Filet de cabillaud", "Purée de pommes de terre", "Yaourt nature"]),
    ]
    for col, (label, foods) in zip([col_ex1, col_ex2, col_ex3, col_ex4], exemples):
        with col:
            if st.button(label, use_container_width=True, key=f"ex_{label}"):
                result = generate_ia_coach_analysis(foods)
                st.session_state.analyse_result = result
                st.rerun()

# ═══════════════════════════════════════════════════════════════
# TAB 2 – RÉSULTAT JSON & SCRIPT
# ═══════════════════════════════════════════════════════════════
with tab2:
    if st.session_state.analyse_result is None:
        st.markdown("""
        <div style='background:white; border-radius:16px; padding:3rem;
                    text-align:center; box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
            <div style='font-size:4rem'>🤖</div>
            <h3 style='color:#00838F'>Aucune analyse en cours</h3>
            <p style='color:#888'>
                Allez dans l'onglet <b>📸 Analyse plateau</b>,
                sélectionnez des aliments et cliquez sur Analyser.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        result = st.session_state.analyse_result

        # ─── Script TTS en vedette ─────────────────────────────
        st.markdown("### 🎙️ Script TTS généré")
        st.markdown(f"""
        <div class='tts-script-box'>
            <div style='font-size:0.8rem; opacity:0.7; margin-bottom:0.8rem; letter-spacing:1px'>
                🎙️ SCRIPT AUDIO — {result["voice_style"].upper()}
            </div>
            {result["tts_script"]}
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        words = len(result["tts_script"].split())
        c1.metric("📝 Mots", words)
        c2.metric("🎯 Confiance IA", f"{result['confidence']*100:.0f}%")
        c3.metric("🥗 Aliments détectés", len(result["detected_foods"]))

        st.divider()

        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown("### 🥗 Résumé nutritionnel")
            st.markdown(f"""
            <div style='background:white; border-radius:14px; padding:1.2rem;
                        box-shadow:0 2px 6px rgba(0,0,0,0.06);'>
                <p style='color:#555; font-size:0.9rem; margin-bottom:0.8rem'>
                    {result["food_summary"]}
                </p>
                <b style='color:#00838F'>Aliments identifiés :</b><br>
                <div style='display:flex; flex-wrap:wrap; gap:0.4rem; margin-top:0.5rem'>
                    {"".join(f"<span style='background:#E0F7FA; border-radius:20px; padding:0.2rem 0.7rem; color:#006064; font-size:0.82rem'>{f}</span>" for f in result["detected_foods"])}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 💡 Bénéfices identifiés")
            for b in result["benefits"]:
                st.markdown(f"""
                <div style='background:#E8F5E9; border-radius:10px; padding:0.5rem 0.9rem;
                            margin-bottom:0.4rem; color:#2E7D32; font-size:0.9rem'>
                    ✅ {b.capitalize()}
                </div>
                """, unsafe_allow_html=True)

        with col_right:
            st.markdown("### 🛡️ Notes de sécurité pédagogique")
            for note in result["safety_notes"]:
                st.markdown(f"""
                <div style='background:#FFF3E0; border-radius:10px; padding:0.5rem 0.9rem;
                            margin-bottom:0.4rem; color:#E65100; font-size:0.85rem;
                            border-left:3px solid #FF9800'>
                    ⚠️ {note.capitalize()}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style='background:#E8EAF6; border-radius:12px; padding:0.9rem;'>
                <b style='color:#3949AB'>🎭 Style vocal recommandé</b><br>
                <p style='color:#555; font-size:0.9rem; margin:0.3rem 0 0 0'>
                    {result["voice_style"].capitalize()}
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # ─── JSON complet ──────────────────────────────────────
        st.markdown("### 📋 JSON complet (à intégrer dans votre système TTS)")
        json_str = json.dumps(result, ensure_ascii=False, indent=2)

        st.markdown(f"""
        <div class='json-box'>
            <pre style='margin:0; white-space:pre-wrap'>{json_str}</pre>
        </div>
        """, unsafe_allow_html=True)

        col_copy, col_dl, _ = st.columns([1, 1, 2])
        with col_copy:
            st.code(json_str, language="json")
        with col_dl:
            st.download_button(
                "⬇️ Télécharger JSON",
                data=json_str,
                file_name=f"ia_coach_{datetime.today().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                use_container_width=True,
            )

        st.divider()
        col_gen, col_reset = st.columns([2, 1])
        with col_reset:
            if st.button("🔄 Nouvelle analyse", use_container_width=True):
                st.session_state.analyse_result = None
                st.rerun()

# ═══════════════════════════════════════════════════════════════
# TAB 3 – GUIDE PÉDAGOGIQUE
# ═══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 📚 Guide pédagogique – IA Coach Enfant")
    st.markdown("""
    <div style='background:white; border-radius:16px; padding:1.5rem;
                box-shadow:0 2px 8px rgba(0,0,0,0.07); margin-bottom:1rem;'>
        <h4 style='color:#006064; margin-top:0'>🎯 Objectif pédagogique</h4>
        <p style='color:#555'>
            Le Coach IA agit comme un <b>allié bienveillant</b> qui transforme le moment du repas
            en <b>petite mission positive</b>. Il encourage les enfants à goûter et découvrir
            sans jamais culpabiliser, menacer ou forcer.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_do, col_dont = st.columns(2)

    with col_do:
        st.markdown("""
        <div style='background:#E8F5E9; border-radius:16px; padding:1.2rem;'>
            <h4 style='color:#2E7D32; margin-top:0'>✅ Ce que le Coach FAIT</h4>
            <ul style='color:#555; font-size:0.9rem'>
                <li>Parle comme un héros protecteur et enthousiaste</li>
                <li>Utilise des métaphores positives ("plein d'énergie", "mission")</li>
                <li>Valorise chaque aliment selon ses bénéfices concrets</li>
                <li>Invite à <i>goûter</i>, pas à finir l'assiette</li>
                <li>Respecte la satiété de l'enfant</li>
                <li>Utilise un vocabulaire simple (4–11 ans)</li>
                <li>Génère un script fluide pour lecture TTS</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_dont:
        st.markdown("""
        <div style='background:#FFEBEE; border-radius:16px; padding:1.2rem;'>
            <h4 style='color:#C62828; margin-top:0'>❌ Ce que le Coach NE FAIT PAS</h4>
            <ul style='color:#555; font-size:0.9rem'>
                <li>Culpabiliser ("si tu ne finis pas...")</li>
                <li>Menacer ou faire du chantage</li>
                <li>Ridiculiser l'enfant</li>
                <li>Parler du poids, de la minceur ou de "grossir"</li>
                <li>Forcer à finir l'assiette</li>
                <li>Ignorer la satiété</li>
                <li>Faire des promesses médicales absurdes</li>
                <li>Utiliser du jargon nutritionnel</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### 🎭 Formulations recommandées")
    formulations = [
        ("mission énergie", "Transforme le repas en aventure positive"),
        ("plein de force", "Associe la nourriture à la capacité d'agir"),
        ("corps en forme", "Résultat positif et concret"),
        ("goûte avec courage", "Invite sans forcer"),
        ("bouchées de champion", "Valorise chaque effort"),
        ("chaque bouchée aide ton corps", "Lien action–bénéfice simple"),
        ("continue ta mission", "Clôture héroïque et motivante"),
        ("je suis là pour t'aider", "Ton protecteur et bienveillant"),
    ]
    for f, expl in formulations:
        st.markdown(f"""
        <div style='background:white; border-radius:10px; padding:0.6rem 1rem;
                    box-shadow:0 1px 4px rgba(0,0,0,0.06); margin-bottom:0.4rem;
                    display:flex; gap:1rem; align-items:center;'>
            <span style='background:#E0F7FA; border-radius:20px; padding:0.2rem 0.8rem;
                         color:#006064; font-weight:600; font-size:0.85rem; white-space:nowrap'>
                "{f}"
            </span>
            <small style='color:#888'>{expl}</small>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### 📏 Structure du script TTS")
    st.markdown("""
    <div style='background:white; border-radius:14px; padding:1.2rem;
                box-shadow:0 2px 6px rgba(0,0,0,0.06);'>
        <ol style='color:#555; font-size:0.9rem; line-height:2'>
            <li><b style='color:#006064'>Accroche motivante</b> — attire l'attention, ton héroïque</li>
            <li><b style='color:#006064'>Mention du plat</b> — cite 1 à 3 éléments visibles</li>
            <li><b style='color:#006064'>Association bénéfice</b> — énergie, force, concentration, croissance</li>
            <li><b style='color:#006064'>Invitation douce</b> — "goûte", "essaie", "chaque bouchée"</li>
            <li><b style='color:#006064'>Clôture héroïque</b> — formule positive et encourageante</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🔌 Intégration système TTS")
    st.code("""
# Exemple d'intégration Python avec le JSON généré
import json
import requests  # ou bibliothèque TTS de votre choix

# Charger l'analyse IA
with open("ia_coach_20240417_1330.json") as f:
    data = json.load(f)

# Extraire le script
script = data["tts_script"]
voice_style = data["voice_style"]
confidence = data["confidence"]

# Envoyer au moteur TTS (ex: Qwen TTS, ElevenLabs, etc.)
if confidence >= 0.6:
    tts_engine.speak(script, voice=voice_style)
else:
    # Faible confiance : utiliser le script générique
    tts_engine.speak("Ton repas est prêt, aventurier !")
""", language="python")
