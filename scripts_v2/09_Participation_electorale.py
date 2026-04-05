import pandas as pd
import numpy as np
from pathlib import Path
import unicodedata

# ==========================================
# 1. PARAMETRES
# ==========================================
BASE_DIR = Path(".")
# Attention : j'ai gardé le nom de ton fichier avec le (2)
FILE_DATA = BASE_DIR / "data_raw/2022_raw/9. Participation electorale/resultats-par-niveau-burvot-t1-france-entiere(2).txt"

# ==========================================
# 2. OUTILS
# ==========================================
def remove_accents(text):
    if pd.isna(text): return text
    text = str(text)
    clean_text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    return clean_text.strip().upper()

# ==========================================
# 3. TRAITEMENT
# ==========================================
def process_participation(year):
    print(f"⏳ Traitement Participation Electorale {year} (Correction active)...")

    mapping = {
        5: 'localisation',
        9: 'pct_abstentions_inscrits',
        11: 'pct_votants_inscrits',
        14: 'pct_blancs_votants',
        17: 'pct_nuls_votants',
        20: 'pct_exprimes_votants',
        27: 'ARTHAUD', 34: 'ROUSSEL', 41: 'MACRON', 48: 'LASSALLE',
        55: 'LE_PEN', 62: 'ZEMMOUR', 69: 'MELENCHON', 76: 'HIDALGO',
        83: 'JADOT', 90: 'PECRESSE', 97: 'POUTOU', 104: 'DUPONT_AIGNAN'
    }

    try:
        # LECTURE BLINDÉE : On lit tout sans header, puis on découpe.
        raw_df = pd.read_csv(
            FILE_DATA, 
            sep=';', 
            encoding='latin-1', 
            header=None,       # On ignore les en-têtes
            skiprows=1,        # On saute la première ligne contenant les mauvais titres
            low_memory=False
        )
        
        # On extrait uniquement les colonnes dont on a besoin via leurs index
        df = raw_df[list(mapping.keys())].copy()
        
        # On les renomme proprement
        df.columns = [mapping[k] for k in mapping.keys()]
        
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier : {e}")
        return

    # NETTOYAGE TEXTE
    df['localisation'] = df['localisation'].apply(remove_accents)
    df = df.dropna(subset=['localisation'])

    # CONVERSION CHIFFRES
    cols_chiffres = df.columns.drop('localisation')
    for col in cols_chiffres:
        df[col] = df[col].astype(str).str.replace(',', '.')
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # AGRÉGATION
    print("🔄 Regroupement des données par commune...")
    df_final = df.groupby('localisation', as_index=False).mean()

    # CALCUL DES BLOCS
    df_final['Ext_Droite'] = df_final['LE_PEN'] + df_final['ZEMMOUR']
    df_final['Ext_Gauche'] = df_final['LASSALLE'] + df_final['ARTHAUD']
    df_final['Centre'] = df_final['MACRON']
    df_final['Droite'] = df_final['PECRESSE'] + df_final['DUPONT_AIGNAN']
    df_final['Gauche'] = df_final['ROUSSEL'] + df_final['MELENCHON'] + df_final['HIDALGO'] + df_final['JADOT'] + df_final['POUTOU']

    # EXPORT
    colonnes_a_exporter = [
        'localisation', 'pct_votants_inscrits', 'pct_abstentions_inscrits', 
        'pct_blancs_votants', 'pct_nuls_votants', 'pct_exprimes_votants',
        'Ext_Droite', 'Ext_Gauche', 'Centre', 'Droite', 'Gauche'
    ]

    df_export = df_final[colonnes_a_exporter].copy()
    cols_num_export = df_export.columns.drop('localisation')

    df_export[cols_num_export] = np.round(df_export[cols_num_export], 2)
    df_export['annee'] = year

    dossier_sortie = BASE_DIR / "data_filtered" / str(year)
    dossier_sortie.mkdir(parents=True, exist_ok=True)
    fichier_sortie = dossier_sortie / f"CLEAN_9_Participation_Politique_{year}.csv"

    df_export.to_csv(
        fichier_sortie, 
        sep=";", 
        index=False, 
        encoding="utf-8-sig", 
        decimal=".", 
        float_format="%.2f"
    )
    
    print(f"✅ Succès ! Fichier généré avec {len(df_export)} communes uniques.")
    print(f"📁 Sauvegardé ici : {fichier_sortie}")

if __name__ == "__main__":
    process_participation(2022)