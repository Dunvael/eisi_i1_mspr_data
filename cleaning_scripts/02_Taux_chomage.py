import pandas as pd
import numpy as np
from pathlib import Path
import sys

BASE_DIR = Path(".")

FILE_DATA = BASE_DIR / "data_raw" / "2022_raw" / "6. Sexe_nationalite_immigration" / "TD_NAT2_2022.xlsx"
FILE_COMMUNES = BASE_DIR / "data_cleaned" / "communes_2022_cleaned.csv"

DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2022"
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)


def clean_taux_chomage(year):
    print(f"Nettoyage taux de chômage {year}")

    if not FILE_DATA.exists():
        print(f"Fichier source introuvable : {FILE_DATA}")
        sys.exit(1)

    if not FILE_COMMUNES.exists():
        print(f"Référentiel communes introuvable : {FILE_COMMUNES}")
        print("Lancer d'abord : py cleaning_scripts/00_create_referentiel.py")
        sys.exit(1)

    df_ref = pd.read_csv(FILE_COMMUNES, sep=";", dtype=str, encoding="utf-8")
    df_ref = df_ref[["code_insee", "nom_commune"]]
    df_ref["code_insee"] = df_ref["code_insee"].astype(str).str.zfill(5)

    # Trouver la ligne où commence le vrai tableau
    df_preview = pd.read_excel(FILE_DATA, nrows=20, header=None)

    header_idx = None
    for i, row in df_preview.iterrows():
        if row.astype(str).str.contains("CODGEO").any():
            header_idx = i
            break

    if header_idx is None:
        print("Impossible de trouver CODGEO.")
        sys.exit(1)

    df_raw = pd.read_excel(FILE_DATA, skiprows=header_idx, dtype=str)

    # Nettoyage des noms de colonnes pour éviter les espaces et retours de ligne
    df_raw.columns = (
        df_raw.columns
        .astype(str)
        .str.strip()
        .str.replace("\n", "", regex=False)
        .str.replace(" ", "", regex=False)
    )

    # Colonnes brutes utiles :
    # INATC1 = Français, INATC2 = Étrangers
    # SEXE1 = Hommes, SEXE2 = Femmes
    # TACTR11 = emploi, TACTR12 = chômeur
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

    colonnes_manquantes = [
        col for col in colonnes_a_garder.keys()
        if col not in df_raw.columns
    ]

    if colonnes_manquantes:
        print("Colonnes manquantes :", colonnes_manquantes)
        print("Colonnes disponibles :", list(df_raw.columns))
        sys.exit(1)

    df = df_raw[list(colonnes_a_garder.keys())].rename(columns=colonnes_a_garder)

    df["code_insee"] = df["code_insee"].astype(str).str.zfill(5)

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

    for col in colonnes_emploi + colonnes_chomeur:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(r"\s+", "", regex=True)
            .str.replace(",", ".", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["emploi_total"] = df[colonnes_emploi].sum(axis=1, min_count=1)
    df["chomeurs_total"] = df[colonnes_chomeur].sum(axis=1, min_count=1)
    df["actifs_total"] = df["emploi_total"] + df["chomeurs_total"]

    df["taux_chomage"] = np.where(
        df["actifs_total"] > 0,
        (df["chomeurs_total"] / df["actifs_total"]) * 100,
        np.nan
    )

    print(df[df["taux_chomage"] == 100][[
    "emploi_total",
    "chomeurs_total",
    "actifs_total"]])

    df = pd.merge(
        df[["code_insee", "taux_chomage"]],
        df_ref,
        on="code_insee",
        how="left"
    )

    df = df.dropna(subset=["nom_commune"])
    df = df.rename(columns={"nom_commune": "localisation"})

    df_final = df[["localisation", "taux_chomage"]].copy()
    df_final["annee"] = year
    df_final["taux_chomage"] = df_final["taux_chomage"].round(2)

    fichier_sortie = DIR_OUTPUT / f"02_taux_chomage_{year}_cleaned.csv"
    df_final.to_csv(fichier_sortie, sep=";", index=False, encoding="utf-8-sig")

    print(f"Terminé : {len(df_final)} lignes sauvegardées")
    print(f"Fichier créé : {fichier_sortie}")
    

    print(df.shape)
    print(df.info())
    print(df.isna().sum())
    print(df["taux_chomage"].describe())
    print("NaN taux chômage :", df["taux_chomage"].isna().sum())
    print("Taux > 70% :", (df["taux_chomage"] > 70).sum())
    print("Taux = 100% :", (df["taux_chomage"] == 100).sum())
        


if __name__ == "__main__":
    clean_taux_chomage(2022)