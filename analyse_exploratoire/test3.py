import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv(
    "data_cleaned/2022/03_categorie_sociale_2022_cleaned.csv",
    sep=";"
)

cols = [
    "pourcentage_agri",
    "pourcentage_cadres",
    "pourcentage_employes",
    "pourcentage_ouvriers"
]

print("\n--- INFO DATASET ---")
print(df.shape)
print(df.info())

print("\n--- NA PAR COLONNE ---")
print(df.isna().sum())

print("\n--- POURCENTAGE DE NaN ---")
print((df.isna().mean() * 100).round(2))

print("\n--- STATISTIQUES ---")
print(df[cols].describe())

# ===== MISSINGNO =====
msno.matrix(df)
plt.title("Valeurs manquantes - catégorie sociale")
plt.show()

msno.bar(df)
plt.title("Nombre de valeurs manquantes - catégorie sociale")
plt.show()

# ===== HISTOGRAMMES =====
for col in cols:
    plt.figure(figsize=(8, 5))
    df[col].hist(bins=50)
    plt.title(f"Distribution - {col}")
    plt.xlabel(col)
    plt.ylabel("Nombre de communes")
    plt.show()

# ===== BOXPLOTS =====
for col in cols:
    plt.figure(figsize=(8, 3))
    sns.boxplot(x=df[col])
    plt.title(f"Valeurs aberrantes - {col}")
    plt.show()

# ===== CHECK SOMME DES POURCENTAGES =====
df["somme_pourcentages"] = df[cols].sum(axis=1, min_count=1)

print("\n--- SOMME DES POURCENTAGES ---")
print(df["somme_pourcentages"].describe())

print("\nNombre de communes avec somme > 100.5 :")
print((df["somme_pourcentages"] > 100.5).sum())

print("\nNombre de communes avec somme < 99.5 :")
print((df["somme_pourcentages"] < 99.5).sum())

print("\nCommunes avec NaN dans au moins une catégorie :")
print(df[df[cols].isna().any(axis=1)].head(20))