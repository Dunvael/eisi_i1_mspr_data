import pandas as pd
import os
import unicodedata

# chemins
input_file = "../data_raw/communes_france_2022.csv"
output_folder = "../data_clean"
output_file = os.path.join(output_folder, "densite_population_2022_clean.csv")

os.makedirs(output_folder, exist_ok=True)

# charger données
df = pd.read_csv(input_file)

# 1️⃣ garder colonnes nécessaires
df = df[
    [
        "nom_sans_accent",
        "reg_nom",
        "dep_nom",
        "population",
        "superficie_km2",
        "densite",
        "grille_densite",
    ]
]

# 2️⃣ renommer colonnes
df = df.rename(
    columns={
        "nom_sans_accent": "localisation",
        "reg_nom": "region",
        "dep_nom": "departement",
        "population": "nb_pers",
        "grille_densite": "type_densite",
    }
)

# fonction pour enlever accents
def remove_accents(text):
    if pd.isna(text):
        return text
    text = str(text)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    return text

# 3️⃣ localisation : majuscule début de mot
df["localisation"] = df["localisation"].str.title()

# 4️⃣ region : enlever accents
df["region"] = df["region"].apply(remove_accents)

# 5️⃣ departement : enlever accents
df["departement"] = df["departement"].apply(remove_accents)

# 6️⃣ densite → conversion en hexadecimal
df["densite"] = pd.to_numeric(df["densite"], errors="coerce")
df["densite"] = df["densite"].apply(lambda x: hex(int(x)) if pd.notnull(x) else None)

# 7️⃣ grille_densite : remplacer vide par 0
df["type_densite"] = df["type_densite"].fillna(0)

# sauvegarde
df.to_csv(output_file, index=False)

print("Fichier nettoyé généré :", output_file)