import pandas as pd
import numpy as np
from pathlib import Path
import sys

print(" Estimation des Revenus")

# =========================================================
# 1. CONFIGURATION DES CHEMINS
# =========================================================
BASE_DIR = Path(".")

# Ton référentiel magique (standardisé)
FILE_REF = BASE_DIR / "data_cleaned" / "2024" / "00_referentiel_communes_22_24_clean.csv"

# Le fichier source téléchargé depuis l'Insee
FILE_RAW = BASE_DIR / "data_raw" / "2024_raw" / "4. Revenue" / "revenues_23.csv"

DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2024" / "04_Revenus"
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)
FILE_OUTPUT = DIR_OUTPUT / "04_revenus_2024_estim_clean.csv"

# =========================================================
# 2. PARAMÈTRES ÉCONOMIQUES
# =========================================================
TAUX_EVOLUTION_2024 = 1.032  # Évolution estimée des salaires (+3.2%)
INDICATEUR_REVENU = 'MED_SL' # Médiane du Niveau de Vie 

def estimer_revenus():
    if not FILE_REF.exists() or not FILE_RAW.exists():
        print("Fichiers introuvables.")
        sys.exit(1)

    print("Chargement du référentiel et des données brutes INSEE...")
    df_ref = pd.read_csv(FILE_REF, sep=";", dtype=str)
    
    try:
        df_raw = pd.read_csv(FILE_RAW, sep=';', dtype=str)
    except:
        df_raw = pd.read_csv(FILE_RAW, sep=',', dtype=str) 

    lignes_depart = len(df_raw)

    # =========================================================
    # 3. FILTRAGE ET PRÉPARATION (T)
    # =========================================================
    print(f"Isolation de l'indicateur {INDICATEUR_REVENU}...")
    
    # On ne garde que les lignes qui concernent le revenu médian
    df_rev = df_raw[df_raw['FILOSOFI_MEASURE'] == INDICATEUR_REVENU].copy()
    
    # Nettoyage des géographies et des valeurs
    df_rev["GEO"] = df_rev["GEO"].astype(str).str.strip().str.zfill(5)
    
    df_rev["OBS_VALUE"] = pd.to_numeric(df_rev["OBS_VALUE"], errors="coerce")
    nb_nan_initiaux = df_rev["OBS_VALUE"].isna().sum()

    # =========================================================
    # 4. ALIGNEMENT RÉFÉRENTIEL ET FUSIONS
    # =========================================================
    print("Alignement sur la zone d'étude et gestion des fusions...")
    
    df_mapped = pd.merge(df_ref, df_rev, left_on="code_insee_2024", right_on="GEO", how="inner")
    
    if df_mapped.empty:
        df_mapped = pd.merge(df_ref, df_rev, left_on="code_insee_2022", right_on="GEO", how="inner")

    df_agg = df_mapped.groupby(["code_insee_2024", "nom_commune_2024"])["OBS_VALUE"].mean().reset_index()

    comptage_fusions = df_mapped.drop_duplicates(subset=["code_insee_2022"]).groupby("code_insee_2024").size()
    nb_communes_fusionnees = len(comptage_fusions[comptage_fusions > 1])

    # =========================================================
    # 5. PROJECTION 2024 ET IMPUTATION
    # =========================================================
    print(f"Application du taux d'évolution de +{(TAUX_EVOLUTION_2024 - 1)*100:.1f}%...")
    
    df_agg['revenu_estime_2024'] = (df_agg['OBS_VALUE'] * TAUX_EVOLUTION_2024).round(2)

    mediane_nationale_2024 = df_agg['revenu_estime_2024'].median()
    df_agg['revenu_estime_2024'] = df_agg['revenu_estime_2024'].fillna(mediane_nationale_2024)

    lignes_fin = len(df_agg)

    # =========================================================
    # 6. EXPORT ET DASHBOARD
    # =========================================================
    df_agg['annee'] = 2024
    df_export = df_agg[['code_insee_2024', 'nom_commune_2024', 'revenu_estime_2024', 'annee']].copy()

    df_export.to_csv(FILE_OUTPUT, sep=";", index=False, encoding="utf-8-sig")

    print("\n" + "="*50)
    print("RAPPORT : REVENUS 2024")
    print("="*50)
    print(f"Lignes brutes totales (fichier INSEE) : {lignes_depart:,}")
    print(f"Communes finales consolidées          : {lignes_fin:,}")
    print("-" * 50)
    print(f"Fusions gérées (Moyenne des revenus)  : {nb_communes_fusionnees}")
    print(f" Données masquées INSEE (NaN) gérées   : {nb_nan_initiaux}")
    print("-" * 50)
    print(f"Revenu Médian National Est. 2024      : {mediane_nationale_2024:,.2f} €")
    print("="*50 + "\n")
    
    print("Aperçu (Top 3) :")
    print(df_export.head(3))

if __name__ == "__main__":
    estimer_revenus()