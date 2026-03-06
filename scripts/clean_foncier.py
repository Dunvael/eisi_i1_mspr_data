import pandas as pd
import os
import unicodedata

# ==========================================
# CONFIGURATION
# ==========================================
# Noms des fichiers (à adapter selon les vrais noms téléchargés)
INPUT_FONCIER = "fd_logement_2022.csv"
INPUT_COMMUNES = "communes_insee_2022.csv"
OUTPUT_FILENAME = "foncier_logement_2022_clean.csv"

current_dir = os.path.dirname(os.path.abspath(__file__))
input_foncier_path = os.path.join(current_dir, "..", "data_raw", INPUT_FONCIER)
input_communes_path = os.path.join(current_dir, "..", "data_raw", INPUT_COMMUNES)
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

# ==========================================
# TRAITEMENT PRINCIPAL
# ==========================================
print(f"Chargement du fichier {INPUT_FONCIER}...")

# 1. Charger les données de logement
try:
    df = pd.read_csv(input_foncier_path, sep=';', low_memory=False, encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv(input_foncier_path, sep=';', low_memory=False, encoding='latin-1')

# 2. Garder uniquement les colonnes demandées (en s'assurant qu'elles existent)
cols_to_keep = ["commune", "STOCD", "HLML", "CATL", "DIPLM", "IMMIM", "TACTM", "VOIT", "TRANSM", "SURF", "NBPI"]
# Ajustement si la colonne s'appelle "communes" avec un S dans ton fichier
df = df.rename(columns={"communes": "commune"}) 
cols_presentes = [c for c in cols_to_keep if c in df.columns]

df = df[cols_presentes].copy()

# 3. Renommer les colonnes selon ton cahier des charges
renaming_dict = {
    "commune": "code_commune", # Temporaire avant la jointure
    "STOCD": "statut_occupation",
    "HLML": "logement_hlm",
    "CATL": "categorie_logement",
    "DIPLM": "niveau_etudes",
    "IMMIM": "statut_immigre",
    "TACTM": "type_activite",
    "VOIT": "nb_voitures",
    "TRANSM": "mode_transport",
    "SURF": "superficie",
    "NBPI": "nb_pieces"
}
df = df.rename(columns=renaming_dict)

# 4. "Donner du sens" : Remplacer les lettres/codes INSEE par des valeurs claires et numériques
# Dictionnaires basés sur la documentation standard INSEE Logement
map_stocd = {'10': 1, '21': 2, '22': 2, '30': 3, 'Z': 0} # 1: Proprio, 2: Locataire, 3: Gratuit, 0: Sans objet
map_hlml = {'1': 1, '2': 0, 'Z': 0, 'Y': 0} # 1: HLM, 0: Non HLM/Sans objet
map_voit = {'0': 0, '1': 1, '2': 2, '3': 3, 'Z': 0} # Z = Sans objet -> 0
map_immim = {'1': 1, '2': 0, 'Z': 0} # 1: Immigré, 0: Non immigré
map_tactm = {'11': 1, '12': 2, '21': 3, '22': 4, 'Z': 0} # 1: Actif, 2: Chômeur, 3: Retraité, etc.

# Application des mappings (en gérant les types strings pour matcher l'INSEE)
df["statut_occupation"] = df["statut_occupation"].astype(str).map(map_stocd).fillna(df["statut_occupation"])
df["logement_hlm"] = df["logement_hlm"].astype(str).map(map_hlml).fillna(df["logement_hlm"])
df["nb_voitures"] = df["nb_voitures"].astype(str).map(map_voit).fillna(df["nb_voitures"])
df["statut_immigre"] = df["statut_immigre"].astype(str).map(map_immim).fillna(df["statut_immigre"])

# Nettoyage de la superficie et des pièces (convertir en numérique pur)
for col in ["superficie", "nb_pieces"]:
    if col in df.columns:
        # Remplacer 'Z' ou espaces par du vide, puis convertir en float/int
        df[col] = df[col].astype(str).replace(['Z', 'Y', ''], '0')
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

# 5. Jointure avec le fichier des communes pour récupérer le VRAI nom
print(f"Chargement des communes depuis {INPUT_COMMUNES}...")
communes_df = pd.read_csv(input_communes_path, dtype={"code_commune_INSEE": str})

# On s'assure que les codes sont bien des strings pour la jointure
df["code_commune"] = df["code_commune"].astype(str)

df = df.merge(
    communes_df[["code_commune_INSEE", "nom_commune"]], 
    left_on="code_commune", 
    right_on="code_commune_INSEE", 
    how="left"
)

# 6. Finaliser la colonne localisation
df = df.rename(columns={"nom_commune": "localisation"})
df["localisation"] = df["localisation"].apply(remove_accents).str.title()
df = df.drop(columns=["code_commune", "code_commune_INSEE"])

# Ajouter l'année
df["annee"] = 2022

# ==========================================
# SAUVEGARDE
# ==========================================
print(f"Sauvegarde en cours vers : {output_file}")
df.to_csv(output_file, index=False)
print("Succès ! Fichier Foncier nettoyé et mis en forme.")