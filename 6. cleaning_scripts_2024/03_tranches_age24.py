import pandas as pd
import numpy as np
from pathlib import Path
import sys

print("Démographie 2024 :Tranches d'Âge")

# =========================================================
# 1. CONFIGURATION DES CHEMINS
# =========================================================
BASE_DIR = Path(".")

FILE_REF = BASE_DIR / "data_cleaned" / "2024" / "00_referentiel_communes_22_24_clean.csv"

FILE_POP_2024 = BASE_DIR / "data_cleaned" / "2024" / "01_Densite_population" / "01.3_population_densite_2024_clean.csv"

FILE_DATA_2022 = BASE_DIR / "data_raw" / "2022_raw" / "5_demographie_2022" / "DEMOGRAPHIE_PAR_SEXE_PAR_DEP_ET_COM_1968_TO_2022.xlsx"

FILE_OUTPUT = BASE_DIR / "data_cleaned" / "2024" / "03_Demographie" / "03_tranches_age_2024_clean.csv"

# Coefficients de structure INSEE (2022 -> 2024)
COEFFS_INSEE = {
    '00_14': 0.978, '15_29': 0.992, '30_44': 1.004, 
    '45_59': 0.995, '60_74': 1.018, '75_plus': 1.035 
}

def calcul_age_median(row, age_cols, midpoints):
    total = row[age_cols].sum()
    if total == 0 or pd.isna(total):
        return np.nan

    seuil = total / 2
    cumul = 0

    for col, midpoint in zip(age_cols, midpoints):
        cumul += row[col]
        if cumul >= seuil:
            return midpoint
    return np.nan

