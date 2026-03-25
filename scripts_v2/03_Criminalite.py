import pandas as pd
from pathlib import Path
import sys

# ==============================================================================
# 1. CONFIGURATION DU PIPELINE
# ==============================================================================
BASE_DIR = Path(".")

# ⚠️ Fichiers sources : La Criminalité + notre Master !
FILE_DELINQUANCE  = BASE_DIR / "data_raw" / "2022_raw" / "3. Criminalite" / "donne_criminalite.csv"
FILE_MASTER       = BASE_DIR / "data_filtered" / "communes_france.csv"

# Dossier d'export
DIR_2022 = BASE_DIR / "data_filtered" / "2022"
DIR_2022.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# 2. CHARGEMENT DU DICTIONNAIRE UNIQUE (MASTER)
# ==============================================================================
def charger_dictionnaire_master():
    """Charge le Fichier Master pour traduire tous les codes INSEE de France."""
    print("⏳ Création du dictionnaire des villes depuis le Master...")
    if not FILE_MASTER.exists():
        print(f"⚠️ Fichier Master introuvable ({FILE_MASTER}). Les codes ne seront pas traduits.")
        return {}
    try:
        # On lit notre fichier Master propre
        df_master = pd.read_csv(FILE_MASTER, sep=";", dtype=str, encoding='utf-8')
        # Dictionnaire : code_insee (5 chiffres) -> nom_commune
        return dict(zip(df_master['code_insee'].str.zfill(5), df_master['nom_commune']))
    except Exception as e:
        print(f"⚠️ Erreur lors de la lecture du Master : {e}")
        return {}

# ==============================================================================
# 3. MOTEUR DE TRAITEMENT (ETL)
# ==============================================================================
def run_etl():
    print("🚀 DÉMARRAGE : Nettoyage de la Criminalité (Toute la France + 2017/2022)...")
    
    if not FILE_DELINQUANCE.exists():
        print(f"❌ ERREUR : Fichier introuvable ({FILE_DELINQUANCE}).")
        sys.exit(1)

    # Chargement de notre dictionnaire global
    dict_communes = charger_dictionnaire_master()

    try:
        # --- LECTURE ---
        print("⏳ Chargement du fichier de délinquance...")
        df = pd.read_csv(FILE_DELINQUANCE, sep=";", dtype={'CODGEO_2025': str}, encoding='utf-8')
        print(f"📊 Données chargées : {len(df):,} lignes brutes.")

        # --- SÉLECTION ET RENOMMAGE ---
        colonnes_cibles = {
            'CODGEO_2025': 'localisation', 
            'annee': 'annee', 
            'indicateur': 'indicateur', 
            'est_diffuse': 'est_diffuse',
            'nombre': 'nb_faits'
        }
        cols_presentes = [col for col in colonnes_cibles.keys() if col in df.columns]
        df = df[cols_presentes].rename(columns=colonnes_cibles)

        # --- NETTOYAGE & TRADUCTION ---
        # --- NETTOYAGE & TRADUCTION ---
        print("⚙️ Application des filtres et du nettoyage...")

        # 1. Traduction des codes en noms de communes avec le MASTER
        if 'localisation' in df.columns:
            # On s'assure d'avoir le bon format de code
            df['localisation'] = df['localisation'].str.zfill(5)
            
            if dict_communes:
                # ⚠️ LA CORRECTION : On traduit, mais on ne fait PAS de fillna()
                df['localisation'] = df['localisation'].map(dict_communes)
                
                # On supprime toutes les lignes où la traduction a échoué (les fameux codes non trouvés)
                df = df.dropna(subset=['localisation'])
                
            # Majuscule propre pour l'affichage
            df['localisation'] = df['localisation'].str.title()

        # 2. Traduction de "diff" et "ndiff"

        # 2. Traduction de "diff" et "ndiff"
        if 'Médiatisation' in df.columns:
            df['Médiatisation'] = df['Médiatisation'].map({'diff': 'Médiatisé', 'ndiff': 'Non médiatisé'}).fillna(df['est_diffuse'])

        # 3. Nettoyage des Nombres
        if 'nb_faits' in df.columns:
            df['nb_faits'] = df['nb_faits'].astype(str).str.replace(',', '.')
            df['nb_faits'] = pd.to_numeric(df['nb_faits'], errors='coerce').fillna(0).astype(int)

        # 4. Filtrage sur 2017 et 2022 UNIQUEMENT
        if 'annee' in df.columns:
            df['annee'] = df['annee'].astype(str).str.replace(r'\.0$', '', regex=True)
            df = df[df['annee'].isin(['2017', '2022'])]

        # --- EXPORT ---
        chemin_sortie = DIR_2022 / "CLEAN_3_Criminalite_2016_2024.csv"
        df.to_csv(chemin_sortie, sep=";", index=False, encoding="utf-8-sig")
        
        print(f"✅ SUCCÈS TOTAL : Fichier nettoyé pour la France entière (2017/2022) ! ({len(df):,} lignes au final)")
        print(f"📂 Emplacement : {chemin_sortie}")

    except Exception as e:
        print(f"❌ Une erreur a interrompu le script : {e}")

if __name__ == "__main__":
    run_etl()