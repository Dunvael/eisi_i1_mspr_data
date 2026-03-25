import pandas as pd
from pathlib import Path
import sys

# ==============================================================================
# 1. CONFIGURATION DU PROJET
# ==============================================================================
BASE_DIR = Path(".")

# Chemins d'entrée
RAW_PATH = BASE_DIR / "data_raw" / "2022_raw" / "1. Niveaux etudes"
FILE_DATA = RAW_PATH / "DS_RP_DIPLOMES_PRINC_2022_data.csv"
FILE_META = RAW_PATH / "DS_RP_DIPLOMES_PRINC_2022_metadata.csv"

# ⚠️ Chemin du référentiel Master
REF_PATH = BASE_DIR / "data_filtered" / "communes_france.csv"

# Chemins de sortie
DIR_2022 = BASE_DIR / "data_filtered" / "2022"
DIR_HIST = BASE_DIR / "data_filtered" / "2017"

DIR_2022.mkdir(parents=True, exist_ok=True)
DIR_HIST.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# 2. CHARGEMENT DES DICTIONNAIRES DE LIAISON
# ==============================================================================
def load_resources():
    print("⏳ Chargement des dictionnaires de liaison...")
    
    # 1. Dictionnaire des Diplômes (Depuis le metadata)
    try:
        df_meta = pd.read_csv(FILE_META, sep=";")
        df_educ = df_meta[df_meta['COD_VAR'] == 'EDUC']
        dict_diplomes = dict(zip(df_educ['COD_MOD'], df_educ['LIB_MOD']))
    except Exception as e:
        print(f"⚠️ Erreur de lecture des métadonnées (Diplômes) : {e}")
        dict_diplomes = {}

    # 2. Dictionnaire des Communes (Depuis le MASTER)
    try:
        print("⏳ Lecture du Dictionnaire Master des communes...")
        df_ref = pd.read_csv(REF_PATH, sep=";", dtype=str, encoding='utf-8')
        
        # Le Master a les colonnes : code_insee, nom_commune
        dict_communes = dict(zip(df_ref['code_insee'].str.zfill(5), df_ref['nom_commune']))
        
        # La liste des codes valides
        valid_codes = set(df_ref['code_insee'].str.zfill(5))
        
    except Exception as e:
        print(f"❌ ERREUR CRITIQUE : Impossible de lire {REF_PATH}")
        print("💡 As-tu bien lancé 'python scripts_v2/00_clean_master_communes.py' en premier ?")
        sys.exit(1)
        
    return dict_diplomes, dict_communes, valid_codes


# ==============================================================================
# 3. PIPELINE DE TRAITEMENT DES DONNÉES
# ==============================================================================
def run_etl():
    print("🚀 DÉMARRAGE : Nettoyage et liaison des données (Dossier 1)...")
    
    if not FILE_DATA.exists():
        print(f"❌ ERREUR : Le fichier {FILE_DATA.name} est introuvable.")
        sys.exit(1)

    dict_diplomes, dict_communes, communes_valides = load_resources()
    all_chunks = []
    
    # On lit le gros fichier par morceaux (chunks)
    reader = pd.read_csv(FILE_DATA, sep=";", chunksize=100000, low_memory=False)
    
    for chunk in reader:
        # --- 1. Renommage des colonnes ---
        cols = {'EDUC': 'diplome', 'GEO': 'localisation', 'SEX': 'sexe', 'TIME_PERIOD': 'annee', 'OBS_VALUE': 'nb_pers'}
        cols_presentes = {k: v for k, v in cols.items() if k in chunk.columns}
        chunk = chunk[list(cols_presentes.keys())].rename(columns=cols_presentes)

        # --- 2. Filtrage Temporel (22, 17, 16) ---
        # ⚠️ NOUVEAU : On garde aussi 2016 pour notre logique de fallback
        if 'annee' in chunk.columns:
            chunk = chunk[chunk['annee'].astype(str).isin(['2022', '2017', '2016'])]
            if chunk.empty: continue

        # --- 3. Filtrage par code INSEE (Grâce au Master) ---
        if 'localisation' in chunk.columns:
            chunk['localisation'] = chunk['localisation'].astype(str).str.zfill(5)
            chunk = chunk[chunk['localisation'].isin(communes_valides)]
            if chunk.empty: continue

        # --- 4. NETTOYAGE ET LIAISONS ---
        if 'diplome' in chunk.columns:
            chunk = chunk[chunk['diplome'] != '_T']
        
        if 'sexe' in chunk.columns:
            chunk['sexe'] = chunk['sexe'].str.replace('_T', 'T').str.strip()
        
        if 'localisation' in chunk.columns and dict_communes:
            chunk['localisation'] = chunk['localisation'].map(dict_communes).fillna(chunk['localisation'])
            chunk['localisation'] = chunk['localisation'].str.title()
        
        if 'diplome' in chunk.columns and dict_diplomes:
            chunk['diplome'] = chunk['diplome'].map(dict_diplomes).fillna(chunk['diplome'])
        
        if 'nb_pers' in chunk.columns:
            chunk['nb_pers'] = pd.to_numeric(chunk['nb_pers'], errors='coerce').fillna(0).astype(int)

        all_chunks.append(chunk)

    if not all_chunks:
        print("⚠️ Terminé : Aucune donnée trouvée après filtrage.")
        return

    # --- 5. LOGIQUE EXPERTE : Fallback 2017 sinon 2016 ---
    print(f"⏳ Application de la logique historique (2017 en priorité, sinon 2016)...")
    df_global = pd.concat(all_chunks, ignore_index=True)
    
    # Séparation 2022
    df_2022 = df_global[df_global['annee'].astype(str) == '2022']
    
    # Isolation de l'historique (2016 et 2017)
    df_hist = df_global[df_global['annee'].astype(str).isin(['2017', '2016'])].copy()
    
    # L'Astuce : On trie par année décroissante (2017 en premier). 
    # S'il y a un doublon (une ville a été recensée en 2016 ET 2017), on supprime la ligne de 2016 (keep='first')
    df_hist = df_hist.sort_values(by='annee', ascending=False)
    df_hist = df_hist.drop_duplicates(subset=['localisation', 'diplome', 'sexe'], keep='first')

    # --- 6. Sauvegarde ---
    if not df_2022.empty:
        chemin_2022 = DIR_2022 / "CLEAN_1_Niveaux_etudes_2022.csv"
        df_2022.to_csv(chemin_2022, sep=";", index=False, encoding="utf-8-sig")
        print(f"✅ Fichier 2022 sauvegardé ({len(df_2022):,} lignes).")
    
    if not df_hist.empty:
        # On l'appelle "_2017.csv" pour le Dashboard, même s'il contient un peu de 2016
        chemin_hist = DIR_HIST / "CLEAN_1_Niveaux_etudes_2017.csv"
        df_hist.to_csv(chemin_hist, sep=";", index=False, encoding="utf-8-sig")
        print(f"✅ Fichier Historique sauvegardé avec logique de fallback ({len(df_hist):,} lignes).")

if __name__ == "__main__":
    run_etl()