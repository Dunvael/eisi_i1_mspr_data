import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Répertoire racine du projet
BASE_DIR = Path(".")

# Fichier brut contenant les données des catégories sociales
FILE_DATA = BASE_DIR / "data_raw" / "2022_raw" / "3_categorie_sociale_2022" / "CATEGORIE_SOCIAL_ET_DEMOGRAPHIE_PAR_COM_2011_TO_2022.xlsx"

# Référentiel des communes nettoyé
FILE_COMMUNES = BASE_DIR / "data_cleaned" / "communes_2022_cleaned.csv"

# Dossier de sortie des fichiers nettoyés
DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2022"

# Création du dossier s'il n'existe pas
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)



# FONCTION PRINCIPALE ETL
def clean_categorie_sociale(year):

    print("Nettoyage categorie sociale")


    # ÉTAPE 1 : DÉTECTION AUTOMATIQUE DE L’EN-TÊTE

    # Lecture des premières lignes du fichier Excel
    # afin de trouver la vraie ligne contenant les colonnes
    df_preview = pd.read_excel(
        FILE_DATA,
        nrows=80,
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
        print(df_preview.head(20))
        sys.exit(1)


    # ÉTAPE 2 : LECTURE DU FICHIER EXCEL

    # Lecture réelle du fichier avec le bon header
    df = pd.read_excel(
        FILE_DATA,
        skiprows=header_idx,
        dtype=str
    )


    # ÉTAPE 3 : NETTOYAGE DES NOMS DE COLONNES

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace("\n", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace('"', "", regex=False)
        .str.replace("'", "", regex=False)
    )


    # ÉTAPE 4 : SÉLECTION ET RENOMMAGE DES COLONNES

    # Dictionnaire des colonnes utiles
    mapping = {

        "CODGEO": "code_insee",

        # AGRICULTEURS
        "C22_POP1524_STAT_GSEC11_21": "agri_15_24",
        "C22_POP2554_STAT_GSEC11_21": "agri_25_54",
        "C22_POP55P_STAT_GSEC11_21": "agri_55p",

        # CADRES
        "C22_POP1524_STAT_GSEC13_23": "cadres_15_24",
        "C22_POP2554_STAT_GSEC13_23": "cadres_25_54",
        "C22_POP55P_STAT_GSEC13_23": "cadres_55p",

        # EMPLOYÉS
        "C22_POP1524_STAT_GSEC15_25": "employes_15_24",
        "C22_POP2554_STAT_GSEC15_25": "employes_25_54",
        "C22_POP55P_STAT_GSEC15_25": "employes_55p",

        # OUVRIERS
        "C22_POP1524_STAT_GSEC16_26": "ouvriers_15_24",
        "C22_POP2554_STAT_GSEC16_26": "ouvriers_25_54",
        "C22_POP55P_STAT_GSEC16_26": "ouvriers_55p",
    }

    # Sélection et renommage des colonnes
    df = df[
        list(mapping.keys())
    ].rename(columns=mapping)

    # Normalisation des codes INSEE
    df["code_insee"] = (
        df["code_insee"]
        .astype(str)
        .str.zfill(5)
    )


    # ÉTAPE 5 : CONVERSION DES COLONNES NUMÉRIQUES

    for col in df.columns:

        if col != "code_insee":

            # Conversion en numérique
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )


    # ÉTAPE 6 : CALCUL DES TOTAUX PAR CATÉGORIE

    # Calcul du total agriculteurs
    df["agri_total"] = (df[["agri_15_24","agri_25_54","agri_55p"]].sum(axis=1, min_count=1))

    # Calcul du total cadres
    df["cadres_total"] = (df[["cadres_15_24","cadres_25_54","cadres_55p"]].sum(axis=1, min_count=1))

    # Calcul du total employés
    df["employes_total"] = (df[["employes_15_24","employes_25_54","employes_55p"]].sum(axis=1, min_count=1))

    # Calcul du total ouvriers
    df["ouvriers_total"] = (df[["ouvriers_15_24","ouvriers_25_54","ouvriers_55p"]].sum(axis=1, min_count=1))


    # ÉTAPE 7 : CALCUL DU TOTAL D’ACTIFS

    df["total_actifs"] = (df["agri_total"] + df["cadres_total"] + df["employes_total"] + df["ouvriers_total"])


    # CONTRÔLES DES VALEURS MANQUANTES

    print("NaN total_actifs :")
    print(df["total_actifs"].isna().sum())

    print("total_actifs = 0 :")
    print((df["total_actifs"] == 0).sum())

    print(
        df[df["total_actifs"].isna()][[
            "code_insee",
            "agri_total",
            "cadres_total",
            "employes_total",
            "ouvriers_total"
        ]].head(20)
    )


    # ÉTAPE 8 : CALCUL DES POURCENTAGES

    # Pourcentage agriculteurs
    df["pourcentage_agri"] = np.where(df["total_actifs"] > 0, (df["agri_total"] / df["total_actifs"]) * 100, np.nan)

    # Pourcentage cadres
    df["pourcentage_cadres"] = np.where(df["total_actifs"] > 0, (df["cadres_total"] / df["total_actifs"]) * 100, np.nan)

    # Pourcentage employés
    df["pourcentage_employes"] = np.where(df["total_actifs"] > 0, (df["employes_total"] / df["total_actifs"]) * 100, np.nan)

    # Pourcentage ouvriers
    df["pourcentage_ouvriers"] = np.where(df["total_actifs"] > 0, (df["ouvriers_total"] / df["total_actifs"]) * 100, np.nan)


    # Liste des colonnes de pourcentages
    cols_pct = [

        "pourcentage_agri",
        "pourcentage_cadres",
        "pourcentage_employes",
        "pourcentage_ouvriers"
    ]


    # Vérification des NaN sur les pourcentages
    print(df[cols_pct].isna().sum())


    # ÉTAPE 9 : CHARGEMENT DU RÉFÉRENTIEL COMMUNES

    # Lecture du référentiel
    df_ref = pd.read_csv(
        FILE_COMMUNES,
        sep=";",
        dtype=str
    )

    # Conservation des colonnes utiles
    df_ref = df_ref[[
        "code_insee",
        "nom_commune"
    ]]

    # Normalisation des codes INSEE
    df_ref["code_insee"] = (
        df_ref["code_insee"]
        .astype(str)
        .str.zfill(5)
    )

    # Suppression des doublons éventuels
    df_ref = df_ref.drop_duplicates(
        subset=["code_insee"]
    )


    # ÉTAPE 10 : JOINTURE AVEC LE RÉFÉRENTIEL

    df = pd.merge(
        df,
        df_ref,
        on="code_insee",
        how="left"
    )


    # CONTRÔLE DES COMMUNES NON TROUVÉES

    communes_non_trouvees = df[
        df["nom_commune"].isna()
    ]

    print("\n--- COMMUNES NON TROUVÉES ---")

    print(
        communes_non_trouvees[[
            "code_insee"
        ]].head(50)
    )

    print("Nombre :", len(communes_non_trouvees))


    # Suppression des communes non retrouvées
    df = df.dropna(
        subset=["nom_commune"]
    ).copy()

    print(
        "Communes non trouvées :",
        df["nom_commune"].isna().sum()
    )

    # Harmonisation du nom de colonne
    df = df.rename(columns={
        "nom_commune": "localisation"
    })


    # ÉTAPE 11 : ANALYSE DES VALEURS MANQUANTES

    # Lignes contenant des NaN dans les pourcentages
    df_nan = df[
        df[cols_pct].isna().any(axis=1)
    ].copy()

    print("Nombre lignes NaN :")
    print(len(df_nan))

    print("\nNaN total_actifs :")
    print(df_nan["total_actifs"].isna().sum())

    print("\nTotal_actifs = 0 :")
    print((df_nan["total_actifs"] == 0).sum())

    print("\nAutres cas :")

    print(
        df_nan[
            (~df_nan["total_actifs"].isna()) &
            (df_nan["total_actifs"] != 0)
        ][[
            "code_insee",
            "localisation",
            "total_actifs"
        ]]
    )


    # ÉTAPE 12 : ANALYSE DES COLONNES BRUTES

    cols_brutes = [

        # AGRICULTEURS
        "agri_15_24",
        "agri_25_54",
        "agri_55p",

        # CADRES
        "cadres_15_24",
        "cadres_25_54",
        "cadres_55p",

        # EMPLOYÉS
        "employes_15_24",
        "employes_25_54",
        "employes_55p",

        # OUVRIERS
        "ouvriers_15_24",
        "ouvriers_25_54",
        "ouvriers_55p",
    ]


    # Vérification des NaN sur les colonnes brutes
    print("\n--- NaN colonnes brutes ---")

    print(
        df[cols_brutes]
        .isna()
        .sum()
    )


    # Détection des lignes partiellement vides
    print("\n--- Lignes avec NaN partiels ---")

    mask_partiel = (

        df[cols_brutes].isna().any(axis=1)

        &

        ~df[cols_brutes].isna().all(axis=1)
    )

    print(
        df[mask_partiel][
            ["code_insee"] + cols_brutes
        ].head(50)
    )

    print("\nNombre lignes NaN partiels :")
    print(mask_partiel.sum())


    # ÉTAPE 13 : CONSTRUCTION DU DATASET FINAL

    df_final = df[[
        "code_insee",
        "localisation",
        "pourcentage_agri",
        "pourcentage_cadres",
        "pourcentage_employes",
        "pourcentage_ouvriers"
    ]].copy()

    # Ajout de l’année
    df_final["annee"] = year


    # Liste des colonnes à arrondir
    cols_pct = [
        "pourcentage_agri",
        "pourcentage_cadres",
        "pourcentage_employes",
        "pourcentage_ouvriers"
    ]

    # Arrondi des valeurs
    df_final[cols_pct] = (
        df_final[cols_pct]
        .round(2)
    )


    # ÉTAPE 14 : EXPORT DU FICHIER FINAL

    fichier = (
        DIR_OUTPUT /
        f"03_categorie_sociale_{year}_cleaned.csv"
    )

    df_final.to_csv(
        fichier,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Fichier créé : {fichier}")


# POINT D’ENTRÉE DU SCRIPT
if __name__ == "__main__":
    clean_categorie_sociale(2022)