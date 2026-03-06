import pandas as pd
import os

# chemins fichiers
input_file = "../data_raw/criminalite_communes.csv"
communes_file = "../data_raw/communes_france.csv"

output_folder = "../data_clean"
output_file = os.path.join(output_folder, "criminalite_2017_2022_clean.csv")

# créer dossier si absent
os.makedirs(output_folder, exist_ok=True)

# charger données criminalité
df = pd.read_csv(input_file)

# garder colonnes nécessaires
df = df[[
    "CODEGEO_2025",
    "annees",
    "indicateur",
    "est_diffuse"
]]

# renommer colonne
df = df.rename(columns={
    "CODEGEO_2025": "code_commune"
})

# garder uniquement 2017 et 2022
df = df[df["annees"].isin([2017, 2022])]

# nettoyer est_diffuse
df["est_diffuse"] = df["est_diffuse"].fillna(0).astype(int)

# charger table des communes
communes = pd.read_csv(communes_file)

# garder seulement colonnes utiles
communes = communes[["code_commune_INSEE", "nom_commune"]]

# fusion avec les communes
df = df.merge(
    communes,
    left_on="code_commune",
    right_on="code_commune_INSEE",
    how="left"
)

# renommer nom_commune -> localisation
df = df.rename(columns={
    "nom_commune": "localisation"
})

# supprimer colonnes inutiles
df = df.drop(columns=["code_commune_INSEE", "code_commune"])

# supprimer lignes vides
df = df.dropna(subset=["localisation"])

# sauvegarder fichier nettoyé
df.to_csv(output_file, index=False)

print("Fichier nettoyé généré :", output_file)