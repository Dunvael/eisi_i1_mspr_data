import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt


# CONFIGURATION

# Chemin vers le fichier brut catégories sociales
FILE_RAW = "data_raw/2022_raw/3_categorie_sociale_2022/CATEGORIE_SOCIAL_ET_DEMOGRAPHIE_PAR_COM_2011_TO_2022.xlsx"


# LECTURE DU DATASET BRUT

# Le fichier Excel contient plusieurs lignes avant le vrai tableau.
# On détecte automatiquement la ligne contenant CODGEO.

df_preview = pd.read_excel(
    FILE_RAW,
    nrows=80,
    header=None
)

header_idx = None

# Recherche automatique de la ligne contenant les noms de colonnes
for i, row in df_preview.iterrows():

    if row.astype(str).str.contains("CODGEO").any():
        header_idx = i
        break

# Vérification sécurité
if header_idx is None:
    raise ValueError("Impossible de trouver la ligne d'en-tête contenant CODGEO.")


# Lecture réelle du fichier Excel
df = pd.read_excel(
    FILE_RAW,
    skiprows=header_idx,
    dtype=str
)


# NETTOYAGE MINIMAL DES NOMS DE COLONNES

# Suppression des espaces, retours ligne et caractères parasites
df.columns = (
    df.columns
    .astype(str)
    .str.strip()
    .str.replace("\n", "", regex=False)
    .str.replace(" ", "", regex=False)
    .str.replace('"', "", regex=False)
    .str.replace("'", "", regex=False)
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

# Nombre de valeurs manquantes
print("\n--- NOMBRE DE NaN PAR COLONNE ---")
print(df.isna().sum())

# Pourcentage de valeurs manquantes
print("\n--- POURCENTAGE DE NaN ---")
print((df.isna().mean() * 100).round(2))


# VISUALISATION DES VALEURS MANQUANTES

# Matrice des valeurs manquantes
msno.matrix(df)
plt.title("Répartition des valeurs manquantes - Catégories sociales")
plt.show()

# Histogramme des valeurs manquantes
msno.bar(df)
plt.title("Nombre de valeurs manquantes - Catégories sociales")
plt.show()


# ANALYSE DES DOUBLONS

# Vérification des doublons globaux
print("\n--- DOUBLONS ---")
print(df.duplicated().sum())


# ANALYSE DES CODES INSEE

# Vérification de la clé géographique CODGEO
if "CODGEO" in df.columns:

    # Nombre de communes uniques
    print("\n--- NOMBRE DE CODES INSEE UNIQUES ---")
    print(df["CODGEO"].nunique())

    # Vérification du format des codes INSEE
    print("\n--- LONGUEUR DES CODES INSEE ---")
    print(df["CODGEO"].astype(str).str.len().value_counts())

    # Recherche de doublons sur CODGEO
    print("\n--- DOUBLONS SUR CODE INSEE ---")
    print(df.duplicated(subset=["CODGEO"]).sum())


# ANALYSE DES COLONNES CATÉGORIES SOCIALES

# Colonnes correspondant aux catégories sociales
colonnes_categories = [

    # AGRICULTEURS
    "C22_POP1524_STAT_GSEC11_21",
    "C22_POP2554_STAT_GSEC11_21",
    "C22_POP55P_STAT_GSEC11_21",

    # CADRES
    "C22_POP1524_STAT_GSEC13_23",
    "C22_POP2554_STAT_GSEC13_23",
    "C22_POP55P_STAT_GSEC13_23",

    # EMPLOYÉS
    "C22_POP1524_STAT_GSEC15_25",
    "C22_POP2554_STAT_GSEC15_25",
    "C22_POP55P_STAT_GSEC15_25",

    # OUVRIERS
    "C22_POP1524_STAT_GSEC16_26",
    "C22_POP2554_STAT_GSEC16_26",
    "C22_POP55P_STAT_GSEC16_26",
]

# Conservation uniquement des colonnes réellement présentes
colonnes_presentes = [
    col for col in colonnes_categories
    if col in df.columns
]

print("\n--- COLONNES CATÉGORIES SOCIALES PRÉSENTES ---")
print(colonnes_presentes)


# ANALYSE DES VALEURS MANQUANTES SUR LES COLONNES SOCIALES

print("\n--- VALEURS MANQUANTES SUR COLONNES SOCIALES ---")

print(
    df[colonnes_presentes]
    .isna()
    .sum()
)


# EXEMPLES DE VALEURS

print("\n--- EXEMPLES DE VALEURS SUR COLONNES SOCIALES ---")

print(
    df[
        ["CODGEO"] + colonnes_presentes
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