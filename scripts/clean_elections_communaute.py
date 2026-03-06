import pandas as pd
import os
import unicodedata

# ==========================================
# CONFIGURATION
# ==========================================
# Nom du fichier source communautaire (à adapter)
INPUT_FILENAME = "resultats_pres_2022_bureaux_nettoyes.csv" 
OUTPUT_FILENAME = "elections_communaute_2022_clean.csv"

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

def clean_and_convert_numeric(series):
    """Convertit les pourcentages avec virgules en décimales (float)"""
    return pd.to_numeric(series.astype(str).str.replace(',', '.').str.replace('%', ''), errors='coerce').fillna(0)

# ==========================================
# TRAITEMENT PRINCIPAL
# ==========================================
print(f"Chargement et nettoyage de {INPUT_FILENAME}...")

# Les fichiers communautaires peuvent être en utf-8 ou latin-1, avec séparateur ',' ou ';'
try:
    df = pd.read_csv(input_file, sep=';', low_memory=False, encoding='utf-8')
    if df.shape[1] < 5:  # Si mauvais séparateur
        df = pd.read_csv(input_file, sep=',', low_memory=False, encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv(input_file, sep=';', low_memory=False, encoding='latin-1')

# 1. Identifier la colonne de la localisation (commune)
col_commune = [c for c in df.columns if "commune" in c.lower()][0]

# 2. Création du dataset propre
new_df = pd.DataFrame()
new_df["localisation"] = df[col_commune].apply(remove_accents).str.title()

# 3. Extraction et nettoyage des métriques générales (Tolérance sur les noms exacts)
metrics_map = {
    "abstention_inscrits": ["abstention", "inscrit"],
    "votants_inscrits": ["votant", "inscrit"],
    "blancs_votans": ["blanc", "votant"],
    "nuls_votants": ["nul", "votant"],
    "exprimes_votants": ["exprime", "votant"],
    "exprimes_inscrits": ["exprime", "inscrit"]
}

for final_name, keywords in metrics_map.items():
    # Cherche la colonne qui contient tous les mots-clés (ex: 'abstention' ET 'inscrit')
    matching_cols = [c for c in df.columns if all(kw in c.lower() for kw in keywords)]
    if matching_cols:
        new_df[final_name] = clean_and_convert_numeric(df[matching_cols[0]])

# 4. Regroupement par bords politiques
# Fonction pour trouver la colonne d'un candidat selon son nom
def get_candidat_col(nom):
    cols = [c for c in df.columns if nom.lower() in c.lower() and "exprime" in c.lower()]
    if not cols: # Si "exprime" n'est pas dans le nom de la colonne, on cherche juste le nom
        cols = [c for c in df.columns if nom.lower() in c.lower()]
    return clean_and_convert_numeric(df[cols[0]]) if cols else 0

# Extraction dynamique
arthaud = get_candidat_col("arthaud")
roussel = get_candidat_col("roussel")
macron = get_candidat_col("macron")
lassalle = get_candidat_col("lassalle")
le_pen = get_candidat_col("pen")  # Le Pen
zemmour = get_candidat_col("zemmour")
melenchon = get_candidat_col("melenchon")
hidalgo = get_candidat_col("hidalgo")
jadot = get_candidat_col("jadot")
pecresse = get_candidat_col("pecresse")
poutou = get_candidat_col("poutou")
dupont_a = get_candidat_col("dupont")

# Agrégation selon tes catégories
new_df["pct_ext_droite"] = le_pen + zemmour
new_df["pct_ext_gauche"] = lassalle + arthaud
new_df["pct_centre"] = macron
new_df["pct_droite"] = pecresse + dupont_a
new_df["pct_gauche"] = roussel + melenchon + hidalgo + jadot + poutou

# 5. Agrégation par commune (Moyenne des bureaux de vote)
df_final = new_df.groupby("localisation", as_index=False).mean()

# 6. Forcer 2 chiffres après la virgule au maximum
cols_numeriques = [c for c in df_final.columns if c != "localisation"]
df_final[cols_numeriques] = df_final[cols_numeriques].round(2)

df_final["annee"] = 2022

# ==========================================
# SAUVEGARDE
# ==========================================
print(f"Sauvegarde en cours vers : {output_file}")
df_final.to_csv(output_file, index=False)
print("Succès ! Fichier communautaire nettoyé et agrégé.")