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

#Contrôle couverture Y / X : 
def check_couverture_y_x(df_y, df_x, name):
    codes_y = set(df_y["code_insee"])
    codes_x = set(df_x["code_insee"])

    absent_du_x = codes_y - codes_x
    absent_du_y = codes_x - codes_y

    print(f"\n--- CHECK Y / {name} ---")
    print("Dans Y mais absent du X :", len(absent_du_x))
    print("Dans X mais absent du Y :", len(absent_du_y))

    #Génération des 92 Y que l'on a pas dans les variables explicatives : 
    # if len(absent_du_x) > 0:
    #     print("Exemples absents du X :", list(absent_du_x)[:20])

    # print("\n--- COMMUNES DE Y ABSENTES DU X ---")

    # print(
    #     df_y[
    #         df_y["code_insee"].isin(absent_du_x)
    #         ].head(100)
    # )
    # df_absents = df_y[
    # df_y["code_insee"].isin(absent_du_x)
    # ]

    # df_absents.to_csv(
    #     "communes_absentes_x.csv",
    #     sep=";",
    #     index=False,
    #     encoding="utf-8-sig"
    # )

    print("Fichier exporté : communes_absentes_x.csv")

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
print("Après votes_politique :", df_final.shape)

# --------------------------------
# DEBUG chomage
# --------------------------------
# Debug Check pour savoir les NaN présents dans Y mais pas dans X et inversement
check_couverture_y_x(
    elections,
    chomage,
    "chomage"
)

cols_chomage = [
    "taux_chomage"
]

codes_y = set(elections["code_insee"])

codes_nan_interne = set(
    chomage[
        chomage[cols_chomage]
        .isna()
        .any(axis=1)
    ]["code_insee"]
)

print(
    "NaN internes présents dans Y :",
    len(codes_nan_interne & codes_y)
)

df_final = df_final.merge(
    chomage.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)

print("Après chomage :", df_final.shape)

print("NaN après chomage :")
print(
    df_final.isna().sum()[
        df_final.isna().sum() > 0
    ]
)

# --------------------------------

df_final = df_final.merge(
    densite.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)
print("Après densité :", df_final.shape)

# --------------------------------------------------------
check_couverture_y_x(
    elections,
    demographie,
    "demographie"
)

cols_demo = [
    "pct_jeunes",
    "pct_seniors",
    "age_median"
]

codes_y = set(elections["code_insee"])

codes_nan_interne = set(
    demographie[
        demographie[cols_demo]
        .isna()
        .any(axis=1)
    ]["code_insee"]
)

print(
    "NaN internes présents dans Y :",
    len(codes_nan_interne & codes_y)
)


df_final = df_final.merge(
    demographie.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)
print("Après demographie :", df_final.shape)

print("NaN après demographie :")
print(
    df_final.isna().sum()[
        df_final.isna().sum() > 0
    ]
)


# --------------------------------------------------------

check_couverture_y_x(
    elections,
    immigration,
    "immigration"
)

cols_immigration = [
    "taux_immigration"
]

codes_y = set(elections["code_insee"])

codes_nan_interne = set(
    immigration[
        immigration[cols_immigration]
        .isna()
        .any(axis=1)
    ]["code_insee"]
)

print(
    "NaN internes présents dans Y :",
    len(codes_nan_interne & codes_y)
)


df_final = df_final.merge(
    immigration.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)
print("Après immigration :", df_final.shape)

print("NaN après immigration :")
print(
    df_final.isna().sum()[
        df_final.isna().sum() > 0
    ]
)


# ----------------------------------------------

# --------------------------------
# Debug Check associations
# --------------------------------

check_couverture_y_x(
    elections,
    associations,
    "associations"
)

cols_associations = [
    "nb_associations"
]

codes_y = set(elections["code_insee"])

codes_nan_interne = set(
    associations[
        associations[cols_associations]
        .isna()
        .any(axis=1)
    ]["code_insee"]
)

print(
    "NaN internes présents dans Y :",
    len(codes_nan_interne & codes_y)
)

df_final = df_final.merge(
    associations.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)

print("Après associations :", df_final.shape)

print("NaN après associations :")
print(
    df_final.isna().sum()[
        df_final.isna().sum() > 0
    ]
)

# ------------------------------------------------

# --------------------------------
# Debug Check entreprises
# --------------------------------

check_couverture_y_x(
    elections,
    entreprises,
    "entreprises"
)

cols_entreprises = [
    "nb_creations_entreprises"
]

codes_y = set(elections["code_insee"])

codes_nan_interne = set(
    entreprises[
        entreprises[cols_entreprises]
        .isna()
        .any(axis=1)
    ]["code_insee"]
)

print(
    "NaN internes présents dans Y :",
    len(codes_nan_interne & codes_y)
)

df_final = df_final.merge(
    entreprises.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)

print("Après entreprises :", df_final.shape)

print("NaN après entreprises :")
print(
    df_final.isna().sum()[
        df_final.isna().sum() > 0
    ]
)


#--------------------------------------------------


df_final = df_final.merge(
    criminalite.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left"
)
print("Après criminalité :", df_final.shape)

# --------------------------------
#Debug Check pour savoir les NaN présent dans Y mais pas dans X et inversement
check_couverture_y_x(
    elections,
    categorie_sociale,
    "categorie_sociale"
)

cols_pct = [
    "pourcentage_agri",
    "pourcentage_cadres",
    "pourcentage_employes",
    "pourcentage_ouvriers"
]

codes_y = set(elections["code_insee"])

codes_nan_interne = set(
    categorie_sociale[
        categorie_sociale[cols_pct]
        .isna()
        .any(axis=1)
    ]["code_insee"]
)

print(
    "NaN internes présents dans Y :",
    len(codes_nan_interne & codes_y)
)

df_final = df_final.merge(
    categorie_sociale.drop(columns=["localisation"], errors="ignore"),
    on="code_insee",
    how="left")

print("Après categorie_sociale :", df_final.shape)

print("NaN après categorie_sociale :")
print(    
    df_final.isna().sum()[
        df_final.isna().sum() > 0
        ]
)

# --------------------------------

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