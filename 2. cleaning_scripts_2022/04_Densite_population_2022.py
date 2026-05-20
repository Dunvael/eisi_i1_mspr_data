import pandas as pd
from pathlib import Path
import sys

BASE_DIR = Path(".")

FILE_DATA = BASE_DIR / "data_raw" / "2022_raw" / "4_densite_population_2022" / "POPULATION_ET_DENSITE_PAR_COM_2022.csv"
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

    # Colonnes à garder
    df = df[[
        "code_insee",
        "population",
        "superficie_km2",
        "densite"
    ]]

    # Formatage : 123 en 00123
    df["code_insee"] = df["code_insee"].str.zfill(5)

    df["population"] = pd.to_numeric(df["population"], errors="coerce") # si erreur NaN sinon met nombre
    df["superficie_km2"] = pd.to_numeric(df["superficie_km2"], errors="coerce")
    df["densite"] = pd.to_numeric(df["densite"], errors="coerce")

    # Merge avec référentiel
    df_ref = pd.read_csv(FILE_COMMUNES, sep=";", dtype=str) #chargement du referentiel
    df_ref = df_ref[["code_insee", "nom_commune"]] #nettoyage referentiel : selection des colonnes

    df_ref["code_insee"] = df_ref["code_insee"].astype(str).str.zfill(5) 
    df_ref = df_ref.drop_duplicates(subset=["code_insee"]) #suppressions des doublons

    df = pd.merge(df, df_ref, on="code_insee", how="left") #ajout du nom de commune

    print("Communes non trouvées :", df["nom_commune"].isna().sum()) #debug pr identifier les codes INSEE qui match pas

    df = df.dropna(subset=["nom_commune"]).copy()

    df = df.rename(columns={"nom_commune": "localisation"})

    #dataset final
    df_final = df[[
        "code_insee",
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