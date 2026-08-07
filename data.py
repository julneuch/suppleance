import json
import os
import datetime
import pandas as pd

DATA_DIR = "data"
COLLABORATEUR_PATH = os.path.join(DATA_DIR, "collaborateurs.json")
ORGA_PATH = os.path.join(DATA_DIR, "organisation.json")
INVENTAIRE_PATH = os.path.join(DATA_DIR, "inventaire.json")

NATURES = (
    "🧠 Connaissance clé",
    "📋 Exécution d'une tâche",
    "💻 Application-outil",
)
STATUS = (
    "🟡 Initié",
    "🟢 Complet",
    "📤 Proposé",
    "❌ Refusé",
    "🔴 Non Initié",
)
CARACTERE = (
    "⭐ Unique",
    "💎 Rare",
)
DELAI = (
    "3️⃣ 3 mois",
    "6️⃣ 6 mois",
    "9️⃣ 9 mois",
    "1️⃣2️⃣ 12 mois",
)
TEMPO = (
    "🚀 jusqu'à 1 semaine",
    "⏱️ jusqu'à 1 mois",
    "⏲️ jusqu'à 3 mois",
    "⏳ jusqu'à 6 mois",
    "🕰️ au delà de 6 mois",
)
DIVISION = ("Entreprise", "Crédit")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


def ouvrir_collaborateurs(path=COLLABORATEUR_PATH):
    if not os.path.exists(path):
        collabs = default_collaborateurs()
    with open(path, mode="r", encoding="utf-8") as file:
        collabs = pd.read_json(file, orient="records")

    return collabs


def ouvrir_collaborateurs_managers(path=COLLABORATEUR_PATH):
    return ouvrir_collaborateurs(path=path)[
        ouvrir_collaborateurs(path=path)["Manager"] == True
    ]


def ouvrir_collaborateurs_rh(path=COLLABORATEUR_PATH):
    return ouvrir_collaborateurs(path=path)[
        ouvrir_collaborateurs(path=path)["RH"] == True
    ]


def default_collaborateurs():
    """
    Crée un fichier JSON avec des collaborateurs par défaut si le fichier n'existe pas.
    """
    collabs = {
        "Jules Dupont": {
            "date_in": "2023-01-01",
            "date_out": None,
            # "division": DIVISION[0],
            "RH": False,
            "Manager": False,
            "fonction": "Analyste",
            "noeud": 1,
        },
        "Marie Curie": {
            "date_in": "2025-12-01",
            "date_out": "2026-01-31",
            # "division": DIVISION[1],
            "RH": False,
            "Manager": False,
            "fonction": "Chercheuse",
            "noeud": 2,
        },
        "Albert Einstein": {
            "date_in": "2009-03-01",
            "date_out": None,
            # "division": DIVISION[0],
            "RH": False,
            "Manager": True,
            "fonction": "Physicien",
            "noeud": 1,
        },
        "Julien Rey": {
            "date_in": "2019-05-01",
            "date_out": None,
            # "division": DIVISION[0],
            "RH": False,
            "Manager": True,
            "fonction": "Développeur",
            "noeud": 4,
        },
        "Christophe Lopez": {
            "date_in": "2017-05-01",
            "date_out": None,
            # "division": DIVISION[0],
            "RH": True,
            "Manager": True,
            "fonction": "Business Partner",
            "noeud": 2,
        },
        "Richard Duc": {
            "date_in": "2021-07-01",
            "date_out": None,
            # "division": DIVISION[1],
            "RH": False,
            "Manager": True,
            "fonction": "Designer",
            "noeud": 5,
        },
        "Maryline Spycher": {
            "date_in": "2011-01-01",
            "date_out": None,
            # "division": DIVISION[1],
            "RH": False,
            "Manager": True,
            "fonction": "Consultante",
            "noeud": 7,
        },
    }
    df = pd.DataFrame.from_dict(collabs, orient="index").reset_index()
    df = df.rename(columns={"index": "collaborateur"})
    df.to_json(COLLABORATEUR_PATH, orient="records", indent=4, force_ascii=False)
    return df


