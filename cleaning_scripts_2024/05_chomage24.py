import pandas as pd
import numpy as np
from pathlib import Path
import sys

print("🚀 Pipeline 2024 : Le VRAI Taux de Chômage (Basé sur les 15-64 ans)")

# =========================================================
# 1. CONFIGURATION DES CHEMINS
# =========================================================
BASE_DIR = Path(".")

FILE_REF = BASE_DIR / "data_cleaned" / "2024" / "00_referentiel_communes_22_24_clean.csv"
FILE_POP_2024 = BASE_DIR / "data_cleaned" / "2024" / "01_Densite_population" / "01.3_population_densite_2024_clean.csv"

# Le fichier DARES pour les chômeurs (Vérifie le nom exact de ton dossier "5. Chomage" ou "6. Chomage")
FILE_DARES_2024 = BASE_DIR / "data_raw" / "2024_raw" / "5. Chomage" / "chomage.csv"

# Ton fichier des âges (La solution parfaite pour la population active !)
FILE_DATA_2022 = BASE_DIR / "data_raw" / "2022_raw" / "13. Demographie" / "pop-sexe-age-quinquennal6822.xlsx"

DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2024" / "05_Chomage"
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)
FILE_OUTPUT = DIR_OUTPUT / "05_chomage_2024_clean.csv"

# Coefficients INSEE pour projeter 2022 -> 2024
COEFFS_INSEE = {
    '15_29': 0.992, '30_44': 1.004, '45_59': 0.995, '60_74': 1.018
}

