import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import missingno as msno

print("Analyse Exploratoire - Associations 2024")


# 1. CHARGEMENT DES DONNÉES

file_path = "data_cleaned/2024/06_Associations/06_associations_2024_clean.csv"

try:
    df = pd.read_csv(file_path, sep=";")
    print(f"Fichier chargé avec succès ! ({len(df)} communes analysées)")
except FileNotFoundError:
    print(f"Erreur : Le fichier {file_path} est introuvable.")
    exit()

sns.set_theme(style="whitegrid")


# 2. VALEURS MANQUANTES

print(" Génération du graphique de complétude...")

# Colonnes ciblées
colonnes_visibles = ['code_insee_2024', 'nb_associations_total', 'annee']

# Graphique de complétude des données
fig_msno = plt.figure(figsize=(7, 5))
ax_msno = fig_msno.add_subplot(111)

msno.bar(df[colonnes_visibles], ax=ax_msno, fontsize=11, color=(0.4, 0.4, 0.4))
plt.title("Nombre de valeurs manquantes - Associations", fontsize=14, pad=20)
plt.tight_layout()
plt.show()


# 3. DISTRIBUTION DU NOMBRE D’ASSOCIATIONS

print("Génération de l'histogramme...")
plt.figure(figsize=(8, 5))

plt.hist(df['nb_associations_total'].dropna(), bins=50, range=(0, 500), color="#1f77b4")

plt.title("Distribution du nombre d'associations par commune", fontsize=12, pad=15)
plt.xlabel("Nombre d'associations", fontsize=12)
plt.ylabel("Nombre de communes", fontsize=12)

plt.grid(True, which='both', linestyle='-', alpha=0.7)

plt.tight_layout()
plt.show()


# 4. # 3. DISTRIBUTION DU NOMBRE D’ASSOCIATIONS

print(" Génération du boxplot...")
plt.figure(figsize=(10, 3))


sns.boxplot(
    x=df['nb_associations_total'], 
    color="white", 
    flierprops={"marker": "o", "markerfacecolor": "none", "markeredgecolor": "black", "markersize": 5}
)

plt.title("Valeurs aberrantes - Nombre d'associations", fontsize=14)
plt.xlabel("Nombre d'associations", fontsize=12)

plt.tight_layout()
plt.show()

print("Script terminé avec succès !")