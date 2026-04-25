"""
IA Coach Enfant – Analyse un plateau de cantine et génère un script TTS motivant.
Basé sur le prompt pédagogique du formateur Keskia.
"""

import streamlit as st
import json
import sys, os
import io
import asyncio
import base64
import requests as _requests
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.mock_data import (
    generate_ia_coach_analysis, FOOD_CATEGORIES, PLATS,
)

# ── TTS : ElevenLabs → edge-tts (Eloïse) → gtts ────────────────
try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False

HAS_TTS = HAS_EDGE_TTS or HAS_GTTS

# Voix enfant Microsoft — fallback gratuit le plus proche cartoon
ELOISE_VOICE = "fr-FR-EloiseNeural"

# Paramètres ElevenLabs — style dessin animé expressif
ELEVEN_MODEL   = "eleven_multilingual_v2"   # Supporte le français natif
ELEVEN_VOICE   = "nPczCjzI2devNBz1zQrb"    # Charlie — jeune, énergique
ELEVEN_SETTINGS = {
    "stability": 0.25,          # Faible = très expressif, varié
    "similarity_boost": 0.75,
    "style": 0.65,              # Élevé = intonation dramatique/cartoon
    "use_speaker_boost": True,
    "speed": 1.1,               # Légèrement plus rapide = énergie
}


# Préfixe parlé pour l'ambiance Sonic
SONIC_INTRO = "Sonic, à toute vitesse !"


def generate_elevenlabs_audio(text: str, api_key: str, voice_id: str) -> bytes | None:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key,
    }
    payload = {
        "text": SONIC_INTRO + text,
        "model_id": ELEVEN_MODEL,
        "voice_settings": ELEVEN_SETTINGS,
    }
    try:
        resp = _requests.post(url, json=payload, headers=headers, timeout=20)
        if resp.status_code == 200:
            return resp.content
        return None
    except Exception:
        return None


async def _eloise_audio(text: str) -> bytes:
    # Eloïse = voix enfant Microsoft — plus cartoon qu'Henri
    # rate +10% + pitch +8Hz pour plus d'énergie
    communicate = edge_tts.Communicate(
        SONIC_INTRO + text, ELOISE_VOICE, rate="+10%", pitch="+8Hz"
    )
    buf = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buf.write(chunk["data"])
    buf.seek(0)
    return buf.read()


def generate_eloise_audio(text: str) -> bytes | None:
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_eloise_audio(text))
        loop.close()
        return result
    except Exception:
        return None


def generate_audio(text: str, eleven_key: str = "", voice_id: str = ELEVEN_VOICE) -> bytes | None:
    # 1. ElevenLabs (meilleure qualité cartoon)
    if eleven_key.strip():
        data = generate_elevenlabs_audio(text, eleven_key.strip(), voice_id.strip() or ELEVEN_VOICE)
        if data:
            return data
    # 2. edge-tts Eloïse (voix enfant gratuite)
    if HAS_EDGE_TTS:
        data = generate_eloise_audio(text)
        if data:
            return data
    # 3. gtts dernier recours
    if HAS_GTTS:
        try:
            tts = gTTS(text=SONIC_INTRO + text, lang="fr", slow=False)
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            return buf.read()
        except Exception:
            pass
    return None


