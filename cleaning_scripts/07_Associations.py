import pandas as pd
from pathlib import Path
import sys

BASE_DIR = Path(".")

FILE_DATA = BASE_DIR / "data_raw" / "2022_raw" / "14. Associations" / "creation_association2000_a_2024.xlsx"
FILE_COMMUNES = BASE_DIR / "data_cleaned" / "communes_2022_cleaned.csv"

DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2022"
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)


def clean_associations(year):
    print(f"Nettoyage associations {year}")

    if not FILE_DATA.exists():
        print(f" Fichier introuvable : {FILE_DATA}")
        sys.exit(1)

    if not FILE_COMMUNES.exists():
        print(f" Référentiel introuvable : {FILE_COMMUNES}")
        sys.exit(1)

    # 1. REFERENTIEL
    df_ref = pd.read_csv(FILE_COMMUNES, sep=";", dtype=str)
    df_ref["code_insee"] = df_ref["code_insee"].astype(str).str.zfill(5)

    # 2. LECTURE DATA
    df = pd.read_excel(FILE_DATA, dtype=str)

    df.columns = df.columns.str.strip()

    # 3. RENOMMAGE
    df = df.rename(columns={
        "INSEE": "code_insee",
        "NOM": "nom_commune",
        "ASSO2022": "nb_associations"
    })

    df["code_insee"] = df["code_insee"].astype(str).str.zfill(5)

    # Vérification
    if "nb_associations" not in df.columns:
        print(" Colonne ASSO2022 introuvable")
        print(df.columns.tolist())
        sys.exit(1)

    # 4. NETTOYAGE
    df["code_insee"] = df["code_insee"].astype(str).str.zfill(5)

    df["nb_associations"] = (
        df["nb_associations"]
        .astype(str)
        .str.replace(r"\s+", "", regex=True)
    )

    df["nb_associations"] = pd.to_numeric(df["nb_associations"], errors="coerce")

    # 5. MERGE
    df = pd.merge(
        df[["code_insee", "nb_associations"]],
        df_ref,
        on="code_insee",
        how="left"
    )

    df = df.rename(columns={"nom_commune": "localisation"})

    # 6. CLEAN FINAL
    df_final = df[["localisation", "nb_associations"]].copy()

    df_final = df_final.dropna(subset=["localisation", "nb_associations"])
    df_final = df_final[df_final["localisation"].astype(str).str.strip() != ""]

    df_final["annee"] = year

    # 7. EXPORT
    fichier = DIR_OUTPUT / f"07_associations_{year}.csv"
    df_final.to_csv(fichier, sep=";", index=False, encoding="utf-8-sig")

    print(f" Fichier créé : {fichier}")
    print(f" Lignes : {len(df_final)}")

    print(df["code_insee"].head(10))


if __name__ == "__main__":
    clean_associations(2022)