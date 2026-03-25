import pandas as pd
from pathlib import Path
import sys

# ==============================================================================
# 1. CONFIGURATION
# ==============================================================================
BASE_DIR = Path(".")

# ⚠️ Fichier brut INSEE (Vérifie bien ton chemin exact comme on l'avait corrigé)
FILE_RAW_COMMUNES = BASE_DIR / "data_raw" / "2022_raw" / "lien vers code communes 2022" / "commune_2022.csv"

# Dossier d'export
DIR_FILTERED = BASE_DIR / "data_filtered"
DIR_FILTERED.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# 2. NETTOYAGE DU MASTER
# ==============================================================================
def run_etl():
    print("🚀 DÉMARRAGE : Création du Fichier Master (Toutes les communes incluses)...")
    
    if not FILE_RAW_COMMUNES.exists():
        print(f"❌ ERREUR : Le fichier {FILE_RAW_COMMUNES} est introuvable.")
        sys.exit(1)

    try:
        # --- 1. LECTURE ---
        print("⏳ Lecture du fichier brut de l'INSEE...")
        df = pd.read_csv(FILE_RAW_COMMUNES, sep=",", dtype=str, encoding='utf-8')
        print(f"📊 Données brutes chargées : {len(df):,} lignes.")

        # ⚠️ LA CORRECTION EST ICI : On ne filtre plus ! On garde les COM, COMD, ARM...
        # On passe directement à la sélection des colonnes.

        # --- 2. SÉLECTION ET RENOMMAGE ---
        colonnes_a_garder = {
            'COM': 'code_insee',
            'LIBELLE': 'nom_commune',
            'DEP': 'code_departement',
            'REG': 'code_region'
        }
        
        cols_presentes = [col for col in colonnes_a_garder.keys() if col in df.columns]
        df = df[cols_presentes].rename(columns=colonnes_a_garder)

        # ⚠️ GESTION DES CASES VIDES : On remplace les cases vides (NaN) par du texte vide
        # Comme ça, la ligne n'est pas supprimée et le nom de la ville est sauvé !
        df = df.fillna("")

        # --- 3. FORMATAGE ---
        print("⚙️ Formatage des codes INSEE...")
        if 'code_insee' in df.columns:
            df['code_insee'] = df['code_insee'].str.zfill(5)
            
        if 'nom_commune' in df.columns:
            df['nom_commune'] = df['nom_commune'].str.strip()

        # --- 4. EXPORT ---
        chemin_sortie = DIR_FILTERED / "MASTER_communes_france.csv"
        df.to_csv(chemin_sortie, sep=";", index=False, encoding="utf-8-sig")
        
        print(f"✅ SUCCÈS TOTAL : Dictionnaire Master généré AVEC les communes déléguées ! ({len(df):,} communes prêtes)")
        print(f"📂 Fichier disponible ici : {chemin_sortie}")

    except Exception as e:
        print(f"❌ Une erreur a interrompu le script : {e}")

if __name__ == "__main__":
    run_etl()