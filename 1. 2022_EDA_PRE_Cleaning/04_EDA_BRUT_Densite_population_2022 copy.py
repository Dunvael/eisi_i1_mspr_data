import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt


# CONFIGURATION

# Chemin vers le fichier brut population / densité
FILE_RAW = "data_raw/2022_raw/4_densite_population_2022/POPULATION_ET_DENSITE_PAR_COM_2022.csv"


# LECTURE DU DATASET BRUT

# Lecture du fichier CSV brut
# dtype=str permet de conserver les formats d'origine, notamment les codes INSEE
df = pd.read_csv(
    FILE_RAW,
    dtype=str
)


# INFOS GÉNÉRALES

# Dimensions du dataset
print("\n--- DIMENSIONS DU DATASET ---")
print(df.shape)

# Aperçu des premières lignes
print("\n--- APERÇU DES DONNÉES ---")
print(df.head())

# Types des colonnes
print("\n--- TYPES DES COLONNES ---")
print(df.info())

# Liste des colonnes
print("\n--- NOMS DES COLONNES ---")
print(df.columns)


# ANALYSE DES VALEURS MANQUANTES

# Nombre de valeurs manquantes par colonne
print("\n--- NOMBRE DE NaN PAR COLONNE ---")
print(df.isna().sum())

# Pourcentage de valeurs manquantes par colonne
print("\n--- POURCENTAGE DE NaN ---")
print((df.isna().mean() * 100).round(2))


# VISUALISATION DES VALEURS MANQUANTES

# Matrice des valeurs manquantes
msno.matrix(df)
plt.title("Répartition des valeurs manquantes - Densité population")
plt.show()

# Histogramme des valeurs manquantes
msno.bar(df)
plt.title("Nombre de valeurs manquantes - Densité population")
plt.show()


# ANALYSE DES DOUBLONS

# Vérification des doublons globaux
print("\n--- DOUBLONS ---")
print(df.duplicated().sum())


# ANALYSE DES CODES INSEE

# Vérification de la clé géographique code_insee
if "code_insee" in df.columns:

    # Nombre de communes uniques
    print("\n--- NOMBRE DE CODES INSEE UNIQUES ---")
    print(df["code_insee"].nunique())

    # Vérification du format des codes INSEE
    print("\n--- LONGUEUR DES CODES INSEE ---")
    print(df["code_insee"].astype(str).str.len().value_counts())

    # Recherche de doublons sur code_insee
    print("\n--- DOUBLONS SUR CODE INSEE ---")
    print(df.duplicated(subset=["code_insee"]).sum())


# ANALYSE DES COLONNES NUMÉRIQUES

# Colonnes quantitatives utilisées dans le dataset densité
colonnes_numeriques = [
    "population",
    "superficie_km2",
    "densite"
]

# Conservation uniquement des colonnes réellement présentes
colonnes_presentes = [
    col for col in colonnes_numeriques
    if col in df.columns
]

print("\n--- COLONNES NUMÉRIQUES PRÉSENTES ---")
print(colonnes_presentes)


# Valeurs manquantes sur les colonnes numériques

print("\n--- VALEURS MANQUANTES SUR COLONNES NUMÉRIQUES ---")

print(
    df[colonnes_presentes]
    .isna()
    .sum()
)


# Exemples de valeurs numériques

print("\n--- EXEMPLES DE VALEURS NUMÉRIQUES ---")

print(
    df[
        ["code_insee"] + colonnes_presentes
    ].head(20)
)


# ANALYSE DES VALEURS NON NUMÉRIQUES

# Vérification des valeurs impossibles à convertir en numérique
for col in colonnes_presentes:

    valeurs_non_num = pd.to_numeric(
        df[col]
        .astype(str)
        .str.replace(r"\s+", "", regex=True)
        .str.replace(",", ".", regex=False),
        errors="coerce"
    ).isna().sum()

    print(
        f"{col} - valeurs non convertibles en numérique : {valeurs_non_num}"
    )


# STATISTIQUES DES COLONNES NUMÉRIQUES APRÈS CONVERSION TEMPORAIRE

df_num = df[colonnes_presentes].copy()

for col in colonnes_presentes:
    df_num[col] = pd.to_numeric(
        df_num[col]
        .astype(str)
        .str.replace(r"\s+", "", regex=True)
        .str.replace(",", ".", regex=False),
        errors="coerce"
    )

print("\n--- STATISTIQUES DES COLONNES NUMÉRIQUES ---")
print(df_num.describe())