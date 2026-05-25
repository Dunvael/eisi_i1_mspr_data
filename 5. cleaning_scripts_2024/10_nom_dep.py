import pandas as pd
from pathlib import Path
import sys
import requests

print("Nettoyage fichier POPULATION & DENSITÉ")


# 1. CONFIGURATION DES CHEMINS

BASE_DIR = Path(".")

FILE_REF = BASE_DIR / "data_cleaned" / "2024" / "00_referentiel_communes_22_24_clean.csv"

FILE_POP_RAW = (
    BASE_DIR
    / "data_raw"
    / "2024_raw"
    / "1. Densite population"
    / "population+densite+superficie_km2_2024.csv"
)

FILE_OUTPUT = (
    BASE_DIR
    / "data_cleaned"
    / "2024"
    / "10_nom_departement.csv"
)


# 2. CHARGEMENT DES DONNÉES

try:
    df_ref = pd.read_csv(FILE_REF, sep=";", dtype=str)
    print(f"Référentiel chargé : {len(df_ref)} lignes")
    try:
        df_pop = pd.read_csv(FILE_POP_RAW, sep=";", dtype=str)
    except:
        df_pop = pd.read_csv(FILE_POP_RAW, sep=",", dtype=str)
    print(f"Fichier population chargé : {len(df_pop)} lignes")

except Exception as e:
    print(f"Erreur chargement fichiers : {e}")
    sys.exit(1)


# 3. NETTOYAGE


# Colonnes nécessaires au mapping département
colonnes_utiles = [
    "code_insee",
    "dep_nom"
]

# Vérification des colonnes
colonnes_existantes = [col for col in colonnes_utiles if col in df_pop.columns]

df_clean = df_pop[colonnes_existantes].copy()

# Suppression des doublons
df_clean = df_clean.drop_duplicates()

# Renommage des colonnes
df_clean = df_clean.rename(columns={
    "code_insee": "code_insee_2024",
    "dep_nom": "nom_departement"
})

# Tri
df_clean = df_clean.sort_values(by="code_insee_2024")


df_clean = df_clean.reset_index(drop=True)


# 4. CRÉATION DOSSIER

FILE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)


# 5. EXPORT CSV

try:
    df_clean.to_csv(FILE_OUTPUT, sep=";", index=False, encoding="utf-8-sig")

    print("===================================")
    print("Fichier nettoyé généré avec succès")
    print(FILE_OUTPUT)
    print("===================================")

    print(df_clean.head())

except Exception as e:
    print(f"Erreur export CSV : {e}")