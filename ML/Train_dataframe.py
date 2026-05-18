import pandas as pd
import sqlite3
from pathlib import Path


# Définition des chemins principaux : 

# "DIR" correspond au dossier contenant l’ensemble des datasets nettoyés de l’année 2022
#
# DB_PATH : chemin de la base de données SQLite finale qui contiendra le dataframe ML consolidé

DIR = Path("data_cleaned/2022")
DB_PATH = Path("data_cleaned/Train_dataframe.db")


# Chargement ci-dessous des datasets nettoyés
# Chaque dataset correspond à une thématique : élections, chômage, démographie, criminalité etc... 
# (Tous les fichiers ont été nettoyés au préalable dans les scripts ETL précédents).

elections = pd.read_csv(DIR / "Y_classe_politique_2022_cleaned.csv", sep=";")
# votes_politique = pd.read_csv(DIR / "X_votes_politiques_2022_cleaned.csv", sep=";") A utiliser
revenus = pd.read_csv(DIR / "01_revenus_median_2021_cleaned.csv", sep=";")
chomage = pd.read_csv(DIR / "02_taux_chomage_2022_cleaned.csv", sep=";")
categorie_sociale = pd.read_csv(DIR / "03_categorie_sociale_2022_cleaned.csv", sep=";")
densite = pd.read_csv(DIR / "04_densite_population_2022_cleaned.csv", sep=";")
demographie = pd.read_csv(DIR / "05_demographie_2022_cleaned.csv", sep=";")
immigration = pd.read_csv(DIR / "06_taux_immigration_2022_cleaned.csv", sep=";")
associations = pd.read_csv(DIR / "07_associations_2022_cleaned.csv", sep=";")
entreprises = pd.read_csv(DIR / "08_creation_entreprises_2022_cleaned.csv", sep=";")
criminalite = pd.read_csv(DIR / "09_criminalite_diff_ndiff_2022_cleaned.csv", sep=";")

datasets = [
    elections,
    # votes_politique,
    revenus,
    chomage,
    densite,
    demographie,
    immigration,
    associations,
    entreprises,
    criminalite,
    categorie_sociale
]


# Harmonisation


for df in datasets:

    df["code_insee"] = (
        df["code_insee"]
        .astype(str)
        .str.zfill(5)
    )

    if "localisation" in df.columns:
        df["localisation"] = (
            df["localisation"]
            .astype(str)
            .str.strip()
        )

    df.drop(
        columns=["annee"],
        inplace=True,
        errors="ignore"
    )




# Construction dataframe final


df_final = elections.copy()



# df_final = df_final.merge(
#     votes_politique.drop(columns=["localisation"], errors="ignore"),
#     on="code_insee",
#     how="left"
# )



df_final = df_final.merge(
    chomage.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)

df_final = df_final.merge(
    densite.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)

df_final = df_final.merge(
    demographie.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)

df_final = df_final.merge(
    immigration.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)

df_final = df_final.merge(
    associations.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)

df_final = df_final.merge(
    entreprises.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)

df_final = df_final.merge(
    criminalite.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)

df_final = df_final.merge(
    categorie_sociale.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)

df_final = df_final.merge(
    revenus[["code_insee", "revenu_median_final", "classe_revenu"]], 
    on="code_insee",
    how="left"
)

nb_lignes_avec_nan = df_final.isna().any(axis=1).sum()
print("Lignes avec au moins un NaN :", nb_lignes_avec_nan)


# Suppression des NaN


print("\nShape avant suppression NaN :", df_final.shape)

df_final = df_final.dropna()

print("Shape après suppression NaN :", df_final.shape)


# Ajout année


df_final["annee"] = 2022


# Export CSV


csv_output = DIR / "Z_dataframe_final_ml.csv"

df_final.to_csv(
    csv_output,
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("CSV créé :", csv_output)


# Export SQLite


conn = sqlite3.connect(DB_PATH)

df_final.to_sql(
    "training_data",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

print("Base SQLite créée :", DB_PATH)


# Stats finales


print("\n--- SHAPE FINAL ---")
print(df_final.shape)

print("\n--- NaN restants ---")
print(df_final.isna().sum())