import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt


# CONFIGURATION

# Chemin vers le fichier brut chômage / activité
FILE_RAW = "data_raw/2022_raw/2_chomage_2022/ACTIVITE_IMMIGRATION_PAR_COM_2022.xlsx"


# LECTURE DU DATASET BRUT

# Le fichier Excel contient des lignes d'en-tête avant le vrai tableau.
# On lit d'abord les premières lignes pour trouver automatiquement la ligne contenant CODGEO.

df_preview = pd.read_excel(FILE_RAW, nrows=20, header=None)

header_idx = None

for i, row in df_preview.iterrows():
    if row.astype(str).str.contains("CODGEO").any():
        header_idx = i
        break

if header_idx is None:
    raise ValueError("Impossible de trouver la ligne d'en-tête contenant CODGEO.")

# Lecture du fichier Excel à partir de la vraie ligne d'en-tête
df = pd.read_excel(FILE_RAW, skiprows=header_idx, dtype=str)


# NETTOYAGE MINIMAL DES NOMS DE COLONNES

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
plt.title("Répartition des valeurs manquantes - Chômage 2022")
plt.show()

msno.bar(df)
plt.title("Nombre de valeurs manquantes - Chômage 2022")
plt.show()


# ANALYSE DES DOUBLONS

print("\n--- DOUBLONS ---")
print(df.duplicated().sum())


# ANALYSE DES CODES INSEE

if "CODGEO" in df.columns:

    print("\n--- NOMBRE DE CODES INSEE UNIQUES ---")
    print(df["CODGEO"].nunique())

    print("\n--- LONGUEUR DES CODES INSEE ---")
    print(df["CODGEO"].astype(str).str.len().value_counts())

    print("\n--- DOUBLONS SUR CODE INSEE ---")
    print(df.duplicated(subset=["CODGEO"]).sum())


# ANALYSE DES COLONNES UTILISÉES POUR LE CALCUL DU CHÔMAGE

colonnes_chomage = [
    "INATC1_SEXE1_TACTR11",
    "INATC1_SEXE2_TACTR11",
    "INATC2_SEXE1_TACTR11",
    "INATC2_SEXE2_TACTR11",
    "INATC1_SEXE1_TACTR12",
    "INATC1_SEXE2_TACTR12",
    "INATC2_SEXE1_TACTR12",
    "INATC2_SEXE2_TACTR12",
]

colonnes_presentes = [col for col in colonnes_chomage if col in df.columns]

print("\n--- COLONNES CHÔMAGE PRÉSENTES ---")
print(colonnes_presentes)

print("\n--- VALEURS MANQUANTES SUR COLONNES CHÔMAGE ---")
print(df[colonnes_presentes].isna().sum())

print("\n--- EXEMPLES DE VALEURS SUR COLONNES CHÔMAGE ---")
print(df[["CODGEO"] + colonnes_presentes].head(20))


# ANALYSE DES VALEURS NON NUMÉRIQUES

for col in colonnes_presentes:
    valeurs_non_num = pd.to_numeric(
        df[col]
        .astype(str)
        .str.replace(r"\s+", "", regex=True)
        .str.replace(",", ".", regex=False),
        errors="coerce"
    ).isna().sum()

    print(f"{col} - valeurs non convertibles en numérique : {valeurs_non_num}")