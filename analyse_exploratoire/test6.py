import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt
import seaborn as sns

# Chargement dataset
df = pd.read_csv(
    "data_cleaned/2022/06_taux_immigration_2022_cleaned.csv",
    sep=";"
)

print("\n--- INFO DATASET ---")
print(df.shape)
print(df.info())

print("\n--- NA PAR COLONNE ---")
print(df.isna().sum())

print("\n--- POURCENTAGE DE NaN ---")
print((df.isna().mean() * 100).round(2))

print("\n--- STATISTIQUES ---")
print(df["taux_immigration"].describe())

# ===== MISSINGNO =====

msno.matrix(df)
plt.title("Valeurs manquantes - taux immigration")
plt.show()

msno.bar(df)
plt.title("Nombre de valeurs manquantes - taux immigration")
plt.show()

# ===== HISTOGRAMME =====

plt.figure(figsize=(8,5))
df["taux_immigration"].hist(bins=50)

plt.title("Distribution du taux d'immigration")
plt.xlabel("Taux immigration (%)")
plt.ylabel("Nombre de communes")

plt.show()

# ===== BOXPLOT =====

plt.figure(figsize=(8,3))

sns.boxplot(x=df["taux_immigration"])

plt.title("Valeurs aberrantes - taux immigration")

plt.show()

# ===== TOP COMMUNES =====

print("\n--- TOP 20 taux immigration ---")
print(
    df.sort_values(
        "taux_immigration",
        ascending=False
    ).head(20)
)

# ===== COMMUNES SANS DONNÉES =====

print("\n--- Taux immigration NaN ---")

print(
    df[df["taux_immigration"].isna()]
    .head(20)
)

# ===== VALEURS EXTRÊMES =====

print(
    "\nCommunes avec taux immigration > 50% :",
    (df["taux_immigration"] > 50).sum()
)

print(
    "Communes avec taux immigration = 100% :",
    (df["taux_immigration"] == 100).sum()
)