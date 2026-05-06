import pandas as pd
from pathlib import Path
import sys

BASE_DIR = Path(".")

FILE_DATA = BASE_DIR / "data_raw" / "2022_raw" / "2. Densite population" / "communes-france-2022.csv"
FILE_COMMUNES = BASE_DIR / "data_cleaned" / "communes_2022_cleaned.csv"

DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2022"
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)


def clean_densite(year):
    print("Nettoyage densité population")

    if not FILE_DATA.exists():
        print("Fichier introuvable")
        sys.exit(1)

    # Chargement
    df = pd.read_csv(FILE_DATA, dtype=str)

    # Colonnes utiles
    df = df[[
        "code_insee",
        "population",
        "superficie_km2",
        "densite"
    ]]

    # Nettoyage types
    df["code_insee"] = df["code_insee"].str.zfill(5)

    df["population"] = pd.to_numeric(df["population"], errors="coerce")
    df["superficie_km2"] = pd.to_numeric(df["superficie_km2"], errors="coerce")
    df["densite"] = pd.to_numeric(df["densite"], errors="coerce")

    # Merge avec référentiel
    df_ref = pd.read_csv(FILE_COMMUNES, sep=";", dtype=str)

    df = pd.merge(df, df_ref, on="code_insee", how="left")

    df = df.rename(columns={"nom_commune": "localisation"})

    df_final = df[[
        "localisation",
        "population",
        "superficie_km2",
        "densite"
    ]].copy()

    df_final["annee"] = year

    # Arrondi
    df_final["densite"] = df_final["densite"].round(2)

    # Export
    fichier = DIR_OUTPUT / f"04_densite_population_{year}_cleaned.csv"
    df_final.to_csv(fichier, sep=";", index=False, encoding="utf-8-sig")

    print(f"Fichier créé : {fichier}")


if __name__ == "__main__":
    clean_densite(2022)