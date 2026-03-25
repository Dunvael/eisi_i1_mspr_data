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

# Chemin du référentiel régional (Script 00)
REF_PATH = BASE_DIR / "data_filtered" / "liste_codes_communes_region.csv"

# Chemins de sortie
DIR_2022 = BASE_DIR / "data_filtered" / "2022"
DIR_HIST = BASE_DIR / "data_filtered" / "2017"

DIR_2022.mkdir(parents=True, exist_ok=True)
DIR_HIST.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# 2. CHARGEMENT DES DICTIONNAIRES DE LIAISON (LE SECRET DU SCRIPT)
# ==============================================================================
def load_resources():
    print("⏳ Chargement des dictionnaires de liaison...")
    
    # 1. Dictionnaire des Diplômes (Depuis le metadata)
    try:
        df_meta = pd.read_csv(FILE_META, sep=";")
        # On ne garde que les lignes qui concernent la variable EDUC (Diplômes)
        df_educ = df_meta[df_meta['COD_VAR'] == 'EDUC']
        # On fait le lien : Code (ex: 300_RP) -> Libellé (ex: CAP, BEP...)
        dict_diplomes = dict(zip(df_educ['COD_MOD'], df_educ['LIB_MOD']))
        
        # On récupère aussi les noms de villes de l'INSEE au cas où
        df_geo = df_meta[df_meta['COD_VAR'] == 'GEO']
        dict_villes_insee = dict(zip(df_geo['COD_MOD'], df_geo['LIB_MOD']))
    except Exception as e:
        print(f"⚠️ Erreur de lecture des métadonnées : {e}")
        dict_diplomes = {}
        dict_villes_insee = {}

    # 2. Dictionnaire des Communes (Depuis ton référentiel)
    try:
        # engine='python' permet d'éviter les soucis de séparateurs (, ou ;)
        df_ref = pd.read_csv(REF_PATH, sep=None, engine='python')
        col_code = df_ref.columns[0]
        df_ref[col_code] = df_ref[col_code].astype(str).str.zfill(5)
        
        valid_codes = set(df_ref[col_code])
        
        # Si ton fichier de référence a une 2ème colonne (le nom de la ville), on l'utilise !
        dict_communes = {}
        if len(df_ref.columns) > 1:
            col_nom = df_ref.columns[1]
            dict_communes = dict(zip(df_ref[col_code], df_ref[col_nom]))
            
        # On fusionne avec les noms officiels de l'INSEE si besoin
        for code in valid_codes:
            if code not in dict_communes or pd.isna(dict_communes[code]):
                dict_communes[code] = dict_villes_insee.get(code, f"Commune ({code})")
                
    except Exception as e:
        print(f"❌ ERREUR CRITIQUE : Impossible de lire {REF_PATH}")
        sys.exit(1)
        
    return dict_diplomes, dict_communes, valid_codes


# ==============================================================================
# 3. PIPELINE DE TRAITEMENT DES DONNÉES
# ==============================================================================
def run_etl():
    print("🚀 DÉMARRAGE : Nettoyage et liaison des données...")
    
    dict_diplomes, dict_communes, communes_valides = load_resources()
    all_chunks = []
    
    reader = pd.read_csv(FILE_DATA, sep=";", chunksize=100000, low_memory=False)
    
    for chunk in reader:
        # --- 1. Renommage des colonnes ---
        cols = {'EDUC': 'diplome', 'GEO': 'localisation', 'SEX': 'sexe', 'TIME_PERIOD': 'annee', 'OBS_VALUE': 'nb_pers'}
        chunk = chunk[list(cols.keys())].rename(columns=cols)

        # --- 2. Filtrage Temporel (22, 17, 16) ---
        chunk = chunk[chunk['annee'].astype(str).isin(['2022', '2017', '2016'])]
        if chunk.empty: continue

        # --- 3. Filtrage par code INSEE (Région) ---
        chunk['localisation'] = chunk['localisation'].astype(str)
        chunk = chunk[chunk['localisation'].isin(communes_valides)]
        if chunk.empty: continue

        # --- 4. NETTOYAGE ET LIAISONS ---
        
        # A. Diplômes : Suppression définitive de la ligne Total "_T"
        chunk = chunk[chunk['diplome'] != '_T']
        
        # B. Sexe : On remplace le _T par un T propre
        chunk['sexe'] = chunk['sexe'].str.replace('_T', 'T').str.strip()
        
        # C. LIAISON 1 : Remplacement du code INSEE par le NOM de la ville
        chunk['localisation'] = chunk['localisation'].map(dict_communes).fillna(chunk['localisation'])
        
        # D. LIAISON 2 : Remplacement du code Diplôme par le texte descriptif
        if dict_diplomes:
            chunk['diplome'] = chunk['diplome'].map(dict_diplomes).fillna(chunk['diplome'])
        
        # E. Nombres : Entiers stricts
        chunk['nb_pers'] = pd.to_numeric(chunk['nb_pers'], errors='coerce').fillna(0).astype(int)

        all_chunks.append(chunk)

    if not all_chunks:
        print("⚠️ Terminé : Aucune donnée trouvée.")
        return

    # --- 5. Logique de Fallback (2017 sinon 2016) ---
    print(f"⏳ Application du tri et des doublons historiques...")
    df_global = pd.concat(all_chunks, ignore_index=True)
    
    df_2022 = df_global[df_global['annee'].astype(str) == '2022']
    
    df_hist = df_global[df_global['annee'].astype(str).isin(['2017', '2016'])].copy()
    df_hist = df_hist.sort_values(by='annee', ascending=False)
    df_hist = df_hist.drop_duplicates(subset=['localisation', 'diplome', 'sexe'], keep='first')

    # --- 6. Sauvegarde ---
    if not df_2022.empty:
        df_2022.to_csv(DIR_2022 / "CLEAN_1_Niveaux_etudes_2022.csv", sep=";", index=False, encoding="utf-8-sig")
        print(f"✅ Fichier 2022 sauvegardé ({len(df_2022)} lignes).")
    
    if not df_hist.empty:
        df_hist.to_csv(DIR_HIST / "CLEAN_1_Niveaux_etudes_2017.csv", sep=";", index=False, encoding="utf-8-sig")
        print(f"✅ Fichier Historique sauvegardé ({len(df_hist)} lignes).")

if __name__ == "__main__":
    run_etl()