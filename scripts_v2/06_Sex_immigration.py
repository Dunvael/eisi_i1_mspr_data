import pandas as pd
import numpy as np
import unicodedata
from pathlib import Path

# ==========================================
# 1. PARAMETRES
# ==========================================
BASE_DIR = Path(".")
FILE_DATA = BASE_DIR / "data_raw/2022_raw/6. Sexe_immigration/TD_NAT2_2022.xlsx"

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
def process_activite_nationalite(year):
    print(f"Traitement Activité & Nationalité {year} avec Numpy...")

    # 3.1 Lecture du fichier (Comme pour NAT1 : onglet COM et ligne 11)
    df = pd.read_excel(FILE_DATA, sheet_name='COM', skiprows=10)

    # Nettoyage des noms de colonnes
    df.columns = df.columns.astype(str).str.strip().str.replace('\n', '')

    # 3.2 SÉLECTION ET RENOMMAGE
    # CODGEO (index 0) et LIBGEO (index 1)
    df = df.rename(columns={df.columns[0]: 'code_insee', df.columns[1]: 'localisation'})
    
    df['localisation'] = df['localisation'].apply(remove_accents)
    df['code_insee'] = df['code_insee'].astype(str).str.zfill(5)
    df['annee'] = str(year)

    # 3.3 CONVERSION ET ARRONDI (NUMPY 2 DÉCIMALES)
    # On cible toutes les colonnes qui contiennent 'INATC' (les stats)
    cols_stats = [c for c in df.columns if 'INATC' in c]
    
    # Conversion en nombres et remplacement des vides par 0
    df[cols_stats] = df[cols_stats].apply(pd.to_numeric, errors='coerce').fillna(0)
    
    # On force les 2 décimales avec Numpy
    df[cols_stats] = np.round(df[cols_stats], 2)

    # 3.4 AGRÉGATION (Nationalité + Activité, on additionne les sexes)
    # Dictionnaires basés sur ton image de mapping
    nationality_map = {'INATC1': 'FR', 'INATC2': 'ET'}
    activity_map = {
        'TACTR11': 'EMPLOI',
        'TACTR12': 'CHOMEUR',
        'TACTR21': 'RETRAITE',
        'TACTR22': 'ETUDIANT',
        'TACTR24': 'AU_FOYER',
        'TACTR26': 'AUTRE_INACTIF'
    }

    colonnes_creees = []

    try:
        # Boucle magique pour créer toutes les colonnes automatiquement
        for nat_code, nat_label in nationality_map.items():
            for act_code, act_label in activity_map.items():
                
                # Noms des colonnes INSEE
                col_hommes = f"{nat_code}_SEXE1_{act_code}"
                col_femmes = f"{nat_code}_SEXE2_{act_code}"
                
                # Nom de notre nouvelle colonne (ex: FR_EMPLOI)
                nouvelle_col = f"{nat_label}_{act_label}"
                
                # Si les colonnes existent bien, on additionne et on garde 2 décimales
                if col_hommes in df.columns and col_femmes in df.columns:
                    df[nouvelle_col] = np.round(df[col_hommes] + df[col_femmes], 2)
                    colonnes_creees.append(nouvelle_col)
                    
    except KeyError as e:
        print(f"Erreur : La colonne {e} est introuvable.")
        return

    # 3.5 SELECTION FINALE
    colonnes_finales = ['code_insee', 'localisation', 'annee'] + colonnes_creees
    df_final = df[colonnes_finales]

    # 3.6 SAUVEGARDE
    dossier_sortie = BASE_DIR / "data_filtered" / str(year)
    dossier_sortie.mkdir(parents=True, exist_ok=True)
    fichier_sortie = dossier_sortie / f"CLEAN_6_Sexe_Nationalite_Activite_{year}.csv"
    
    # On sauvegarde avec le point comme séparateur décimal pour le Dashboard
    df_final.to_csv(fichier_sortie, sep=";", index=False, encoding="utf-8-sig", decimal=".")
    print(f"Succès ! Fichier créé : {fichier_sortie.name} ({len(df_final)} communes)")

if __name__ == "__main__":
    if FILE_DATA.exists():
        process_activite_nationalite(2022)
    else:
        print(f"Fichier introuvable : {FILE_DATA}")