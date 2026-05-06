import pandas as pd
import numpy as np
from pathlib import Path
import sys

BASE_DIR = Path(".")

FILE_DATA = BASE_DIR / "data_raw" / "2022_raw" / "6. Sexe_nationalite_immigration" / "TD_NAT2_2022.xlsx"
FILE_COMMUNES = BASE_DIR / "data_cleaned" / "communes_2022_cleaned.csv"

DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2022"
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)


def clean_taux_immigration(year):
    print(f"Nettoyage taux d'immigration {year}")

    if not FILE_DATA.exists():
        print(f"Fichier source introuvable : {FILE_DATA}")
        sys.exit(1)

    if not FILE_COMMUNES.exists():
        print(f"Référentiel communes introuvable : {FILE_COMMUNES}")
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

    # Renommage code commune
    df_raw = df_raw.rename(columns={
        "CODGEO": "code_insee"
    })

    if "code_insee" not in df_raw.columns:
        print("Colonne code_insee introuvable.")
        print("Colonnes disponibles :", list(df_raw.columns))
        sys.exit(1)

    df_raw["code_insee"] = df_raw["code_insee"].astype(str).str.zfill(5)

    # Colonnes utiles :
    # INATC1 = Français
    # INATC2 = Étrangers
    # Peu importe SEXE et TACTR, on prend tout
    colonnes_francais = [
        col for col in df_raw.columns
        if col.startswith("INATC1_SEXE")
    ]

    colonnes_etrangers = [
        col for col in df_raw.columns
        if col.startswith("INATC2_SEXE")
    ]

    if not colonnes_francais or not colonnes_etrangers:
        print("Colonnes Français / Étrangers introuvables.")
        print("Colonnes français détectées :", colonnes_francais)
        print("Colonnes étrangers détectées :", colonnes_etrangers)
        print("Colonnes disponibles :", list(df_raw.columns))
        sys.exit(1)

    df = df_raw[["code_insee"] + colonnes_francais + colonnes_etrangers].copy()

    # Conversion numérique
    for col in colonnes_francais + colonnes_etrangers:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(r"\s+", "", regex=True)
            .str.replace(",", ".", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Calculs
    df["population_francaise"] = df[colonnes_francais].sum(axis=1)
    df["population_etrangere"] = df[colonnes_etrangers].sum(axis=1)

    df["population_totale"] = (
        df["population_francaise"] + df["population_etrangere"]
    )

    df["taux_immigration"] = np.where(
        df["population_totale"] > 0,
        (df["population_etrangere"] / df["population_totale"]) * 100,
        np.nan
    )

    # Jointure avec le référentiel
    df = pd.merge(
        df[["code_insee", "taux_immigration"]],
        df_ref,
        on="code_insee",
        how="left"
    )

    df = df.dropna(subset=["nom_commune"])
    df = df.rename(columns={"nom_commune": "localisation"})

    # Fichier final
    df_final = df[["localisation", "taux_immigration"]].copy()

    df_final = df_final.dropna(subset=["localisation", "taux_immigration"])
    df_final = df_final[df_final["localisation"].astype(str).str.strip() != ""]

    df_final["annee"] = year
    df_final["taux_immigration"] = df_final["taux_immigration"].round(2)

    fichier_sortie = DIR_OUTPUT / f"06_taux_immigration_{year}_cleaned.csv"
    df_final.to_csv(fichier_sortie, sep=";", index=False, encoding="utf-8-sig")

    print(f"Terminé : {len(df_final)} lignes sauvegardées")
    print(f"Fichier créé : {fichier_sortie}")


if __name__ == "__main__":
    clean_taux_immigration(2022)