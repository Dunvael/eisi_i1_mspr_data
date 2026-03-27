import pandas as pd
import numpy as np
from pathlib import Path
import unicodedata

# ==========================================
# 1. PARAMETRES
# ==========================================
BASE_DIR = Path(".")
FILE_DATA = BASE_DIR / "data_raw/2022_raw/8. Taux_abstention/resultats-par-niveau-burvot-t1-france-entiere.txt"

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
def process_abstention(year):
    print(f"Traitement Abstention {year} (Format X.XX)...")

    # 3.1 LECTURE
    colonnes_fictives = list(range(105))
    df = pd.read_csv(FILE_DATA, sep=';', encoding='latin-1', header=0, names=colonnes_fictives, low_memory=False)

    # 3.2 SÉLECTION (Commune, Inscrits, Abstentions, Votants)
    df = df[[5, 7, 8, 10]].copy()
    df.columns = ['localisation', 'inscrits', 'abstentions', 'votants']

    # 3.3 NETTOYAGE TEXTE
    df = df.dropna(subset=['localisation'])
    df['localisation'] = df['localisation'].apply(remove_accents)
    df['annee'] = str(year)

    # 3.4 CONVERSION NUMERIQUE (Numpy float)
    cols_num = ['inscrits', 'abstentions', 'votants']
    df[cols_num] = df[cols_num].apply(pd.to_numeric, errors='coerce').fillna(0).astype(float)

    # 3.5 AGRÉGATION PAR COMMUNE
    df_final = df.groupby(['localisation', 'annee'], as_index=False)[cols_num].sum()

    # 3.6 CALCUL DES TAUX (Pour avoir de vraies décimales utiles)
    # Taux d'abstention = (Abstentions / Inscrits) * 100
    df_final['taux_abstention'] = np.where(df_final['inscrits'] > 0, 
                                           (df_final['abstentions'] / df_final['inscrits']) * 100, 0)
    
    # Arrondi Numpy à 2 chiffres
    cols_finales = ['inscrits', 'abstentions', 'votants', 'taux_abstention']
    df_final[cols_finales] = np.round(df_final[cols_finales], 2)

    # 3.7 SAUVEGARDE (decimal="." et format strict)
    dossier_sortie = BASE_DIR / "data_filtered" / str(year)
    dossier_sortie.mkdir(parents=True, exist_ok=True)
    fichier_sortie = dossier_sortie / f"CLEAN_8_Abstention_{year}.csv"
    
    df_final.to_csv(
        fichier_sortie, 
        sep=";", 
        index=False, 
        encoding="utf-8-sig", 
        decimal=".", 
        float_format="%.2f"
    )
    print(f"Terminé ! Fichier : {fichier_sortie.name}")

if __name__ == "__main__":
    if FILE_DATA.exists():
        process_abstention(2022)