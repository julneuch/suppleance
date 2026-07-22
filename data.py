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
    "🟡 Incomplet",
    "🟢 Complet",
)
CARACTERE = (
    "⭐ Unique",
    "💎 Rare",
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
            "division": DIVISION[0],
            "RH": False,
            "Manager": False,
            "fonction": "Analyste",
        },
        "Marie Curie": {
            "date_in": "2025-12-01",
            "date_out": "2026-01-31",
            "division": DIVISION[1],
            "RH": False,
            "Manager": False,
            "fonction": "Chercheuse",
        },
        "Albert Einstein": {
            "date_in": "2009-03-01",
            "date_out": None,
            "division": DIVISION[0],
            "RH": False,
            "Manager": True,
            "fonction": "Physicien",
        },
        "Julien Rey": {
            "date_in": "2019-05-01",
            "date_out": None,
            "division": DIVISION[0],
            "RH": False,
            "Manager": True,
            "fonction": "Développeur",
        },
        "Christophe Lopez": {
            "date_in": "2017-05-01",
            "date_out": None,
            "division": DIVISION[0],
            "RH": True,
            "Manager": True,
            "fonction": "Business Partner",
        },
        "Richard Duc": {
            "date_in": "2021-07-01",
            "date_out": None,
            "division": DIVISION[1],
            "RH": False,
            "Manager": True,
            "fonction": "Designer",
        },
        "Maryline Spycher": {
            "date_in": "2011-01-01",
            "date_out": None,
            "division": DIVISION[1],
            "RH": False,
            "Manager": True,
            "fonction": "Consultante",
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
            "noeud": 1,
            "nature": NATURES[0],
            "caractère": CARACTERE[0],
            "description": "Connaissance générale",
            "titulaire": "Albert Einstein",
            "Suppléant 1": "Christophe Lopez",
            "Suppléant 2": None,
            "status": STATUS[1],
            "pourcentage": 100,
            "documentation": [],
            "update_at": "2026-07-22",
        },
        {
            "noeud": 1,
            "nature": NATURES[1],
            "caractère": CARACTERE[1],
            "description": "Mise a jour du referentiel produit",
            "titulaire": "Albert Einstein",
            "Suppléant 1": None,
            "Suppléant 2": None,
            "status": STATUS[0],
            "pourcentage": 0,
            "documentation": [],
            "update_at": "2026-07-22",
        },
        {
            "noeud": 2,
            "nature": NATURES[1],
            "caractère": CARACTERE[1],
            "description": "Executer le controle SCI 4512-4",
            "titulaire": "Albert Einstein",
            "Suppléant 1": "Christophe Lopez",
            "Suppléant 2": None,
            "status": STATUS[0],
            "pourcentage": 50,
            "documentation": ["procédure", "tutoriel"],
            "update_at": "2026-07-22",
        },
        {
            "noeud": 2,
            "nature": NATURES[1],
            "caractère": CARACTERE[1],
            "description": "Executer le controle SCI 4512-5",
            "titulaire": "Albert Einstein",
            "Suppléant 1": None,
            "Suppléant 2": None,
            "status": STATUS[0],
            "pourcentage": 0,
            "documentation": ["Guide"],
            "update_at": "2026-07-22",
        },
        {
            "noeud": 2,
            "nature": NATURES[1],
            "caractère": CARACTERE[1],
            "description": "Executer le controle SCI 4514-5",
            "titulaire": "Albert Einstein",
            "Suppléant 1": None,
            "Suppléant 2": None,
            "status": STATUS[0],
            "pourcentage": 0,
            "documentation": [],
            "update_at": "2026-07-22",
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


def ecrire_inventaire(inventaire, path=INVENTAIRE_PATH):
    inventaire = inventaire[
        [
            "noeud",
            "nature",
            "caractère",
            "description",
            "titulaire",
            "Suppléant 1",
            "Suppléant 2",
            "status",
            "pourcentage",
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
