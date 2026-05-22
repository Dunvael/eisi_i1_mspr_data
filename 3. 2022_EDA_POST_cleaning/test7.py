import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv(
    "data_cleaned/2022/07_associations_2022_cleaned.csv",
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
print(df["nb_associations"].describe())

# Missingno
msno.matrix(df)
plt.title("Valeurs manquantes - associations")
plt.show()

msno.bar(df)
plt.title("Nombre de valeurs manquantes - associations")
plt.show()

# Histogramme
plt.figure(figsize=(8, 5))
df["nb_associations"].hist(bins=50)
plt.title("Distribution du nombre d'associations")
plt.xlabel("Nombre d'associations")
plt.ylabel("Nombre de communes")
plt.show()

# Boxplot
plt.figure(figsize=(8, 3))
sns.boxplot(x=df["nb_associations"])
plt.title("Valeurs aberrantes - nombre d'associations")
plt.show()

# Top communes
print("\n--- TOP 20 communes avec le plus d'associations créés---")
print(
    df.sort_values("nb_associations", ascending=False)
    .head(20)
)

# NaN
print("\n--- Communes avec nb_associations NaN ---")
print(
    df[df["nb_associations"].isna()]
    .head(20)
)

# Valeurs spécifiques
print("\nCommunes avec 0 association :", (df["nb_associations"] == 0).sum())
print("Communes avec plus de 100 associations :", (df["nb_associations"] > 100).sum())