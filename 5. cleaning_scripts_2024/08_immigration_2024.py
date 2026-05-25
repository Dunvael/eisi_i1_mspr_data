import pandas as pd
import numpy as np
from pathlib import Path
import sys

print("🚀 Pipeline 2024 : Démographie (Modélisation Immigration 2024)")

# =========================================================
# 1. PARAMÈTRES ET CHEMINS
# =========================================================
# Coefficient de croissance estimé de la part immigrée (Insee 2022 -> 2024)
COEFF_2024 = 1.10 

BASE_DIR = Path(".")

FILE_REF = BASE_DIR / "data_cleaned" / "2024" / "00_referentiel_communes_22_24_clean.csv"
FILE_POP_2024 = BASE_DIR / "data_cleaned" / "2024" / "01_Densite_population" / "01.3_population_densite_2024_clean.csv"

# Fichier source INSEE 2022
FILE_INSEE_EXCEL = BASE_DIR / "data_raw" / "2022_raw" / "6_taux_immigration_2022" / "ACTIVITE_IMMIGRATION_PAR_COM_2022.xlsx"

DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2024" / "08_Immigration"
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)
FILE_OUTPUT = DIR_OUTPUT / "08_immigration_2024_clean.csv"

def modeliser_immigration():
    if not all(p.exists() for p in [FILE_REF, FILE_POP_2024, FILE_INSEE_EXCEL]):
        print("Fichiers introuvables.")
        sys.exit(1)

    print("Chargement du référentiel et de la population 2024...")
    df_ref = pd.read_csv(FILE_REF, sep=";", dtype=str)
    
    df_pop = pd.read_csv(FILE_POP_2024, sep=";", dtype=str)
    df_pop['population'] = pd.to_numeric(df_pop['population'], errors='coerce').fillna(0).astype(int)

    # =========================================================
    # 2. EXTRACTION DES DONNÉES INSEE (2022)
    # =========================================================
    print("Extraction des volumes historiques depuis l'Excel INSEE...")
    try:
        df_preview = pd.read_excel(FILE_INSEE_EXCEL, nrows=25, header=None)
        header_idx = next(i for i, row in df_preview.iterrows() if "CODGEO" in row.astype(str).values)
        df_struct = pd.read_excel(FILE_INSEE_EXCEL, skiprows=header_idx, dtype={'CODGEO': str})
    except Exception as e:
        print(f"Erreur lors de la lecture Excel : {e}")
        sys.exit(1)

    df_struct.columns = df_struct.columns.astype(str).str.strip()
    df_struct['code_insee_source'] = df_struct['CODGEO'].astype(str).str.strip().str.zfill(5)

    # Identification des colonnes Français (INATC1) et Étrangers/Immigrés (INATC2)
    cols_fr = [c for c in df_struct.columns if 'INATC1' in c]
    cols_et = [c for c in df_struct.columns if 'INATC2' in c]

    for col in cols_fr + cols_et:
        df_struct[col] = pd.to_numeric(df_struct[col], errors='coerce').fillna(0)

    # Calcul des volumes bruts 2022
    df_struct['volume_total_2022'] = df_struct[cols_fr + cols_et].sum(axis=1)
    df_struct['volume_immi_2022'] = df_struct[cols_et].sum(axis=1)

    # =========================================================
    # 3. ALIGNEMENT RÉFÉRENTIEL ET AGRÉGATION
    # =========================================================
    print("Alignement géographique et consolidation des fusions...")
    
    df_mapped = pd.merge(df_ref, df_struct[['code_insee_source', 'volume_total_2022', 'volume_immi_2022']], left_on="code_insee_2022", right_on="code_insee_source", how="inner")
    
    # Agrégation par commune 2024 (On additionne les volumes AVANT de calculer le ratio)
    df_agg = df_mapped.groupby(["code_insee_2024", "nom_commune_2024"])[["volume_total_2022", "volume_immi_2022"]].sum().reset_index()

   # =========================================================
    # 4. CALCUL DU TAUX PROJETÉ ET APPLICATION 2024
    # =========================================================
    print("Application de la croissance tendancielle et calcul des volumes 2024...")
    
    df_final = pd.merge(df_ref[["code_insee_2024", "nom_commune_2024"]].drop_duplicates(), df_pop[['code_insee_2024', 'population']], on="code_insee_2024", how="inner")
    df_final = pd.merge(df_final, df_agg[['code_insee_2024', 'volume_total_2022', 'volume_immi_2022']], on="code_insee_2024", how="left")

    # Calcul du ratio de base 2022 pour la commune 
    df_final['ratio_2022'] = np.where(
        df_final['volume_total_2022'] > 0,
        df_final['volume_immi_2022'] / df_final['volume_total_2022'],
        np.nan
    )

    # Projection 2024
    df_final['taux_immigration_pct'] = (df_final['ratio_2022'] * COEFF_2024 * 100)
    
    # =========================================================
    # Imputation pour les communes inconnues (Médiane Départementale)
    # =========================================================
    print("Imputation des valeurs manquantes par la médiane départementale...")
    
    # 1. On extrait le département
    df_final['code_dept'] = df_final['code_insee_2024'].astype(str).str[:2]
    
    # 2. Médiane par département
    df_final['mediane_dept'] = df_final.groupby('code_dept')['taux_immigration_pct'].transform('median')
    
    # 3. Médiane nationale (en secours au cas où un département entier est vide)
    mediane_nationale = df_final['taux_immigration_pct'].median()
    
    # 4. Remplacement en cascade : Médiane Dept d'abord, puis Nationale, puis on arrondit
    df_final['taux_immigration_pct'] = df_final['taux_immigration_pct'].fillna(df_final['mediane_dept']).fillna(mediane_nationale).round(2)
    
    # 5. Nettoyage des colonnes temporaires
    df_final = df_final.drop(columns=['code_dept', 'mediane_dept'])
    
    df_final['taux_immigration_pct'] = df_final['taux_immigration_pct'].clip(upper=100.0)

    # Calcul du nombre d'individus 2024
    df_final['nb_immigres_2024'] = (df_final['population'] * (df_final['taux_immigration_pct'] / 100)).round(0).astype(int)

    # =========================================================
    # 5. EXPORT FINAL
    # =========================================================
    df_final['annee'] = 2024
    
    cols_export = [
        "code_insee_2024", "nom_commune_2024", 
        "nb_immigres_2024", "taux_immigration_pct", "annee"
    ]
    df_export = df_final[cols_export].copy()

    df_export.to_csv(FILE_OUTPUT, sep=";", index=False, encoding="utf-8-sig")

    print("\n" + "="*50)
    print("RAPPORT : IMMIGRATION  2024")
    print("="*50)
    print(f"Communes traitées             : {len(df_export):,}")
    print(f"Total pop. immigrée estimée   : {df_export['nb_immigres_2024'].sum():,.0f}")
    print("-" * 50)
    print(f" Taux moyen par commune     : {df_export['taux_immigration_pct'].mean():.2f} %")
    print(f" Valeurs manquantes (NaN)   : {df_export['taux_immigration_pct'].isna().sum()}")
    print("="*50 + "\n")
    
    print(" Aperçu :")
    print(df_export.head(3))

if __name__ == "__main__":
    modeliser_immigration()