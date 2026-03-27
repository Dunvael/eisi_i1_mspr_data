import pandas as pd
import numpy as np  # <-- Ajout de la bibliothèque Numpy
from pathlib import Path

# ==========================================
# 1. PARAMETRES
# ==========================================
BASE_DIR = Path(".")
FILE_DATA = BASE_DIR / "data_raw/2022_raw/5. Age_immigration/TD_NAT1_2022.xlsx"
FILE_REFERENTIEL = BASE_DIR / "data_raw/referentiel_communes.csv"

# ==========================================
# 3. TRAITEMENT
# ==========================================
def process_nationalite(year):
    print(f"Traitement Nationalite {year} avec Numpy...")

    # 3.1 Lecture du fichier (onglet 'COM', titres ligne 11 donc skiprows=10)
    df = pd.read_excel(FILE_DATA, sheet_name='COM', skiprows=10)

    # Nettoyage immédiat des noms de colonnes (enlève les espaces et sauts de ligne)
    df.columns = df.columns.astype(str).str.strip().str.replace('\n', '')

    # 3.2 Sélection et renommage
    df = df.rename(columns={df.columns[0]: 'code_insee', df.columns[1]: 'localisation'})
    
    df['code_insee'] = df['code_insee'].astype(str).str.zfill(5)
    df['annee'] = str(year)

    # 3.3 JOINTURE RÉFÉRENTIEL (Pour les accents)
    if FILE_REFERENTIEL.exists():
        df_ref = pd.read_csv(FILE_REFERENTIEL, sep=";", dtype={'code_insee': str})
        df = pd.merge(df, df_ref[['code_insee', 'nom_commune_propre']], on='code_insee', how='left')
        df['localisation'] = df['nom_commune_propre'].fillna(df['localisation'])

    # 3.4 CONVERSION NUMÉRIQUE ET ARRONDI NUMPY
    cols_stats = [c for c in df.columns if c.startswith('AGE')]
    
    # Étape A : On transforme le texte en vrai nombre, on remplace le vide par 0
    df[cols_stats] = df[cols_stats].apply(pd.to_numeric, errors='coerce').fillna(0)
    
    # Étape B : On utilise Numpy pour forcer 2 décimales sur toutes ces colonnes d'un coup
    df[cols_stats] = np.round(df[cols_stats], 2)

    # 3.5 AGRÉGATION (Calcul des tranches par nationalité)
    try:
        # --- 15 à 24 ans ---
        df['FR_15_24'] = df['AGE415_INATC1_SEXE1'] + df['AGE415_INATC1_SEXE2']
        df['ET_15_24'] = df['AGE415_INATC2_SEXE1'] + df['AGE415_INATC2_SEXE2']

        # --- 25 à 54 ans ---
        df['FR_25_54'] = df['AGE425_INATC1_SEXE1'] + df['AGE425_INATC1_SEXE2']
        df['ET_25_54'] = df['AGE425_INATC2_SEXE1'] + df['AGE425_INATC2_SEXE2']

        # --- 55 ans ou plus ---
        df['FR_55_PLUS'] = df['AGE455_INATC1_SEXE1'] + df['AGE455_INATC1_SEXE2']
        df['ET_55_PLUS'] = df['AGE455_INATC2_SEXE1'] + df['AGE455_INATC2_SEXE2']
    except KeyError as e:
        print(f"Erreur : La colonne {e} est introuvable.")
        return

    # 3.6 SELECTION FINALE
    colonnes_finales = [
        'code_insee', 'localisation', 'annee',
        'FR_15_24', 'ET_15_24', 'FR_25_54', 'ET_25_54', 'FR_55_PLUS', 'ET_55_PLUS'
    ]
    df_final = df[colonnes_finales]

    # 3.7 SAUVEGARDE
    dossier_sortie = BASE_DIR / "data_filtered" / str(year)
    dossier_sortie.mkdir(parents=True, exist_ok=True)
    fichier_sortie = dossier_sortie / f"CLEAN_5_Nationalite_{year}.csv"
    
    # Le paramètre decimal="." garantit que les décimales Numpy soient bien lues par ton Dashboard
    df_final.to_csv(fichier_sortie, sep=";", index=False, encoding="utf-8-sig", decimal=".")
    print(f"Succès ! Fichier créé : {fichier_sortie.name} ({len(df_final)} communes)")

if __name__ == "__main__":
    if FILE_DATA.exists():
        process_nationalite(2022)
    else:
        print(f"Fichier introuvable : {FILE_DATA}")