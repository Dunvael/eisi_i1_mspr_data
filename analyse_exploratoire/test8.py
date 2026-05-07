import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv(
    "data_cleaned/2022/08_creation_entreprises_2022_cleaned.csv",
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
print(df["nb_creations_entreprises"].describe())

msno.matrix(df)
plt.title("Valeurs manquantes - créations entreprises")
plt.show()

msno.bar(df)
plt.title("Nombre de valeurs manquantes - créations entreprises")
plt.show()

plt.figure(figsize=(8, 5))
df["nb_creations_entreprises"].hist(bins=50)
plt.title("Distribution des créations d'entreprises")
plt.xlabel("Nombre de créations d'entreprises")
plt.ylabel("Nombre de communes")
plt.show()

plt.figure(figsize=(8, 3))
sns.boxplot(x=df["nb_creations_entreprises"])
plt.title("Valeurs aberrantes - créations entreprises")
plt.show()

print("\n--- TOP 20 créations entreprises ---")
print(
    df.sort_values("nb_creations_entreprises", ascending=False)
    .head(20)
)

print("\n--- Communes avec nb_creations_entreprises NaN ---")
print(
    df[df["nb_creations_entreprises"].isna()]
    .head(20)
)

print("\nCommunes avec 0 création :", (df["nb_creations_entreprises"] == 0).sum())
print("Communes avec plus de 100 créations :", (df["nb_creations_entreprises"] > 100).sum())