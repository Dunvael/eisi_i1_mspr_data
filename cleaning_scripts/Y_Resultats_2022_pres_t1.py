import pandas as pd
import numpy as np
from pathlib import Path
import unicodedata
import sys

BASE_DIR = Path(".")

FILE_DATA = BASE_DIR / "data_raw" / "2022_raw" / "12. Resultat1er_tour" / "presidentielle_2022_t1.parquet"
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
        print(f"Fichier parquet introuvable : {FILE_DATA}")
        sys.exit(1)

    if not FILE_COMMUNES.exists():
        print(f"Référentiel communes introuvable : {FILE_COMMUNES}")
        sys.exit(1)

    # Référentiel communes
    df_ref = pd.read_csv(FILE_COMMUNES, sep=";", dtype=str, encoding="utf-8")
    df_ref = df_ref[["code_insee", "nom_commune"]].copy()
    df_ref["code_insee"] = df_ref["code_insee"].astype(str).str.zfill(5)

    # Lecture du parquet
    df = pd.read_parquet(
        FILE_DATA,
        columns=["code_commune", "nom", "voix"]
    )

    df = df.rename(columns={"code_commune": "code_insee"})

    df["code_insee"] = df["code_insee"].astype(str).str.zfill(5)

    df["nom"] = (
        df["nom"]
        .apply(remove_accents)
        .str.upper()
        .str.strip()
    )

    df["voix"] = pd.to_numeric(df["voix"], errors="coerce").fillna(0)

    # Association candidat → bloc politique
    mapping_bloc = {
        "ARTHAUD": "extreme_gauche",
        "POUTOU": "extreme_gauche",

        "ROUSSEL": "gauche",
        "MELENCHON": "gauche",
        "HIDALGO": "gauche",
        "JADOT": "gauche",

        "MACRON": "centre",
        "LASSALLE": "centre",

        "PECRESSE": "droite",
        "DUPONT-AIGNAN": "droite",

        "LE PEN": "extreme_droite",
        "ZEMMOUR": "extreme_droite",
    }

    df["bloc_politique"] = df["nom"].map(mapping_bloc)

    candidats_non_associes = df[df["bloc_politique"].isna()]["nom"].unique()

    if len(candidats_non_associes) > 0:
        print("Candidats non associés à un bloc :")
        print(candidats_non_associes)
        sys.exit(1)

    # Agrégation voix par commune et bloc
    df_blocs = (
        df.groupby(["code_insee", "bloc_politique"], as_index=False)["voix"]
        .sum()
    )

    # Total exprimés par commune
    df_blocs["total_exprimes_commune"] = (
        df_blocs.groupby("code_insee")["voix"]
        .transform("sum")
    )

    # Pourcentage du bloc dans la commune
    df_blocs["score_bloc"] = np.where(
        df_blocs["total_exprimes_commune"] > 0,
        df_blocs["voix"] / df_blocs["total_exprimes_commune"] * 100,
        np.nan
    )

    # Une ligne par commune
    df_scores = df_blocs.pivot_table(
        index="code_insee",
        columns="bloc_politique",
        values="score_bloc",
        fill_value=0
    ).reset_index()

    df_scores.columns.name = None

    df_scores = df_scores.rename(columns={
        "extreme_droite": "score_extreme_droite",
        "extreme_gauche": "score_extreme_gauche",
        "centre": "score_centre",
        "droite": "score_droite",
        "gauche": "score_gauche",
    })

    cols_scores = [
        "score_extreme_droite",
        "score_extreme_gauche",
        "score_centre",
        "score_droite",
        "score_gauche",
    ]

    for col in cols_scores:
        if col not in df_scores.columns:
            df_scores[col] = 0

    df_scores[cols_scores] = df_scores[cols_scores].round(2)

    # Classe politique dominante = Y
    df_scores["classe_politique"] = (
        df_scores[cols_scores]
        .idxmax(axis=1)
        .str.replace("score_", "", regex=False)
    )

    # Jointure nom commune
    df_scores = pd.merge(
        df_scores,
        df_ref,
        on="code_insee",
        how="left"
    )

    df_scores = df_scores.rename(columns={"nom_commune": "localisation"})
    df_scores["localisation"] = df_scores["localisation"].apply(remove_accents)

    df_scores = df_scores.dropna(subset=["localisation", "classe_politique"])
    df_scores = df_scores[df_scores["localisation"].astype(str).str.strip() != ""]

    # Fichier Y
    df_y = df_scores[
        [
            "code_insee",
            "localisation",
            "classe_politique"
        ]
    ].copy()

    df_y["annee"] = year

    # Fichier X votes
    df_x_votes = df_scores[
        [
            "code_insee",
            "localisation",
            "score_extreme_droite",
            "score_extreme_gauche",
            "score_centre",
            "score_droite",
            "score_gauche",
        ]
    ].copy()

    df_x_votes["annee"] = year

    fichier_y = DIR_OUTPUT / f"Y_classe_politique_{year}_cleaned.csv"
    fichier_x = DIR_OUTPUT / f"X_votes_politiques_{year}_cleaned.csv"

    df_y.to_csv(fichier_y, sep=";", index=False, encoding="utf-8-sig")
    df_x_votes.to_csv(fichier_x, sep=";", index=False, encoding="utf-8-sig")

    print("\n--- Répartition des classes politiques ---")
    print(df_y["classe_politique"].value_counts())

    print(f"\nFichier Y créé : {fichier_y}")
    print(f"Lignes Y : {len(df_y)}")

    print(f"\nFichier X votes créé : {fichier_x}")
    print(f"Lignes X : {len(df_x_votes)}")


if __name__ == "__main__":
    clean_resultats_elections(2022)