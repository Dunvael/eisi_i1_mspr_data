import pandas as pd
from pathlib import Path
import sys

print("Nettoyage fichier POPULATION & DENSITÉ")

# =========================================================
# 1. CONFIGURATION DES CHEMINS
# =========================================================
BASE_DIR = Path(".")
FILE_REF = BASE_DIR / "data_cleaned" / "2024" / "00_referentiel_communes_22_24_clean.csv"

FILE_POP_RAW = BASE_DIR / "data_raw" / "2024_raw" / "1. Densite population" / "population+densite+superficie_km2_2024.csv"
FILE_OUTPUT = BASE_DIR / "data_cleaned" / "2024" / "01_Densite_population" / "01.3_population_densite_2024_clean.csv"

def nettoyer_population():
    if not FILE_REF.exists() or not FILE_POP_RAW.exists():
        print("Fichiers introuvables.")
        sys.exit(1)

    df_ref = pd.read_csv(FILE_REF, sep=";", dtype=str)
    
    print("Lecture du fichier brut...")
    df_raw = pd.read_csv(FILE_POP_RAW, sep=",", dtype=str)

    lignes_depart = len(df_raw)

    # =========================================================
    # 2. PRÉPARATION DES DONNÉES 
    # =========================================================
    cols_utiles = ["code_insee", "population", "superficie_km2"]
    
    for col in cols_utiles:
        if col not in df_raw.columns:
            print(f" Colonne manquante : {col}. Présentes : {df_raw.columns.tolist()}")
            sys.exit(1)

    df_clean = df_raw[cols_utiles].copy()
    
    # Nettoyage des codes INSEE
    df_clean["code_insee"] = df_clean["code_insee"].astype(str).str.strip().str.zfill(5)
    
    # On compte les NaN textuels ou réels
    masque_nan_pop = df_clean["population"].isna() | (df_clean["population"].astype(str).str.strip().str.lower() == "nan") | (df_clean["population"].astype(str).str.strip() == "")
    masque_nan_sup = df_clean["superficie_km2"].isna() | (df_clean["superficie_km2"].astype(str).str.strip().str.lower() == "nan") | (df_clean["superficie_km2"].astype(str).str.strip() == "")
    
    nb_nan_total = masque_nan_pop.sum() + masque_nan_sup.sum()

    # On compte les 0 explicites
    nb_zero_pop = (df_clean["population"].astype(str).str.strip() == "0").sum()
    nb_zero_sup = (df_clean["superficie_km2"].astype(str).str.strip() == "0").sum()
    nb_zero_total = nb_zero_pop + nb_zero_sup

    # Sécurisation numérique
    df_clean["population"] = pd.to_numeric(df_clean["population"], errors='coerce').fillna(0).astype(int)
    df_clean["superficie_km2"] = pd.to_numeric(df_clean["superficie_km2"], errors='coerce').fillna(0.0)

    # =========================================================
    # 3. ALIGNEMENT RÉFÉRENTIEL ET FUSIONS
    # =========================================================
    print("Application du référentiel géographique 2024...")
    
    df_mapped = pd.merge(df_ref, df_clean, left_on="code_insee_2024", right_on="code_insee", how="inner")
    
    if df_mapped.empty:
        df_mapped = pd.merge(df_ref, df_clean, left_on="code_insee_2022", right_on="code_insee", how="inner")

    # Après ce groupby, les colonnes s'appellent officiellement "code_insee_2024" et "nom_commune_2024"
    df_final = df_mapped.groupby(["code_insee_2024", "nom_commune_2024"])[["population", "superficie_km2"]].sum().reset_index()

    # =========================================================
    # 4. RECALCUL DE LA DENSITÉ ET TAUX DE PERFECTION
    # =========================================================
    print("Recalcul des densités...")
    df_final["densite"] = df_final.apply(
        lambda row: round(row["population"] / row["superficie_km2"], 2) if row["superficie_km2"] > 0 else 0, 
        axis=1
    )

    comptage_fusions = df_mapped.drop_duplicates(subset=["code_insee_2022"]).groupby("code_insee_2024").size()
    nb_communes_fusionnees = len(comptage_fusions[comptage_fusions > 1])
    
    lignes_fin = len(df_final)

    # ---------------------------------------------------------
    # CALCUL DU TAUX DE PERFECTION (Précision)
    # ---------------------------------------------------------
    # Une ligne parfaite a une population > 0 ET une superficie > 0
    lignes_imparfaites = ((df_final["population"] == 0) | (df_final["superficie_km2"] == 0)).sum()
    taux_parfait = ((lignes_fin - lignes_imparfaites) / lignes_fin) * 100 if lignes_fin > 0 else 0

    # ---------------------------------------------------------
    # FORMATAGE FINAL DES COLONNES (Modifié ici)
    # ---------------------------------------------------------
    df_final["annee"] = 2024
    
    # On sélectionne directement les colonnes avec leurs vrais noms
    df_final = df_final[["code_insee_2024", "nom_commune_2024", "population", "superficie_km2", "densite", "annee"]]

    # =========================================================
    # 5. EXPORT ET DASHBOARD
    # =========================================================
    Path(FILE_OUTPUT).parent.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(FILE_OUTPUT, sep=";", index=False, encoding="utf-8-sig")

    print("\n" + "="*50)
    print(" POPULATION & DENSITÉ")
    print("="*50)
    print(f" Lignes brutes totales        : {lignes_depart:,}")
    print(f" Communes finales consolidées : {lignes_fin:,}")
    print("-" * 50)
    print(f" Fusions gérées               : {nb_communes_fusionnees}")
    print(f" Valeurs manquantes (NaN)     : {nb_nan_total}")
    print(f" Valeurs égales à 0 au départ : {nb_zero_total}")
    print("-" * 50)
    print(f" Total Population France      : {df_final['population'].sum():,}")
    print(f" TAUX DE PERFECTION (Précision): {taux_parfait:.2f} %")
    print("="*50 + "\n")
    
    print("Aperçu (Top 3) :")
    print(df_final.head(3))

if __name__ == "__main__":
    nettoyer_population()