import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv(
    "data_cleaned/2022/04_densite_population_2022_cleaned.csv",
    sep=";"
)

cols = [
    "population",
    "superficie_km2",
    "densite"]

print("\n--- INFO DATASET ---")
print(df.shape)
print(df.info())

print("\n--- NA PAR COLONNE ---")
print(df.isna().sum())

print("\n--- POURCENTAGE DE NaN ---")
print((df.isna().mean() * 100).round(2))

print("\n--- STATISTIQUES ---")
print(df[cols].describe())

# Missingno
msno.matrix(df)
plt.title("Valeurs manquantes - densité population")
plt.show()

msno.bar(df)
plt.title("Nombre de valeurs manquantes - densité population")
plt.show()

# Histogrammes
for col in cols:
    plt.figure(figsize=(8, 5))
    df[col].hist(bins=50)
    plt.title(f"Distribution - {col}")
    plt.xlabel(col)
    plt.ylabel("Nombre de communes")
    plt.show()

# Boxplots
for col in cols:
    plt.figure(figsize=(8, 3))
    sns.boxplot(x=df[col])
    plt.title(f"Valeurs aberrantes - {col}")
    plt.show()

# Valeurs extrêmes utiles à afficher
print("\n--- TOP 10 POPULATION ---")
print(df.sort_values("population", ascending=False).head(10))

print("\n--- TOP 10 DENSITÉ ---")
print(df.sort_values("densite", ascending=False).head(10))

print("\n--- SUPERFICIE <= 0 ---")
print(df[df["superficie_km2"] <= 0])