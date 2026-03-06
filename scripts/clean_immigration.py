import pandas as pd
import os
import unicodedata
import re

# ==========================================
# CONFIGURATION
# ==========================================
# Nom du fichier source téléchargé (à adapter si nécessaire)
INPUT_FILENAME = "base-ic-sexe-age-nationalite-2022.csv" 
OUTPUT_FILENAME = "immigration_2022_clean.csv"

# Chemins
current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, "..", "data_raw", INPUT_FILENAME)
output_folder = os.path.join(current_dir, "..", "data_clean")
output_file = os.path.join(output_folder, OUTPUT_FILENAME)

# Créer le dossier data_clean si besoin
os.makedirs(output_folder, exist_ok=True)

# ==========================================
# FONCTIONS UTILES
# ==========================================
def remove_accents(text):
    """Enlève les accents d'une chaîne de caractères."""
    if isinstance(text, str):
        text = unicodedata.normalize('NFKD', text)
        return "".join([c for c in text if not unicodedata.combining(c)])
    return text

def get_sum_of_columns(dataframe, pattern_nat, pattern_age):
    """
    Identifie les colonnes correspondant à une nationalité et un âge donnés
    (pour Hommes et Femmes confondus) et en retourne la somme.
    """
    # Explication du Regex :
    # Doit contenir le pattern de nationalité (ex: NAT1_1)
    # ET le pattern d'âge (ex: 0014)
    # Indépendamment de 'H' ou 'F' (Sexe)
    
    matched_cols = [
        col for col in dataframe.columns 
        if re.search(pattern_nat, col) and re.search(pattern_age, col)
    ]
    
    # Debug: afficher ce qu'on additionne
    # print(f"Regroupement pour Nat:{pattern_nat}, Age:{pattern_age} -> {matched_cols}")
    
    if not matched_cols:
        return 0
    return dataframe[matched_cols].sum(axis=1)

# ==========================================
# TRAITEMENT PRINCIPAL
# ==========================================
print(f"Début du nettoyage de {INPUT_FILENAME}...")

# 1. Charger les données
# L'INSEE utilise souvent ';' comme séparateur et l'encodage utf-8 ou latin-1
try:
    df = pd.read_csv(input_file, sep=';', low_memory=False, encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv(input_file, sep=';', low_memory=False, encoding='latin-1')

# 2. Nettoyer la colonne Localisation (LIBGEO)
df = df.rename(columns={"LIBGEO": "localisation"})
df["localisation"] = df["localisation"].apply(remove_accents)

# 3. Création des nouvelles colonnes agrégées (Cf. votre image)
# Nous utilisons des dictionnaires pour définir les correspondances
new_df = pd.DataFrame()
new_df["localisation"] = df["localisation"]

# --- DÉFINITION DES PATTERNS INSEE (À VÉRIFIER DANS VOTRE CSV) ---
# Français
P_FR = "NAT1_1" 
# Étrangers
P_ETR = "NAT1_2" 

# Tranches d'âges brutes INSEE (exemples fréquents dans les fichiers NAT1)
# Il faut parfois sommer plusieurs tranches d'âges fines de l'INSEE pour 
# obtenir vos tranches (ex: 1517 + 1824 + 2529 = 15-29 ans)
AGES_MAP = {
    "0_14_ans": "0014",
    # Exemple si l'INSEE sépare : sommer P22_H1519, P22_H2024, etc.
    # Ici on suppose que le fichier brut contient déjà des tranches larges
    "15_29_ans": "1529", 
    "30_44_ans": "3044",
    "45_59_ans": "4559",
    "60_74_ans": "6074",
    "75_ans_plus": "75P" # Souvent noté 75P ou 7599
}

print("Agrégation des données par nationalité et tranches d'âges...")

# Boucle pour créer les colonnes Français
for final_age_name, insee_age_pattern in AGES_MAP.items():
    new_col_name = f"nb_fr_{final_age_name}"
    new_df[new_col_name] = get_sum_of_columns(df, P_FR, insee_age_pattern)

# Boucle pour créer les colonnes Étrangers
for final_age_name, insee_age_pattern in AGES_MAP.items():
    new_col_name = f"nb_etr_{final_age_name}"
    new_df[new_col_name] = get_sum_of_columns(df, P_ETR, insee_age_pattern)

# 4. Ajouter l'année
new_df["annee"] = 2022

# ==========================================
# SAUVEGARDE
# ==========================================
# Remplacer les valeurs potentiellement vides par 0
new_df = new_df.fillna(0)

print(f"Sauvegarde du fichier nettoyé vers : {output_file}")
new_df.to_csv(output_file, index=False)

print("Terminé !")