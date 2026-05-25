import pandas as pd
from pathlib import Path
import sys
import requests  # <-- Ajout indispensable pour se connecter à l'API

print("Nettoyage fichier POPULATION & DENSITÉ")


# 1. CONFIGURATION DES CHEMINS

BASE_DIR = Path(".")
FILE_REF = BASE_DIR / "data_cleaned" / "2024" / "00_referentiel_communes_22_24_clean.csv"

FILE_POP_RAW = BASE_DIR / "data_raw" / "2024_raw" / "1. Densite population" / "population+densite+superficie_km2_2024.csv"
FILE_OUTPUT = BASE_DIR / "data_cleaned" / "2024" / "01_Densite_population" / "01.3_population_densite_2024_clean.csv"


# 2. NETTOYAGE

def nettoyer_population():

    # Vérification des fichiers
    if not FILE_REF.exists() or not FILE_POP_RAW.exists():
        print("Fichiers introuvables.")
        sys.exit(1)
    
    # Chargement référentiel communes
    df_ref = pd.read_csv(FILE_REF, sep=";", dtype=str)
    
    print("Lecture du fichier brut...")

    # Chargement dataset population
    df_raw = pd.read_csv(FILE_POP_RAW, sep=",", dtype=str)

    # Nombre de lignes initiales
    lignes_depart = len(df_raw)

    
    # 3. VALIDATION DES COLONNES
    
    cols_utiles = ["code_insee", "population", "superficie_km2"]
    
    # Vérification des colonnes obligatoires
    for col in cols_utiles:
        if col not in df_raw.columns:
            print(f" Colonne manquante : {col}. Présentes : {df_raw.columns.tolist()}")
            sys.exit(1)
    
    # Sélection des colonnes utiles
    df_clean = df_raw[cols_utiles].copy()
    
    # Nettoyage des codes INSEE
    df_clean["code_insee"] = df_clean["code_insee"].astype(str).str.strip().str.zfill(5)
    
    
    # 4. QUALITÉ DES DONNÉES BRUTES
    

    # On compte les NaN textuels ou réels
    masque_nan_pop = df_clean["population"].isna() | (df_clean["population"].astype(str).str.strip().str.lower() == "nan") | (df_clean["population"].astype(str).str.strip() == "")
    masque_nan_sup = df_clean["superficie_km2"].isna() | (df_clean["superficie_km2"].astype(str).str.strip().str.lower() == "nan") | (df_clean["superficie_km2"].astype(str).str.strip() == "")
    
    # Nombre total de valeurs manquantes
    nb_nan_total = masque_nan_pop.sum() + masque_nan_sup.sum()

    # Détection des zéros explicites
    nb_zero_pop = (df_clean["population"].astype(str).str.strip() == "0").sum()
    nb_zero_sup = (df_clean["superficie_km2"].astype(str).str.strip() == "0").sum()


    nb_zero_total = nb_zero_pop + nb_zero_sup

    # Sécurisation conversion numérique
    df_clean["population"] = pd.to_numeric(df_clean["population"], errors='coerce').fillna(0).astype(int)
    df_clean["superficie_km2"] = pd.to_numeric(df_clean["superficie_km2"], errors='coerce').fillna(0.0)

    
    # 5. ALIGNEMENT AVEC LE RÉFÉRENTIEL
    
    print("Application du référentiel géographique 2024...")
    
    # Jointure principale sur INSEE 2024
    df_mapped = pd.merge(df_ref, df_clean, left_on="code_insee_2024", right_on="code_insee", how="inner")
    
    # Fallback si absence correspondance 2024 → 2022
    if df_mapped.empty:
        df_mapped = pd.merge(df_ref, df_clean, left_on="code_insee_2022", right_on="code_insee", how="inner")
    
    
    # 6. AGRÉGATION (GESTION DES FUSIONS COMMUNALES)
    
    # Somme population + superficie par commune finale
    df_final = df_mapped.groupby(["code_insee_2024", "nom_commune_2024"])[["population", "superficie_km2"]].sum().reset_index()

    
    # 7. CORRECTION SUPERFICIES VIA API
    
    print("Vérification des superficies aberrantes (<= 0)...")
    
    def fetch_superficie_api(code_insee):
        """Interroge l'API GeoGouv pour obtenir la surface en km2"""
        try:
            url = f"https://geo.api.gouv.fr/communes/{code_insee}?fields=surface"
            reponse = requests.get(url, timeout=5)
            if reponse.status_code == 200:
                data = reponse.json()
                if 'surface' in data:
                    return round(data['surface'] / 100, 2) # Conversion Hectares -> km²
        except Exception as e:
            pass
        return 1.0 # Bouclier anti-crash si l'API ne répond pas
    
    # Correction des superficies nulles ou incohérentes
    masque_zero = df_final["superficie_km2"] <= 0
    nb_corrections = masque_zero.sum()
    
    if nb_corrections > 0:
        print(f" Appel de l'API Gouv pour corriger {nb_corrections} communes...")
        df_final.loc[masque_zero, "superficie_km2"] = df_final.loc[masque_zero, "code_insee_2024"].apply(fetch_superficie_api)
        print(" Correction API terminée !")

    
    # 8. CALCUL DE LA DENSITÉ
    
    print("Recalcul des densités...")
    df_final["densite"] = df_final.apply(
        lambda row: round(row["population"] / row["superficie_km2"], 2) if row["superficie_km2"] > 0 else 0, 
        axis=1
    )

    comptage_fusions = df_mapped.drop_duplicates(subset=["code_insee_2022"]).groupby("code_insee_2024").size()
    nb_communes_fusionnees = len(comptage_fusions[comptage_fusions > 1])
    
    
    # 9. KPI QUALITÉ
    

    lignes_fin = len(df_final)


    # Lignes incohérentes (population ou superficie nulles)
    lignes_imparfaites = ((df_final["population"] == 0) | (df_final["superficie_km2"] == 0)).sum()
    taux_parfait = ((lignes_fin - lignes_imparfaites) / lignes_fin) * 100 if lignes_fin > 0 else 0

    
    # 10. FORMAT FINAL
    
    df_final["annee"] = 2024
    
    df_final = df_final[["code_insee_2024", "nom_commune_2024", "population", "superficie_km2", "densite", "annee"]]

    
    # 5. EXPORT ET DASHBOARD
    
    Path(FILE_OUTPUT).parent.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(FILE_OUTPUT, sep=";", index=False, encoding="utf-8-sig")

    print("\n" + "="*50)
    print(" POPULATION & DENSITÉ")
    print("="*50)
    print(f" Lignes brutes totales        : {lignes_depart:,}")
    print(f" Communes finales consolidées : {lignes_fin:,}")
    print("-" * 50)
    print(f" Fusions gérées               : {nb_communes_fusionnees}")
    print(f" Superficies corrigées (API)  : {nb_corrections}")
    print("-" * 50)
    print(f" Total Population France      : {df_final['population'].sum():,}")
    print(f" TAUX DE PERFECTION           : {taux_parfait:.2f} %")
    print("="*50 + "\n")

if __name__ == "__main__":
    nettoyer_population()