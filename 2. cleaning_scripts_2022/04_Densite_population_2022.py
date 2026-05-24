import pandas as pd
from pathlib import Path
import sys


# 1. Configuration des chemins : 

# Répertoire racine du projet
BASE_DIR = Path(".")

# Chemin vers le fichier brut densité / population
FILE_DATA = BASE_DIR / "data_raw" / "2022_raw" / "4_densite_population_2022" / "POPULATION_ET_DENSITE_PAR_COM_2022.csv"

# Chemin vers le référentiel communal nettoyé
FILE_COMMUNES = BASE_DIR / "data_cleaned" / "communes_2022_cleaned.csv"

# Dossier de sortie des fichiers nettoyés
DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2022"

# Création du dossier de sortie s'il n'existe pas
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)



# 2. Nettoyage du dataset densité population : 

def clean_densite(year):

    print("Nettoyage densité population")

    # Vérification de l'existence du fichier brut
    if not FILE_DATA.exists():
        print("Fichier introuvable")
        sys.exit(1)


    # Étape 1 : Extraction / Chargement

    # Lecture du fichier CSV brut
    # dtype=str permet de conserver les formats d'origine
    df = pd.read_csv(FILE_DATA, dtype=str)



    # Étape 2 : Sélection des colonnes utiles

    # Conservation uniquement des variables nécessaires au projet :
    # - code commune
    # - population
    # - superficie
    # - densité
    df = df[[
        "code_insee",
        "population",
        "superficie_km2",
        "densite"
    ]]



    # Étape 3 : Normalisation des formats

    # Formatage du code INSEE sur 5 caractères
    # Exemple : 123 devient 00123
    df["code_insee"] = df["code_insee"].str.zfill(5)



    # Étape 4 : Conversion des types numériques

    # Conversion des colonnes numériques
    # errors="coerce" transforme les valeurs invalides en NaN
    df["population"] = pd.to_numeric(
        df["population"],
        errors="coerce"
    )

    df["superficie_km2"] = pd.to_numeric(
        df["superficie_km2"],
        errors="coerce"
    )

    df["densite"] = pd.to_numeric(
        df["densite"],
        errors="coerce"
    )



    # Étape 5 : Contrôle qualité des valeurs manquantes

    # Vérification des NaN présents dans les colonnes numériques
    print("\n--- NaN colonnes numériques ---")

    print(
        df[[
            "population",
            "superficie_km2",
            "densite"
        ]].isna().sum()
    )



    # Étape 6 : Chargement du référentiel communal

    # Chargement du référentiel nettoyé des communes
    df_ref = pd.read_csv(
        FILE_COMMUNES,
        sep=";",
        dtype=str
    )

    # Conservation uniquement des colonnes utiles
    df_ref = df_ref[[
        "code_insee",
        "nom_commune"
    ]]



    # Étape 7 : Normalisation du référentiel

    # Formatage des codes INSEE du référentiel
    df_ref["code_insee"] = (
        df_ref["code_insee"]
        .astype(str)
        .str.zfill(5)
    )

    # Suppression des doublons :
    # chaque commune doit être unique dans le référentiel
    df_ref = df_ref.drop_duplicates(
        subset=["code_insee"]
    )



    # Étape 8 : Jointure avec le référentiel communal

    # Ajout du nom des communes à partir du référentiel
    df = pd.merge(
        df,
        df_ref,
        on="code_insee",
        how="left"
    )



    # Étape 9 : Contrôle des communes non retrouvées

    # Identification des communes absentes du référentiel
    print(
        "Communes non trouvées :",
        df["nom_commune"].isna().sum()
    )



    # Étape 10 : Suppression des communes invalides

    # Suppression des lignes sans nom de commune
    # car elles ne peuvent pas être exploitées dans le projet
    df = df.dropna(
        subset=["nom_commune"]
    ).copy()



    # Étape 11 : Harmonisation des noms de colonnes

    # Renommage de la commune en "localisation"
    # afin d'uniformiser les datasets du projet
    df = df.rename(
        columns={
            "nom_commune": "localisation"
        }
    )



    # Étape 12 : Construction du dataset final

    # Sélection finale des colonnes nettoyées
    df_final = df[[
        "code_insee",
        "localisation",
        "population",
        "superficie_km2",
        "densite"
    ]].copy()

    # Ajout de l'année de référence
    df_final["annee"] = year



    # Étape 13 : Formatage final

    # Arrondi de la densité à 2 décimales
    df_final["densite"] = (
        df_final["densite"]
        .round(2)
    )



    # Étape 14 : Export du dataset nettoyé

    # Génération du chemin du fichier exporté
    fichier = (
        DIR_OUTPUT /
        f"04_densite_population_{year}_cleaned.csv"
    )

    # Export CSV :
    # - séparateur ;
    # - sans index
    # - encodage UTF-8 compatible Excel
    df_final.to_csv(
        fichier,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Fichier créé : {fichier}")



# Point d'entrée du script
if __name__ == "__main__":
    clean_densite(2022)