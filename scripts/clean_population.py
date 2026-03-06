import pandas as pd
import os
import unicodedata

# fichiers source
file_2022 = "../data_raw/population_2022.csv"
file_2016 = "../data_raw/population_2016.csv"

# dossier sortie
output_folder = "../data_clean"
os.makedirs(output_folder, exist_ok=True)

# fonction pour enlever accents
def remove_accents(text):
    if isinstance(text, str):
        text = unicodedata.normalize('NFKD', text)
        return "".join([c for c in text if not unicodedata.combining(c)])
    return text


# ==========================
# TRAITEMENT 2022
# ==========================

df22 = pd.read_csv(file_2022)

# colonnes à garder
cols_2022 = ["LIBGEO"] + list(df22.columns[6:12]) + list(df22.columns[82:90]) + list(df22.columns[92:100]) + list(df22.columns[100:108])

df22 = df22[cols_2022]

# renommer
df22 = df22.rename(columns={
    "LIBGEO": "localisation"
})

# enlever accents
df22["localisation"] = df22["localisation"].apply(remove_accents)

# ajouter année
df22["annee"] = 2022


# ==========================
# TRAITEMENT 2016
# ==========================

df16 = pd.read_csv(file_2016)

cols_2016 = ["LIBGEO"] + list(df16.columns[6:12]) + list(df16.columns[82:90]) + list(df16.columns[92:100]) + list(df16.columns[100:108])

df16 = df16[cols_2016]

df16 = df16.rename(columns={
    "LIBGEO": "localisation"
})

df16["localisation"] = df16["localisation"].apply(remove_accents)

df16["annee"] = 2016


# ==========================
# CONCATENER LES 2 ANNEES
# ==========================

df = pd.concat([df16, df22])

# remplacer valeurs vides
df = df.fillna(0)

# sauvegarder fichier nettoyé
output_file = os.path.join(output_folder, "population_age_statut_2016_2022_clean.csv")
df.to_csv(output_file, index=False)

print("Fichier nettoyé généré :", output_file)