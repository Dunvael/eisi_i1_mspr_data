import pandas as pd
from pathlib import Path

DIR = Path("data_cleaned/2022")

elections = pd.read_csv(DIR / "Y_classe_politique_2022_cleaned.csv", sep=";")
votes_politique = pd.read_csv(DIR / "X_votes_politiques_2022_cleaned.csv", sep=";")
revenus = pd.read_csv(DIR / "01_revenus_median_2021_cleaned.csv", sep=";")
chomage = pd.read_csv(DIR / "02_taux_chomage_2022_cleaned.csv", sep=";")
densite = pd.read_csv(DIR / "04_densite_population_2022_cleaned.csv", sep=";")
demographie = pd.read_csv(DIR / "05_demographie_2022_cleaned.csv", sep=";")
immigration = pd.read_csv(DIR / "06_taux_immigration_2022_cleaned.csv", sep=";")
associations = pd.read_csv(DIR / "07_associations_2022_cleaned.csv", sep=";")
entreprises = pd.read_csv(DIR / "08_creation_entreprises_2022_cleaned.csv", sep=";")
criminalite = pd.read_csv(DIR / "09_criminalite_diff_ndiff_2022_cleaned.csv", sep=";")
categorie_sociale = pd.read_csv(DIR / "03_categorie_sociale_2022_cleaned.csv", sep=";")

datasets = [elections, votes_politique, chomage, densite, demographie, immigration, associations, entreprises, criminalite, 
            categorie_sociale, revenus]

for df in datasets:
    df["code_insee"] = df["code_insee"].astype(str).str.zfill(5)

    if "localisation" in df.columns:
        df["localisation"] = df["localisation"].astype(str).str.strip()

    df.drop(columns=["annee"], inplace=True, errors="ignore")

df_final = elections.copy()

print("Base élections :", df_final.shape)

for name, df in [
    ("elections", elections),
    ("votes_politique", votes_politique),
    ("revenus", revenus),
    ("chomage", chomage),
    ("densite", densite),
    ("demographie", demographie),
    ("immigration", immigration),
    ("association", associations),
    ("entreprises", entreprises),
    ("criminalite", criminalite),
    ("categorie_sociale", categorie_sociale),
]:
    
    print("\n", name)
    print("lignes :", len(df))
    print("codes INSEE uniques :", df["code_insee"].nunique())
    print("doublons code_insee :", df["code_insee"].duplicated().sum())


df_final = df_final.merge(
    votes_politique.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)
print("Après votes_politiqu :", df_final.shape)

df_final = df_final.merge(
    chomage.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)
print("Après chômage :", df_final.shape)

df_final = df_final.merge(
    densite.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)
print("Après densité :", df_final.shape)

df_final = df_final.merge(
    demographie.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)
print("Après demographie :", df_final.shape)

df_final = df_final.merge(
    immigration.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)
print("Après immigration :", df_final.shape)

df_final = df_final.merge(
    associations.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)
print("Après associations :", df_final.shape)

df_final = df_final.merge(
    entreprises.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)
print("Après entreprises :", df_final.shape)

df_final = df_final.merge(
    criminalite.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)
print("Après criminalité :", df_final.shape)

df_final = df_final.merge(
    categorie_sociale.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)
print("Après categorie_sociale :", df_final.shape)


df_final = df_final.merge(
    revenus[["code_insee", "revenu_median_final"]],
    on="code_insee",
    how="left"
)
print("Après revenus :", df_final.shape)

print(
    df_final[df_final["revenu_median_final"].isna()][
        ["code_insee", "localisation"]
    ].head(100)
)

df_final["annee"] = 2022

print("\n--- NaN ---")
print(df_final.isna().sum())

print("\n--- Pourcentage NaN ---")
print((df_final.isna().mean() * 100).round(2))

df_final.to_csv(DIR / "Z_dataframe_final_ml.csv", sep=";", index=False, encoding="utf-8-sig")

print("Dataframe créé.")