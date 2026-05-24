import pandas as pd


# CONFIGURATION

FILE_RAW = "data_raw/2022_raw/7_association_2022/CREATION_ASSOCIATION_PAR_COM_2000_a_2024.xlsx"


# LECTURE DU DATASET BRUT

df = pd.read_excel(
    FILE_RAW,
    dtype=str
)

df.columns = df.columns.astype(str).str.strip()


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

if "INSEE" in df.columns:

    df["code_insee"] = (
        df["INSEE"]
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
    "ASSO2022"
]

colonnes_presentes = [
    col for col in colonnes_numeriques
    if col in df.columns
]

print("\n--- COLONNES NUMÉRIQUES PRÉSENTES ---")
print(colonnes_presentes)


# EXEMPLES DE VALEURS NUMÉRIQUES

print("\n--- EXEMPLES DE VALEURS NUMÉRIQUES ---")

colonnes_affichage = []

if "INSEE" in df.columns:
    colonnes_affichage.append("INSEE")

if "NOM" in df.columns:
    colonnes_affichage.append("NOM")

print(
    df[
        colonnes_affichage + colonnes_presentes
    ].head(20)
)