import pandas as pd
import numpy as np
from pathlib import Path
import unicodedata
import sys

BASE_DIR = Path(".")

FILE_DATA = BASE_DIR / "data_raw" / "2022_raw" / "12. Resultat1er_tour" / "p2022-resultats-bureaux-t1.csv"
FILE_COMMUNES = BASE_DIR / "data_cleaned" / "communes_2022_cleaned.csv"

DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2022"
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)


def remove_accents(text):
    if pd.isna(text):
        return text

    text = str(text).strip()
    text = "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )
    return text


def clean_resultats_elections(year):
    print(f"Nettoyage résultats élections {year}")

    if not FILE_DATA.exists():
        print(f"Fichier source introuvable : {FILE_DATA}")
        sys.exit(1)

    if not FILE_COMMUNES.exists():
        print(f"Référentiel communes introuvable : {FILE_COMMUNES}")
        sys.exit(1)

    # Référentiel communes
    df_ref = pd.read_csv(FILE_COMMUNES, sep=";", dtype=str, encoding="utf-8")
    df_ref = df_ref[["code_insee", "nom_commune"]]
    df_ref["code_insee"] = df_ref["code_insee"].astype(str).str.zfill(5)

    # Lecture du fichier élections
    df = pd.read_csv(FILE_DATA, sep=",", dtype=str, encoding="utf-8")

    df.columns = df.columns.astype(str).str.strip()

    # Renommage code commune
    df = df.rename(columns={
        "CodeInsee": "code_insee",
        "Commune": "commune_brute"
    })

    df["code_insee"] = df["code_insee"].astype(str).str.zfill(5)

    # Colonnes candidats exprimés
    colonnes_exp = [
        "ARTHAUD.exp",
        "ROUSSEL.exp",
        "MACRON.exp",
        "LASSALLE.exp",
        "LE PEN.exp",
        "ZEMMOUR.exp",
        "MÉLENCHON.exp",
        "HIDALGO.exp",
        "JADOT.exp",
        "PÉCRESSE.exp",
        "POUTOU.exp",
        "DUPONT-AIGNAN.exp",
    ]

    colonnes_necessaires = ["code_insee", "Exprimés"] + colonnes_exp

    colonnes_manquantes = [
        col for col in colonnes_necessaires
        if col not in df.columns
    ]

    if colonnes_manquantes:
        print("Colonnes manquantes :", colonnes_manquantes)
        print("Colonnes disponibles :", df.columns.tolist())
        sys.exit(1)

    # Conversion numérique
    for col in ["Exprimés"] + colonnes_exp:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .str.replace(r"\s+", "", regex=True)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Agrégation par commune car le fichier est par bureau de vote
    df = (
        df[["code_insee", "Exprimés"] + colonnes_exp]
        .groupby("code_insee", as_index=False)
        .sum()
    )

    # Blocs politiques
    df["extreme_droite"] = df["LE PEN.exp"] + df["ZEMMOUR.exp"]

    df["extreme_gauche"] = (
        df["MÉLENCHON.exp"]
        + df["ARTHAUD.exp"]
        + df["POUTOU.exp"]
    )

    df["centre"] = (
        df["MACRON.exp"]
        + df["LASSALLE.exp"]
    )

    df["droite"] = (
        df["PÉCRESSE.exp"]
        + df["DUPONT-AIGNAN.exp"]
    )

    df["gauche"] = (
        df["ROUSSEL.exp"]
        + df["HIDALGO.exp"]
        + df["JADOT.exp"]
    )

    colonnes_blocs = [
        "extreme_droite",
        "extreme_gauche",
        "centre",
        "droite",
        "gauche"
    ]

    # Classe politique gagnante = Y du modèle
    df["classe_politique"] = df[colonnes_blocs].idxmax(axis=1)

    # Scores en pourcentage des exprimés
    for col in colonnes_blocs:
        df[f"score_{col}"] = np.where(
            df["Exprimés"] > 0,
            df[col] / df["Exprimés"] * 100,
            np.nan
        )

    # Jointure avec référentiel
    df = pd.merge(
        df,
        df_ref,
        on="code_insee",
        how="left"
    )

    df = df.rename(columns={"nom_commune": "localisation"})

    # Nettoyage localisation
    df["localisation"] = df["localisation"].apply(remove_accents)

    # Dataset final
    df_final = df[
        [
            "localisation",
            "classe_politique",
            "score_extreme_droite",
            "score_extreme_gauche",
            "score_centre",
            "score_droite",
            "score_gauche",
        ]
    ].copy()

    df_final = df_final.dropna(subset=["localisation", "classe_politique"])
    df_final = df_final[df_final["localisation"].astype(str).str.strip() != ""]

    cols_scores = [
        "score_extreme_droite",
        "score_extreme_gauche",
        "score_centre",
        "score_droite",
        "score_gauche",
    ]

    df_final[cols_scores] = df_final[cols_scores].round(2)

    df_final["annee"] = year

    fichier_sortie = DIR_OUTPUT / f"Y_resultats_elections_1er_tour_{year}.csv"
    df_final.to_csv(fichier_sortie, sep=";", index=False, encoding="utf-8-sig")

    print(f"Fichier créé : {fichier_sortie}")
    print(f"Lignes sauvegardées : {len(df_final)}")


if __name__ == "__main__":
    clean_resultats_elections(2022)