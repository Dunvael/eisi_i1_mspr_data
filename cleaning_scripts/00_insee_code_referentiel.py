import pandas as pd
from pathlib import Path
import sys

# 1. CONFIGURATION

BASE_DIR = Path(".")

# Fichier brut INSEE 
FILE_RAW_COMMUNES = BASE_DIR / "data_raw" / "2022_raw" / "0. Code INSEE 2022" / "commune_2022.csv"

# Dossier d'export
DIR_CLEANED = BASE_DIR / "data_cleaned"
DIR_CLEANED.mkdir(parents=True, exist_ok=True)

# 2. NETTOYAGE DU REFERENTIEL
def run_etl():
    print("NETTOYAGE DU REFERENTIEL CODE INSEE")
    
    if not FILE_RAW_COMMUNES.exists():
        print(f"❌ ERREUR : Le fichier {FILE_RAW_COMMUNES} est introuvable.")
        sys.exit(1)

    try:
        #  1. LECTURE 
        print("⏳ Lecture du fichier brut de l'INSEE...")
        df = pd.read_csv(FILE_RAW_COMMUNES, sep=",", dtype=str, encoding='utf-8')
        print(f"Données brutes chargées : {len(df):,} lignes.")


        #  2. SÉLECTION ET RENOMMAGE 
        colonnes_a_garder = {
            'COM': 'code_insee',
            'LIBELLE': 'nom_commune',
            'DEP': 'code_departement',
            'REG': 'code_region'
        }
        
        cols_presentes = [col for col in colonnes_a_garder.keys() if col in df.columns]
        df = df[cols_presentes].rename(columns=colonnes_a_garder)

        df = df.dropna(subset=["code_insee"])
        df["nom_commune"] = df["nom_commune"].fillna("inconnu")
        
        print("Formatage des codes INSEE...")
        df["code_insee"] = df["code_insee"].astype(str).str.zfill(5)
        df["nom_commune"] = df["nom_commune"].astype(str).str.strip()
        

        df = df.drop_duplicates(subset=["code_insee"])

        print(df.isna().sum())
        

        # EXPORT
        chemin_sortie = DIR_CLEANED / "communes_2022_cleaned.csv"
        df.to_csv(chemin_sortie, sep=";", index=False, encoding="utf-8-sig")
        
        print(f"SUCCÈS : Fichier nettoyé ! ({len(df):,} communes prêtes)")
        print(f"Fichier disponible ici : {chemin_sortie}")
        
        

    except Exception as e:
        print(f"Une erreur a interrompu le script : {e}")

if __name__ == "__main__":
    run_etl()