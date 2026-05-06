import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt
import seaborn as sns


import matplotlib
matplotlib.use("TkAgg")


# Charger le fichier cleaned
df = pd.read_csv(
    "data_cleaned/2022/01_revenus_median_2021_cleaned.csv",
    sep=";"
)

# ===== INFOS GÉNÉRALES =====
print("\n--- INFO DATASET ---")
print(df.shape)
print(df.info())

print("\n--- NA PAR COLONNE ---")
print(df.isna().sum())

# ===== MISSINGNO =====
msno.matrix(df)
plt.title("Distribution des valeurs manquantes")
plt.show()

msno.bar(df)
plt.title("Nombre de valeurs manquantes")
plt.show()

# ===== DISTRIBUTION =====
plt.figure(figsize=(8,5))
df["revenu_median"].hist(bins=50)
plt.title("Distribution du revenu médian")
plt.xlabel("Revenu médian")
plt.ylabel("Nombre de communes")
plt.show()

# ===== BOXPLOT =====
plt.figure(figsize=(8,3))
sns.boxplot(x=df["revenu_median"])
plt.title("Détection des valeurs aberrantes")
plt.show()

# ===== STATISTIQUES =====
print("\n--- STATISTIQUES ---")
print(df["revenu_median"].describe())

# ===== NA CHECK =====
pourcentage_nan = df["revenu_median"].isna().mean() * 100
print(f"\nPourcentage de NaN revenu : {pourcentage_nan:.2f}%")