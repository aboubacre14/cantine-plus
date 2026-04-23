"""
Cantine+ – Générateur de données simulées
Représente un jeu de données de type "repas servis dans des cantines à Rennes"
Variables : date, météo, cantine, menus, taux de gaspillage, participation, coût, CO2
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

# ─────────────────────────────────────────────
#  RÉFÉRENTIEL DES PLATS
# ─────────────────────────────────────────────
PLATS = {
    "entrees": [
        "Salade de tomates",
        "Carottes râpées",
        "Salade verte",
        "Betteraves vinaigrette",
        "Taboulé",
        "Salade de concombre",
        "Quiche lorraine",
        "Soupe de légumes",
        "Melon",
        "Pamplemousse",
    ],
    "plats": [
        "Poulet rôti",
        "Steak haché sauce tomate",
        "Poisson pané",
        "Gratin de courgettes",
        "Lasagnes bolognaise",
        "Rôti de porc",
        "Sauté de veau",
        "Omelette aux fines herbes",
        "Filet de cabillaud",
        "Escalope de dinde",
        "Hachis parmentier",
        "Quenelles sauce tomate",
    ],
    "accompagnements": [
        "Riz",
        "Pâtes",
        "Purée de pommes de terre",
        "Haricots verts",
        "Carottes glacées",
        "Pommes de terre sautées",
        "Semoule",
        "Lentilles",
        "Gratin dauphinois",
        "Flageolets",
    ],
    "desserts": [
        "Yaourt nature",
        "Compote de pommes",
        "Fruits frais de saison",
        "Tarte aux pommes",
        "Mousse au chocolat",
        "Fromage blanc",
        "Crème caramel",
        "Poire au sirop",
    ],
}

# Score popularité (0–1) pour chaque plat – détermine le waste rate simulé
POPULARITE = {
    # Entrées
    "Salade de tomates": 0.72, "Carottes râpées": 0.68, "Salade verte": 0.55,
    "Betteraves vinaigrette": 0.48, "Taboulé": 0.75, "Salade de concombre": 0.60,
    "Quiche lorraine": 0.82, "Soupe de légumes": 0.63, "Melon": 0.88, "Pamplemousse": 0.52,
    # Plats
    "Poulet rôti": 0.85, "Steak haché sauce tomate": 0.80, "Poisson pané": 0.62,
    "Gratin de courgettes": 0.50, "Lasagnes bolognaise": 0.90, "Rôti de porc": 0.76,
    "Sauté de veau": 0.70, "Omelette aux fines herbes": 0.65, "Filet de cabillaud": 0.58,
    "Escalope de dinde": 0.72, "Hachis parmentier": 0.83, "Quenelles sauce tomate": 0.67,
    # Accompagnements
    "Riz": 0.78, "Pâtes": 0.85, "Purée de pommes de terre": 0.82, "Haricots verts": 0.62,
    "Carottes glacées": 0.65, "Pommes de terre sautées": 0.88, "Semoule": 0.72,
    "Lentilles": 0.55, "Gratin dauphinois": 0.86, "Flageolets": 0.53,
    # Desserts
    "Yaourt nature": 0.68, "Compote de pommes": 0.73, "Fruits frais de saison": 0.80,
    "Tarte aux pommes": 0.88, "Mousse au chocolat": 0.92, "Fromage blanc": 0.70,
    "Crème caramel": 0.85, "Poire au sirop": 0.75,
}

# Empreinte CO2 par portion (kg CO2 eq)
CO2_PAR_PLAT = {
    "Poulet rôti": 3.2, "Steak haché sauce tomate": 5.8, "Poisson pané": 2.1,
    "Gratin de courgettes": 0.8, "Lasagnes bolognaise": 4.5, "Rôti de porc": 3.6,
    "Sauté de veau": 4.8, "Omelette aux fines herbes": 1.2, "Filet de cabillaud": 2.4,
    "Escalope de dinde": 2.8, "Hachis parmentier": 3.5, "Quenelles sauce tomate": 2.0,
}

# Coût par portion (€)
COUT_PAR_REPAS = {
    "Poulet rôti": 4.20, "Steak haché sauce tomate": 4.80, "Poisson pané": 3.90,
    "Gratin de courgettes": 2.80, "Lasagnes bolognaise": 4.50, "Rôti de porc": 4.10,
    "Sauté de veau": 5.20, "Omelette aux fines herbes": 2.60, "Filet de cabillaud": 4.30,
    "Escalope de dinde": 3.70, "Hachis parmentier": 3.50, "Quenelles sauce tomate": 3.20,
}

METEO = ["Ensoleillé", "Nuageux", "Pluvieux", "Froid", "Chaud"]
CANTINES = ["Cantine A – Centre-ville", "Cantine B – Nord", "Cantine C – Sud"]

ALLERGENES = [
    "Gluten", "Lactose", "Arachides", "Fruits à coque", "Oeufs",
    "Poisson", "Soja", "Sésame", "Sulfites", "Céleri",
]

BADGES_ELEVE = [
    {"nom": "Héros anti-gaspi", "emoji": "🦸", "condition": "Pas de gaspillage 5 jours"},
    {"nom": "Explorateur", "emoji": "🧭", "condition": "A goûté 10 plats différents"},
    {"nom": "Champion vert", "emoji": "🌿", "condition": "Feedback 20 repas"},
    {"nom": "Super goûteur", "emoji": "⭐", "condition": "A noté chaque repas 1 semaine"},
    {"nom": "Légume-power", "emoji": "🥦", "condition": "A aimé 5 plats avec légumes"},
]

# ─────────────────────────────────────────────
#  GÉNÉRATION DES DONNÉES HISTORIQUES
# ─────────────────────────────────────────────
def generate_historical_data(months: int = 6) -> pd.DataFrame:
    records = []
    start_date = datetime.today() - timedelta(days=months * 30)
    current = start_date

    while current <= datetime.today() - timedelta(days=1):
        if current.weekday() < 5:
            meteo = random.choice(METEO)
            jour = current.weekday()

            for cantine in CANTINES:
                entree = random.choice(PLATS["entrees"])
                plat = random.choice(PLATS["plats"])
                accomp = random.choice(PLATS["accompagnements"])
                dessert = random.choice(PLATS["desserts"])

                pop_score = (
                    POPULARITE.get(entree, 0.65)
                    + POPULARITE.get(plat, 0.65)
                    + POPULARITE.get(accomp, 0.65)
                    + POPULARITE.get(dessert, 0.65)
                ) / 4

                waste_base = (1 - pop_score) * 0.35
                if jour in [0, 4]:
                    waste_base += 0.03
                if meteo == "Ensoleillé":
                    waste_base += 0.02
                waste_rate = max(0.02, min(0.45, waste_base + np.random.normal(0, 0.02)))

                participation_base = 0.72 + pop_score * 0.15
                if jour in [0, 4]:
                    participation_base -= 0.06
                if meteo == "Pluvieux":
                    participation_base += 0.04
                if meteo == "Ensoleillé":
                    participation_base -= 0.05
                participation_rate = max(0.35, min(0.98, participation_base + np.random.normal(0, 0.03)))

                nb_convives_prevus = random.randint(180, 320)
                nb_convives_reels = int(nb_convives_prevus * participation_rate)

                cout = COUT_PAR_REPAS.get(plat, 3.80)
                co2 = CO2_PAR_PLAT.get(plat, 2.5) + np.random.normal(0, 0.2)

                records.append({
                    "date": current.date(),
                    "jour_semaine": current.strftime("%A"),
                    "meteo": meteo,
                    "cantine": cantine,
                    "entree": entree,
                    "plat": plat,
                    "accompagnement": accomp,
                    "dessert": dessert,
                    "nb_convives_prevus": nb_convives_prevus,
                    "nb_convives_reels": nb_convives_reels,
                    "taux_participation": round(participation_rate * 100, 1),
                    "taux_gaspillage": round(waste_rate * 100, 1),
                    "cout_repas": round(cout, 2),
                    "co2_kg": round(max(0.5, co2), 2),
                    "popularite_score": round(pop_score, 3),
                })
        current += timedelta(days=1)

    return pd.DataFrame(records)


# ─────────────────────────────────────────────
#  MENU DE LA SEMAINE EN COURS
# ─────────────────────────────────────────────
def get_current_week_menu() -> pd.DataFrame:
    today = datetime.today()
    monday = today - timedelta(days=today.weekday())
    rows = []
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
    for i, jour in enumerate(jours):
        date = monday + timedelta(days=i)
        plat = PLATS["plats"][i % len(PLATS["plats"])]
        rows.append({
            "jour": jour,
            "date": date.strftime("%d/%m/%Y"),
            "entree": PLATS["entrees"][i % len(PLATS["entrees"])],
            "plat": plat,
            "accompagnement": PLATS["accompagnements"][i % len(PLATS["accompagnements"])],
            "dessert": PLATS["desserts"][i % len(PLATS["desserts"])],
            "cout_estime": round(COUT_PAR_REPAS.get(plat, 3.80), 2),
            "co2_estime": round(CO2_PAR_PLAT.get(plat, 2.5), 2),
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
#  KPI SEMAINE EN COURS
# ─────────────────────────────────────────────
def get_current_week_kpis() -> dict:
    return {
        "waste_rate": 12.4,
        "waste_delta": -2.1,
        "participation_rate": 81.3,
        "participation_delta": +3.5,
        "co2_saved": 47.2,
        "cost_saved": 138.0,
        "repas_solidaires": 23,
    }


# ─────────────────────────────────────────────
#  PROFIL PARENT / ENFANT
# ─────────────────────────────────────────────
def get_parent_profile() -> dict:
    return {
        "parent_prenom": "Sophie",
        "enfant_prenom": "Emma",
        "enfant_age": 8,
        "classe": "CE2 – Mme Dupont",
        "cantine": "Cantine A – Centre-ville",
        "allergies": ["Gluten", "Arachides"],
        "regime": "Standard",
        "aliments_aimes": ["Lasagnes bolognaise", "Poulet rôti", "Mousse au chocolat", "Pâtes"],
        "aliments_non_aimes": ["Betteraves vinaigrette", "Flageolets", "Pamplemousse"],
        "points": 340,
        "badges_obtenus": ["Héros anti-gaspi", "Explorateur"],
        "nb_repas_mois": 18,
        "presence_ce_mois": 18,
    }


# ─────────────────────────────────────────────
#  PROFIL ÉLÈVE (gamification)
# ─────────────────────────────────────────────
def get_student_profile() -> dict:
    return {
        "prenom": "Emma",
        "classe": "CE2",
        "points": 340,
        "niveau": "Héros",
        "badges": ["Héros anti-gaspi", "Explorateur", "Super goûteur"],
        "repas_notes": 42,
        "serie_actuelle": 5,
        "meilleure_serie": 12,
        "plat_prefere": "Lasagnes bolognaise",
    }


# ─────────────────────────────────────────────
#  MENU 2 SEMAINES (parent / élève)
# ─────────────────────────────────────────────
def get_two_weeks_menu() -> list:
    today = datetime.today()
    monday = today - timedelta(days=today.weekday())
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
    weeks = []
    for week_offset in range(2):
        week = []
        for day_offset, jour in enumerate(jours):
            date = monday + timedelta(weeks=week_offset, days=day_offset)
            idx = week_offset * 5 + day_offset
            plat = PLATS["plats"][idx % len(PLATS["plats"])]
            pop = POPULARITE.get(plat, 0.65)
            co2 = CO2_PAR_PLAT.get(plat, 2.5)
            week.append({
                "jour": jour,
                "date": date,
                "date_str": date.strftime("%d/%m"),
                "entree": PLATS["entrees"][idx % len(PLATS["entrees"])],
                "plat": plat,
                "accompagnement": PLATS["accompagnements"][idx % len(PLATS["accompagnements"])],
                "dessert": PLATS["desserts"][idx % len(PLATS["desserts"])],
                "co2": co2,
                "popularite": round(pop * 100),
                "risque": round((1 - pop) * 35, 1),
                "est_passe": date.date() < today.date(),
                "est_aujourd_hui": date.date() == today.date(),
            })
        weeks.append(week)
    return weeks


# ─────────────────────────────────────────────
#  REPAS SOLIDAIRES (invendus)
# ─────────────────────────────────────────────
def get_repas_solidaires() -> list:
    today = datetime.today()
    return [
        {
            "id": "RS001",
            "nom": "Poulet rôti + Riz",
            "cantine": "Cantine A – Centre-ville",
            "quantite": 8,
            "prix_normal": 4.20,
            "prix_reduit": 1.50,
            "heure_retrait": "13h30 – 14h00",
            "date": today.strftime("%d/%m/%Y"),
            "calories": 520,
            "co2": 3.2,
            "disponible": True,
        },
        {
            "id": "RS002",
            "nom": "Lasagnes bolognaise",
            "cantine": "Cantine B – Nord",
            "quantite": 5,
            "prix_normal": 4.50,
            "prix_reduit": 1.80,
            "heure_retrait": "13h45 – 14h15",
            "date": today.strftime("%d/%m/%Y"),
            "calories": 610,
            "co2": 4.5,
            "disponible": True,
        },
        {
            "id": "RS003",
            "nom": "Gratin de courgettes + Semoule",
            "cantine": "Cantine C – Sud",
            "quantite": 12,
            "prix_normal": 2.80,
            "prix_reduit": 1.00,
            "heure_retrait": "13h30 – 14h00",
            "date": today.strftime("%d/%m/%Y"),
            "calories": 380,
            "co2": 0.8,
            "disponible": True,
        },
        {
            "id": "RS004",
            "nom": "Hachis parmentier",
            "cantine": "Cantine A – Centre-ville",
            "quantite": 3,
            "prix_normal": 3.50,
            "prix_reduit": 1.20,
            "heure_retrait": "14h00 – 14h30",
            "date": today.strftime("%d/%m/%Y"),
            "calories": 490,
            "co2": 3.5,
            "disponible": True,
        },
    ]


# ─────────────────────────────────────────────
#  HISTORIQUE INVENDUS
# ─────────────────────────────────────────────
def get_historique_invendus() -> pd.DataFrame:
    today = datetime.today()
    rows = []
    plats_list = PLATS["plats"]
    for i in range(14):
        date = today - timedelta(days=i)
        if date.weekday() < 5:
            for cantine in random.sample(CANTINES, k=random.randint(1, 3)):
                plat = random.choice(plats_list)
                qt = random.randint(2, 20)
                collecte = random.randint(0, qt)
                rows.append({
                    "date": date.strftime("%d/%m/%Y"),
                    "cantine": cantine,
                    "plat": plat,
                    "quantite_declaree": qt,
                    "quantite_collectee": collecte,
                    "prix_reduit": round(COUT_PAR_REPAS.get(plat, 3.80) * 0.35, 2),
                    "statut": "Collecté" if collecte >= qt * 0.8 else ("Partiel" if collecte > 0 else "Non collecté"),
                })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
#  DONNÉES ENTREPRISE
# ─────────────────────────────────────────────
def get_enterprise_kpis() -> dict:
    return {
        "reservations_taux": 73.2,
        "reservations_delta": +4.1,
        "satisfaction_note": 4.1,
        "satisfaction_delta": +0.3,
        "co2_par_repas": 2.8,
        "co2_delta": -0.2,
        "reduction_gaspillage": 18.5,
        "reduction_delta": +3.2,
        "nb_salaries": 240,
        "nb_reservations_semaine": 876,
    }


def get_enterprise_menu() -> list:
    today = datetime.today()
    monday = today - timedelta(days=today.weekday())
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
    result = []
    for week_offset in range(4):
        week = {"semaine": f"Semaine {week_offset + 1}", "jours": []}
        for day_offset, jour in enumerate(jours):
            date = monday + timedelta(weeks=week_offset, days=day_offset)
            idx = week_offset * 5 + day_offset
            plat = PLATS["plats"][idx % len(PLATS["plats"])]
            week["jours"].append({
                "jour": jour,
                "date": date.strftime("%d/%m"),
                "plat": plat,
                "entree": PLATS["entrees"][idx % len(PLATS["entrees"])],
                "dessert": PLATS["desserts"][idx % len(PLATS["desserts"])],
                "co2": CO2_PAR_PLAT.get(plat, 2.5),
                "cout": COUT_PAR_REPAS.get(plat, 3.80),
                "popularite": round(POPULARITE.get(plat, 0.65) * 100),
                "votes_pour": random.randint(30, 90),
                "votes_contre": random.randint(5, 30),
                "reservations": random.randint(40, 120),
            })
        result.append(week)
    return result


def get_enterprise_top_plats() -> pd.DataFrame:
    plats = PLATS["plats"]
    rows = []
    for plat in plats:
        pop = POPULARITE.get(plat, 0.65)
        rows.append({
            "Plat": plat,
            "Note moyenne": round(3.0 + pop * 2.0, 1),
            "Réservations": random.randint(200, 800),
            "Satisfaction (%)": round(pop * 100),
            "CO₂ (kg)": CO2_PAR_PLAT.get(plat, 2.5),
        })
    df = pd.DataFrame(rows).sort_values("Réservations", ascending=False)
    return df.head(10)


def get_gaspillage_prevision() -> pd.DataFrame:
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
    return pd.DataFrame({
        "Jour": jours,
        "Gaspillage prévu (%)": [14.2, 11.8, 13.5, 12.1, 18.7],
        "Gaspillage réel (%)": [13.8, 10.9, 14.2, 11.5, 19.3],
    })


# ─────────────────────────────────────────────
#  IA COACH ENFANT – Génération JSON TTS
# ─────────────────────────────────────────────
FOOD_CATEGORIES = {
    "protéines": [
        "Poulet rôti", "Steak haché sauce tomate", "Poisson pané", "Rôti de porc",
        "Sauté de veau", "Omelette aux fines herbes", "Filet de cabillaud",
        "Escalope de dinde", "Hachis parmentier", "Quenelles sauce tomate",
        "Jambon", "Thon", "Sardines", "Fromage",
    ],
    "féculents": [
        "Riz", "Pâtes", "Purée de pommes de terre", "Semoule", "Lentilles",
        "Gratin dauphinois", "Pommes de terre sautées", "Flageolets", "Pain",
        "Quenelles sauce tomate", "Lasagnes bolognaise",
    ],
    "légumes": [
        "Haricots verts", "Carottes glacées", "Salade verte", "Salade de tomates",
        "Carottes râpées", "Betteraves vinaigrette", "Salade de concombre",
        "Taboulé", "Soupe de légumes", "Gratin de courgettes", "Épinards",
        "Brocoli", "Petits pois", "Courgettes",
    ],
    "fruits": [
        "Fruits frais de saison", "Melon", "Pamplemousse", "Poire au sirop",
        "Compote de pommes", "Pomme", "Banane", "Orange", "Kiwi",
    ],
    "desserts": [
        "Mousse au chocolat", "Tarte aux pommes", "Crème caramel", "Yaourt nature",
        "Fromage blanc", "Gâteau", "Crêpe",
    ],
    "produits_laitiers": [
        "Yaourt nature", "Fromage blanc", "Fromage", "Lait",
    ],
}


def categorize_foods(foods: list) -> list:
    cats = set()
    for food in foods:
        for cat, items in FOOD_CATEGORIES.items():
            if any(food.lower() in item.lower() or item.lower() in food.lower() for item in items):
                cats.add(cat)
    return list(cats)


def generate_ia_coach_analysis(selected_foods: list) -> dict:
    categories = categorize_foods(selected_foods)

    has_protein = "protéines" in categories
    has_starch  = "féculents" in categories
    has_veggie  = "légumes" in categories
    has_fruit   = "fruits" in categories or "desserts" in categories

    # ── Construire la liste parlée de TOUS les aliments ──────────
    DESSERT_KEYWORDS = ["compote", "pomme", "kiwi", "banane", "fruit", "orange",
                        "poire", "yaourt", "crème", "mousse", "tarte", "gâteau"]
    FRUIT_KEYWORDS   = ["compote", "pomme", "kiwi", "banane", "orange", "poire",
                        "melon", "fraise", "raisin", "abricot"]
    PROTEIN_KEYWORDS = ["poulet", "boeuf", "veau", "porc", "dinde", "saumon",
                        "cabillaud", "thon", "jambon", "oeuf", "omelette", "ravioli"]
    VEG_KEYWORDS     = ["tomate", "carotte", "haricot", "brocoli", "épinard",
                        "courgette", "légume", "salade", "basilic", "petits pois"]

    # Sépare plats et desserts pour les citer naturellement
    plats   = [f for f in selected_foods
               if not any(k in f.lower() for k in DESSERT_KEYWORDS)]
    desserts = [f for f in selected_foods
                if any(k in f.lower() for k in DESSERT_KEYWORDS)]

    def liste_naturelle(items):
        if not items:       return ""
        if len(items) == 1: return items[0]
        return ", ".join(items[:-1]) + f" et {items[-1]}"

    menu_plats   = liste_naturelle(plats)   or liste_naturelle(selected_foods)
    menu_dessert = liste_naturelle(desserts)

    # Choix du plat "héros" à mettre en avant (protéine ou premier plat)
    heros = next(
        (f for f in selected_foods if any(k in f.lower() for k in PROTEIN_KEYWORDS)),
        selected_foods[0],
    )
    # Choix du légume à mettre en avant
    veggie_star = next(
        (f for f in selected_foods if any(k in f.lower() for k in VEG_KEYWORDS)),
        None,
    )

    dessert_phrase = (
        f"Et pour finir : {menu_dessert}, un vrai boost de vitamines ! "
        if menu_dessert else ""
    )

    if has_protein and has_starch and has_veggie:
        script = (
            f"Salut jeune héros ! "
            f"Aujourd'hui au menu : {menu_plats} ! "
            f"{heros} te donne la force pour courir plus vite que Sonic. "
            f"{f'{veggie_star} recharge tes super-pouvoirs. ' if veggie_star else ''}"
            f"{dessert_phrase}"
            f"Mission du jour : goûter chaque plat pour devenir imbattable !"
        )
        voice = "voix de super-héros énergique, style Sonic le hérisson, dynamique et rassurante"
    elif has_protein and has_starch:
        script = (
            f"Bonjour les héros de la cantine ! "
            f"Aujourd'hui au menu : {menu_plats} ! "
            f"{heros} nourrit tes muscles comme un vrai champion. "
            f"{dessert_phrase}"
            f"Mission du jour : chaque bouchée te rend plus fort et plus rapide !"
        )
        voice = "voix de capitaine courageux, motivante et chaleureuse"
    elif has_veggie and has_protein:
        script = (
            f"Salut jeune héros ! "
            f"Aujourd'hui au menu : {menu_plats} ! "
            f"{veggie_star or heros} améliore ta vision… parfait pour les missions secrètes ! "
            f"{heros} te donne la force des aventuriers. "
            f"{dessert_phrase}"
            f"Mission du jour : goûter chaque couleur de ton assiette !"
        )
        voice = "voix d'aventurière maligne et enthousiaste, style Sonic"
    elif has_veggie:
        script = (
            f"Bonjour les héros ! "
            f"Aujourd'hui au menu : {menu_plats} ! "
            f"{veggie_star or selected_foods[0]} te donne des super-pouvoirs pour voir loin. "
            f"{dessert_phrase}"
            f"Mission du jour : goûter chaque couleur dans ton assiette !"
        )
        voice = "voix d'exploratrice curieuse et encourageante"
    elif has_fruit:
        script = (
            f"Salut champion ! "
            f"Aujourd'hui au menu : {menu_plats} ! "
            f"{menu_dessert or selected_foods[0]} apporte des vitamines pour finir ta mission en beauté. "
            f"Ton corps te dit merci. Bravo, héros !"
        )
        voice = "voix joyeuse et souriante, ton de fin de mission réussie"
    else:
        script = (
            f"Salut jeune héros ! "
            f"Aujourd'hui au menu : {menu_plats} ! "
            f"{dessert_phrase}"
            f"Ce repas te donne de l'énergie pour bouger, apprendre et grandir. "
            f"Mission du jour : goûter avec courage et avancer comme un vrai héros !"
        )
        voice = "voix de héros bienveillant, rassurante et positive"

    benefits = []
    if has_protein:
        benefits.append("donne la force des aventuriers et aide les muscles à grandir")
    if has_starch:
        benefits.append("recharge l'énergie pour courir, jouer et apprendre")
    if has_veggie:
        benefits.append("améliore la vision et apporte des vitamines essentielles")
    if has_fruit:
        benefits.append("offre un coup de boost naturel pour finir la mission")
    if not benefits:
        benefits = [
            "aide à grandir et rester en forme",
            "donne de l'énergie pour la journée",
            "soutient la concentration et la bonne humeur",
        ]

    if selected_foods:
        food_summary = f"Plateau de cantine composé de {', '.join(selected_foods[:3])}."
        if len(categories) >= 3:
            food_summary += " Repas équilibré avec plusieurs groupes alimentaires."
    else:
        food_summary = "Plateau de cantine avec plusieurs éléments nutritifs identifiés."

    confidence = min(0.99, 0.75 + len(categories) * 0.05 + min(len(selected_foods), 4) * 0.03)

    return {
        "detected_foods": selected_foods,
        "food_summary": food_summary,
        "benefits": benefits[:3],
        "voice_style": voice,
        "tts_script": script,
        "safety_notes": [
            "éviter toute culpabilisation",
            "encourager à goûter sans forcer",
            "ne pas faire de promesse médicale",
            "adapter le message si le plat est peu identifiable",
            "respecter la satiété de l'enfant",
        ],
        "confidence": round(confidence, 2),
    }


# ─────────────────────────────────────────────
#  CACHE STREAMLIT
# ─────────────────────────────────────────────
_df_cache = None


def get_historical_df() -> pd.DataFrame:
    global _df_cache
    if _df_cache is None:
        _df_cache = generate_historical_data(6)
    return _df_cache
