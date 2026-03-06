import pandas as pd
import os
import unicodedata

# ==========================================
# CONFIGURATION
# ==========================================
# Nom du fichier source téléchargé (à adapter selon le vrai nom du fichier)
INPUT_FILENAME = "base-ic-activite-nationalite-2022.csv" 
OUTPUT_FILENAME = "activite_nationalite_2022_clean.csv"

# Chemins
current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, "..", "data_raw", INPUT_FILENAME)
output_folder = os.path.join(current_dir, "..", "data_clean")
output_file = os.path.join(output_folder, OUTPUT_FILENAME)

os.makedirs(output_folder, exist_ok=True)

# ==========================================
# FONCTION DE NETTOYAGE
# ==========================================
def remove_accents(text):
    """Supprime les accents des noms de villes."""
    if isinstance(text, str):
        text = unicodedata.normalize('NFKD', text)
        return "".join([c for c in text if not unicodedata.combining(c)])
    return text

# ==========================================
# TRAITEMENT PRINCIPAL
# ==========================================
print(f"Chargement et nettoyage de {INPUT_FILENAME}...")

# 1. Charger les données (gestion des séparateurs INSEE classiques)
try:
    df = pd.read_csv(input_file, sep=';', low_memory=False, encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv(input_file, sep=';', low_memory=False, encoding='latin-1')

# 2. Renommer et nettoyer LIBGEO
df = df.rename(columns={"LIBGEO": "localisation"})
df["localisation"] = df["localisation"].apply(remove_accents)

# 3. Création du nouveau dataset avec les colonnes combinées
new_df = pd.DataFrame()
new_df["localisation"] = df["localisation"]
new_df["annee"] = 2022

# Dictionnaire de correspondance issu de ton image
# TACTR11 = En emploi, TACTR12 = Chômeurs, etc.
activites = {
    "TACTR11": "en_emploi",
    "TACTR12": "chomeurs",
    "TACTR21": "retraites",
    "TACTR22": "etudiants",
    "TACTR24": "au_foyer",
    "TACTR26": "autres_inactifs"
}

# 4. Combiner par sexe (Sexe 1 + Sexe 2) pour Français (INATC1) et Étrangers (INATC2)
for code_tactr, nom_final in activites.items():
    
    # --- FRANÇAIS (INATC1) ---
    # On cherche les colonnes qui contiennent INATC1_SEXE1 (hommes) et le code d'activité, etc.
    cols_fr_hommes = [c for c in df.columns if "INATC1_SEXE1" in c and code_tactr in c]
    cols_fr_femmes = [c for c in df.columns if "INATC1_SEXE2" in c and code_tactr in c]
    
    # Addition H + F
    new_df[f"fr_{nom_final}"] = df[cols_fr_hommes].sum(axis=1) + df[cols_fr_femmes].sum(axis=1)
    
    # --- ÉTRANGERS (INATC2) ---
    cols_etr_hommes = [c for c in df.columns if "INATC2_SEXE1" in c and code_tactr in c]
    cols_etr_femmes = [c for c in df.columns if "INATC2_SEXE2" in c and code_tactr in c]
    
    # Addition H + F
    new_df[f"etr_{nom_final}"] = df[cols_etr_hommes].sum(axis=1) + df[cols_etr_femmes].sum(axis=1)

# 5. Nettoyage final (remplacer les éventuels NaN par 0)
new_df = new_df.fillna(0)

# ==========================================
# SAUVEGARDE
# ==========================================
print(f"Sauvegarde en cours vers : {output_file}")
new_df.to_csv(output_file, index=False)
print("Succès ! Fichier généré.")