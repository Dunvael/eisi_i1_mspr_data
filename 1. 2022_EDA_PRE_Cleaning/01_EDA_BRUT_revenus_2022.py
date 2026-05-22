import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt


# CONFIGURATION

# Chemin vers le fichier brut des revenus médians
FILE_RAW = "data_raw/2022_raw/1_revenu_median_2022/REVENU_2021_DISPONIBLE_PAR_COM.csv"


# LECTURE DU DATASET BRUT

# Lecture du fichier CSV brut
# dtype=str permet de conserver les formats d'origine
try:
    df = pd.read_csv(
        FILE_RAW,
        sep=";",
        dtype=str,
        encoding="utf-8"
    )
except UnicodeDecodeError:
    df = pd.read_csv(
        FILE_RAW,
        sep=";",
        dtype=str,
        encoding="latin1"
    )


# INFOS GÉNÉRALES

print("\n--- DIMENSIONS DU DATASET ---")
print(df.shape)

print("\n--- APERÇU DES DONNÉES ---")
print(df.head())

print("\n--- TYPES DES COLONNES ---")
print(df.info())

print("\n--- NOMS DES COLONNES ---")
print(df.columns)


# ANALYSE DES VALEURS MANQUANTES

print("\n--- NOMBRE DE NaN PAR COLONNE ---")
print(df.isna().sum())

print("\n--- POURCENTAGE DE NaN ---")
print((df.isna().mean() * 100).round(2))


# VISUALISATION DES VALEURS MANQUANTES

msno.matrix(df)
plt.title("Répartition des valeurs manquantes")
plt.show()

msno.bar(df)
plt.title("Nombre de valeurs manquantes")
plt.show()


# ANALYSE DES DOUBLONS

print("\n--- DOUBLONS ---")
print(df.duplicated().sum())


# ANALYSE DES CODES INSEE

# Vérification de la clé principale CODGEO
if "CODGEO" in df.columns:

    print("\n--- NOMBRE DE CODES INSEE UNIQUES ---")
    print(df["CODGEO"].nunique())

    print("\n--- LONGUEUR DES CODES INSEE ---")
    print(df["CODGEO"].astype(str).str.len().value_counts())

    print("\n--- DOUBLONS SUR CODE INSEE ---")
    print(df.duplicated(subset=["CODGEO"]).sum())


# ANALYSE DES REVENUS MÉDIANS

# Q221 correspond au revenu médian communal
if "Q221" in df.columns:

    print("\n--- DISTRIBUTION DES REVENUS MÉDIANS ---")
    print(df["Q221"].describe())

    print("\n--- EXEMPLES DE VALEURS REVENU MÉDIAN ---")
    print(df["Q221"].head(20))

    print("\n--- NOMBRE DE REVENUS MANQUANTS ---")
    print(df["Q221"].isna().sum())


# ANALYSE DES COMMUNES SANS REVENU

if "Q221" in df.columns and "CODGEO" in df.columns:

    print("\n--- COMMUNES SANS REVENU ---")
    print(df[df["Q221"].isna()][["CODGEO", "Q221"]].head(20))