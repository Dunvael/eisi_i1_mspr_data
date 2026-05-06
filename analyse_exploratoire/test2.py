import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt
import seaborn as sns

# Charger le fichier cleaned
df = pd.read_csv(
    "data_cleaned/2022/02_taux_chomage_2022_cleaned.csv",
    sep=";"
)

# ===== INFOS =====
print("\n--- INFO DATASET ---")
print(df.shape)
print(df.info())

print("\n--- NA PAR COLONNE ---")
print(df.isna().sum())

# ===== MISSINGNO =====
msno.matrix(df)
plt.title("Valeurs manquantes - taux de chômage")
plt.show()

msno.bar(df)
plt.title("Nombre de valeurs manquantes - taux de chômage")
plt.show()

# ===== HISTOGRAMME =====
plt.figure(figsize=(8,5))
df["taux_chomage"].hist(bins=50)
plt.title("Distribution du taux de chômage")
plt.xlabel("Taux de chômage (%)")
plt.ylabel("Nombre de communes")
plt.show()

# ===== BOXPLOT =====
plt.figure(figsize=(8,3))
sns.boxplot(x=df["taux_chomage"])
plt.title("Détection des valeurs aberrantes - taux de chômage")
plt.show()

# ===== STATS =====
print("\n--- STATISTIQUES ---")
print(df["taux_chomage"].describe())

# ===== NA CHECK =====
pourcentage_nan = df["taux_chomage"].isna().mean() * 100
print(f"\nPourcentage de NaN taux chômage : {pourcentage_nan:.4f}%")