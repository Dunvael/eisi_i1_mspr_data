import pandas as pd
import numpy as np
from pathlib import Path
import sys

print(" Créations d'Entreprises")


# 1. CONFIGURATION DES CHEMINS

BASE_DIR = Path(".")


FILE_REF = BASE_DIR / "data_cleaned" / "2024" / "00_referentiel_communes_22_24_clean.csv"
FILE_POP_2024 = BASE_DIR / "data_cleaned" / "2024" / "01_Densite_population" / "01.3_population_densite_2024_clean.csv"

FILE_RAW = BASE_DIR / "data_raw" / "2024_raw" / "7. Creation_entreprises" / "entreprises_2024.csv"

DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2024" / "07_Entreprises"
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)
FILE_OUTPUT = DIR_OUTPUT / "07_creations_entreprises_2024_clean.csv"

def nettoyer_entreprises():
    if not all(p.exists() for p in [FILE_REF, FILE_POP_2024, FILE_RAW]):
        print("Fichiers introuvables.")
        sys.exit(1)

    print("Chargement du référentiel, de la population et du tissu économique...")
    df_ref = pd.read_csv(FILE_REF, sep=";", dtype=str)
    
    df_pop = pd.read_csv(FILE_POP_2024, sep=";", dtype=str)

    # Conversion population en numérique
    df_pop['population'] = pd.to_numeric(df_pop['population'], errors='coerce').fillna(0).astype(int)

    df_raw = pd.read_csv(FILE_RAW, sep=";", dtype=str)

    
    # 2. FILTRAGE
    
    print(" Filtrage des créations totales par commune en 2024...")
    
    # On isole uniquement les totaux ("_T") par commune ("COM") pour l'année 2024
    df_2024 = df_raw[
        (df_raw["TIME_PERIOD"] == "2024") &
        (df_raw["GEO_OBJECT"] == "COM") &
        (df_raw["ACTIVITY"] == "_T")
    ].copy()

    df_2024["GEO"] = df_2024["GEO"].astype(str).str.strip().str.zfill(5)
    # Conversion valeur numérique 
    df_2024["OBS_VALUE"] = pd.to_numeric(df_2024["OBS_VALUE"], errors="coerce").fillna(0)

    df_entreprises = df_2024.groupby("GEO", as_index=False)["OBS_VALUE"].sum()

    
    # 3. ALIGNEMENT SUR LE RÉFÉRENTIEL
    
    print("Alignement géographique et gestion des fusions...")
    # Jointure sur code INSEE 2024
    df_mapped = pd.merge(df_ref, df_entreprises, left_on="code_insee_2024", right_on="GEO", how="left")

    masque_nan = df_mapped["OBS_VALUE"].isna()
    if masque_nan.any():
        df_fallback = pd.merge(df_ref, df_entreprises, left_on="code_insee_2022", right_on="GEO", how="inner")
        df_mapped.update(df_fallback[["code_insee_2024", "OBS_VALUE"]])

    # Agrégation (On additionne les créations en cas de fusion de communes)
    df_agg = df_mapped.groupby(["code_insee_2024", "nom_commune_2024"])["OBS_VALUE"].sum().reset_index()
    
    df_agg["OBS_VALUE"] = df_agg["OBS_VALUE"].fillna(0).astype(int)

    
    # 4. FEATURE ENGINEERING
    
    print("Calcul du dynamisme entrepreneurial (Taux pour 1000 hab)...")
    
    df_final = pd.merge(df_agg, df_pop[['code_insee_2024', 'population']], on='code_insee_2024', how='inner')
    # Taux de création d'entreprises pour 1000 habitants
    df_final["taux_creation_entreprises_1000_hab"] = np.where(
        df_final["population"] > 0,
        (df_final["OBS_VALUE"] / df_final["population"]) * 1000,
        0
    ).round(2)

    
    # 5. RENOMMAGE ET EXPORT
    
    df_final = df_final.rename(columns={"OBS_VALUE": "nb_creations_entreprises_2024"})
    df_final['annee'] = 2024
    
    cols_export = [
        "code_insee_2024", "nom_commune_2024", 
        "nb_creations_entreprises_2024", "taux_creation_entreprises_1000_hab", "annee"
    ]
    
    df_export = df_final[cols_export].copy()

    df_export.to_csv(FILE_OUTPUT, sep=";", index=False, encoding="utf-8-sig")

    print("\n" + "="*50)
    print("RAPPORT : CRÉATIONS D'ENTREPRISES 2024")
    print("="*50)
    print(f"Communes traitées             : {len(df_export):,}")
    print(f"Total Créations (2024)        : {df_export['nb_creations_entreprises_2024'].sum():,.0f}")
    print("-" * 50)
    print(f"Taux moyen (/1000 hab)     : {df_export['taux_creation_entreprises_1000_hab'].mean():.2f}")
    print(f"Valeurs manquantes (NaN)   : {df_export['nb_creations_entreprises_2024'].isna().sum()}")
    print("="*50 + "\n")
    
    print("Aperçu :")
    print(df_export.head(3))

if __name__ == "__main__":
    nettoyer_entreprises()