def traiter_demographie():
    # =========================================================
    # 2. CHARGEMENT ET PRÉPARATION
    # =========================================================
    if not FILE_REF.exists() or not FILE_POP_2024.exists() or not FILE_DATA_2022.exists():
        print("Fichiers introuvables.")
        sys.exit(1)

    print("Chargement des données...")
    df_ref = pd.read_csv(FILE_REF, sep=";", dtype=str)
    
    df_pop = pd.read_csv(FILE_POP_2024, sep=";", dtype=str)
    df_pop['population'] = pd.to_numeric(df_pop['population'], errors='coerce').fillna(0).astype(int)

    df_excel = pd.read_excel(FILE_DATA_2022, sheet_name="COM_2022", skiprows=13, dtype=str)
    df_excel.columns = df_excel.columns.astype(str).str.strip()
    
    df_excel["DR"] = df_excel["DR"].astype(str).str.zfill(2)
    df_excel["CR"] = df_excel["CR"].astype(str).str.zfill(3)
    df_excel["code_insee_2022_source"] = df_excel["DR"] + df_excel["CR"]

    # =========================================================
    # 3. PROJECTION DES VOLUMES 2022 AVEC COEFFICIENTS
    # =========================================================
    print("Application du vieillissement de population (Coefficients INSEE)...")

    tranches_mapping = {
        "t_0_4": ("ageq_rec01s1rpop2022", "ageq_rec01s2rpop2022", COEFFS_INSEE['00_14']),
        "t_5_9": ("ageq_rec02s1rpop2022", "ageq_rec02s2rpop2022", COEFFS_INSEE['00_14']),
        "t_10_14": ("ageq_rec03s1rpop2022", "ageq_rec03s2rpop2022", COEFFS_INSEE['00_14']),
        "t_15_19": ("ageq_rec04s1rpop2022", "ageq_rec04s2rpop2022", COEFFS_INSEE['15_29']),
        "t_20_24": ("ageq_rec05s1rpop2022", "ageq_rec05s2rpop2022", COEFFS_INSEE['15_29']),
        "t_25_29": ("ageq_rec06s1rpop2022", "ageq_rec06s2rpop2022", COEFFS_INSEE['15_29']),
        "t_30_34": ("ageq_rec07s1rpop2022", "ageq_rec07s2rpop2022", COEFFS_INSEE['30_44']),
        "t_35_39": ("ageq_rec08s1rpop2022", "ageq_rec08s2rpop2022", COEFFS_INSEE['30_44']),
        "t_40_44": ("ageq_rec09s1rpop2022", "ageq_rec09s2rpop2022", COEFFS_INSEE['30_44']),
        "t_45_49": ("ageq_rec10s1rpop2022", "ageq_rec10s2rpop2022", COEFFS_INSEE['45_59']),
        "t_50_54": ("ageq_rec11s1rpop2022", "ageq_rec11s2rpop2022", COEFFS_INSEE['45_59']),
        "t_55_59": ("ageq_rec12s1rpop2022", "ageq_rec12s2rpop2022", COEFFS_INSEE['45_59']),
        "t_60_64": ("ageq_rec13s1rpop2022", "ageq_rec13s2rpop2022", COEFFS_INSEE['60_74']),
        "t_65_69": ("ageq_rec14s1rpop2022", "ageq_rec14s2rpop2022", COEFFS_INSEE['60_74']),
        "t_70_74": ("ageq_rec15s1rpop2022", "ageq_rec15s2rpop2022", COEFFS_INSEE['60_74']),
        "t_75_79": ("ageq_rec16s1rpop2022", "ageq_rec16s2rpop2022", COEFFS_INSEE['75_plus']),
        "t_80_84": ("ageq_rec17s1rpop2022", "ageq_rec17s2rpop2022", COEFFS_INSEE['75_plus']),
        "t_85_89": ("ageq_rec18s1rpop2022", "ageq_rec18s2rpop2022", COEFFS_INSEE['75_plus']),
        "t_90_94": ("ageq_rec19s1rpop2022", "ageq_rec19s2rpop2022", COEFFS_INSEE['75_plus']),
        "t_95_plus": ("ageq_rec20s1rpop2022", "ageq_rec20s2rpop2022", COEFFS_INSEE['75_plus']),
    }

    age_cols = list(tranches_mapping.keys())
    midpoints = [2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5, 57.5, 62.5, 67.5, 72.5, 77.5, 82.5, 87.5, 92.5, 97.5]

    for tranche, (col_h, col_f, coeff) in tranches_mapping.items():
        h = pd.to_numeric(df_excel[col_h], errors="coerce").fillna(0)
        f = pd.to_numeric(df_excel[col_f], errors="coerce").fillna(0)
        df_excel[tranche] = (h + f) * coeff

    # =========================================================
    # 4. ALIGNEMENT RÉFÉRENTIEL ET FUSIONS
    # =========================================================
    print("Mapping géographique et gestion des fusions...")
    
    # Exclut les arrondissements et fait la correspondance 2022->2024
    df_mapped = pd.merge(df_ref, df_excel, left_on="code_insee_2022", right_on="code_insee_2022_source", how="inner")
    
    df_agg = df_mapped.groupby(["code_insee_2024", "nom_commune_2024"])[age_cols].sum().reset_index()

    # Calcul des proportions structurelles de la nouvelle commune
    df_agg['total_projete'] = df_agg[age_cols].sum(axis=1).replace(0, np.nan)
    for col in age_cols:
        df_agg[f"prop_{col}"] = df_agg[col] / df_agg['total_projete']

    # =========================================================
    # 5. CROISEMENT AVEC LA VRAIE POPULATION 2024
    # =========================================================
    print("Calcul des indicateurs finaux sur la population 2024...")
    
    df_final = pd.merge(df_agg, df_pop[['code_insee_2024', 'population']], on='code_insee_2024', how='inner')

    # On applique les proportions aux vrais volumes 2024
    final_tranches_cols = []
    for col in age_cols:
        nom_col = f"{col}_2024"
        final_tranches_cols.append(nom_col)
        df_final[nom_col] = (df_final['population'] * df_final[f"prop_{col}"]).fillna(0)

    # Groupements : Jeunes (< 25 ans = les 5 premières tranches) et Seniors (>= 65 ans = les 7 dernières)
    jeunes_cols = final_tranches_cols[:5]
    seniors_cols = final_tranches_cols[13:]

    df_final['jeunes'] = df_final[jeunes_cols].sum(axis=1)
    df_final['seniors'] = df_final[seniors_cols].sum(axis=1)

    df_final['pct_jeunes'] = np.where(df_final['population'] > 0, (df_final['jeunes'] / df_final['population']) * 100, np.nan)
    df_final['pct_seniors'] = np.where(df_final['population'] > 0, (df_final['seniors'] / df_final['population']) * 100, np.nan)

    # Âge médian
    df_final['age_median'] = df_final.apply(lambda row: calcul_age_median(row, final_tranches_cols, midpoints), axis=1)

    # =========================================================
    # 6. NETTOYAGE ET EXPORT
    # =========================================================
    df_final['annee'] = 2024
    df_final['pct_jeunes'] = df_final['pct_jeunes'].round(2)
    df_final['pct_seniors'] = df_final['pct_seniors'].round(2)
    df_final['age_median'] = df_final['age_median'].round(1)

    cols_export = ['code_insee_2024', 'nom_commune_2024', 'pct_jeunes', 'pct_seniors', 'age_median', 'annee']
    df_export = df_final[cols_export].copy()

    # Sécurité supplémentaire
    df_export = df_export.dropna(subset=['nom_commune_2024'])

    Path(FILE_OUTPUT).parent.mkdir(parents=True, exist_ok=True)
    df_export.to_csv(FILE_OUTPUT, sep=";", index=False, encoding="utf-8-sig")

    print("\n" + "="*50)
    print("RAPPORT : DÉMOGRAPHIE & ÂGE 2024")
    print("="*50)
    print(f"Fichier créé : {FILE_OUTPUT.name}")
    print(f"Communes traitées : {len(df_export):,}")
    print(f"Moyenne nationale pct_jeunes  : {df_export['pct_jeunes'].mean():.2f} %")
    print(f"Moyenne nationale pct_seniors : {df_export['pct_seniors'].mean():.2f} %")
    print(f"Médiane de l'âge médian FR    : {df_export['age_median'].median():.1f} ans")
    print("="*50 + "\n")
    
    print("Aperçu :")
    print(df_export.head(3))

if __name__ == "__main__":
    traiter_demographie()