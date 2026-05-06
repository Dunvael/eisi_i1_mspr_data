import pandas as pd
import numpy as np
from pathlib import Path
import sys

BASE_DIR = Path(".")

FILE_DATA = BASE_DIR / "data_raw" / "2022_raw" / "4. Age_secteur activite_statut_taux activite global" / "base-cc-evol-struct-pop-2022.xlsx"
FILE_COMMUNES = BASE_DIR / "data_cleaned" / "communes_2022_cleaned.csv"

DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2022"
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)


def clean_categorie_sociale(year):
    print("Nettoyage categorie sociale")

    # Lecture preview pour trouver la vraie ligne d'en-tête
    df_preview = pd.read_excel(FILE_DATA, nrows=80, header=None)

    header_idx = None
    for i, row in df_preview.iterrows():
        if row.astype(str).str.contains("CODGEO").any():
            header_idx = i
            break

    if header_idx is None:
        print("Impossible de trouver CODGEO.")
        print(df_preview.head(20))
        sys.exit(1)

    # Lecture réelle avec le bon header
    df = pd.read_excel(FILE_DATA, skiprows=header_idx, dtype=str)

    # Nettoyage des noms de colonnes
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace("\n", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace('"', "", regex=False)
        .str.replace("'", "", regex=False)
    )

    # Colonnes utiles
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

    df = df[list(mapping.keys())].rename(columns=mapping)

    df["code_insee"] = df["code_insee"].astype(str).str.zfill(5)

    # Conversion numérique
    for col in df.columns:
        if col != "code_insee":
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Totaux
    df["agri_total"] = df[["agri_15_24","agri_25_54","agri_55p"]].sum(axis=1)
    df["cadres_total"] = df[["cadres_15_24","cadres_25_54","cadres_55p"]].sum(axis=1)
    df["employes_total"] = df[["employes_15_24","employes_25_54","employes_55p"]].sum(axis=1)
    df["ouvriers_total"] = df[["ouvriers_15_24","ouvriers_25_54","ouvriers_55p"]].sum(axis=1)

    # Total actifs
    df["total_actifs"] = (
        df["agri_total"]
        + df["cadres_total"]
        + df["employes_total"]
        + df["ouvriers_total"]
    )

    # Pourcentages
    df["pourcentage_agri"] = df["agri_total"] / df["total_actifs"] * 100
    df["pourcentage_cadres"] = df["cadres_total"] / df["total_actifs"] * 100
    df["pourcentage_employes"] = df["employes_total"] / df["total_actifs"] * 100
    df["pourcentage_ouvriers"] = df["ouvriers_total"] / df["total_actifs"] * 100

    # Merge avec communes
    df_ref = pd.read_csv(FILE_COMMUNES, sep=";", dtype=str)
    df = pd.merge(df, df_ref, on="code_insee", how="left")

    df = df.rename(columns={"nom_commune": "localisation"})

    df_final = df[[
        "localisation",
        "pourcentage_agri",
        "pourcentage_cadres",
        "pourcentage_employes",
        "pourcentage_ouvriers"
    ]].copy()

    df_final["annee"] = year

    cols_pct = ["pourcentage_agri", "pourcentage_cadres", "pourcentage_employes", "pourcentage_ouvriers"]

    df_final[cols_pct] = df_final[cols_pct].round(2)

    # Export
    fichier = DIR_OUTPUT / f"03_categorie_sociale_{year}_cleaned.csv"
    df_final.to_csv(fichier, sep=";", index=False, encoding="utf-8-sig")

    print(f"Fichier créé : {fichier}")


if __name__ == "__main__":
    clean_categorie_sociale(2022)