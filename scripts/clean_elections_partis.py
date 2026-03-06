import pandas as pd
import os
import unicodedata

# ==========================================
# CONFIGURATION
# ==========================================
INPUT_FILENAME = "resultats-par-niveau-burvot-t1-france-entiere.csv" # Même fichier que le critère 8
OUTPUT_FILENAME = "elections_partis_2022_clean.csv"

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
    return pd.to_numeric(series.astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

# ==========================================
# TRAITEMENT PRINCIPAL
# ==========================================
print(f"Chargement et nettoyage de {INPUT_FILENAME} pour les résultats des partis...")

try:
    df = pd.read_csv(input_file, sep=';', low_memory=False, encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv(input_file, sep=';', low_memory=False, encoding='latin-1')

# 1. Isoler la localisation et nettoyer
new_df = pd.DataFrame()
# La colonne "Libellé de la commune" est généralement à l'index 3 (colonne D)
col_commune = [c for c in df.columns if "commune" in c.lower()][0]
new_df["localisation"] = df[col_commune].apply(remove_accents).str.title()

# 2. Extraire les métriques générales de participation (colonnes de base)
# On cherche les colonnes qui contiennent ces mots-clés
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

# 3. Récupérer les % par candidat via leurs indices de colonnes Excel
# Conversion Lettre Excel -> Index (A=0, B=1... AB=27)
idx_Arthaud = 27  # AB
idx_Roussel = 34  # AI
idx_Macron = 41   # AP
idx_Lassalle = 48 # AW
idx_LePen = 55    # BD
idx_Zemmour = 62  # BK
idx_Melenchon = 69# BR
idx_Hidalgo = 76  # BY
idx_Jadot = 83    # CF
idx_Pecresse = 90 # CM
idx_Poutou = 97   # CT
idx_DupontA = 104 # DA

# Extraire et nettoyer les valeurs pour chaque candidat
v_arthaud = clean_french_percentage(df.iloc[:, idx_Arthaud])
v_roussel = clean_french_percentage(df.iloc[:, idx_Roussel])
v_macron = clean_french_percentage(df.iloc[:, idx_Macron])
v_lassalle = clean_french_percentage(df.iloc[:, idx_Lassalle])
v_lepen = clean_french_percentage(df.iloc[:, idx_LePen])
v_zemmour = clean_french_percentage(df.iloc[:, idx_Zemmour])
v_melenchon = clean_french_percentage(df.iloc[:, idx_Melenchon])
v_hidalgo = clean_french_percentage(df.iloc[:, idx_Hidalgo])
v_jadot = clean_french_percentage(df.iloc[:, idx_Jadot])
v_pecresse = clean_french_percentage(df.iloc[:, idx_Pecresse])
v_poutou = clean_french_percentage(df.iloc[:, idx_Poutou])
v_duponta = clean_french_percentage(df.iloc[:, idx_DupontA])

# 4. Agréger selon tes règles politiques
new_df["pct_ext_droite"] = v_lepen + v_zemmour
new_df["pct_ext_gauche"] = v_lassalle + v_arthaud
new_df["pct_centre"] = v_macron
new_df["pct_droite"] = v_pecresse + v_duponta
new_df["pct_gauche"] = v_roussel + v_melenchon + v_hidalgo + v_jadot + v_poutou

# 5. Agréger par commune
# Le fichier liste les bureaux de vote. On fait la moyenne des pourcentages par ville.
df_final = new_df.groupby("localisation", as_index=False).mean()

# Arrondir à 2 décimales pour faire propre
df_final = df_final.round(2)
df_final["annee"] = 2022

# ==========================================
# SAUVEGARDE
# ==========================================
print(f"Sauvegarde en cours vers : {output_file}")
df_final.to_csv(output_file, index=False)
print("Succès ! Fichier nettoyé, agrégé par partis et par commune.")