import pandas as pd
import numpy as np
from pathlib import Path
import sys


# 1. Configuration des chemins

BASE_DIR = Path(".")

# Chemin vers le fichier brut activité / immigration
FILE_DATA = BASE_DIR / "data_raw" / "2022_raw" / "6_taux_immigration_2022" / "ACTIVITE_IMMIGRATION_PAR_COM_2022.xlsx"

# Chemin vers le référentiel communal nettoyé
FILE_COMMUNES = BASE_DIR / "data_cleaned" / "communes_2022_cleaned.csv"

# Dossier de sortie des fichiers nettoyés
DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2022"

# Création du dossier de sortie s'il n'existe pas
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)


# 2. Nettoyage du dataset taux d'immigration

def clean_taux_immigration(year):

    print(f"Nettoyage taux d'immigration {year}")

    # Vérification de l'existence du fichier source
    if not FILE_DATA.exists():
        print(f"Fichier source introuvable : {FILE_DATA}")
        sys.exit(1)

    # Vérification de l'existence du référentiel communal
    if not FILE_COMMUNES.exists():
        print(f"Référentiel communes introuvable : {FILE_COMMUNES}")
        sys.exit(1)


    # Étape 1 : Chargement du référentiel communal

    df_ref = pd.read_csv(FILE_COMMUNES, sep=";", dtype=str, encoding="utf-8")

    # Conservation uniquement des colonnes utiles à la jointure
    df_ref = df_ref[["code_insee", "nom_commune"]]

    # Normalisation du code INSEE sur 5 caractères
    df_ref["code_insee"] = df_ref["code_insee"].astype(str).str.zfill(5)

    # Suppression des doublons sur le code INSEE
    df_ref = df_ref.drop_duplicates(subset=["code_insee"])


    # Étape 2 : Détection automatique de l'en-tête du fichier Excel

    # Lecture partielle du fichier pour trouver la ligne contenant CODGEO
    df_preview = pd.read_excel(FILE_DATA, nrows=20, header=None)

    header_idx = None

    for i, row in df_preview.iterrows():

        # Recherche de la ligne qui contient le vrai nom des colonnes
        if row.astype(str).str.contains("CODGEO").any():
            header_idx = i
            break

    # Sécurité si l'en-tête n'est pas retrouvé
    if header_idx is None:
        print("Impossible de trouver CODGEO.")
        sys.exit(1)


    # Étape 3 : Lecture du fichier brut

    # Lecture réelle du fichier Excel à partir de la ligne d'en-tête détectée
    df_raw = pd.read_excel(FILE_DATA, skiprows=header_idx, dtype=str)


    # Étape 4 : Nettoyage des noms de colonnes

    # Suppression des espaces et retours à la ligne dans les noms de colonnes
    df_raw.columns = (
        df_raw.columns
        .astype(str)
        .str.strip()
        .str.replace("\n", "", regex=False)
        .str.replace(" ", "", regex=False)
    )


    # Étape 5 : Normalisation du code commune

    # Renommage de CODGEO en code_insee
    df_raw = df_raw.rename(columns={
        "CODGEO": "code_insee"
    })

    # Vérification de la présence du code INSEE
    if "code_insee" not in df_raw.columns:
        print("Colonne code_insee introuvable.")
        print("Colonnes disponibles :", list(df_raw.columns))
        sys.exit(1)

    # Formatage du code INSEE sur 5 caractères
    df_raw["code_insee"] = df_raw["code_insee"].astype(str).str.zfill(5)


    # Étape 6 : Identification des colonnes utiles

    # INATC1 = population française
    # INATC2 = population étrangère
    # Les colonnes sont récupérées automatiquement selon leur préfixe
    colonnes_francais = [
        col for col in df_raw.columns
        if col.startswith("INATC1_SEXE")
    ]

    colonnes_etrangers = [
        col for col in df_raw.columns
        if col.startswith("INATC2_SEXE")
    ]

    # Vérification de la présence des colonnes attendues
    if not colonnes_francais or not colonnes_etrangers:
        print("Colonnes Français / Étrangers introuvables.")
        print("Colonnes français détectées :", colonnes_francais)
        print("Colonnes étrangers détectées :", colonnes_etrangers)
        print("Colonnes disponibles :", list(df_raw.columns))
        sys.exit(1)


    # Étape 7 : Création du dataframe de travail

    # Conservation du code INSEE et des colonnes nécessaires au calcul
    df = df_raw[["code_insee"] + colonnes_francais + colonnes_etrangers].copy()


    # Étape 8 : Conversion des colonnes numériques

    for col in colonnes_francais + colonnes_etrangers:

        # Nettoyage des valeurs textuelles :
        # - suppression des espaces
        # - remplacement de la virgule décimale par un point
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(r"\s+", "", regex=True)
            .str.replace(",", ".", regex=False)
        )

        # Conversion en numérique
        # Les valeurs invalides deviennent NaN
        df[col] = pd.to_numeric(df[col], errors="coerce")


    # Étape 9 : Calcul des populations

    # Somme des colonnes correspondant à la population française
    df["population_francaise"] = df[colonnes_francais].sum(axis=1, min_count=1)

    # Somme des colonnes correspondant à la population étrangère
    df["population_etrangere"] = df[colonnes_etrangers].sum(axis=1, min_count=1)

    # Population totale utilisée pour le calcul du taux
    df["population_totale"] = (
        df["population_francaise"] + df["population_etrangere"]
    )


    # Étape 10 : Calcul du taux d'immigration

    # Calcul du pourcentage de population étrangère dans la population totale
    # Si la population totale est nulle, le taux est mis à NaN
    df["taux_immigration"] = np.where(
        df["population_totale"] > 0, #si aucune donnée exploitable dans le fichier INSEE alors NaN
        (df["population_etrangere"] / df["population_totale"]) * 100,
        np.nan
    )


    # Étape 11 : Contrôle des communes avec population totale nulle

    df_population_nulle = df[
        df["population_totale"] == 0
    ].copy()

    print("\n--- COMMUNES AVEC POPULATION TOTALE NULLE ---")
    print(df_population_nulle.shape)

    print(df_population_nulle[["code_insee","population_francaise","population_etrangere","population_totale"]].head(50))

    print(df_population_nulle[["code_insee","population_francaise","population_etrangere","population_totale"]].head(50))


    # Étape 12 : Contrôle des communes avec taux d'immigration NaN

    df_taux_nan = df[df["taux_immigration"].isna()].copy()

    print("\n--- COMMUNES AVEC TAUX IMMIGRATION NaN ---")
    print(df_taux_nan.shape)

    print(df_taux_nan[["code_insee","population_francaise","population_etrangere","population_totale","taux_immigration"]])


    # Étape 13 : Jointure avec le référentiel communal

    df = pd.merge(
        df[["code_insee", "taux_immigration"]],
        df_ref,
        on="code_insee",
        how="left"
    )


    # Étape 14 : Contrôle des communes non retrouvées après jointure

    print("Communes non trouvées après merge :", df["nom_commune"].isna().sum())

    print(df[df["nom_commune"].isna()][["code_insee"]].head(50))


    # Étape 15 : Suppression des communes non exploitables

    # Suppression des lignes sans nom de commune
    df = df.dropna(subset=["nom_commune"]).copy()

    # Harmonisation du nom de colonne avec les autres datasets
    df = df.rename(columns={"nom_commune": "localisation"})


    # Étape 16 : Construction du fichier final

    df_final = df[["code_insee","localisation", "taux_immigration"]].copy()

    # Suppression de sécurité des localisations manquantes
    df_final = df_final.dropna(subset=["localisation"])

    # Suppression des localisations vides
    df_final = df_final[df_final["localisation"].astype(str).str.strip() != ""]

    # Ajout de l'année de référence
    df_final["annee"] = year

    # Arrondi du taux d'immigration à 2 décimales
    df_final["taux_immigration"] = df_final["taux_immigration"].round(2)


    # Étape 17 : Export du dataset nettoyé

    fichier_sortie = DIR_OUTPUT / f"06_taux_immigration_{year}_cleaned.csv"

    df_final.to_csv(fichier_sortie, sep=";", index=False, encoding="utf-8-sig")

    print(f"Terminé : {len(df_final)} lignes sauvegardées")
    print(f"Fichier créé : {fichier_sortie}")


    # Étape 18 : Contrôles qualité finaux

    print("Lignes après lecture :", len(df))

    print(df_final.isna().sum())


# Point d'entrée du script
if __name__ == "__main__":
    clean_taux_immigration(2022)