def detect_foods_mistral(image_bytes: bytes, api_key: str, mime: str = "image/jpeg") -> list:
    """
    Envoie l'image à Mistral Pixtral-12B et retourne la liste des aliments détectés.
    """
    b64 = base64.b64encode(image_bytes).decode()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "pixtral-12b-2409",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"},
                    },
                    {
                        "type": "text",
                        "text": (
                            "Tu es un expert en nutrition scolaire qui analyse des plateaux de cantine. "
                            "Analyse cette image EN SUIVANT CET ORDRE STRICT :\n"
                            "1. Assiette principale : liste TOUS les aliments qu'elle contient (viande, légumes, féculents, sauce, garniture)\n"
                            "2. Bol ou ramequin : liste TOUS les aliments qu'il contient\n"
                            "3. Pain ou viennoiserie : nomme-le\n"
                            "4. Fruit : nomme-le\n"
                            "5. Produit laitier (yaourt, fromage, crème) : nomme-le\n"
                            "6. Boisson : nomme-la\n"
                            "Termine un contenant complètement avant de passer au suivant. "
                            "Ne saute aucun aliment visible, même les sauces, herbes ou garnitures. "
                            "Utilise des noms simples et courants en français (ex: 'Poulet rôti', 'Haricots verts', 'Purée de carottes'). "
                            "Réponds UNIQUEMENT avec un tableau JSON à plat, sans catégories, sans explication. "
                            "Format : [\"Aliment 1\", \"Aliment 2\", ...]"
                        ),
                    },
                ],
            }
        ],
        "max_tokens": 600,
        "temperature": 0.1,
    }
    try:
        resp = _requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"]
            import re

            # 1. Chercher un tableau JSON dans la réponse (multi-lignes)
            match = re.search(r"\[[\s\S]*?\]", content)
            if match:
                raw = match.group()
                # Nettoyer les problèmes courants de JSON
                raw = re.sub(r",\s*\]", "]", raw)       # virgule finale
                raw = re.sub(r"[\n\r\t]", " ", raw)     # retours à la ligne
                raw = re.sub(r"\s{2,}", " ", raw)        # espaces multiples
                try:
                    foods = json.loads(raw)
                    return [str(f).strip() for f in foods if str(f).strip()]
                except Exception:
                    pass

            # 2. Extraire toutes les chaînes entre guillemets
            items = re.findall(r'"([^"]{2,50})"', content)
            if items:
                return items

            # 3. Extraire ligne par ligne (liste à tirets ou numérotée)
            lines = []
            for line in content.split("\n"):
                line = re.sub(r"^[\s\-\*\d\.]+", "", line).strip().strip('",')
                if 2 < len(line) < 60:
                    lines.append(line)
            return lines if lines else []
        else:
            # Stocker l'erreur dans session pour affichage
            import streamlit as st
            st.session_state["mistral_error"] = f"Erreur {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        import streamlit as st
        st.session_state["mistral_error"] = str(e)
    return []


def audio_player(audio_bytes: bytes) -> str:
    """Lecteur base64 — fonctionne sur iOS Safari et Android Chrome."""
    b64 = base64.b64encode(audio_bytes).decode()
    return f"""
    <div style="background:linear-gradient(135deg,#0044AA,#1A90FF);
                border-radius:20px; padding:1.4rem; color:white; text-align:center;
                box-shadow:0 6px 20px rgba(0,68,170,0.4);">
        <div style="font-size:2rem; margin-bottom:0.3rem">⚡</div>
        <div style="font-weight:800; font-size:1rem; letter-spacing:2px; margin-bottom:1rem">
            MESSAGE DU COACH SONIC
        </div>
        <audio controls style="width:100%; border-radius:10px;">
            <source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg">
        </audio>
    </div>
    """


# ── Détection automatique des aliments depuis l'image ────────────
def simulate_food_detection(image_file) -> dict:
    import random as _rnd
    seed = sum(ord(c) for c in image_file.name) + image_file.size % 100
    rng = _rnd.Random(seed)
    proteines = rng.sample(FOOD_CATEGORIES["protéines"], rng.randint(1, 2))
    legumes   = rng.sample(FOOD_CATEGORIES["légumes"],   rng.randint(1, 2))
    feculents = rng.sample(FOOD_CATEGORIES["féculents"], rng.randint(0, 1))
    fruits    = rng.sample(
        FOOD_CATEGORIES["fruits"] + FOOD_CATEGORIES["desserts"], 1,
    )
    return {
        "sel_prot":   proteines,
        "sel_leg":    legumes,
        "sel_fec":    feculents,
        "sel_fruits": fruits,
        "sel_autres": [],
    }


