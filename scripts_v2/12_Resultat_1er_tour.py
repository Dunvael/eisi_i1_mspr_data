import pandas as pd
import numpy as np
from pathlib import Path
import unicodedata


BASE_DIR = Path(".")

# ⚠️ Modifie ce chemin pour pointer vers ton nouveau fichier data.gouv
FILE_DATA = BASE_DIR / "data_raw/2022_raw/12. Resultat1er_tour/p2022-resultats-bureaux-t1.csv"



def remove_accents(text):
    if pd.isna(text): return text
    text = str(text)
    clean_text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    return clean_text.strip().upper()


def process_resultats_t1(year=2022):
    print(f"⏳ Lancement du nettoyage des Résultats Électoraux {year}...")

    # Les colonnes exactes qu'on veut extraire du fichier brut
    colonnes_brutes = [
        'Commune', 'Abstentions_ins', 'Votants_ins', 'Blancs_vot', 'Nuls_vot', 
        'Exprimés_ins', 'Exprimés_vot', 
        'ARTHAUD.exp', 'ROUSSEL.exp', 'MACRON.exp', 'LASSALLE.exp', 
        'LE PEN.exp', 'ZEMMOUR.exp', 'MÉLENCHON.exp', 'HIDALGO.exp', 
        'JADOT.exp', 'PÉCRESSE.exp', 'POUTOU.exp', 'DUPONT-AIGNAN.exp'
    ]

    # Le dictionnaire pour renommer proprement les colonnes
    mapping_renommage = {
        'Commune': 'localisation',
        'Abstentions_ins': 'abstention_inscrits',
        'Votants_ins': 'votants_inscrits',
        'Blancs_vot': 'blancs_votants',
        'Nuls_vot': 'nuls_votants',
        'Exprimés_ins': 'exprimes_inscrits',
        'Exprimés_vot': 'exprimes_votants'
    }

    try:
        # LECTURE DU FICHIER (sep=',' car c'est un vrai CSV standard)
        df = pd.read_csv(FILE_DATA, sep=',', usecols=colonnes_brutes, low_memory=False)
        
    except Exception as e:
        print(f"❌ Erreur de lecture : {e}")
        return


    df.rename(columns=mapping_renommage, inplace=True)
    df['localisation'] = df['localisation'].apply(remove_accents)
    df = df.dropna(subset=['localisation'])

    cols_num = df.columns.drop('localisation')
    for col in cols_num:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 3.3 CRÉATION DES BLOCS POLITIQUES
    df['Ext_Droite'] = df['LE PEN.exp'] + df['ZEMMOUR.exp']
    df['Ext_Gauche'] = df['LASSALLE.exp'] + df['ARTHAUD.exp']
    df['Centre'] = df['MACRON.exp']
    df['Droite'] = df['PÉCRESSE.exp'] + df['DUPONT-AIGNAN.exp']
    df['Gauche'] = df['ROUSSEL.exp'] + df['MÉLENCHON.exp'] + df['HIDALGO.exp'] + df['JADOT.exp'] + df['POUTOU.exp']


    print("🔄 Regroupement des bureaux de vote par commune...")
    df_final = df.groupby('localisation', as_index=False).mean()


    colonnes_a_garder = [
        'localisation', 'abstention_inscrits', 'votants_inscrits', 
        'blancs_votants', 'nuls_votants', 'exprimes_inscrits', 'exprimes_votants',
        'Ext_Droite', 'Ext_Gauche', 'Centre', 'Droite', 'Gauche'
    ]


    df_export = df_final[colonnes_a_garder].copy()
    cols_a_arrondir = df_export.columns.drop('localisation')


    df_export[cols_a_arrondir] = np.round(df_export[cols_a_arrondir], 2)
    df_export['annee'] = year


    dossier_sortie = BASE_DIR / "data_filtered" / str(year)
    dossier_sortie.mkdir(parents=True, exist_ok=True)
    fichier_sortie = dossier_sortie / f"CLEAN_12_Resultats_T1_{year}.csv"

    df_export.to_csv(
        fichier_sortie, 
        sep=";", # On exporte avec un ; pour être cohérent avec tous tes autres fichiers propres
        index=False, 
        encoding="utf-8-sig", 
        decimal=".", 
        float_format="%.2f"
    )
    
    print(f"✅ Succès ! Fichier Électoral généré avec {len(df_export)} communes.")
    print(f"📁 Sauvegardé ici : {fichier_sortie}")

if __name__ == "__main__":
    process_resultats_t1(2022)


