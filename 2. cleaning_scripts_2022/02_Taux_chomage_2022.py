import pandas as pd
import numpy as np
from pathlib import Path
import sys

# CONFIGURATION DES CHEMINS

# Répertoire racine du projet
BASE_DIR = Path(".")

# Fichier brut contenant les données emploi / chômage
FILE_DATA = BASE_DIR / "data_raw" / "2022_raw" / "2_chomage_2022" / "ACTIVITE_IMMIGRATION_PAR_COM_2022.xlsx"

# Référentiel des communes nettoyé
FILE_COMMUNES = BASE_DIR / "data_cleaned" / "communes_2022_cleaned.csv"

# Dossier de sortie
DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2022"

# Création du dossier s'il n'existe pas
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)


# FONCTION PRINCIPALE ETL

def clean_taux_chomage(year):

    print(f"Nettoyage taux de chômage {year}")

    # VÉRIFICATION DES FICHIERS

    if not FILE_DATA.exists():
        print(f"Fichier source introuvable : {FILE_DATA}")
        sys.exit(1)

    if not FILE_COMMUNES.exists():
        print(f"Référentiel communes introuvable : {FILE_COMMUNES}")
        sys.exit(1)


    # ÉTAPE 1 : CHARGEMENT DU RÉFÉRENTIEL COMMUNES

    # Lecture du référentiel nettoyé
    df_ref = pd.read_csv(
        FILE_COMMUNES,
        sep=";",
        dtype=str,
        encoding="utf-8"
    )

    # Conservation des colonnes utiles
    df_ref = df_ref[["code_insee", "nom_commune"]]

    # Normalisation des codes INSEE
    df_ref["code_insee"] = (
        df_ref["code_insee"]
        .astype(str)
        .str.zfill(5)
    )

    # Suppression des doublons éventuels
    df_ref = df_ref.drop_duplicates(subset=["code_insee"])


    # ÉTAPE 2 : DÉTECTION AUTOMATIQUE DE L’EN-TÊTE

    # Lecture des premières lignes du fichier Excel
    df_preview = pd.read_excel(
        FILE_DATA,
        nrows=20,
        header=None
    )

    header_idx = None

    # Recherche de la ligne contenant "CODGEO"
    for i, row in df_preview.iterrows():

        if row.astype(str).str.contains("CODGEO").any():
            header_idx = i
            break

    # Arrêt du script si aucun header trouvé
    if header_idx is None:
        print("Impossible de trouver CODGEO.")
        sys.exit(1)


    # ÉTAPE 3 : LECTURE DU FICHIER EXCEL

    # Lecture du fichier à partir du bon header
    df_raw = pd.read_excel(
        FILE_DATA,
        skiprows=header_idx,
        dtype=str
    )


    # ÉTAPE 4 : NETTOYAGE DES NOMS DE COLONNES

    df_raw.columns = (
        df_raw.columns
        .astype(str)
        .str.strip()
        .str.replace("\n", "", regex=False)
        .str.replace(" ", "", regex=False)
    )


    # ÉTAPE 5 : SÉLECTION ET RENOMMAGE DES COLONNES

    # Dictionnaire des colonnes utiles
    colonnes_a_garder = {

        "CODGEO": "code_insee",

        "INATC1_SEXE1_TACTR11": "emploi_hommes_francais",
        "INATC1_SEXE2_TACTR11": "emploi_femmes_francais",
        "INATC2_SEXE1_TACTR11": "emploi_hommes_etrangers",
        "INATC2_SEXE2_TACTR11": "emploi_femmes_etrangers",

        "INATC1_SEXE1_TACTR12": "chomeur_hommes_francais",
        "INATC1_SEXE2_TACTR12": "chomeur_femmes_francais",
        "INATC2_SEXE1_TACTR12": "chomeur_hommes_etrangers",
        "INATC2_SEXE2_TACTR12": "chomeur_femmes_etrangers",
    }

    # Vérification des colonnes manquantes
    colonnes_manquantes = [
        col for col in colonnes_a_garder.keys()
        if col not in df_raw.columns
    ]

    if colonnes_manquantes:

        print("Colonnes manquantes :", colonnes_manquantes)
        print("Colonnes disponibles :", list(df_raw.columns))
        sys.exit(1)

    # Sélection des colonnes utiles
    df = df_raw[
        list(colonnes_a_garder.keys())
    ].rename(columns=colonnes_a_garder)

    # Normalisation du code INSEE
    df["code_insee"] = (df["code_insee"].astype(str).str.zfill(5))


    # ÉTAPE 6 : LISTE DES COLONNES EMPLOI / CHÔMAGE

    colonnes_emploi = [
        "emploi_hommes_francais",
        "emploi_femmes_francais",
        "emploi_hommes_etrangers",
        "emploi_femmes_etrangers",
    ]

    colonnes_chomeur = [
        "chomeur_hommes_francais",
        "chomeur_femmes_francais",
        "chomeur_hommes_etrangers",
        "chomeur_femmes_etrangers",
    ]


    # ÉTAPE 7 : CONVERSION DES COLONNES NUMÉRIQUES

    for col in colonnes_emploi + colonnes_chomeur:

        # Nettoyage des formats numériques
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(r"\s+", "", regex=True)
            .str.replace(",", ".", regex=False)
        )

        # Conversion en float
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )


    # ÉTAPE 8 : CALCULS DES INDICATEURS

    # Somme des personnes en emploi
    df["emploi_total"] = df[colonnes_emploi].sum(axis=1, min_count=1)

    # Somme des chômeurs
    df["chomeurs_total"] = df[colonnes_chomeur].sum(axis=1, min_count=1)

    # Calcul de la population active
    df["actifs_total"] = (df["emploi_total"] + df["chomeurs_total"])

    # Calcul du taux de chômage
    df["taux_chomage"] = np.where(
        df["actifs_total"] > 0,
        (df["chomeurs_total"] / df["actifs_total"]) * 100,
        np.nan)


    # ÉTAPE 9 : JOINTURE AVEC LE RÉFÉRENTIEL COMMUNES

    df = pd.merge(
        df,
        df_ref,
        on="code_insee",
        how="left"
    )


    # ÉTAPE 10 : CONTRÔLES DE COHÉRENCE

    # Affichage des communes avec taux NaN
    print("\n--- COMMUNES AVEC TAUX_CHOMAGE NaN ---")

    print(df[df["taux_chomage"].isna()][[
        "code_insee",
        "nom_commune",
        "taux_chomage",
        "emploi_total",
        "chomeurs_total",
        "actifs_total"
    ]])

    # Affichage des communes avec taux = 100
    print("\n--- COMMUNES AVEC TAUX_CHOMAGE = 100 ---")

    print(df[df["taux_chomage"] == 100][[
        "code_insee",
        "nom_commune",
        "taux_chomage",
        "emploi_total",
        "chomeurs_total",
        "actifs_total"
    ]])


    # ÉTAPE 11 : SUPPRESSION DES COMMUNES NON TROUVÉES

    df = df.dropna(subset=["nom_commune"])

    # Harmonisation du nom de colonne
    df = df.rename(columns={
        "nom_commune": "localisation"
    })


    # ÉTAPE 12 : CONTRÔLES DES VALEURS MANQUANTES

    # Vérification des NaN sur le taux
    print("\n--- LIGNES AVEC TAUX_CHOMAGE NaN ---")

    print(df[df["taux_chomage"].isna()][[
        "code_insee",
        "emploi_total",
        "chomeurs_total",
        "actifs_total"
    ]])

    # Vérification des taux très élevés
    print("\n--- LIGNES AVEC TAUX_CHOMAGE > 70 ---")

    print(df[df["taux_chomage"] > 70][[
        "code_insee",
        "emploi_total",
        "chomeurs_total",
        "actifs_total",
        "taux_chomage"
    ]])


    # ÉTAPE 13 : ANALYSE DES NaN

    df_nan = df[df["taux_chomage"].isna()].copy()

    print("\n--- CHECK NaN taux chômage ---")

    print("Nombre lignes NaN :")
    print(len(df_nan))

    print("\nNaN actifs_total :")
    print(df_nan["actifs_total"].isna().sum())

    print("\nactifs_total = 0 :")
    print((df_nan["actifs_total"] == 0).sum())


    # ÉTAPE 14 : ANALYSE DES COLONNES BRUTES

    cols_brutes = [
        "emploi_hommes_francais",
        "emploi_femmes_francais",
        "emploi_hommes_etrangers",
        "emploi_femmes_etrangers",

        "chomeur_hommes_francais",
        "chomeur_femmes_francais",
        "chomeur_hommes_etrangers",
        "chomeur_femmes_etrangers",
    ]

    print("\n--- NaN colonnes brutes ---")

    print(
        df[cols_brutes]
        .isna()
        .sum()
    )


    # Détection des lignes partiellement vides
    mask_partiel = (
        df[cols_brutes].isna().any(axis=1)
        &
        ~df[cols_brutes].isna().all(axis=1)
    )

    print("\nNombre lignes NaN partiels :")
    print(mask_partiel.sum())


    # ÉTAPE 15 : CONSTRUCTION DU DATASET FINAL

    df_final = df[[
        "code_insee",
        "localisation",
        "taux_chomage"
    ]].copy()

    # Ajout de l’année
    df_final["annee"] = year

    # Arrondi du taux de chômage
    df_final["taux_chomage"] = (
        df_final["taux_chomage"]
        .round(2)
    )


    # ÉTAPE 16 : EXPORT DU FICHIER FINAL

    fichier_sortie = (
        DIR_OUTPUT /
        f"02_taux_chomage_{year}_cleaned.csv"
    )

    df_final.to_csv(
        fichier_sortie,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )


    # ÉTAPE 17 : STATISTIQUES FINALES

    print("\n--- STATS FINALES ---")

    print(df_final.shape)

    print(df_final.info())

    print(df_final.isna().sum())

    print(df_final["taux_chomage"].describe())

    print(
        "NaN taux chômage :",
        df_final["taux_chomage"].isna().sum()
    )

    print(
        "Taux > 70% :",
        (df_final["taux_chomage"] > 70).sum()
    )

    print(
        "Taux = 100% :",
        (df_final["taux_chomage"] == 100).sum()
    )

    print(f"\nFichier créé : {fichier_sortie}")


# POINT D’ENTRÉE DU SCRIPT
if __name__ == "__main__":
    clean_taux_chomage(2022)