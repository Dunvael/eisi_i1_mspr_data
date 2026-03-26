import pandas as pd
from pathlib import Path
import unicodedata
import numpy as np

# ==========================================
# 1. PARAMETRES
# ==========================================
BASE_DIR = Path(".")
FILE_DATA = BASE_DIR / "data_raw/2022_raw/4. Age_activite/base-cc-evol-struct-pop-2022.xlsx"

# ==========================================
# 2. OUTILS DE NETTOYAGE
# ==========================================
def remove_accents(text):
    """Enleve les accents et met en majuscules."""
    if pd.isna(text): return text
    text = str(text)
    clean_text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    return clean_text.strip().upper()

def excel_col_to_idx(col_str):
    """Convertit la lettre de colonne Excel en index."""
    num = 0
    for c in col_str.upper():
        num = num * 26 + (ord(c) - ord('A') + 1)
    return num - 1

def get_col_range(start_col, end_col):
    """Genere une liste d'index entre deux lettres Excel."""
    return list(range(excel_col_to_idx(start_col), excel_col_to_idx(end_col) + 1))

# ==========================================
# 3. TRAITEMENT DES DONNEES
# ==========================================
def process_year(sheet_name, year):
    print(f"Traitement de l'annee {year}...")
    
    # 3.1 Lecture du fichier
    df = pd.read_excel(FILE_DATA, sheet_name=sheet_name, skiprows=5)

    # 3.2 Selection des colonnes cibles
    idx_base = [excel_col_to_idx('A'), excel_col_to_idx('D')]
    idx_age = get_col_range('G', 'L')
    idx_sec_1524 = get_col_range('CE', 'CL')
    idx_sec_2554 = get_col_range('CN', 'CU')
    idx_sec_55p = get_col_range('CW', 'DD')
    
    colonnes_a_garder = idx_base + idx_age + idx_sec_1524 + idx_sec_2554 + idx_sec_55p
    df = df.iloc[:, colonnes_a_garder].copy()

   
    col_code = df.columns[0]
    col_lib = df.columns[1]
    df = df.rename(columns={col_lib: 'localisation', col_code: 'code_insee'})
    
    # 3.4 Nettoyage du texte et des codes
    df['localisation'] = df['localisation'].apply(remove_accents)
    df['code_insee'] = df['code_insee'].astype(str).str.zfill(5)
    df['annee'] = str(year)


    # 3.7 Selection finale et sauvegarde
    colonnes_finales = ['code_insee', 'localisation', 'annee'] 
    df_final = df[colonnes_finales]


    colonnes_statiques = [c for c in df.columns if c not in ['code_insee', 'localisation', 'annee']]
    # df[colonnes_statiques] = df[colonnes_statiques].apply(pd.to_numeric, errors='coerce').fillna(0).round(2)

    df[colonnes_statiques] = df[colonnes_statiques].apply(pd.to_numeric, errors='coerce')
    df[colonnes_statiques] = df[colonnes_statiques].fillna(0)
    df[colonnes_statiques] = np.floor(df[colonnes_statiques]* 100) / 100
    df[colonnes_statiques] = df[colonnes_statiques].replace(0.0, 0)

    colonnes_finales = ['code_insee', 'localisation', 'annee'] + colonnes_statiques
    df_final = df[colonnes_finales]


    dossier_sortie = BASE_DIR / "data_filtered" / str(year)
    dossier_sortie.mkdir(parents=True, exist_ok=True)
    fichier_sortie = dossier_sortie / f"CLEAN_4_Population_Activite_{year}.csv"
    
    df_final.to_csv(fichier_sortie, sep=";", index=False, encoding="utf-8-sig")
    print(f"Termine pour {year}. Fichier cree : {fichier_sortie.name}")

# ==========================================
# 4. LANCEMENT
# ==========================================
if __name__ == "__main__":
    if FILE_DATA.exists():
        process_year('COM_2022', 2022)
        process_year('COM_2016', 2016)
        print("Script d'extraction termine avec succes.")
    else:
        print(f"Erreur : Le fichier {FILE_DATA} est introuvable.")