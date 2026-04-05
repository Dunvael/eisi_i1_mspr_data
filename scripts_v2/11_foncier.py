import polars as pl
import pandas as pd
import numpy as np
from pathlib import Path
import unicodedata

# ==========================================
# 1. PARAMETRES ET CHEMINS
# ==========================================
BASE_DIR = Path(".")

# Tes chemins exacts
FILE_DATA = BASE_DIR / "data_raw/2022_raw/11. Foncier/FD_LOGEMT_2022.csv"
FILE_COG = BASE_DIR / "data_filtered/communes_france.csv" 

# ==========================================
# 2. OUTILS
# ==========================================
def remove_accents(text):
    if pd.isna(text): return text
    text = str(text)
    clean_text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    return clean_text.strip().upper()

# ==========================================
# 3. TRAITEMENT 100% AVEC POLARS
# ==========================================
def process_foncier_100pct(year=2022):
    print(f"🚀 Lancement du nettoyage INSEE - Foncier {year} (Mode POLARS 100%)...")

    mapping_colonnes = {
        'COMMUNE': 'code_insee',
        'communes': 'code_insee', 
        'STOCD': 'statut_occupation',
        'HLML': 'logement_hlm',
        'CATL': 'categorie_logement',
        'DIPLM': 'niveau_etudes',
        'IMMIM': 'immigre',
        'TACTM': 'type_activite',
        'VOIT': 'nb_voitures',
        'TRANSM': 'mode_transport',
        'SURF': 'superficie',
        'NBPI': 'nb_pieces'
    }

    
    try:
        df_cog = pd.read_csv(FILE_COG, sep=';', dtype=str)
        # Astuce : on nettoie les accents TOUT DE SUITE sur ce petit fichier
        df_cog['nom_commune'] = df_cog['nom_commune'].apply(remove_accents)
        # Conversion en Polars
        cog_pl = pl.DataFrame(df_cog[['code_insee', 'nom_commune']])
        print("✅ Fichier des communes chargé et nettoyé.")
    except Exception as e:
        print(f"❌ Erreur de lecture du fichier COG : {e}")
        return

    print("⏳ Analyse des 28,2 millions de lignes en cours (Veuillez patienter)...")

    # --- MAGIE POLARS ---
    try:
        # 1. Scanner le fichier sans le charger en RAM
        lazy_df = pl.scan_csv(FILE_DATA, separator=';', infer_schema_length=0)
        
        # 2. Sélectionner uniquement les colonnes utiles
        colonnes_dispo = lazy_df.collect_schema().names()
        col_commune = 'COMMUNE' if 'COMMUNE' in colonnes_dispo else 'communes'
        cols_a_garder = [col_commune] + [c for c in mapping_colonnes.keys() if c != 'COMMUNE' and c != 'communes' and c in colonnes_dispo]
        
        lazy_df = lazy_df.select(cols_a_garder)
        
        # 3. Renommer
        rename_dict = {c: mapping_colonnes[c] for c in cols_a_garder if c in mapping_colonnes}
        lazy_df = lazy_df.rename(rename_dict)

        # 4. Remplacer les lettres par des chiffres
        cols_num = [c for c in lazy_df.collect_schema().names() if c != 'code_insee']
        
        exprs = []
        for col in cols_num:
            expr = pl.col(col)
            expr = pl.when(expr == 'Z').then(pl.lit('0'))\
                     .when(expr == 'Y').then(pl.lit('1'))\
                     .when(expr == 'X').then(pl.lit('2'))\
                     .when(expr == 'N').then(pl.lit('0'))\
                     .when(expr == 'O').then(pl.lit('1'))\
                     .otherwise(expr)
            
            # ---> LA CORRECTION EST ICI (.alias(col)) <---
            expr = expr.cast(pl.Float64, strict=False).alias(col)
            exprs.append(expr)
            
        lazy_df = lazy_df.with_columns(exprs)

        # 5. Jointure avec le dictionnaire de communes
        lazy_df = lazy_df.join(cog_pl.lazy(), on='code_insee', how='left')
        
        # Consolidation du nom de la commune
        lazy_df = lazy_df.with_columns(
            pl.coalesce(["nom_commune", "code_insee"]).alias("localisation")
        ).drop(["code_insee", "nom_commune"]).drop_nulls(subset=["localisation"])

        # 6. Grouper par commune et calculer la moyenne mathématique
        lazy_df = lazy_df.group_by("localisation").mean()

        # 7. EXECUTION DU MOTEUR
        print("🚀 Démarrage du moteur Polars...")
        df_final_polars = lazy_df.collect()
        
        print(f"📊 Calculs terminés pour {len(df_final_polars)} communes !")

        # --- RETOUR EN PANDAS POUR LES FINITIONS ---
        df_final = df_final_polars.to_pandas()
        
        # Arrondi propre
        df_final[cols_num] = np.round(df_final[cols_num], 2)
        df_final['annee'] = year

        # --- EXPORT ---
        dossier_sortie = BASE_DIR / "data_filtered" / str(year)
        dossier_sortie.mkdir(parents=True, exist_ok=True)
        fichier_sortie = dossier_sortie / f"CLEAN_11_Foncier_{year}.csv"

        df_final.to_csv(fichier_sortie, sep=";", index=False, decimal=".", float_format="%.2f")
        
        print(f"✅ Mission accomplie ! Fichier 100% généré.")
        print(f"📁 Sauvegardé ici : {fichier_sortie}")

    except Exception as e:
        print(f"❌ Erreur avec Polars : {e}")

if __name__ == "__main__":
    process_foncier_100pct(2022)