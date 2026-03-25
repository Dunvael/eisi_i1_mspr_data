import pandas as pd
from pathlib import Path
import unicodedata
import sys

# ==============================================================================
# 1. CONFIGURATION DU PIPELINE
# ==============================================================================
BASE_DIR = Path(".")

# Fichier source brut
RAW_PATH = BASE_DIR / "data_raw" / "2022_raw" / "2. Densite population"
FILE_DATA = RAW_PATH / "communes-france-2022.csv" 

# Dossier d'export propre
DIR_2022 = BASE_DIR / "data_filtered" / "2022"
DIR_2022.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# 2. RÈGLES MÉTIER (NETTOYAGE TEXTE)
# ==============================================================================
def clean_texte_complet(texte):
    """Supprime les accents et met une majuscule à chaque mot."""
    if pd.isna(texte): return texte
    # Retrait des accents
    texte_propre = ''.join(c for c in unicodedata.normalize('NFD', str(texte)) if unicodedata.category(c) != 'Mn')
    return texte_propre.strip().title()

def clean_majuscule_seule(texte):
    """Met une majuscule à chaque mot sans toucher aux accents (pour la localisation)."""
    if pd.isna(texte): return texte
    return str(texte).strip().title()

# ==============================================================================
# 3. MOTEUR DE TRAITEMENT (ETL)
# ==============================================================================
def run_etl():
    print("🚀 DÉMARRAGE : Nettoyage Industriel de la Densité de Population...")
    
    if not FILE_DATA.exists():
        print(f"❌ ERREUR CRITIQUE : Le fichier source est introuvable.")
        print(f"   Vérifie le chemin : {FILE_DATA}")
        sys.exit(1)

    try:
        # --- LECTURE ---
        df = pd.read_csv(FILE_DATA, sep=None, engine='python', encoding='utf-8')
        print(f"📊 Données brutes chargées : {len(df)} lignes trouvées.")

        # --- SÉLECTION ET RENOMMAGE ---
        colonnes_map = {
            'nom_sans_accent': 'localisation', 
            'reg_nom': 'region', 
            'dep_nom': 'departement',
            'population': 'nb_pers', 
            'superficie_km2': 'superficie_km2',
            'densite': 'densite', 
            'grille_densite': 'type_densite'
        }
        
        # On sécurise : on ne garde que les colonnes qui existent vraiment
        cols_presentes = [col for col in colonnes_map.keys() if col in df.columns]
        df = df[cols_presentes].rename(columns=colonnes_map)

        # --- TRANSFORMATIONS ---
        print("⚙️ Application des règles de nettoyage...")

        if 'localisation' in df.columns:
            df['localisation'] = df['localisation'].apply(clean_majuscule_seule)
            
        if 'region' in df.columns:
            df['region'] = df['region'].apply(clean_texte_complet)
            
        if 'departement' in df.columns:
            df['departement'] = df['departement'].apply(clean_texte_complet)
            
        if 'type_densite' in df.columns:
            df['type_densite'] = df['type_densite'].fillna(0).replace('', 0)
            
        if 'nb_pers' in df.columns:
            df['nb_pers'] = pd.to_numeric(df['nb_pers'], errors='coerce').fillna(0).astype(int)

        # ⚠️ LE SECRET DE LA DENSITÉ : On garde les décimales (Float)
        if 'densite' in df.columns:
            # On remplace les éventuelles virgules par des points pour que Python calcule bien
            df['densite'] = df['densite'].astype(str).str.replace(',', '.')
            # On convertit en nombre à virgule (Float), SANS ARRRONDIR
            df['densite'] = pd.to_numeric(df['densite'], errors='coerce').fillna(0.0)

        # --- EXPORT ---
        chemin_sortie = DIR_2022 / "CLEAN_2_Densite_population_2022.csv"
        
        # ⚠️ L'ASTUCE PRO : decimal="," force l'export avec de vraies virgules pour Excel
        df.to_csv(chemin_sortie, sep=";", decimal=",", index=False, encoding="utf-8-sig")
        
        print(f"✅ SUCCÈS TOTAL : Fichier nettoyé généré ! ({len(df)} lignes)")
        print(f"📂 Emplacement : {chemin_sortie}")

    except Exception as e:
        print(f"❌ Une erreur a interrompu le script : {e}")

if __name__ == "__main__":
    run_etl()