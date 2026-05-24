import pandas as pd


# CONFIGURATION

FILE_RAW = "data_raw/2022_raw/9_criminalite_2022/CRIMINALITE_PAR_COM_2022.parquet"

FILE_PASSAGE = ("data_raw/2022_raw/referentiels/table_passage_annuelle_2025.xlsx")


# LECTURE DU DATASET BRUT CRIMINALITÉ

df = pd.read_parquet(FILE_RAW)


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


# ANALYSE DES CODES INSEE 2025

if "CODGEO_2025" in df.columns:

    df["CODGEO_2025"] = (
        df["CODGEO_2025"]
        .astype(str)
        .str.strip()
        .str.zfill(5)
    )

    print("\n--- NOMBRE DE CODES INSEE UNIQUES ---")
    print(df["CODGEO_2025"].nunique())

    print("\n--- LONGUEUR DES CODES INSEE ---")
    print(
        df["CODGEO_2025"]
        .astype(str)
        .str.len()
        .value_counts()
    )

    print("\n--- DOUBLONS SUR CODE INSEE ---")
    print(
        df.duplicated(
            subset=["CODGEO_2025"]
        ).sum()
    )


# ANALYSE DES ANNÉES

if "annee" in df.columns:

    print("\n--- ANNÉES DISPONIBLES ---")
    print(
        df["annee"]
        .value_counts()
        .sort_index()
    )


# ANALYSE DES INDICATEURS DISPONIBLES

if "indicateur" in df.columns:

    print("\n--- INDICATEURS DISPONIBLES ---")
    print(
        df["indicateur"]
        .unique()
    )


# ANALYSE DES COLONNES NUMÉRIQUES

colonnes_numeriques = [
    "taux_pour_mille",
    "complement_info_taux"
]

colonnes_presentes = [
    col for col in colonnes_numeriques
    if col in df.columns
]

print("\n--- COLONNES NUMÉRIQUES PRÉSENTES ---")
print(colonnes_presentes)


# EXEMPLES DE VALEURS NUMÉRIQUES

print("\n--- EXEMPLES DE VALEURS NUMÉRIQUES ---")

colonnes_affichage = ["CODGEO_2025","annee","indicateur"] + colonnes_presentes

print(df[colonnes_affichage].head(20))


# ANALYSE TABLE DE PASSAGE

passage = pd.read_excel(FILE_PASSAGE,dtype=str,header=5)

passage.columns = (passage.columns.astype(str).str.strip())

print("\n--- DIMENSIONS TABLE DE PASSAGE ---")
print(passage.shape)

print("\n--- COLONNES TABLE DE PASSAGE ---")
print(passage.columns)

print("\n--- APERÇU TABLE DE PASSAGE ---")
print(passage[["CODGEO_2025", "CODGEO_2022"]].head(20))