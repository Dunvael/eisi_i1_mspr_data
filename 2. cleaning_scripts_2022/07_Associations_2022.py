import pandas as pd
from pathlib import Path
import sys


# 1. Configuration des chemins

BASE_DIR = Path(".")

# Chemin vers le fichier brut des créations d'associations
FILE_DATA = BASE_DIR / "data_raw" / "2022_raw" / "7_association_2022" / "CREATION_ASSOCIATION_PAR_COM_2000_a_2024.xlsx"

# Chemin vers le référentiel communal nettoyé
FILE_COMMUNES = BASE_DIR / "data_cleaned" / "communes_2022_cleaned.csv"

# Dossier de sortie des fichiers nettoyés
DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2022"

# Création du dossier de sortie s'il n'existe pas
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)


# 2. Nettoyage du dataset associations

def clean_associations(year):

    print(f"Nettoyage associations {year}")

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

    # Lecture du fichier Excel contenant les créations d'associations
    df = pd.read_excel(FILE_DATA, dtype=str)

    # Nettoyage des noms de colonnes
    df.columns = df.columns.str.strip()


    # Étape 3 : Renommage des colonnes utiles

    # Renommage des colonnes sources avec des noms homogènes
    df = df.rename(columns={
        "INSEE": "code_insee",
        "NOM": "nom_commune",
        "ASSO2022": "nb_associations"
    })

    # Normalisation du code INSEE sur 5 caractères
    df["code_insee"] = df["code_insee"].astype(str).str.zfill(5)


    # Étape 4 : Vérification de la colonne principale

    # Vérification de la présence de la colonne contenant le nombre d'associations
    if "nb_associations" not in df.columns:
        print(" Colonne ASSO2022 introuvable")
        print(df.columns.tolist())
        sys.exit(1)


    # Étape 5 : Nettoyage et conversion des données

    # Sécurisation du format du code INSEE
    df["code_insee"] = df["code_insee"].astype(str).str.zfill(5)

    # Nettoyage du nombre d'associations :
    # suppression des espaces éventuels
    df["nb_associations"] = (
        df["nb_associations"]
        .astype(str)
        .str.replace(r"\s+", "", regex=True)
    )

    # Conversion du nombre d'associations en numérique
    # Les valeurs invalides deviennent NaN
    df["nb_associations"] = pd.to_numeric(df["nb_associations"], errors="coerce")


    # Étape 6 : Jointure avec le référentiel communal

    # Ajout du nom de commune à partir du référentiel
    df = pd.merge(
        df[["code_insee", "nb_associations"]],
        df_ref,
        on="code_insee",
        how="left"
    )


    # Étape 7 : Contrôle des communes non retrouvées

    print("Communes non trouvées :", df["nom_commune"].isna().sum())

    print(df[df["nom_commune"].isna()][["code_insee"]].head(50))


    # Étape 8 : Suppression des communes non exploitables

    # Suppression des lignes sans nom de commune
    df = df.dropna(subset=["nom_commune"]).copy()

    # Harmonisation du nom de colonne avec les autres datasets
    df = df.rename(columns={"nom_commune": "localisation"})


    # Étape 9 : Construction du dataset final

    df_final = df[["code_insee", "localisation", "nb_associations"]].copy()

    # Ajout de l'année de référence
    df_final["annee"] = year


    # Étape 10 : Export du dataset nettoyé

    fichier = DIR_OUTPUT / f"07_associations_{year}_cleaned.csv"

    df_final.to_csv(fichier, sep=";", index=False, encoding="utf-8-sig")

    print(f" Fichier créé : {fichier}")
    print(f" Lignes : {len(df_final)}")


    # Étape 11 : Contrôle visuel des premiers codes INSEE

    print(df["code_insee"].head(10))


# Point d'entrée du script
if __name__ == "__main__":
    clean_associations(2022)