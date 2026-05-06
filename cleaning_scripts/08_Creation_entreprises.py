import pandas as pd
from pathlib import Path
import sys

BASE_DIR = Path(".")

FILE_DATA = BASE_DIR / "data_raw" / "2022_raw" / "15. Creation_entreprises" / "Creation_entreprises_2012_a_2025.xlsx"
FILE_COMMUNES = BASE_DIR / "data_cleaned" / "communes_2022_cleaned.csv"

DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2022"
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)


def clean_creation_entreprises(year):
    print(f"Nettoyage créations entreprises {year}")

    if not FILE_DATA.exists():
        print(f" Fichier introuvable : {FILE_DATA}")
        sys.exit(1)

    if not FILE_COMMUNES.exists():
        print(f" Référentiel introuvable : {FILE_COMMUNES}")
        sys.exit(1)


    # 1. REFERENTIEL
    df_ref = pd.read_csv(FILE_COMMUNES, sep=";", dtype=str)
    df_ref["code_insee"] = df_ref["code_insee"].str.zfill(5)

    # 2. LECTURE DATA
    # Lecture sans header car le fichier a des lignes de titre au-dessus
    df = pd.read_excel(FILE_DATA, sheet_name="COM", header=None, dtype=str)

    # On garde à partir de la ligne où commencent les données : ligne 5 Excel => index 4 Python
    df = df.iloc[4:].copy()

    # Renommer colonnes utiles
    df = df.rename(columns={
            0: "code_insee",
            1: "nom_brut",
            2: "2012",
            3: "2013",
            4: "2014",
            5: "2015",
            6: "2016",
            7: "2017",
            8: "2018",
            9: "2019",
            10: "2020",
            11: "2021",
            12: "2022",
            13: "2023",
            14: "2024",
            15: "2025"
    })


    df["code_insee"] = df["code_insee"].astype(str).str.zfill(5)

    # 4. VARIABLE 2022
    if "2022" not in df.columns:
        print("Colonne 2022 introuvable")
        print(df.columns.tolist())
        sys.exit(1)

    df["nb_creations_entreprises"] = pd.to_numeric(df["2022"], errors="coerce").fillna(0) #coerce → NaN

    # 5. MERGE
    df = pd.merge(
        df[["code_insee", "nb_creations_entreprises"]],
        df_ref,
        on="code_insee",
        how="left"
    )

    df = df.rename(columns={"nom_commune": "localisation"})

    # 6. FINAL
    df_final = df[[
        "localisation",
        "nb_creations_entreprises"
    ]].copy()

    df_final = df_final.dropna(subset=["localisation"]) #supprime localisation = NaN (vide)
    df_final = df_final[df_final["localisation"].astype(str).str.strip() != ""] #supprime champs vides
    df_final["nb_creations_entreprises"] = df_final["nb_creations_entreprises"].astype(int)

    df_final["annee"] = year

    # 7. EXPORT
    fichier = DIR_OUTPUT / f"08_creation_entreprises_{year}.csv"
    df_final.to_csv(fichier, sep=";", index=False, encoding="utf-8-sig")

    print(f"Fichier créé : {fichier}")
    print(f"Lignes sauvegardées : {len(df_final)}")


if __name__ == "__main__":
    clean_creation_entreprises(2022)