import pandas as pd
from pathlib import Path
import unicodedata

BASE_DIR = Path(".")
FILE_DATA = BASE_DIR / "data_raw/2022_raw/5. Age_immigration/TD_NAT1_2022.xlsx"
FILE_REFERENTIEL = BASE_DIR / "data_raw/referentiel_communes.csv"

def process_nationalite(sheet_name, year):
    print(f"Traitement Nationalite {year}...")

    # 3.1 Lecture du fichier (on saute les 5 lignes d'en-tête)
    df = pd.read_excel(FILE_DATA, sheet_name=0, skiprows=10)

    # 3.2 On garde CODGEO (A), LIBGEO (D) et toutes les stats à partir de G (index 6)
    # On supprime REG, DEP, etc. (colonnes C à F)
    cols_base = [0, 3] # Index de CODGEO et LIBGEO
    cols_stats_idx = list(range(6, len(df.columns)))
    df = df.iloc[:, cols_base + cols_stats_idx].copy()
    df = df.rename(columns={df.columns[0]: 'code_insee', df.columns[1]: 'localisation'})
    
    df['code_insee'] = df['code_insee'].astype(str).str.zfill(5)
    df['annee'] = str(year)



    if FILE_REFERENTIEL.exists():
        # On charge le fichier qui contient les noms parfaits
        df_ref = pd.read_csv(FILE_REFERENTIEL, sep=";", dtype={'code_insee': str})
        
        # On fusionne : on garde tout de l'Insee (left) et on ajoute le nom propre
        df = pd.merge(df, df_ref[['code_insee', 'nom_commune_propre']], on='code_insee', how='left')
        
        # On remplace 'localisation' par le nom propre, sinon on garde l'ancien
        df['localisation'] = df['nom_commune_propre'].fillna(df['localisation'])
    else:
        # Si pas de référentiel, on fait comme avant (nettoyage standard)
        df['localisation'] = df['localisation']



    cols_stats = [c for c in df.columns if c.startswith('AGE')]
    df[cols_stats] = df[cols_stats].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)
    # --- 15 à 24 ans ---
    df['FR_15_24'] = df['AGE415_INATC1_SEXE1'] + df['AGE415_INATC1_SEXE2']
    df['ET_15_24'] = df['AGE415_INATC2_SEXE1'] + df['AGE415_INATC2_SEXE2']

    # --- 25 à 54 ans ---
    df['FR_25_54'] = df['AGE425_INATC1_SEXE1'] + df['AGE425_INATC1_SEXE2']
    df['ET_25_54'] = df['AGE425_INATC2_SEXE1'] + df['AGE425_INATC2_SEXE2']

    # --- 55 ans ou plus ---
    df['FR_55_PLUS'] = df['AGE455_INATC1_SEXE1'] + df['AGE455_INATC1_SEXE2']
    df['ET_55_PLUS'] = df['AGE455_INATC2_SEXE1'] + df['AGE455_INATC2_SEXE2']



    # 3.6 SELECTION DES COLONNES FINALES
    colonnes_finales = [
        'code_insee', 'localisation', 'annee',
        'FR_15_24', 'ET_15_24', 
        'FR_25_54', 'ET_25_54', 
        'FR_55_PLUS', 'ET_55_PLUS'
    ]
    df_final = df[colonnes_finales]



    # 3.7 SAUVEGARDE
    dossier_sortie = BASE_DIR / "data_filtered" / str(year)
    dossier_sortie.mkdir(parents=True, exist_ok=True)
    fichier_sortie = dossier_sortie / f"CLEAN_5_Nationalite_{year}.csv"
    
    df_final.to_csv(fichier_sortie, sep=";", index=False, encoding="utf-8-sig")
    print(f"Extraction réussie : {len(df_final)} lignes traitées.")


if __name__ == "__main__":
    if FILE_DATA.exists():
        process_nationalite('COM_2022', 2022)
    else:
        print(f"Erreur : Le fichier est introuvable à l'adresse {FILE_DATA}")