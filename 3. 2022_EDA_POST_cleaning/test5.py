import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv(
    "data_cleaned/2022/05_demographie_2022_cleaned.csv",
    sep=";"
)

cols = [
    "pct_jeunes",
    "pct_seniors",
    "age_median"
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

msno.matrix(df)
plt.title("Valeurs manquantes - démographie")
plt.show()

msno.bar(df)
plt.title("Nombre de valeurs manquantes - démographie")
plt.show()

for col in cols:
    plt.figure(figsize=(8, 5))
    df[col].hist(bins=50)
    plt.title(f"Distribution - {col}")
    plt.xlabel(col)
    plt.ylabel("Nombre de communes")
    plt.show()

for col in cols:
    plt.figure(figsize=(8, 3))
    sns.boxplot(x=df[col])
    plt.title(f"Valeurs aberrantes - {col}")
    plt.show()

print("\n--- TOP 10 communes les plus jeunes ---")
print(df.sort_values("pct_jeunes", ascending=False).head(10))

print("\n--- TOP 10 communes les plus âgées ---")
print(df.sort_values("pct_seniors", ascending=False).head(10))

print(
    "Communes avec âge médian NaN :",
    df["age_median"].isna().sum()
)

print("\n--- Age médian NaN ---")
print(df[df["age_median"].isna()].head(20))