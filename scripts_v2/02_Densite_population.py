import pandas as pd
from pathlib import Path
import unicodedata
import sys

# ==============================================================================
# 1. CONFIGURATION DU PIPELINE
# ==============================================================================
BASE_DIR = Path(".")

RAW_PATH = BASE_DIR / "data_raw" / "2022_raw" / "2. Densite population"
FILE_DATA = RAW_PATH / "communes-france-2022.csv" 
FILE_MASTER = BASE_DIR / "data_filtered" / "communes_france.csv"

DIR_2022 = BASE_DIR / "data_filtered" / "2022"
DIR_2022.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# 2. OUTILS DE NETTOYAGE
# ==============================================================================
def clean_texte_complet(texte):
    if pd.isna(texte): return texte
    texte_propre = ''.join(c for c in unicodedata.normalize('NFD', str(texte)) if unicodedata.category(c) != 'Mn')
    return texte_propre.strip().title()

# ==============================================================================
# 3. MOTEUR DE TRAITEMENT (ETL)
# ==============================================================================
def run_etl():
    print("🚀 DÉMARRAGE : Nettoyage Densité (Toute la France)...")
    
    if not FILE_DATA.exists():
        print(f"❌ ERREUR : Fichier source introuvable ({FILE_DATA})")
        sys.exit(1)

    # --- CHARGEMENT DU DICTIONNAIRE ---
    dict_communes = {}
    if FILE_MASTER.exists():
        df_master = pd.read_csv(FILE_MASTER, sep=";", dtype=str, encoding='utf-8')
        dict_communes = dict(zip(df_master['code_insee'].str.zfill(5), df_master['nom_commune']))
        print(f"✅ Dictionnaire chargé avec {len(dict_communes):,} villes prêtes pour la traduction.")
    else:
        print("❌ ALERTE : Fichier Master introuvable. Les codes INSEE ne pourront pas être traduits !")

    try:
        print("⏳ Lecture des données de densité...")
        df = pd.read_csv(FILE_DATA, sep=None, engine='python', encoding='utf-8', dtype=str)

        # On cherche la colonne qui contient le code INSEE
        col_insee = next((col for col in ['code_commune_INSEE', 'code_insee', 'insee', 'COM'] if col in df.columns), None)

        # --- SÉLECTION ET RENOMMAGE ---
        colonnes_map = {
            'reg_nom': 'region', 
            'dep_nom': 'departement',
            'population': 'nb_pers', 
            'superficie_km2': 'superficie_km2',
            'densite': 'densite', 
            'grille_densite': 'type_densite'
        }
        
        # On renomme directement le code en 'localisation'
        if col_insee: 
            colonnes_map[col_insee] = 'localisation'
        
        cols_presentes = [col for col in colonnes_map.keys() if col in df.columns]
        df = df[cols_presentes].rename(columns=colonnes_map)

        # --- TRANSFORMATIONS ---
        print("⚙️ Application des règles de nettoyage et TRADUCTION des villes...")

        # ⚠️ LA TRADUCTION INFAILLIBLE :
        if 'localisation' in df.columns:
            # 1. On s'assure que le code est propre (ex: "01001")
            df['localisation'] = df['localisation'].astype(str).str.strip().str.zfill(5)
            
            # 2. On le traduit avec le dictionnaire
            if dict_communes:
                df['localisation'] = df['localisation'].map(dict_communes).fillna(df['localisation'])
            
            # 3. On met de belles majuscules
            df['localisation'] = df['localisation'].str.title()
            
        if 'region' in df.columns: df['region'] = df['region'].apply(clean_texte_complet)
        if 'departement' in df.columns: df['departement'] = df['departement'].apply(clean_texte_complet)

        if 'type_densite' in df.columns: df['type_densite'] = df['type_densite'].fillna("0").replace('', "0")
        if 'nb_pers' in df.columns: df['nb_pers'] = pd.to_numeric(df['nb_pers'], errors='coerce').fillna(0).astype(int)
        
        if 'densite' in df.columns:
            df['densite'] = df['densite'].astype(str).str.replace(',', '.')
            df['densite'] = pd.to_numeric(df['densite'], errors='coerce').fillna(0.0)
            
        if 'superficie_km2' in df.columns:
            df['superficie_km2'] = df['superficie_km2'].astype(str).str.replace(',', '.')
            df['superficie_km2'] = pd.to_numeric(df['superficie_km2'], errors='coerce').fillna(0.0)

        # --- EXPORT ---
        chemin_sortie = DIR_2022 / "CLEAN_2_Densite_population_2022.csv"
        df.to_csv(chemin_sortie, sep=";", index=False, encoding="utf-8-sig")
        
        print(f"✅ SUCCÈS TOTAL : Fichier généré avec les VRAIS NOMS de villes ! ({len(df):,} communes)")

    except Exception as e:
        print(f"❌ Une erreur a interrompu le script : {e}")

if __name__ == "__main__":
    run_etl()