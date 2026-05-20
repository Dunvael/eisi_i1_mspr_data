import pandas as pd
from pathlib import Path
import sys

print("Nettoyage fichier NAISSANCES ")

# =========================================================
# 1. CONFIGURATION DES CHEMINS
# =========================================================
BASE_DIR = Path(".")
FILE_REF = BASE_DIR / "data_cleaned" / "2024" / "00_referentiel_communes_22_24_clean.csv"

# Ton fichier brut de naissances
FILE_NAIS_RAW = BASE_DIR / "data_raw" / "2024_raw" / "1. Densite population" / "naissances2024.csv"
FILE_OUTPUT = BASE_DIR / "data_cleaned" / "2024" / "01_Densite_population" / "01.2_naissances_2024_clean.csv"

def nettoyer_naissances():
    if not FILE_REF.exists() or not FILE_NAIS_RAW.exists():
        print(" Fichiers introuvables.")
        sys.exit(1)

    df_ref = pd.read_csv(FILE_REF, sep=";", dtype=str)
    
    print("Lecture du fichier brut INSEE...")
    df_raw = pd.read_csv(FILE_NAIS_RAW, sep=";", dtype=str)

    lignes_depart = len(df_raw)

    # =========================================================
    # 2. FILTRAGE DES DIMENSIONS
    # =========================================================
    print("Filtrage de l'année 2024 et de l'échelle communale...")
    
    # On isole les communes ("COM") pour 2024
    df_com = df_raw[
        (df_raw["TIME_PERIOD"] == "2024") & 
        (df_raw["GEO_OBJECT"] == "COM")
    ].copy()

    if df_com.empty:
        print("Aucune ligne pour GEO_OBJECT='COM' en 2024")
        sys.exit(1)

    # =========================================================
    # 3. PRÉPARATION DES DONNÉES
    # =========================================================
    # On isole les colonnes GEO (Code INSEE) et OBS_VALUE (Nombre de naissances)
    df_clean = df_com[["GEO", "OBS_VALUE"]].copy()
    
    df_clean["GEO"] = df_clean["GEO"].astype(str).str.strip().str.zfill(5)
    df_clean["OBS_VALUE"] = pd.to_numeric(df_clean["OBS_VALUE"], errors='coerce')

    nb_nan_initiaux = df_clean["OBS_VALUE"].isna().sum()
    df_clean["OBS_VALUE"] = df_clean["OBS_VALUE"].fillna(0).astype(int)

    # =========================================================
    # 4. ALIGNEMENT RÉFÉRENTIEL ET FUSIONS
    # =========================================================
    print("Application du référentiel géographique 2024...")
    
    df_mapped = pd.merge(df_ref, df_clean, left_on="code_insee_2024", right_on="GEO", how="inner")
    
    if df_mapped.empty:
      
        df_mapped = pd.merge(df_ref, df_clean, left_on="code_insee_2022", right_on="GEO", how="inner")

    df_final = df_mapped.groupby(["code_insee_2024", "nom_commune_2024"])["OBS_VALUE"].sum().reset_index()

    comptage_fusions = df_mapped.drop_duplicates(subset=["code_insee_2022"]).groupby("code_insee_2024").size()
    nb_communes_fusionnees = len(comptage_fusions[comptage_fusions > 1])
    
    lignes_fin = len(df_final)
    lignes_imparfaites = (df_final["OBS_VALUE"] == 0).sum()
    taux_parfait = ((lignes_fin - lignes_imparfaites) / lignes_fin) * 100 if lignes_fin > 0 else 0

    # Formatage de sortie
    df_final = df_final.rename(columns={"OBS_VALUE": "nb_naissances"})
    df_final["annee"] = 2024

    # =========================================================
    # 5. EXPORT ET DASHBOARD
    # =========================================================
    Path(FILE_OUTPUT).parent.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(FILE_OUTPUT, sep=";", index=False, encoding="utf-8-sig")

    print("\n" + "="*50)
    print(" NAISSANCES 2024")
    print("="*50)
    print(f"Lignes brutes totales        : {lignes_depart:,}")
    print(f"Lignes isolées (COM en 2024) : {len(df_com):,}")
    print(f"Communes finales consolidées : {lignes_fin:,}")
    print("-" * 50)
    print(f"Fusions gérées               : {nb_communes_fusionnees}")
    print(f" Valeurs manquantes corrigées : {nb_nan_initiaux:,}")
    print("-" * 50)
    print(f" Total naissances calculées   : {df_final['nb_naissances'].sum():,}")
    print(f" Taux perfection (> 0 naiss.) : {taux_parfait:.2f} %")
    print("="*50 + "\n")
    
    print("Aperçu (Top 3) :")
    print(df_final.head(3))

if __name__ == "__main__":
    nettoyer_naissances()