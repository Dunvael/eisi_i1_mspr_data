import pandas as pd
import os
import unicodedata

# ==========================================
# CONFIGURATION
# ==========================================
# Nom du fichier source téléchargé
INPUT_FILENAME = "resultats-par-niveau-burvot-t1-france-entiere.csv" # À adapter avec le vrai nom du fichier
OUTPUT_FILENAME = "abstention_2022_clean.csv"

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
    """Enlève les accents d'une chaîne de caractères."""
    if pd.isna(text):
        return text
    text = str(text)
    # Normalisation unicode pour séparer les caractères de leurs accents
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    return text

# ==========================================
# TRAITEMENT PRINCIPAL
# ==========================================
print(f"Chargement et nettoyage de {INPUT_FILENAME}...")

# 1. Charger les données
# Les fichiers d'élections de data.gouv utilisent souvent ';' et l'encodage latin-1 ou utf-8
try:
    df = pd.read_csv(input_file, sep=';', low_memory=False, encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv(input_file, sep=';', low_memory=False, encoding='latin-1')

# 2. Garder uniquement les colonnes nécessaires
# Note: Dans les fichiers officiels, les colonnes ont souvent une majuscule. 
# Si ton fichier a des minuscules, remplace par "libellé de la commune", etc.
cols_to_keep = ["Libellé de la commune", "Inscrits", "Abstentions", "Votants"]

# Vérification si les colonnes existent (pour éviter les erreurs de casse)
cols_presentes = []
for col in cols_to_keep:
    # Recherche flexible (insensible à la casse) si la colonne exacte n'est pas trouvée
    match = [c for c in df.columns if c.lower() == col.lower()]
    if match:
        cols_presentes.append(match[0])

df = df[cols_presentes]

# 3. Renommer les colonnes
df = df.rename(columns=lambda x: "localisation" if x.lower() == "libellé de la commune" else x.lower())

# 4. Enlever les accents de la colonne localisation
df["localisation"] = df["localisation"].apply(remove_accents)
# Optionnel : mettre la première lettre en majuscule pour être raccord avec les autres fichiers
df["localisation"] = df["localisation"].str.title() 

# 5. Mettre au format numérique (chiffres entiers)
colonnes_chiffres = ["inscrits", "abstentions", "votants"]
for col in colonnes_chiffres:
    # Convertir en numérique (les erreurs deviennent NaN, puis on remplace par 0 et on force en entier)
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

# 6. Agréger les données (Optionnel mais recommandé)
# Le fichier data.gouv est souvent détaillé "par bureau de vote". 
# Il faut donc faire la somme par commune pour avoir les vrais totaux de la ville !
df = df.groupby("localisation", as_index=False)[colonnes_chiffres].sum()

# Ajouter l'année
df["annee"] = 2022

# ==========================================
# SAUVEGARDE
# ==========================================
print(f"Sauvegarde en cours vers : {output_file}")
df.to_csv(output_file, index=False)
print("Succès ! Fichier nettoyé et agrégé par commune.")