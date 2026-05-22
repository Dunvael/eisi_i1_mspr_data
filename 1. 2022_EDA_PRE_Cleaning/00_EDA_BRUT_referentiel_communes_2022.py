import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt


# CONFIGURATION

# Chemin vers le fichier brut du référentiel INSEE 2022
FILE_RAW = "data_raw/2022_raw/0_code_insee_2022/communes_2022.csv"


# LECTURE DU DATASET BRUT

# Lecture du fichier CSV brut :
# - sep="," : séparateur du fichier
# - dtype=str : permet de conserver les codes INSEE avec leurs zéros
# - encoding="utf-8" : gestion correcte des accents
df = pd.read_csv(
    FILE_RAW,
    sep=",",
    dtype=str,
    encoding="utf-8"
)


# INFOS GÉNÉRALES

# Affichage des dimensions :
# nombre de lignes et de colonnes
print("\n--- DIMENSIONS DU DATASET ---")
print(df.shape)

# Aperçu des premières lignes du dataset
print("\n--- APERÇU DES DONNÉES ---")
print(df.head())

# Affichage des types des colonnes :
# utile pour détecter les incohérences de format
print("\n--- TYPES DES COLONNES ---")
print(df.info())

# Liste des colonnes disponibles dans le dataset
print("\n--- NOMS DES COLONNES ---")
print(df.columns)


# ANALYSE DES VALEURS MANQUANTES

# Nombre de valeurs manquantes par colonne
print("\n--- NOMBRE DE NaN PAR COLONNE ---")
print(df.isna().sum())

# Pourcentage de valeurs manquantes
# utile pour mesurer la qualité des données
print("\n--- POURCENTAGE DE NaN ---")
print((df.isna().mean() * 100).round(2))


# VISUALISATION DES VALEURS MANQUANTES AVEC MISSINGNO

# Visualisation graphique de la répartition des valeurs manquantes
msno.matrix(df)
plt.title("Répartition des valeurs manquantes")
plt.show()

# Visualisation du nombre de valeurs présentes/manquantes
msno.bar(df)
plt.title("Nombre de valeurs manquantes")
plt.show()


# ANALYSE DES DOUBLONS

# Vérification des doublons complets dans le dataset
print("\n--- DOUBLONS ---")
print(df.duplicated().sum())


# ANALYSE DES CODES INSEE

# Vérifications sur la clé principale de notre dataset : le code INSEE
if "COM" in df.columns:

    # Nombre de codes INSEE uniques  
    print("\n--- NOMBRE DE CODES INSEE UNIQUES ---")
    print(df["COM"].nunique())

    # Vérification de la longueur des codes INSEE : permet de détecter des formats incohérents
    print("\n--- LONGUEUR DES CODES INSEE ---")
    print(df["COM"].astype(str).str.len().value_counts())

    # Vérification des doublons sur le code INSEE
    print("\n--- DOUBLONS SUR CODE INSEE ---")
    print(df.duplicated(subset=["COM"]).sum())


# ANALYSE DES TYPES DE COMMUNES

# Répartition des différents types de communes : COM, ARM (Arrondissements municipaux)
if "TYPECOM" in df.columns:

    print("\n--- TYPES DE COMMUNES ---")
    print(df["TYPECOM"].value_counts())


# ANALYSE DES DÉPARTEMENTS

# Répartition des communes par département
# head(20) limite l'affichage aux 20 premiers départements
if "DEP" in df.columns:

    print("\n--- RÉPARTITION DES DÉPARTEMENTS ---")
    print(df["DEP"].value_counts().head(20))