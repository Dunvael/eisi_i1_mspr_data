import pandas as pd
import numpy as np
from pathlib import Path
import sys

print("ASSOCIATIONS 2024(Densité & Créations)")

# =========================================================
# 1. CONFIGURATION DES CHEMINS
# =========================================================
BASE_DIR = Path(".")


FILE_REF = BASE_DIR / "data_cleaned" / "2024" / "00_referentiel_communes_22_24_clean.csv"
FILE_POP_2024 = BASE_DIR / "data_cleaned" / "2024" / "01_Densite_population" / "01.3_population_densite_2024_clean.csv"

FILE_RAW = BASE_DIR / "data_raw" / "2024_raw" / "6. Associations" / "associations_2024.xlsx"

DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2024" / "06_Associations"
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)
FILE_OUTPUT = DIR_OUTPUT / "06_associations_2024_clean.csv"

def nettoyer_associations():
    if not all(p.exists() for p in [FILE_REF, FILE_POP_2024, FILE_RAW]):
        print("Fichiers introuvables.")
        sys.exit(1)

    print(" Chargement du référentiel, de la population et des associations...")
    df_ref = pd.read_csv(FILE_REF, sep=";", dtype=str)
    
    df_pop = pd.read_csv(FILE_POP_2024, sep=";", dtype=str)
    df_pop['population'] = pd.to_numeric(df_pop['population'], errors='coerce').fillna(0).astype(int)

    df_raw = pd.read_excel(FILE_RAW, dtype=str, engine="openpyxl")
    
    # Nettoyage des noms de colonnes 
    df_raw.columns = df_raw.columns.astype(str).str.strip()

    # Vérification des colonnes attendues
    cols_attendues = ["INSEE", "TOTASSO2024", "ASSO2024"]
    for col in cols_attendues:
        if col not in df_raw.columns:
            print(f"ERREUR: La colonne '{col}' est absente du fichier Excel.")
            sys.exit(1)

    # =========================================================
    # 2. NETTOYAGE PRÉALABLE DU BRUT
    # =========================================================
    print("Nettoyage des formats et conversion numérique...")
    
    # Code INSEE sur 5 caractères
    df_raw["INSEE"] = df_raw["INSEE"].astype(str).str.strip().str.zfill(5)
    
    for col in ["TOTASSO2024", "ASSO2024"]:
        df_raw[col] = pd.to_numeric(df_raw[col].astype(str).str.replace(",", "."), errors="coerce").fillna(0)

    # =========================================================
    # 3. ALIGNEMENT SUR LE RÉFÉRENTIEL (FUSIONS)
    # =========================================================
    print("Alignement géographique et gestion des fusions...")
    
    df_mapped = pd.merge(df_ref, df_raw[["INSEE", "TOTASSO2024", "ASSO2024"]], left_on="code_insee_2024", right_on="INSEE", how="left")
    
    masque_nan = df_mapped["TOTASSO2024"].isna()
    if masque_nan.any():
        df_fallback = pd.merge(df_ref, df_raw[["INSEE", "TOTASSO2024", "ASSO2024"]], left_on="code_insee_2022", right_on="INSEE", how="inner")
        df_mapped.update(df_fallback[["code_insee_2024", "TOTASSO2024", "ASSO2024"]])

    df_agg = df_mapped.groupby(["code_insee_2024", "nom_commune_2024"])[["TOTASSO2024", "ASSO2024"]].sum().reset_index()

    df_agg["TOTASSO2024"] = df_agg["TOTASSO2024"].fillna(0).astype(int)
    df_agg["ASSO2024"] = df_agg["ASSO2024"].fillna(0).astype(int)

    # =========================================================
    # 4. FEATURE ENGINEERING (ML READY)
    # =========================================================
    print("Calcul des indicateurs de dynamisme (Taux & Densité)...")
    
    # Croisement avec la population
    df_final = pd.merge(df_agg, df_pop[['code_insee_2024', 'population']], on='code_insee_2024', how='inner')

    # 1. Le Taux de création  %
    df_final["taux_creation_pct"] = np.where(
        df_final["TOTASSO2024"] > 0,
        (df_final["ASSO2024"] / df_final["TOTASSO2024"]) * 100,
        0
    ).round(2)

    # 2. La Densité associative (Associations pour 1000 habitants)
    df_final["densite_asso_1000_hab"] = np.where(
        df_final["population"] > 0,
        (df_final["TOTASSO2024"] / df_final["population"]) * 1000,
        0
    ).round(1)

    # =========================================================
    # 5. RENOMMAGE ET EXPORT
    # =========================================================
    df_final = df_final.rename(columns={
        "TOTASSO2024": "nb_associations_total",
        "ASSO2024": "nb_creations_2024"
    })

    df_final['annee'] = 2024
    
    cols_export = [
        "code_insee_2024", "nom_commune_2024", 
        "nb_associations_total", "nb_creations_2024", 
        "taux_creation_pct", "densite_asso_1000_hab", "annee"
    ]
    df_export = df_final[cols_export].copy()

    df_export.to_csv(FILE_OUTPUT, sep=";", index=False, encoding="utf-8-sig")

    print("\n" + "="*50)
    print("RAPPORT : TISSU ASSOCIATIF 2024")
    print("="*50)
    print(f"Communes traitées             : {len(df_export):,}")
    print(f"Total Associations en France  : {df_export['nb_associations_total'].sum():,.0f}")
    print(f"Nouvelles Créations (2024)    : {df_export['nb_creations_2024'].sum():,.0f}")
    print("-" * 50)
    print(f" Taux de création moyen     : {df_export['taux_creation_pct'].mean():.2f} %")
    print(f" Densité moyenne (/1000 hab): {df_export['densite_asso_1000_hab'].mean():.1f}")
    print(f" Valeurs manquantes (NaN)   : {df_export['nb_associations_total'].isna().sum()}")
    print("="*50 + "\n")
    
    print(" Aperçu :")
    print(df_export.head(3))

if __name__ == "__main__":
    nettoyer_associations()