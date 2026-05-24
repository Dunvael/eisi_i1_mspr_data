import pandas as pd


# CONFIGURATION

FILE_RAW = "data_raw/2022_raw/6_taux_immigration_2022/ACTIVITE_IMMIGRATION_PAR_COM_2022.xlsx"


# LECTURE DU DATASET BRUT

# Le fichier contient des lignes techniques avant le vrai tableau.
# On cherche automatiquement la ligne contenant CODGEO.

df_preview = pd.read_excel(
    FILE_RAW,
    nrows=20,
    header=None
)

header_idx = None

for i, row in df_preview.iterrows():

    if row.astype(str).str.contains("CODGEO").any():
        header_idx = i
        break

if header_idx is None:
    raise ValueError("Impossible de trouver la ligne contenant CODGEO.")


# Lecture réelle du fichier à partir de l'en-tête détecté
df = pd.read_excel(
    FILE_RAW,
    skiprows=header_idx,
    dtype=str
)


# Nettoyage léger des noms de colonnes
df.columns = (
    df.columns
    .astype(str)
    .str.strip()
    .str.replace("\n", "", regex=False)
    .str.replace(" ", "", regex=False)
)


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

if "CODGEO" in df.columns:

    df["code_insee"] = (
        df["CODGEO"]
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

# Colonnes utilisées ensuite pour calculer le taux d'immigration :
# INATC1 = population française
# INATC2 = population étrangère

colonnes_francais = [
    col for col in df.columns
    if col.startswith("INATC1_SEXE")
]

colonnes_etrangers = [
    col for col in df.columns
    if col.startswith("INATC2_SEXE")
]

colonnes_numeriques = (
    colonnes_francais
    + colonnes_etrangers
)

colonnes_presentes = [
    col for col in colonnes_numeriques
    if col in df.columns
]

print("\n--- COLONNES NUMÉRIQUES PRÉSENTES ---")
print(colonnes_presentes)

print("\n--- NOMBRE DE COLONNES FRANÇAIS DÉTECTÉES ---")
print(len(colonnes_francais))

print("\n--- NOMBRE DE COLONNES ÉTRANGERS DÉTECTÉES ---")
print(len(colonnes_etrangers))