def ecrire_collaborateurs(collaborateurs, path=COLLABORATEUR_PATH):
    collaborateurs.to_json(
        COLLABORATEUR_PATH, orient="records", indent=4, force_ascii=False
    )


def ouvrir_organisation(path=ORGA_PATH):
    if not os.path.exists(path):
        orga = default_orga()
    with open(path, mode="r", encoding="utf-8") as file:
        orga = pd.read_json(file, orient="records")
    return orga


def ecrire_organisation(organisation, path=ORGA_PATH):
    organisation.to_json(ORGA_PATH, orient="records", indent=4, force_ascii=False)


def ecrire_collaborateurs(collaborateurs, path=COLLABORATEUR_PATH):
    collaborateurs.to_json(
        COLLABORATEUR_PATH, orient="records", indent=4, force_ascii=False
    )


def default_orga():
    """
    Crée un fichier JSON avec une organisation par défaut si le fichier n'existe pas.
    """
    orga = [
        # Division A
        {
            "division": DIVISION[0],
            "departement": "Entreprise",
            "secteur": "Etat-major",
            "responsable": "Albert Einstein",
        },
        {
            "division": DIVISION[0],
            "departement": "PME",
            "secteur": "Région A",
            "responsable": "Christophe Lopez",
        },
        {
            "division": DIVISION[0],
            "departement": "PME",
            "secteur": "Région B",
            "responsable": None,
        },
        {
            "division": DIVISION[0],
            "departement": "PME",
            "secteur": "Région C",
            "responsable": "Julien Rey",
        },
        # Division B
        {
            "division": DIVISION[1],
            "departement": "Département B1",
            "secteur": "Secteur B1-1",
            "responsable": "Richard Duc",
        },
        {
            "division": DIVISION[1],
            "departement": "Département B1",
            "secteur": "Secteur B1-2",
            "responsable": "Richard Duc",
        },
        {
            "division": DIVISION[1],
            "departement": "Département B2",
            "secteur": "Secteur B2-1",
            "responsable": "Maryline Spycher",
        },
    ]
    df = pd.DataFrame(orga)
    df["id"] = range(1, len(df) + 1)
    df = df[["id", "division", "departement", "secteur", "responsable"]]
    df.to_json(ORGA_PATH, orient="records", indent=4, force_ascii=False)
    return df


