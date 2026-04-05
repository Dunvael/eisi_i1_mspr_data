import pandas as pd
import numpy as np
from pathlib import Path
import unicodedata


BASE_DIR = Path(".")

# Chemin mis à jour en fonction de ta capture d'écran
FILE_DATA = BASE_DIR / "data_raw/2022_raw/10. 2021_Revenu_pauvrete_niveau_vie/BASE_TD_FILO_IRIS_2021_DEC.xlsx"

def remove_accents(text):
    """Enlève les accents et met en majuscules pour correspondre aux autres fichiers."""
    if pd.isna(text): return text
    text = str(text)
    clean_text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    return clean_text.strip().upper()


def process_revenux(year):
    print(f" Lancement du nettoyage INSEE - Revenu {year}   ...")

    yy = str(year)[-2:]  # Extrait les 2 derniers chiffres de l'année

    mapping = {
        'LIBIRIS': 'localisation',
        f'DEC_PIMP{yy}': 'pct_menages_imposes',
        f'DEC_TP60{yy}': 'taux_pauvrete_60',
        f'DEC_MED{yy}': 'mediane_niveau_vie',
        f'DEC_D1{yy}': 'decile_1',
        f'DEC_D2{yy}': 'decile_2',
        f'DEC_D3{yy}': 'decile_3',
        f'DEC_D4{yy}': 'decile_4',
        f'DEC_D6{yy}': 'decile_6',
        f'DEC_D7{yy}': 'decile_7',
        f'DEC_D8{yy}': 'decile_8',
        f'DEC_D9{yy}': 'decile_9',
        f'DEC_RD{yy}': 'rapport_interdecile',
        f'DEC_PACT{yy}': 'pct_revenus_activite',
        f'DEC_PTSA{yy}': 'pct_salaires',
        f'DEC_PCHO{yy}': 'pct_indemnites_chomage',
        f'DEC_PBEN{yy}': 'pct_revenus_non_salaries',
        f'DEC_PPEN{yy}': 'pct_pensions_retraites',
        f'DEC_PAUT{yy}': 'pct_autres_revenus'
    }

    try: 
        df =pd.read_excel(FILE_DATA, sheet_name='IRIS_DEC', skiprows=5, dtype=str)
        

        colonnes_presentes = [col for col in mapping.keys() if col in df.columns]
        df = df[colonnes_presentes].copy()


        df.rename(columns=mapping, inplace=True)

    except Exception as e:    
        print(f"❌ Erreur lors de la lecture du fichier Excel : {e}")
        print("Vérifie que ton fichier Excel est bien fermé avant de lancer le script !")
        return
    

    df['localisation'] = df['localisation'].apply(remove_accents)
    df = df.dropna(subset=['localisation'])

    valeurs_nulles = ['s', 'so', 'ns', 'nd', 'nc', '']
    df.replace(valeurs_nulles, np.nan, inplace=True)

    cols_num = df.columns.drop('localisation')
    for col in cols_num:
        df[col] = df[col].astype(str).str.replace(',', '.')
        df[col] = pd.to_numeric(df[col], errors='coerce')


    nb_lignes_avant = len(df)
    df = df[df['rapport_interdecile'] < 10]
    nb_lignes_apres = len(df)
    print(f"🧹 Filtre Outliers : {nb_lignes_avant - nb_lignes_apres} lignes écartées (Rapport Interdécile >= 10 ou Null).")


    print("🔄 Agrégation des données IRIS par commune...")
    df_final = df.groupby('localisation', as_index=False).mean()


    df_final[cols_num] = np.round(df_final[cols_num], 2)
    df_final['annee'] = year


    dossier_sortie = BASE_DIR / "data_filtered" / str(year)
    dossier_sortie.mkdir(parents=True, exist_ok=True)
    fichier_sortie = dossier_sortie / f"CLEAN_10_Revenus_{year}.csv"

    df_final.to_csv(
        fichier_sortie, 
        sep=";", 
        index=False, 
        encoding="utf-8-sig", 
        decimal=".", 
        float_format="%.2f"
    )

    print(f" Succès ! Fichier INSEE généré avec {len(df_final)} communes uniques.")
    print(f" Sauvegardé ici : {fichier_sortie}")

if __name__ == "__main__":
    process_revenux(2021)