# ── Config page ───────────────────────────────────────────────────
st.set_page_config(page_title="IA Coach Enfant · Cantine+", page_icon="⚡", layout="wide")

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
    .detect-badge {
        background: linear-gradient(135deg, #006064, #00838F);
        border-radius: 14px; padding: 1rem 1.2rem;
        color: white; font-size: 0.92rem; margin-top: 0.8rem;
    }
    [data-testid="stMetric"] {
        background: white; border-radius: 14px;
        padding: 0.8rem; box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        border-left: 4px solid #00838F;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────
for key in ("analyse_result", "uploaded_image_name", "audio_bytes"):
    if key not in st.session_state:
        st.session_state[key] = None

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚡ IA Coach Enfant")
    st.divider()

    st.markdown("**🔑 Clé API Mistral**")
    st.caption("Pour détecter les aliments depuis une photo.")
    mistral_key = st.text_input(
        "Clé Mistral AI",
        type="password",
        placeholder="...",
        key="mistral_key",
    )
    if mistral_key.strip():
        st.success("✅ Détection IA activée (Pixtral-12B)")
    else:
        st.info("Sans clé → détection simulée")

    st.divider()
    eleven_key = ""
    voice_id   = ELEVEN_VOICE
    if st.button("🗑️ Réinitialiser", use_container_width=True):
        for k in ("analyse_result", "uploaded_image_name", "audio_bytes",
                  "sel_prot", "sel_leg", "sel_fec", "sel_fruits", "sel_autres",
                  "custom_foods"):
            st.session_state.pop(k, None)
        st.rerun()

# ── Header ────────────────────────────────────────────────────────
st.markdown("# ⚡ IA Coach Enfant — Sonic")
st.markdown("*Uploadez une photo du plateau — le Coach génère un message audio style Sonic !*")
st.divider()

tab1, tab2, tab3 = st.tabs(["📸 Analyse plateau", "🔊 Résultat & Audio", "📚 Guide pédagogique"])

# ═══════════════════════════════════════════════════════════════════
# TAB 1 – ANALYSE DU PLATEAU
# ═══════════════════════════════════════════════════════════════════
with tab1:
    col_photo, col_select = st.columns([1, 1])

    with col_photo:
        st.markdown("### 📸 Photo du plateau")
        st.caption("Uploadez une photo — les aliments seront détectés automatiquement.")

        uploaded = st.file_uploader(
            "Choisir une image",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
        )

        if uploaded:
            # Lire les bytes EN PREMIER avant tout affichage
            img_bytes = uploaded.read()
            st.image(img_bytes, caption="Plateau analysé", use_container_width=True)

            if uploaded.name != st.session_state.uploaded_image_name:
                st.session_state.uploaded_image_name = uploaded.name
                st.session_state.analyse_result = None
                st.session_state.audio_bytes = None

                if mistral_key.strip():
                    with st.spinner("🤖 Pixtral analyse l'image..."):
                        mime = "image/png" if uploaded.name.lower().endswith(".png") else "image/jpeg"
                        foods = detect_foods_mistral(img_bytes, mistral_key.strip(), mime)
                    if foods:
                        st.session_state.custom_foods = foods
                        for k in ("sel_prot", "sel_leg", "sel_fec", "sel_fruits", "sel_autres"):
                            st.session_state[k] = []
                        st.markdown(f"""
                        <div class='detect-badge'>
                            🤖 <b>Pixtral a détecté {len(foods)} aliment(s) :</b>
                            {", ".join(foods)}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        err = st.session_state.pop("mistral_error", "")
                        st.error(f"⚠️ Pixtral n'a pas pu détecter les aliments.\n\n`{err}`" if err else "⚠️ Détection échouée — vérifiez la clé API.")
                else:
                    with st.spinner("🔍 Détection simulée en cours..."):
                        import time; time.sleep(0.8)
                        detected = simulate_food_detection(uploaded)
                    for k, v in detected.items():
                        st.session_state[k] = v
                    total = sum(len(v) for v in detected.values())
                    st.markdown(f"""
                    <div class='detect-badge'>
                        ✅ <b>{total} aliments détectés (simulation)</b> —
                        vérifiez ci-contre puis cliquez <b>Analyser</b> !
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='background:#E0F7FA; border-radius:12px; padding:0.8rem;
                            border-left:4px solid #00838F; margin-top:0.5rem;'>
                    <small style='color:#006064'>
                        ✅ Aliments détectés — cliquez <b>Analyser</b> pour générer le message.
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
                <small style='color:#aaa'>JPG, PNG, WEBP</small>
            </div>
            """, unsafe_allow_html=True)

    with col_select:
        st.markdown("### 🥗 Aliments détectés")

        if "custom_foods" not in st.session_state:
            st.session_state.custom_foods = []

        all_selected = st.session_state.custom_foods
        seen = set()
        all_selected = [x for x in all_selected if not (x in seen or seen.add(x))]

        if all_selected:
            st.markdown(f"""
            <div style='background:#E0F7FA; border-radius:10px; padding:0.8rem 1rem; margin-top:0.5rem;'>
                <b style='color:#006064'>🤖 {len(all_selected)} aliment(s) détecté(s) :</b><br>
                <span style='color:#006064; font-size:0.9rem'>{", ".join(all_selected)}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background:white; border-radius:12px; padding:1.5rem;
                        text-align:center; border:2px dashed #B2EBF2;'>
                <div style='font-size:2rem'>📷</div>
                <p style='color:#888; font-size:0.9rem; margin:0.3rem 0'>
                    Uploadez une photo — les aliments seront détectés automatiquement
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        can_analyse = len(all_selected) > 0
        if not can_analyse:
            st.caption("⚠️ Uploadez une photo pour détecter les aliments.")

        vid = voice_id if "voice_id" in dir() else ELEVEN_VOICE
        if st.button("⚡ Analyser le plateau", type="primary",
                     use_container_width=True, disabled=not can_analyse):
            with st.spinner("⚡ Le Coach prépare son message..."):
                import time; time.sleep(1.0)
                result = generate_ia_coach_analysis(all_selected)
                st.session_state.analyse_result = result
                if HAS_TTS or eleven_key.strip():
                    st.session_state.audio_bytes = generate_audio(
                        result["tts_script"], eleven_key, vid
                    )
            st.success("✅ Prêt ! Consultez l'onglet **🔊 Résultat & Audio**")
            st.balloons()

    # ─── Exemples rapides ─────────────────────────────────────────
    st.divider()
    st.markdown("### ⚡ Autres exemples")
    col_ex1, col_ex2, col_ex3, col_ex4 = st.columns(4)
    exemples = [
        ("🍗 Plat protéiné",   ["Poulet rôti", "Riz", "Haricots verts"]),
        ("🥗 Repas équilibré", ["Lasagnes bolognaise", "Salade verte", "Fruits frais de saison"]),
        ("🥦 Légumes-stars",   ["Gratin de courgettes", "Carottes glacées", "Compote de pommes"]),
        ("🐟 Menu poisson",    ["Filet de cabillaud", "Purée de pommes de terre", "Yaourt nature"]),
    ]
    for col, (label, foods) in zip([col_ex1, col_ex2, col_ex3, col_ex4], exemples):
        with col:
            if st.button(label, use_container_width=True, key=f"ex_{label}"):
                result = generate_ia_coach_analysis(foods)
                st.session_state.analyse_result = result
                vid2 = voice_id if "voice_id" in dir() else ELEVEN_VOICE
                if HAS_TTS or eleven_key.strip():
                    st.session_state.audio_bytes = generate_audio(
                        result["tts_script"], eleven_key, vid2
                    )
                st.rerun()

# ═══════════════════════════════════════════════════════════════════
# TAB 2 – RÉSULTAT & AUDIO
# ═══════════════════════════════════════════════════════════════════
with tab2:
    if st.session_state.analyse_result is None:
        st.markdown("""
        <div style='background:white; border-radius:16px; padding:3rem;
                    text-align:center; box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
            <div style='font-size:4rem'>⚡</div>
            <h3 style='color:#00838F'>Aucune analyse en cours</h3>
            <p style='color:#888'>
                Allez dans l'onglet <b>📸 Analyse plateau</b>,
                uploadez une photo et cliquez sur <b>Analyser le plateau</b>.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        result = st.session_state.analyse_result
        audio_bytes = st.session_state.get("audio_bytes")

        # ─── Lecteur Sonic ────────────────────────────────
        st.markdown("### ⚡ Message du Coach")

        if audio_bytes:
            st.markdown(audio_player(audio_bytes), unsafe_allow_html=True)
            st.download_button(
                "⬇️ Télécharger l'audio MP3",
                data=audio_bytes,
                file_name=f"coach_enfant_{datetime.today().strftime('%Y%m%d_%H%M')}.mp3",
                mime="audio/mpeg",
            )
        elif HAS_TTS or eleven_key.strip():
            if st.button("▶️ Générer l'audio", type="primary"):
                with st.spinner("🎙️ Génération en cours..."):
                    vid3 = voice_id if "voice_id" in dir() else ELEVEN_VOICE
                    audio_bytes = generate_audio(result["tts_script"], eleven_key, vid3)
                    st.session_state.audio_bytes = audio_bytes
                if audio_bytes:
                    st.markdown(audio_player(audio_bytes), unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Connexion internet requise pour générer l'audio.")
        else:
            st.info("📦 Ajoutez une clé ElevenLabs dans la barre latérale.")

        # ─── Métriques ─────────────────────────────────────────────
        c1, c2, c3 = st.columns(3)
        c1.metric("🎯 Confiance IA", f"{result['confidence']*100:.0f}%")
        c2.metric("🥗 Aliments", len(result["detected_foods"]))
        voice_label = "ElevenLabs 🎙️" if eleven_key.strip() else ("Eloïse Neural 🧒" if HAS_EDGE_TTS else "Google TTS")
        c3.metric("🎙️ Voix", voice_label)

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

        # JSON disponible en téléchargement discret uniquement
        json_str = json.dumps(result, ensure_ascii=False, indent=2)
        with st.expander("📋 Voir le JSON complet"):
            st.code(json_str, language="json")
            st.download_button(
                "⬇️ Télécharger JSON",
                data=json_str,
                file_name=f"ia_coach_{datetime.today().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
            )

        st.divider()
        if st.button("🔄 Nouvelle analyse"):
            st.session_state.analyse_result = None
            st.session_state.audio_bytes = None
            st.rerun()

# ═══════════════════════════════════════════════════════════════════
# TAB 3 – GUIDE PÉDAGOGIQUE
# ═══════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 📚 Guide pédagogique – IA Coach Enfant")

    st.markdown("""
    <div style='background:white; border-radius:16px; padding:1.5rem;
                box-shadow:0 2px 8px rgba(0,0,0,0.07); margin-bottom:1rem;'>
        <h4 style='color:#006064; margin-top:0'>🎯 Objectif pédagogique</h4>
        <p style='color:#555'>
            Le Coach IA parle comme un <b>héros bienveillant</b> — style Sonic —
            et transforme le moment du repas en <b>petite mission positive</b>.
            Il encourage sans jamais culpabiliser, menacer ou forcer.
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
                <li>Utilise des métaphores positives ("mission", "énergie")</li>
                <li>Valorise chaque aliment selon ses bénéfices concrets</li>
                <li>Invite à <i>goûter</i>, pas à finir l'assiette</li>
                <li>Utilise un vocabulaire simple (4–11 ans)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_dont:
        st.markdown("""
        <div style='background:#FFEBEE; border-radius:16px; padding:1.2rem;'>
            <h4 style='color:#C62828; margin-top:0'>❌ Ce que le Coach NE FAIT PAS</h4>
            <ul style='color:#555; font-size:0.9rem'>
                <li>Culpabiliser ou menacer</li>
                <li>Parler du poids ou de "grossir"</li>
                <li>Forcer à finir l'assiette</li>
                <li>Ignorer la satiété</li>
                <li>Utiliser du jargon nutritionnel</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### 🔌 Obtenir une clé ElevenLabs (gratuit)")
    st.markdown("""
    <div style='background:white; border-radius:14px; padding:1.2rem;
                box-shadow:0 2px 6px rgba(0,0,0,0.06);'>
        <ol style='color:#555; font-size:0.9rem; line-height:2.2'>
            <li>Va sur <b>elevenlabs.io</b> → créer un compte gratuit</li>
            <li>Clique sur ton avatar en haut à droite → <b>Profile + API Key</b></li>
            <li>Copie la clé et colle-la dans la barre latérale</li>
            <li>Dans <b>Voice Library</b>, choisis une voix jeune/énergique → copie l'ID</li>
        </ol>
        <p style='color:#888; font-size:0.85rem; margin-top:0.5rem'>
            Le quota gratuit (~10 000 caractères/mois) est largement suffisant pour une démo.
        </p>
    </div>
    """, unsafe_allow_html=True)
