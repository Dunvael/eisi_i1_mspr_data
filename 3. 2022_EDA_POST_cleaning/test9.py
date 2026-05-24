import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt
import seaborn as sns


# CHARGEMENT DATASET CLEANED

df = pd.read_csv(
    "data_cleaned/2022/09_criminalite_diff_ndiff_2022_cleaned.csv",
    sep=";"
)

colonnes_taux = [
    "taux_cambriolages_logement",
    "taux_degradations",
    "taux_trafic_stupefiants",
    "taux_usage_stupefiants",
    "taux_violences_intrafamiliales",
    "taux_violences_sexuelles",
    "taux_vols_avec_armes",
    "taux_vols_vehicule",
    "taux_vols_violents_sans_arme"
]


# INFOS GÉNÉRALES


print("\n--- INFO DATASET ---")
print(df.shape)
print(df.info())

print("\n--- APERÇU ---")
print(df.head())


# VALEURS MANQUANTES


print("\n--- NA PAR COLONNE ---")
print(df.isna().sum())

print("\n--- POURCENTAGE DE NaN ---")
print((df.isna().mean() * 100).round(2))

# Visualisation des valeurs manquantes
msno.matrix(df)
plt.title("Valeurs manquantes - criminalité 2022")
plt.show()

msno.bar(df)
plt.title("Nombre de valeurs manquantes - criminalité 2022")
plt.show()


# CONTRÔLES STRUCTURELS


print("\n--- DOUBLONS GLOBAUX ---")
print(df.duplicated().sum())

print("\n--- DOUBLONS SUR CODE INSEE ---")
print(df["code_insee"].duplicated().sum())

print("\n--- LONGUEUR DES CODES INSEE ---")
print(df["code_insee"].astype(str).str.len().value_counts())

print("\n--- COMMUNES SANS LOCALISATION ---")
print(df["localisation"].isna().sum())


# STATISTIQUES DES TAUX


print("\n--- STATISTIQUES DES TAUX ---")
print(df[colonnes_taux].describe())


# DISTRIBUTIONS


for col in colonnes_taux:
    plt.figure(figsize=(8, 5))
    df[col].hist(bins=50)
    plt.title(f"Distribution - {col}")
    plt.xlabel(col)
    plt.ylabel("Nombre de communes")
    plt.show()


# VALEURS ABERRANTES


for col in colonnes_taux:
    plt.figure(figsize=(8, 3))
    sns.boxplot(x=df[col])
    plt.title(f"Valeurs aberrantes - {col}")
    plt.show()


# CONTRÔLE DES VALEURS NÉGATIVES


print("\n--- VALEURS NÉGATIVES ---")

for col in colonnes_taux:
    nb_negatives = (df[col] < 0).sum()
    print(f"{col} : {nb_negatives}")


# COMMUNES AVEC AU MOINS UN TAUX MANQUANT


print("\n--- COMMUNES AVEC NaN DANS AU MOINS UN TAUX ---")
print(df[df[colonnes_taux].isna().any(axis=1)].head(20))


# CONTRÔLE DES TAUX À ZÉRO


print("\n--- NOMBRE DE VALEURS À 0 PAR TAUX ---")

for col in colonnes_taux:
    nb_zero = (df[col] == 0).sum()
    pct_zero = round((nb_zero / len(df)) * 100, 2)
    print(f"{col} : {nb_zero} communes ({pct_zero}%)")