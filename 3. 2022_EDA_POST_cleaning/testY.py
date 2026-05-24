import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt
import seaborn as sns


df = pd.read_csv(
    "data_cleaned/2022/Y_classe_politique_2022_cleaned.csv",
    sep=";",
    encoding="utf-8"
)

print("\n--- INFO DATASET ---")
print(df.shape)
print(df.info())

print("\n--- APERÇU DES DONNÉES ---")
print(df.head())

print("\n--- COLONNES ---")
print(df.columns)

print("\n--- NA PAR COLONNE ---")
print(df.isna().sum())

print("\n--- POURCENTAGE DE NaN ---")
print((df.isna().mean() * 100).round(2))

print("\n--- DOUBLONS ---")
print(df.duplicated().sum())

print("\n--- DOUBLONS SUR CODE INSEE ---")
print(df.duplicated(subset=["code_insee"]).sum())

print("\n--- DISTRIBUTION DES CLASSES POLITIQUES ---")
print(df["classe_politique"].value_counts())

print("\n--- POURCENTAGE DES CLASSES POLITIQUES ---")
print((df["classe_politique"].value_counts(normalize=True) * 100).round(2))

msno.matrix(df)
plt.title("Valeurs manquantes - résultats électoraux")
plt.show()

msno.bar(df)
plt.title("Nombre de valeurs manquantes - résultats électoraux")
plt.show()

plt.figure(figsize=(8, 5))
df["classe_politique"].value_counts().plot(kind="bar")
plt.title("Distribution des classes politiques")
plt.xlabel("Classe politique")
plt.ylabel("Nombre de communes")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

plt.figure(figsize=(8, 5))
sns.countplot(
    data=df,
    x="classe_politique",
    order=df["classe_politique"].value_counts().index
)
plt.title("Répartition des communes par classe politique")
plt.xlabel("Classe politique")
plt.ylabel("Nombre de communes")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

cols_scores = [
    "score_extreme_droite",
    "score_extreme_gauche",
    "score_centre",
    "score_droite",
    "score_gauche",
]

print("\n--- STATISTIQUES DES SCORES POLITIQUES ---")
print(df[cols_scores].describe())

plt.figure(figsize=(10, 5))
df[cols_scores].mean().sort_values(ascending=False).plot(kind="bar")
plt.title("Scores moyens par bloc politique")
plt.xlabel("Bloc politique")
plt.ylabel("Score moyen (%)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

print("\n--- TOP 20 communes score extrême droite ---")
print(
    df.sort_values("score_extreme_droite", ascending=False)
    .head(20)
)

print("\n--- TOP 20 communes score centre ---")
print(
    df.sort_values("score_centre", ascending=False)
    .head(20)
)

print("\n--- TOP 20 communes score gauche ---")
print(
    df.sort_values("score_gauche", ascending=False)
    .head(20)
)

print("\n--- TOP 20 communes score droite ---")
print(
    df.sort_values("score_droite", ascending=False)
    .head(20)
)

print("\nCommunes classées extrême droite :", (df["classe_politique"] == "extreme_droite").sum())
print("Communes classées centre :", (df["classe_politique"] == "centre").sum())
print("Communes classées gauche :", (df["classe_politique"] == "gauche").sum())
print("Communes classées droite :", (df["classe_politique"] == "droite").sum())
print("Communes classées extrême gauche :", (df["classe_politique"] == "extreme_gauche").sum())