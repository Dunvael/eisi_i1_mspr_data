import pandas as pd
import os
import unicodedata

# ==========================================
# CONFIGURATION
# ==========================================
# Nom du fichier source 2017 téléchargé sur data.gouv
INPUT_FILENAME = "Presidentielle_2017_Resultats_Communes_T1.csv" # À adapter
OUTPUT_FILENAME = "elections_2017_clean.csv"

current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, "..", "data_raw", INPUT_FILENAME)
output_folder = os.path.join(current_dir, "..", "data_clean")
output_file = os.path.join(output_folder, OUTPUT_FILENAME)

os.makedirs(output_folder, exist_ok=True)

# ==========================================
# FONCTIONS UTILES
# ==========================================
def remove_accents(text):
    if pd.isna(text):
        return text
    text = str(text)
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

def clean_french_percentage(series):
    """Convertit les pourcentages français (ex: 12,34) en floats (12.34)"""
    return pd.to_numeric(series.astype(str).str.replace(',', '.').str.replace('%', ''), errors='coerce').fillna(0)

# ==========================================
# TRAITEMENT PRINCIPAL
# ==========================================
print(f"Chargement et nettoyage de {INPUT_FILENAME} (Données 2017)...")

try:
    df = pd.read_csv(input_file, sep=';', low_memory=False, encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv(input_file, sep=';', low_memory=False, encoding='latin-1')

new_df = pd.DataFrame()

# 1. Localisation (Libellé de la commune)
col_commune = [c for c in df.columns if "commune" in c.lower()][0]
new_df["localisation"] = df[col_commune].apply(remove_accents).str.title()

# 2. Métriques globales (%votants/inscrits, etc.)
# On cherche dynamiquement les colonnes correspondantes pour éviter les erreurs d'indices
col_votants_ins = [c for c in df.columns if "% Vot/Ins" in c][0]
col_abs_ins = [c for c in df.columns if "% Abs/Ins" in c][0]
col_blancs_vot = [c for c in df.columns if "% Blancs/Vot" in c][0]
col_nuls_vot = [c for c in df.columns if "% Nuls/Vot" in c][0]
col_exp_vot = [c for c in df.columns if "% Exp/Vot" in c][0]

new_df["pct_votants_inscrits"] = clean_french_percentage(df[col_votants_ins])
new_df["pct_abstentions_inscrits"] = clean_french_percentage(df[col_abs_ins])
new_df["pct_blancs_votants"] = clean_french_percentage(df[col_blancs_vot])
new_df["pct_nuls_votants"] = clean_french_percentage(df[col_nuls_vot])
new_df["pct_exprimes_votants"] = clean_french_percentage(df[col_exp_vot])

# 3. Extraction des scores des candidats (par indice de colonne)
# ATTENTION : Si ton fichier brut a des colonnes en plus au début (ex: code département),
# il faudra peut-être décaler ces indices (ex: +2 ou +3). 
# Teste le script, et si les pourcentages sont à 0, modifie les numéros ici.
idx_le_pen = 6
idx_macron = 13
idx_hamon = 20
idx_arthaud = 27
idx_poutou = 34
idx_cheminade = 41
idx_lassalle = 48
idx_melenchon = 55
idx_asselineau = 62
idx_fillon = 69

# 4. Combinaison par parti politique (selon ton cahier des charges)
# Extraire les valeurs propres
v_le_pen = clean_french_percentage(df.iloc[:, idx_le_pen])
v_macron = clean_french_percentage(df.iloc[:, idx_macron])
v_hamon = clean_french_percentage(df.iloc[:, idx_hamon])
v_arthaud = clean_french_percentage(df.iloc[:, idx_arthaud])
v_poutou = clean_french_percentage(df.iloc[:, idx_poutou])
v_cheminade = clean_french_percentage(df.iloc[:, idx_cheminade])
v_lassalle = clean_french_percentage(df.iloc[:, idx_lassalle])
v_melenchon = clean_french_percentage(df.iloc[:, idx_melenchon])
v_asselineau = clean_french_percentage(df.iloc[:, idx_asselineau])
v_fillon = clean_french_percentage(df.iloc[:, idx_fillon])

# --- AGRÉGATION ---
new_df["pct_ext_droite"] = v_le_pen

# Note : Tu avais listé Jean Lassalle dans Extrême Gauche ET dans Droite.
# Je l'ai mis uniquement à Droite pour ne pas compter ses voix en double. 
# Si tu veux le remettre à gauche, ajoute "+ v_lassalle" à la ligne ci-dessous.
new_df["pct_ext_gauche"] = v_arthaud 

new_df["pct_centre"] = v_macron + v_cheminade + v_asselineau
new_df["pct_droite"] = v_fillon + v_lassalle 
new_df["pct_gauche"] = v_melenchon + v_poutou + v_hamon

# 5. Moyenne par commune (pour regrouper les bureaux de vote)
df_final = new_df.groupby("localisation", as_index=False).mean()

# Arrondir à 2 décimales maximum
cols_numeriques = [c for c in df_final.columns if c != "localisation"]
df_final[cols_numeriques] = df_final[cols_numeriques].round(2)

df_final["annee"] = 2017

# ==========================================
# SAUVEGARDE
# ==========================================
print(f"Sauvegarde en cours vers : {output_file}")
df_final.to_csv(output_file, index=False)
print("Succès ! Fichier des élections 2017 nettoyé et agrégé par partis et par commune.")