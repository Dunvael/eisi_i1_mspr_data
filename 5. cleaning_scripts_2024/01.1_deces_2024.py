import pandas as pd
from pathlib import Path
import sys

print("Nettoyage fichier DÉCÈS 2024")


# 1. CONFIGURATION DES CHEMINS

BASE_DIR = Path(".")
FILE_REF = BASE_DIR / "data_cleaned" / "2024" / "00_referentiel_communes_22_24_clean.csv"
FILE_DECES_RAW = BASE_DIR / "data_raw" / "2024_raw" / "1. Densite population" / "deces2024.csv"
FILE_OUTPUT = BASE_DIR / "data_cleaned" / "2024" / "01_Densite_population" / "01.1_deces_2024_clean.csv"

# 2. NETTOYAGE

def nettoyer_deces():
    # Vérification existence des fichiers
    if not FILE_REF.exists() or not FILE_DECES_RAW.exists():
        print("Fichiers introuvables.")
        sys.exit(1)

    # Chargement du référentiel communes
    df_ref = pd.read_csv(FILE_REF, sep=";", dtype=str)
    
    print("Lecture du fichier brut INSEE...")

    # Chargement des données décès brutes
    df_raw = pd.read_csv(FILE_DECES_RAW, sep=";", dtype=str)

    # Sauvegarde du nombre de lignes initiales
    lignes_depart = len(df_raw)

    
    # 3. FILTRAGE DES DONNÉES
    
    print("Filtrage de l'année 2024 et de l'échelle communale...")
    
    # On garde que les lignes des communes pour 2024
    df_com = df_raw[
        (df_raw["TIME_PERIOD"] == "2024") & 
        (df_raw["GEO_OBJECT"] == "COM")
    ].copy()

    if df_com.empty:
        print("Le fichier ne contient aucune ligne pour GEO_OBJECT='COM' en 2024.")
        sys.exit(1)

    
    # 4. PRÉPARATION DES DONNÉES
    

    # isolation des colonnes utiles : GEO (Code INSEE) et OBS_VALUE (Nombre de décès)
    df_clean = df_com[["GEO", "OBS_VALUE"]].copy()
    
    # Standardisation du code INSEE (5 caractères)
    df_clean["GEO"] = df_clean["GEO"].astype(str).str.strip().str.zfill(5)

    # Conversion des valeurs en numérique (décès)
    df_clean["OBS_VALUE"] = pd.to_numeric(df_clean["OBS_VALUE"], errors='coerce')

    # Comptage des NaN initiaux sur les communes 2024
    nb_nan_initiaux = df_clean["OBS_VALUE"].isna().sum()
    df_clean["OBS_VALUE"] = df_clean["OBS_VALUE"].fillna(0).astype(int)

    
    # 5. ALIGNEMENT AVEC LE RÉFÉRENTIEL
    
    print("Application du référentiel géographique 2024...")
    
    # Jointure sur les codes INSEE 2024
    df_mapped = pd.merge(df_ref, df_clean, left_on="code_insee_2024", right_on="GEO", how="inner")
    
    # Fallback si pas de correspondance 2024 → on tente 2022
    if df_mapped.empty:
        df_mapped = pd.merge(df_ref, df_clean, left_on="code_insee_2022", right_on="GEO", how="inner")

    
    # 6. AGRÉGATION (GESTION DES FUSIONS)
    
    
    # Agrégation des décès par commune finale
    df_final = df_mapped.groupby(["code_insee_2024", "nom_commune_2024"])["OBS_VALUE"].sum().reset_index()

    # Détection des communes issues de fusion
    comptage_fusions = df_mapped.drop_duplicates(subset=["code_insee_2022"]).groupby("code_insee_2024").size()
    nb_communes_fusionnees = len(comptage_fusions[comptage_fusions > 1])
    
    
    # 7. KPI QUALITÉ
    
    lignes_fin = len(df_final)

    # Communes avec 0 décès (potentiellement anomalie ou vraie absence)
    lignes_imparfaites = (df_final["OBS_VALUE"] == 0).sum()

    # Taux de complétude des données
    taux_parfait = ((lignes_fin - lignes_imparfaites) / lignes_fin) * 100 if lignes_fin > 0 else 0

    # Renommage final
    df_final = df_final.rename(columns={"OBS_VALUE": "nb_deces"})

    # Ajout de l'année
    df_final["annee"] = 2024

    
    # 8. EXPORT DES DONNÉES
    
    Path(FILE_OUTPUT).parent.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(FILE_OUTPUT, sep=";", index=False, encoding="utf-8-sig")

    
    # 9. RAPPORT FINAL
    
    print("\n" + "="*50)
    print("DÉCÈS 2024 :")
    print("="*50)
    print(f" Lignes brutes totales (Toutes années/régions) : {lignes_depart:,}")
    print(f"Lignes isolées (Communes en 2024)             : {len(df_com):,}")
    print(f"Communes finales après Référentiel            : {lignes_fin:,}")
    print("-" * 50)
    print(f"Fusions gérées automatiquement                : {nb_communes_fusionnees}")
    print(f"Valeurs manquantes (NaN) corrigées en 0       : {nb_nan_initiaux:,}")
    print("-" * 50)
    print(f"Total des décès calculés                      : {df_final['nb_deces'].sum():,}")
    print(f"Taux de perfection (Communes avec décès > 0)  : {taux_parfait:.2f} %")
    print("="*50 + "\n")
    
    print("Aperçu (Top 3) :")
    print(df_final.head(3))
    

# 10. EXECUTION

if __name__ == "__main__":
    nettoyer_deces()