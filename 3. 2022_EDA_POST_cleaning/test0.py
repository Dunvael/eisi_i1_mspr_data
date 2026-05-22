import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt


import matplotlib
matplotlib.use("TkAgg")


# Charger le fichier cleaned
df = pd.read_csv(
    "data_cleaned/communes_2022_cleaned.csv",
    sep=";",
    dtype=str
)

# ===== INFOS GÉNÉRALES =====
print("\n--- INFO DATASET ---")
print(df.shape)
print(df.info())

print("\n--- APERÇU DES DONNÉES ---")
print(df.head())

print("\n--- COLONNES ---")
print(df.columns)

# ===== NETTOYAGE LÉGER POUR VÉRIFICATION =====
for col in ["code_insee", "nom_commune", "code_departement", "code_region"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

# ===== VALEURS MANQUANTES =====
print("\n--- NA PAR COLONNE ---")
print(df.isna().sum())

print("\n--- POURCENTAGE DE NA PAR COLONNE ---")
print((df.isna().mean() * 100).round(2))

# ===== MISSINGNO =====
msno.matrix(df)
plt.title("Distribution des valeurs manquantes - Communes 2022")
plt.show()

msno.bar(df)
plt.title("Nombre de valeurs manquantes - Communes 2022")
plt.show()

# ===== CONTRÔLES QUALITÉ =====
print("\n--- DOUBLONS ---")
print("Nombre de lignes dupliquées :", df.duplicated().sum())

if "code_insee" in df.columns:
    print("Nombre de codes INSEE uniques :", df["code_insee"].nunique())
    print("Nombre de codes INSEE dupliqués :", df["code_insee"].duplicated().sum())

if "nom_commune" in df.columns:
    print("Nombre de communes uniques :", df["nom_commune"].nunique())

if "code_departement" in df.columns:
    print("Nombre de départements :", df["code_departement"].nunique())
    print("\n--- RÉPARTITION PAR DÉPARTEMENT ---")
    print(df["code_departement"].value_counts().sort_index())

if "code_region" in df.columns:
    print("Nombre de régions :", df["code_region"].nunique())
    print("\n--- RÉPARTITION PAR RÉGION ---")
    print(df["code_region"].value_counts().sort_index())

# ===== DISTRIBUTION PAR DÉPARTEMENT =====
if "code_departement" in df.columns:
    plt.figure(figsize=(12, 5))
    df["code_departement"].value_counts().sort_index().plot(kind="bar")
    plt.title("Nombre de communes par département")
    plt.xlabel("Département")
    plt.ylabel("Nombre de communes")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

# ===== DISTRIBUTION PAR RÉGION =====
if "code_region" in df.columns:
    plt.figure(figsize=(8, 5))
    df["code_region"].value_counts().sort_index().plot(kind="bar")
    plt.title("Nombre de communes par région")
    plt.xlabel("Région")
    plt.ylabel("Nombre de communes")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# ===== CHECK FORMAT CODE INSEE =====
if "code_insee" in df.columns:
    print("\n--- FORMAT CODE INSEE ---")
    print(df["code_insee"].str.len().value_counts().sort_index())

    codes_invalides = df[~df["code_insee"].str.match(r"^\d{5}$", na=False)]
    print("Nombre de codes INSEE invalides :", len(codes_invalides))

    if not codes_invalides.empty:
        print(codes_invalides.head())

print("\n Test post-cleaning terminé pour communes_2022_cleaned.csv")