import pandas as pd
import re
import os

# chemins
input_file = "../data_raw/diplomes.csv"
output_folder = "../data_clean"
output_file = os.path.join(output_folder, "niveau_etudes_2022_clean.csv")

# créer le dossier si besoin
os.makedirs(output_folder, exist_ok=True)

# charger données
df = pd.read_csv(input_file)

# garder colonnes nécessaires
df = df[["educ", "geo", "sexe", "time_period", "obs_value"]]

# renommer colonnes
df = df.rename(columns={
    "educ": "diplome",
    "geo": "localisation",
    "time_period": "annee",
    "obs_value": "nb_pers"
})

# garder uniquement 2022
df = df[df["annee"] == 2022]

# corriger sexe
df["sexe"] = df["sexe"].replace("_T", "T")

# nettoyage villes
def clean_city(city):

    if pd.isna(city):
        return city

    city = str(city)

    # enlever caractères spéciaux
    city = re.sub(r'[@*]', '', city)

    # enlever chiffres (codes postaux)
    city = re.sub(r'\d+', '', city)

    # nettoyer espaces
    city = re.sub(r'\s+', ' ', city).strip()

    return city

df["localisation"] = df["localisation"].apply(clean_city)

# dictionnaire diplômes
diplome_map = {
    "ED0-2": "Sans Diplome Ou Brevet",
    "ED3": "CAP BEP",
    "ED4": "Baccalaureat",
    "ED5": "Bac +2",
    "ED6": "Licence",
    "ED7": "Master",
    "ED8": "Doctorat"
}

df["diplome"] = df["diplome"].replace(diplome_map)

# nettoyer nombres
df["nb_pers"] = df["nb_pers"].astype(str)
df["nb_pers"] = df["nb_pers"].str.split(".").str[0]
df["nb_pers"] = pd.to_numeric(df["nb_pers"], errors="coerce")

# sauvegarde
df.to_csv(output_file, index=False)

print("Dataset nettoyé créé :", output_file)