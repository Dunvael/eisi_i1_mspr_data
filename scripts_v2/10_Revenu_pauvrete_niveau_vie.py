import pandas as pd
import numpy as np
from pathlib import Path
import unicodedata

BASE_DIR = Path(".")
FILE_DATA = BASE_DIR / "data_raw/2022_raw/10. 2021_Revenu_pauvrete_niveau_vie/revenu.csv"
FILE_COMMUNES = BASE_DIR / "data_filtered/communes_france.csv"

def remove_accents(text):
    if pd.isna(text): return text
    text = str(text).strip()
    clean_text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    return clean_text.upper()

def process_revenux(year):
    print(f"🚀 Lancement du nettoyage INSEE - Revenu {year} ...")
    
    # 1. Chargement du référentiel
    try: 
        df_ref = pd.read_csv(FILE_COMMUNES, sep=';', dtype=str, encoding='utf-8')
        df_ref = df_ref[['code_insee', 'nom_commune']]
        df_ref['code_insee'] = df_ref['code_insee'].str.zfill(5)
    except Exception as e:    
        print(f"❌ Erreur lecture référentiel : {e}")
        return

    # 2. Mapping INSEE
    mapping = {
        'CODGEO': 'code_insee', 
        'PMIMP21': 'pct_menages_imposes',
        'Q221': 'mediane_niveau_vie',
        'D121' : 'revenu_bas_echelle',
        'D921': 'revenu_haut_echelle',
        'RD': 'rapport_interdecile',
        'PACT21': 'pct_revenus_travail',
        'PPEN21': 'pct_revenus_retraite',
        'PAUT21': 'pct_revenus_patrimoine'
    }

    # 3. Lecture INSEE Intelligente
    try: 
        df_temp = pd.read_csv(FILE_DATA, sep=';', nrows=20, encoding='latin-1', header=None)
        
        header_idx = None
        for i, row in df_temp.iterrows():
            if row.astype(str).str.contains('CODGEO').any():
                header_idx = i
                break
        
        if header_idx is None:
            print("❌ Erreur : Impossible de trouver 'CODGEO' dans les 20 premières lignes.")
            return

        print(f"✅ En-tête trouvé à la ligne {header_idx}")
        df_raw = pd.read_csv(FILE_DATA, sep=';', skiprows=header_idx, dtype=str, encoding='latin-1')
        df_raw.columns = df_raw.columns.str.strip().str.replace('"', '').str.replace("'", "")

        # --- AJOUT CRITIQUE : Application du mapping ---
        cols_presentes = [c for c in mapping.keys() if c in df_raw.columns]
        df_insee = df_raw[cols_presentes].rename(columns=mapping)
        df_insee['code_insee'] = df_insee['code_insee'].str.zfill(5)

    except Exception as e:    
        print(f"❌ Erreur lors de la lecture du fichier CSV : {e}")
        return
    
    # 4. JOINTURE
    print("🔗 Fusion des données avec les noms de communes...")
    df = pd.merge(df_insee, df_ref, on='code_insee', how='left')
    
    df = df.rename(columns={'nom_commune': 'localisation'})
    df = df.drop(columns=['code_insee'])

    # 5. Nettoyage et Conversions
    df['localisation'] = df['localisation'].apply(remove_accents)
    df = df.dropna(subset=['localisation'])
    df.replace(['s', ''], np.nan, inplace=True)

    # Conversion des colonnes numériques
    cols_num = [c for c in df.columns if c != 'localisation']
    for col in cols_num:
        df[col] = df[col].astype(str).str.replace(r'\s+', '', regex=True).str.replace(',', '.')
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Filtre métier
    if 'rapport_interdecile' in df.columns:
        nb_avant = len(df)
        df = df[(df['rapport_interdecile'] < 10) | (df['rapport_interdecile'].isna())]
        print(f"🧹 Filtre Outliers : {nb_avant - len(df)} lignes écartées.")

    # 6. Agrégation finale
    df_final = df.groupby('localisation', as_index=False).mean()
    df_final[cols_num] = np.round(df_final[cols_num], 2)
    df_final['annee'] = year

    # Sortie
    dossier_sortie = BASE_DIR / "data_filtered" / "2022"
    dossier_sortie.mkdir(parents=True, exist_ok=True)
    fichier_sortie = dossier_sortie / f"CLEAN_10_Revenus_{year}.csv"
    df_final.to_csv(fichier_sortie, sep=";", index=False, encoding="utf-8-sig")
    
    print(f"✅ Terminé ! {len(df_final)} communes sauvegardées dans {fichier_sortie.name}")

if __name__ == "__main__":
    process_revenux(2021)