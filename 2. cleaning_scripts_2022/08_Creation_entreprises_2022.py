import pandas as pd
from pathlib import Path
import sys


# 1. Configuration des chemins

BASE_DIR = Path(".")

# Chemin vers le fichier brut des créations d'entreprises
FILE_DATA = BASE_DIR / "data_raw" / "2022_raw" / "8_creation_entreprise_2022" / "NBRE_CREATION_ENTREPRISE_PAR_COM_2012_TO_2025.xlsx"

# Chemin vers le référentiel communal nettoyé
FILE_COMMUNES = BASE_DIR / "data_cleaned" / "communes_2022_cleaned.csv"

# Dossier de sortie des fichiers nettoyés
DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2022"

# Création du dossier de sortie s'il n'existe pas
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)


# 2. Nettoyage du dataset créations d'entreprises

def clean_creation_entreprises(year):

    print(f"Nettoyage créations entreprises {year}")

    # Vérification de l'existence du fichier brut
    if not FILE_DATA.exists():
        print(f" Fichier introuvable : {FILE_DATA}")
        sys.exit(1)

    # Vérification de l'existence du référentiel communal
    if not FILE_COMMUNES.exists():
        print(f" Référentiel introuvable : {FILE_COMMUNES}")
        sys.exit(1)


    # Étape 1 : Chargement du référentiel communal

    df_ref = pd.read_csv(FILE_COMMUNES, sep=";", dtype=str)

    # Conservation uniquement des colonnes utiles à la jointure
    df_ref = df_ref[["code_insee", "nom_commune"]]

    # Normalisation du code INSEE sur 5 caractères
    df_ref["code_insee"] = df_ref["code_insee"].astype(str).str.zfill(5)

    # Suppression des doublons sur le code INSEE
    df_ref = df_ref.drop_duplicates(subset=["code_insee"])


    # Étape 2 : Lecture du fichier brut

    # Lecture sans header car le fichier contient des lignes de titre au-dessus du tableau
    df = pd.read_excel(FILE_DATA, sheet_name="COM", header=None, dtype=str)

    # Conservation des lignes à partir du vrai tableau
    # Ligne 5 dans Excel = index 4 en Python
    df = df.iloc[4:].copy()


    # Étape 3 : Renommage des colonnes

    # Renommage manuel des colonnes du fichier source
    df = df.rename(columns={
            0: "code_insee",
            1: "nom_brut",
            2: "2012",
            3: "2013",
            4: "2014",
            5: "2015",
            6: "2016",
            7: "2017",
            8: "2018",
            9: "2019",
            10: "2020",
            11: "2021",
            12: "2022",
            13: "2023",
            14: "2024",
            15: "2025"
    })


    # Normalisation du code INSEE sur 5 caractères
    df["code_insee"] = df["code_insee"].astype(str).str.zfill(5)


    # Étape 4 : Sélection de la variable 2022

    # Vérification de la présence de la colonne de l'année 2022
    if "2022" not in df.columns:
        print("Colonne 2022 introuvable")
        print(df.columns.tolist())
        sys.exit(1)

    # Conversion de la variable 2022 en numérique
    df["nb_creations_entreprises"] = pd.to_numeric(df["2022"], errors="coerce")


    # Étape 5 : Jointure avec le référentiel communal

    # Ajout du nom de commune à partir du référentiel
    df = pd.merge(
        df[["code_insee", "nb_creations_entreprises"]],
        df_ref,
        on="code_insee",
        how="left"
    )


    # Étape 6 : Contrôle des communes non retrouvées

    print("Communes non trouvées :", df["nom_commune"].isna().sum())

    print(df[df["nom_commune"].isna()][["code_insee"]].head(50))


    # Étape 7 : Suppression des communes non exploitables

    # Suppression des lignes sans nom de commune
    df = df.dropna(subset=["nom_commune"]).copy()

    # Harmonisation du nom de colonne avec les autres datasets
    df = df.rename(columns={"nom_commune": "localisation"})


    # Étape 8 : Construction du dataset final

    df_final = df[[
        "code_insee",
        "localisation",
        "nb_creations_entreprises"
    ]].copy()


    # Ajout de l'année de référence
    df_final["annee"] = year


    # Étape 9 : Export du dataset nettoyé

    fichier = DIR_OUTPUT / f"08_creation_entreprises_{year}_cleaned.csv"

    df_final.to_csv(fichier, sep=";", index=False, encoding="utf-8-sig")

    print(f"Fichier créé : {fichier}")
    print(f"Lignes sauvegardées : {len(df_final)}")


# Point d'entrée du script
if __name__ == "__main__":
    clean_creation_entreprises(2022)