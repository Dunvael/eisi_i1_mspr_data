import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt

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

# 1. Visualiser où sont les NaN
msno.matrix(df)
plt.title("Distribution des valeurs manquantes")
plt.show()

# 2. Quantité de NaN par colonne
msno.bar(df)
plt.title("Nombre de valeurs manquantes")
plt.show()

# 3. Corrélation des NaN (optionnel ici)
msno.heatmap(df)
plt.title("Corrélation des valeurs manquantes")
plt.show()

# ===== DISTRIBUTION =====

plt.figure(figsize=(8,5))
df["revenu_median"].hist(bins=50)
plt.title("Distribution du revenu médian")
plt.xlabel("Revenu")
plt.ylabel("Fréquence")
plt.show()

# ===== ANALYSE SIMPLE =====

print("\n--- STATISTIQUES ---")
print(df["revenu_median"].describe())

# ===== NA CHECK =====
pourcentage_nan = df["revenu_median"].isna().mean() * 100
print(f"\nPourcentage de NaN revenu : {pourcentage_nan:.2f}%")