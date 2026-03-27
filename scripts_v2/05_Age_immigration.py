import pandas as pd
import numpy as np
import unicodedata
from pathlib import Path

# ==========================================
# 1. PARAMETRES
# ==========================================
BASE_DIR = Path(".")
FILE_DATA = BASE_DIR / "data_raw/2022_raw/5. Age_immigration/TD_NAT1_2022.xlsx"

# ==========================================
# 2. OUTILS
# ==========================================
def remove_accents(text):
    """Enlève les accents et met en majuscules."""
    if pd.isna(text): return text
    text = str(text)
    clean_text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    return clean_text.strip().upper()

# ==========================================
# 3. TRAITEMENT
# ==========================================
def process_nationalite(year):
    print(f"Traitement Nationalite {year}...")

    # 3.1 Lecture du fichier (titres ligne 11 donc skiprows=10, onglet 'COM')
    df = pd.read_excel(FILE_DATA, sheet_name='COM', skiprows=10)

    # Nettoyage des noms de colonnes (enlève les espaces cachés et sauts de ligne)
    df.columns = df.columns.astype(str).str.strip().str.replace('\n', '')

    # 3.2 SÉLECTION (Suppression des colonnes C à F)
    # On garde A (index 0), B (index 1), et on reprend à G (index 6 et suivants)
    cols_to_keep = [0, 1] + list(range(6, len(df.columns)))
    df = df.iloc[:, cols_to_keep].copy()

    # 3.3 RENOMMAGE ET NETTOYAGE TEXTE
    df = df.rename(columns={df.columns[0]: 'code_insee', df.columns[1]: 'localisation'})
    
    # Enlever les accents des noms de communes
    df['localisation'] = df['localisation'].apply(remove_accents)
    
    df['code_insee'] = df['code_insee'].astype(str).str.zfill(5)
    df['annee'] = str(year)

    # 3.4 CONVERSION ET ARRONDI (NUMPY 2 DÉCIMALES)
    cols_stats = [c for c in df.columns if c.startswith('AGE')]
    
    # On transforme en chiffres, remplace le vide par 0, et force 2 décimales
    df[cols_stats] = df[cols_stats].apply(pd.to_numeric, errors='coerce').fillna(0)
    df[cols_stats] = np.round(df[cols_stats], 2)

    # 3.5 AGRÉGATION (Combinaison Sexe et Nationalité par tranche d'âge)
    try:
        # J'ai ajouté les 0-14 ans (AGE400) pour que ta donnée soit complète
        if 'AGE400_INATC1_SEXE1' in df.columns:
            df['FR_0_14'] = np.round(df['AGE400_INATC1_SEXE1'] + df['AGE400_INATC1_SEXE2'], 2)
            df['ET_0_14'] = np.round(df['AGE400_INATC2_SEXE1'] + df['AGE400_INATC2_SEXE2'], 2)

        # --- 15 à 24 ans ---
        df['FR_15_24'] = np.round(df['AGE415_INATC1_SEXE1'] + df['AGE415_INATC1_SEXE2'], 2)
        df['ET_15_24'] = np.round(df['AGE415_INATC2_SEXE1'] + df['AGE415_INATC2_SEXE2'], 2)

        # --- 25 à 54 ans ---
        df['FR_25_54'] = np.round(df['AGE425_INATC1_SEXE1'] + df['AGE425_INATC1_SEXE2'], 2)
        df['ET_25_54'] = np.round(df['AGE425_INATC2_SEXE1'] + df['AGE425_INATC2_SEXE2'], 2)

        # --- 55 ans ou plus ---
        df['FR_55_PLUS'] = np.round(df['AGE455_INATC1_SEXE1'] + df['AGE455_INATC1_SEXE2'], 2)
        df['ET_55_PLUS'] = np.round(df['AGE455_INATC2_SEXE1'] + df['AGE455_INATC2_SEXE2'], 2)
    except KeyError as e:
        print(f"Erreur : La colonne {e} est introuvable.")
        return

    # 3.6 SELECTION FINALE
    # On rassemble nos nouvelles colonnes propres
    colonnes_creees = [c for c in ['FR_0_14', 'ET_0_14', 'FR_15_24', 'ET_15_24', 'FR_25_54', 'ET_25_54', 'FR_55_PLUS', 'ET_55_PLUS'] if c in df.columns]
    
    colonnes_finales = ['code_insee', 'localisation', 'annee'] + colonnes_creees
    df_final = df[colonnes_finales]

    # 3.7 SAUVEGARDE
    dossier_sortie = BASE_DIR / "data_filtered" / str(year)
    dossier_sortie.mkdir(parents=True, exist_ok=True)
    fichier_sortie = dossier_sortie / f"CLEAN_5_Nationalite_{year}.csv"
    
    df_final.to_csv(fichier_sortie, sep=";", index=False, encoding="utf-8-sig", decimal=".")
    print(f"Succès ! Fichier créé : {fichier_sortie.name} ({len(df_final)} communes)")

if __name__ == "__main__":
    if FILE_DATA.exists():
        process_nationalite(2022)
    else:
        print(f"Fichier introuvable : {FILE_DATA}")