def calculer_chomage_par_age():
    if not all(p.exists() for p in [FILE_REF, FILE_POP_2024, FILE_DARES_2024, FILE_DATA_2022]):
        print("❌ Fichiers introuvables. Vérifie tes chemins.")
        sys.exit(1)

    print("⏳ Chargement du référentiel et de la population 2024...")
    df_ref = pd.read_csv(FILE_REF, sep=";", dtype=str)
    
    df_pop = pd.read_csv(FILE_POP_2024, sep=";", dtype=str)
    df_pop['population'] = pd.to_numeric(df_pop['population'], errors='coerce').fillna(0).astype(int)

    # =========================================================
    # 2. EXTRACTION DE LA POPULATION 15-64 ANS
    # =========================================================
    print("⚙️ Isolement de la population en âge de travailler (15-64 ans)...")
    
    df_excel = pd.read_excel(FILE_DATA_2022, sheet_name="COM_2022", skiprows=13, dtype=str)
    df_excel.columns = df_excel.columns.astype(str).str.strip()
    
    df_excel["DR"] = df_excel["DR"].astype(str).str.zfill(2)
    df_excel["CR"] = df_excel["CR"].astype(str).str.zfill(3)
    df_excel["code_insee_2022_source"] = df_excel["DR"] + df_excel["CR"]

    # On ne garde QUE les tranches de 15 à 64 ans !
    tranches_actives = {
        "t_15_19": ("ageq_rec04s1rpop2022", "ageq_rec04s2rpop2022", COEFFS_INSEE['15_29']),
        "t_20_24": ("ageq_rec05s1rpop2022", "ageq_rec05s2rpop2022", COEFFS_INSEE['15_29']),
        "t_25_29": ("ageq_rec06s1rpop2022", "ageq_rec06s2rpop2022", COEFFS_INSEE['15_29']),
        "t_30_34": ("ageq_rec07s1rpop2022", "ageq_rec07s2rpop2022", COEFFS_INSEE['30_44']),
        "t_35_39": ("ageq_rec08s1rpop2022", "ageq_rec08s2rpop2022", COEFFS_INSEE['30_44']),
        "t_40_44": ("ageq_rec09s1rpop2022", "ageq_rec09s2rpop2022", COEFFS_INSEE['30_44']),
        "t_45_49": ("ageq_rec10s1rpop2022", "ageq_rec10s2rpop2022", COEFFS_INSEE['45_59']),
        "t_50_54": ("ageq_rec11s1rpop2022", "ageq_rec11s2rpop2022", COEFFS_INSEE['45_59']),
        "t_55_59": ("ageq_rec12s1rpop2022", "ageq_rec12s2rpop2022", COEFFS_INSEE['45_59']),
        "t_60_64": ("ageq_rec13s1rpop2022", "ageq_rec13s2rpop2022", COEFFS_INSEE['60_74'])
    }

    age_cols = list(tranches_actives.keys())
    for tranche, (col_h, col_f, coeff) in tranches_actives.items():
        h = pd.to_numeric(df_excel[col_h], errors="coerce").fillna(0)
        f = pd.to_numeric(df_excel[col_f], errors="coerce").fillna(0)
        df_excel[tranche] = (h + f) * coeff

    # Addition de toutes ces tranches pour avoir le total 15-64
    df_excel["pop_15_64_2022"] = df_excel[age_cols].sum(axis=1)

    # Mapping géographique
    df_mapped = pd.merge(df_ref, df_excel[["code_insee_2022_source", "pop_15_64_2022"]], left_on="code_insee_2022", right_on="code_insee_2022_source", how="inner")
    df_agg = df_mapped.groupby("code_insee_2024")["pop_15_64_2022"].sum().reset_index()

    # =========================================================
    # 3. EXTRACTION DES CHÔMEURS RÉELS (DARES 2024)
    # =========================================================
    print("📈 Extraction des Demandeurs d'Emploi réels (Fichier DARES 2024)...")
    
    # 🛠️ AJOUT DE low_memory=False POUR ÉVITER LE DtypeWarning !
    try:
        df_dares = pd.read_csv(FILE_DARES_2024, sep=';', dtype={'Code commune': str, 'Date': str}, low_memory=False)
    except:
        df_dares = pd.read_csv(FILE_DARES_2024, sep=',', dtype={'Code commune': str, 'Date': str}, low_memory=False)

    # 🛠️ RETOUR À LA CATÉGORIE "ABC" POUR AVOIR LES DONNÉES COMMUNALES
    df_dares = df_dares[
        (df_dares['Date'] == '2024-T4') & (df_dares['Catégorie'] == 'ABC') &
        (df_dares['Sexe'] == 'Total') & (df_dares['Tranche d\'âge'] == 'Total')
    ].copy()

    df_dares['code_insee_source'] = df_dares['Code commune'].astype(str).str.strip().str.zfill(5)
    df_dares['nb_chomeurs_2024'] = pd.to_numeric(df_dares['Nombre de demandeurs d\'emploi'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

    df_chom_map = pd.merge(df_ref, df_dares[['code_insee_source', 'nb_chomeurs_2024']], left_on="code_insee_2024", right_on="code_insee_source", how="left")
    
    masque_nan = df_chom_map['nb_chomeurs_2024'].isna()
    if masque_nan.any():
        df_fallback = pd.merge(df_ref, df_dares[['code_insee_source', 'nb_chomeurs_2024']], left_on="code_insee_2022", right_on="code_insee_source", how="inner")
        df_chom_map.update(df_fallback[['code_insee_2024', 'nb_chomeurs_2024']])

    df_chom_final = df_chom_map.groupby("code_insee_2024")["nb_chomeurs_2024"].sum().reset_index()

    # =========================================================
    # 4. CALCUL DU VRAI TAUX DE CHÔMAGE 2024
    # =========================================================
    print("🎯 Croisement final : Chômeurs / Population 15-64 ans...")
    
    df_final = pd.merge(df_ref[["code_insee_2024", "nom_commune_2024"]].drop_duplicates(), df_pop[['code_insee_2024', 'population']], on="code_insee_2024", how="inner")
    df_final = pd.merge(df_final, df_agg, on="code_insee_2024", how="left")
    df_final = pd.merge(df_final, df_chom_final, on="code_insee_2024", how="left")
    
    # Imputation chômeurs (médiane)
    mediane_chom = df_final['nb_chomeurs_2024'].median()
    df_final['nb_chomeurs_2024'] = df_final['nb_chomeurs_2024'].fillna(mediane_chom).round(0).astype(int)

    # Imputation population 15-64 (si commune non trouvée, on estime à 60% de la pop totale)
    masque_pop_nan = df_final['pop_15_64_2022'].isna() | (df_final['pop_15_64_2022'] == 0)
    df_final.loc[masque_pop_nan, 'pop_15_64_2022'] = df_final.loc[masque_pop_nan, 'population'] * 0.60
    
    # Sécurisation mathématique
    df_final['pop_15_64_2022'] = df_final['pop_15_64_2022'].round(0).astype(int)

    # 🎯 LE CALCUL MAGIQUE
    df_final['taux_chomage_15_64'] = np.where(
        df_final['pop_15_64_2022'] > 0,
        (df_final['nb_chomeurs_2024'] / df_final['pop_15_64_2022']) * 100,
        np.nan
    )

    # Nettoyage des valeurs aberrantes (petits villages)
    df_final.loc[df_final['taux_chomage_15_64'] > 60, 'taux_chomage_15_64'] = np.nan
    mediane_taux = df_final['taux_chomage_15_64'].median()
    df_final['taux_chomage_15_64'] = df_final['taux_chomage_15_64'].fillna(mediane_taux).round(2)

    # =========================================================
    # 5. EXPORT FINAL
    # =========================================================
    df_final['annee'] = 2024
    df_export = df_final[['code_insee_2024', 'nom_commune_2024', 'nb_chomeurs_2024', 'taux_chomage_15_64', 'annee']].copy()

    df_export.to_csv(FILE_OUTPUT, sep=";", index=False, encoding="utf-8-sig")

    print("\n" + "="*50)
    print("🏆 RAPPORT : VRAI TAUX DE CHÔMAGE 2024 (15-64 ANS)")
    print("="*50)
    print(f"Communes traitées             : {len(df_export):,}")
    print(f"Total Demandeurs d'Emploi     : {df_final['nb_chomeurs_2024'].sum():,.0f}")
    print("-" * 50)
    print(f"💼 POP. ÂGE TRAVAILLER (15-64): {df_final['pop_15_64_2022'].sum():,.0f}")
    print(f"📉 TAUX DE CHÔMAGE MOYEN      : {df_export['taux_chomage_15_64'].mean():.2f} %")
    print("="*50 + "\n")
    
    print("🔍 Aperçu :")
    print(df_export.head(3))

if __name__ == "__main__":
    calculer_chomage_par_age()