def default_inventaire():
    """
    Crée un fichier JSON avec un inventaire par défaut si le fichier n'existe pas.
    """
    inventaire = [
        {
            "id_ligne": 1,
            "noeud": 1,
            "nature": NATURES[0],
            "caractère": CARACTERE[0],
            "description": "Connaissance générale",
            "titulaire": "Albert Einstein",
            "Suppléant 1": "Christophe Lopez",
            "Suppléant 2": None,
            "status": STATUS[1],
            "documentation": [],
            "update_at": "2026-07-22",
            "tempo": TEMPO[1],
        },
        {
            "id_ligne": 2,
            "noeud": 1,
            "nature": NATURES[1],
            "caractère": CARACTERE[1],
            "description": "Mise a jour du referentiel produit",
            "titulaire": "Albert Einstein",
            "Suppléant 1": None,
            "Suppléant 2": None,
            "status": STATUS[0],
            "delai": DELAI[0],
            "documentation": [],
            "update_at": "2026-07-22",
            "tempo": TEMPO[0],
        },
        {
            "id_ligne": 3,
            "noeud": 2,
            "nature": NATURES[1],
            "caractère": CARACTERE[1],
            "description": "Executer le controle SCI 4512-4",
            "titulaire": "Albert Einstein",
            "Suppléant 1": "Christophe Lopez",
            "Suppléant 2": None,
            "status": STATUS[4],
            "delai": DELAI[2],
            "documentation": ["procédure", "tutoriel"],
            "update_at": "2026-07-22",
            "tempo": TEMPO[3],
        },
        {
            "id_ligne": 4,
            "noeud": 2,
            "nature": NATURES[1],
            "caractère": CARACTERE[1],
            "description": "Executer le controle SCI 4512-5",
            "titulaire": "Albert Einstein",
            "Suppléant 1": "Jules Dupont",
            "Suppléant 2": None,
            "status": STATUS[0],
            "delai": DELAI[1],
            "documentation": ["Guide"],
            "update_at": "2026-07-22",
            "tempo": TEMPO[1],
        },
        {
            "id_ligne": 5,
            "noeud": 2,
            "nature": NATURES[1],
            "caractère": CARACTERE[1],
            "description": "Executer le controle SCI 4514-5",
            "titulaire": "Albert Einstein",
            "Suppléant 1": None,
            "Suppléant 2": None,
            "status": STATUS[0],
            "delai": DELAI[3],
            "documentation": [],
            "update_at": "2026-07-22",
            "tempo": TEMPO[1],
        },
        {
            "id_ligne": 6,
            "noeud": 1,
            "nature": NATURES[0],
            "caractère": CARACTERE[0],
            "description": "Maitrise des regles de gestion du produit X",
            "tempo": TEMPO[1],
            "titulaire": "Jules Dupont",
            "Suppléant 1": None,
            "Suppléant 2": None,
            "status": STATUS[2],
            "delai": None,
            "documentation": [],
            "update_at": None,
        },
        {
            "id_ligne": 7,
            "noeud": 1,
            "nature": NATURES[1],
            "caractère": CARACTERE[0],
            "description": "Animation du reseau des innovateurs",
            "tempo": TEMPO[1],
            "titulaire": "Jules Dupont",
            "Suppléant 1": "Albert Einstein",
            "Suppléant 2": None,
            "status": STATUS[2],
            "delai": None,
            "documentation": [],
            "update_at": None,
        },
        {
            "id_ligne": 8,
            "noeud": 5,
            "nature": NATURES[0],
            "caractère": CARACTERE[0],
            "description": "Maitrise de controle D45.3",
            "tempo": TEMPO[1],
            "titulaire": "Marie Curie",
            "Suppléant 1": None,
            "Suppléant 2": None,
            "status": STATUS[2],
            "delai": None,
            "documentation": [],
            "update_at": None,
        },
        {
            "id_ligne": 9,
            "noeud": 5,
            "nature": NATURES[0],
            "caractère": CARACTERE[0],
            "description": "Maitrise des règles d'octroi de crédit pour le Panama",
            "tempo": TEMPO[1],
            "titulaire": "Marie Curie",
            "Suppléant 1": "Richard Duc",
            "Suppléant 2": None,
            "status": STATUS[2],
            "delai": None,
            "documentation": [],
            "update_at": None,
        },
    ]
    df = pd.DataFrame(inventaire)
    df.to_json(INVENTAIRE_PATH, orient="records", indent=4, force_ascii=False)
    return df


def ouvrir_inventaire(path=INVENTAIRE_PATH):
    if not os.path.exists(path):
        inventaire = default_inventaire()
    with open(path, mode="r", encoding="utf-8") as file:
        inventaire = pd.read_json(file, orient="records")
    return inventaire


def get_inventaire_propose(user=None):
    """Retourne toutes les saisies avec un statut proposé pour un utilisateur concerné"""
    inventaire = ouvrir_inventaire()
    noeuds = organisation_to_dict(user)
    inventaire_propose = inventaire[inventaire["status"] == STATUS[2]]
    inventaire_propose = inventaire_propose[
        inventaire_propose["noeud"].isin(noeuds.keys())
    ]
    return inventaire_propose


def ecrire_inventaire(inventaire, path=INVENTAIRE_PATH):
    inventaire = inventaire[
        [
            "id_ligne",
            "noeud",
            "nature",
            "caractère",
            "description",
            "tempo",
            "titulaire",
            "Suppléant 1",
            "Suppléant 2",
            "status",
            "delai",
            "documentation",
            "update_at",
        ]
    ]
    inventaire.to_json(INVENTAIRE_PATH, orient="records", indent=4, force_ascii=False)


def organisation_to_dict(user=None):
    orga = ouvrir_organisation()
    if user:
        orga = orga[orga["responsable"] == user]
    id_to_label = {
        row["id"]: f"{row['division']} / {row['departement']} / {row['secteur']}"
        for _, row in orga.iterrows()
    }
    return id_to_label
