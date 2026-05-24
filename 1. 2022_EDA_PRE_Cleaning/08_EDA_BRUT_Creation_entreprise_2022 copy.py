import pandas as pd


# CONFIGURATION

FILE_RAW = "data_raw/2022_raw/8_creation_entreprise_2022/NBRE_CREATION_ENTREPRISE_PAR_COM_2012_TO_2025.xlsx"


# LECTURE DU DATASET BRUT

# Lecture sans header car le fichier contient des lignes de titre avant le tableau
df = pd.read_excel(
    FILE_RAW,
    sheet_name="COM",
    header=None,
    dtype=str
)

# Conservation des lignes à partir du vrai tableau
df = df.iloc[4:].copy()

# Renommage temporaire des colonnes pour faciliter l'EDA
df = df.rename(columns={
    0: "code_insee",
    1: "nom_brut",
    2: "2012",
    3: "2013",
    4: "2014",
    5: "2015",
    6: "2016",
    7: "2017",
    8: "2018",
    9: "2019",
    10: "2020",
    11: "2021",
    12: "2022",
    13: "2023",
    14: "2024",
    15: "2025"
})


# INFOS GÉNÉRALES

print("\n--- DIMENSIONS DU DATASET ---")
print(df.shape)

print("\n--- APERÇU DES DONNÉES ---")
print(df.head())

print("\n--- NOMS DES COLONNES ---")
print(df.columns)


# ANALYSE DES DOUBLONS

print("\n--- DOUBLONS ---")
print(df.duplicated().sum())


# ANALYSE DES CODES INSEE

if "code_insee" in df.columns:

    df["code_insee"] = (
        df["code_insee"]
        .astype(str)
        .str.zfill(5)
    )

    print("\n--- NOMBRE DE CODES INSEE UNIQUES ---")
    print(df["code_insee"].nunique())

    print("\n--- LONGUEUR DES CODES INSEE ---")
    print(
        df["code_insee"]
        .astype(str)
        .str.len()
        .value_counts()
    )

    print("\n--- DOUBLONS SUR CODE INSEE ---")
    print(
        df.duplicated(
            subset=["code_insee"]
        ).sum()
    )


# ANALYSE DES COLONNES NUMÉRIQUES

colonnes_numeriques = [
    "2012",
    "2013",
    "2014",
    "2015",
    "2016",
    "2017",
    "2018",
    "2019",
    "2020",
    "2021",
    "2022",
    "2023",
    "2024",
    "2025"
]

colonnes_presentes = [
    col for col in colonnes_numeriques
    if col in df.columns
]

print("\n--- COLONNES NUMÉRIQUES PRÉSENTES ---")
print(colonnes_presentes)


# EXEMPLES DE VALEURS NUMÉRIQUES

print("\n--- EXEMPLES DE VALEURS NUMÉRIQUES ---")

print(
    df[
        ["code_insee", "nom_brut"] + colonnes_presentes
    ].head(20)
)


# FOCUS VARIABLE UTILISÉE POUR 2022

if "2022" in df.columns:

    print("\n--- VARIABLE UTILISÉE POUR 2022 ---")
    print(df[["code_insee", "nom_brut", "2022"]].head(20))

    print("\n--- VALEURS MANQUANTES SUR 2022 ---")
    print(df["2022"].isna().sum())
    print(df[df["code_insee"].astype(str).str.len() != 5][["code_insee", "nom_brut"]])