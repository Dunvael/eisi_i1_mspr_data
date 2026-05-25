import pandas as pd
import matplotlib

import matplotlib.pyplot as plt
import seaborn as sns
import missingno as msno
import sys

print("Analyse Exploratoire - Catégories Sociales 2024")


# 1. CHARGEMENT DES DONNÉES

file_path = "data_cleaned/2024/09_CS/09_categories_sociales_2024_clean.csv"

try:
    df = pd.read_csv(file_path, sep=";")
    print(f"Fichier chargé avec succès ! ({len(df)} communes analysées)")
except FileNotFoundError:
    print(f"Erreur : Le fichier {file_path} est introuvable. Vérifie ton chemin.")
    sys.exit(1)

sns.set_theme(style="whitegrid")


if 'nom_commune_2024' in df.columns:
    df = df.rename(columns={'nom_commune_2024': 'localisation'})

# Colonnes ciblées
cols_cs = ['pourcentage_agri', 'pourcentage_cadres', 'pourcentage_employes', 'pourcentage_ouvriers']
cols_visibles = ['localisation'] + cols_cs + ['annee']


cols_visibles = [col for col in cols_visibles if col in df.columns]


# 2. VALEURS MANQUANTES

print("Génération des graphiques de complétude...")

# ---  La Matrice (Vue globale) ---
fig_matrix = plt.figure(figsize=(8, 4))
ax_matrix = fig_matrix.add_subplot(111)
msno.matrix(df[cols_visibles], ax=ax_matrix, sparkline=False, fontsize=10, color=(0.25, 0.25, 0.25))
plt.title("Matrice des valeurs manquantes", fontsize=14, pad=20)
plt.show()

# ---  Le Bar Chart (Comptage strict) ---
fig_bar = plt.figure(figsize=(8, 4))
ax_bar = fig_bar.add_subplot(111)
msno.bar(df[cols_visibles], ax=ax_bar, fontsize=10, color=(0.4, 0.4, 0.4))
plt.title("Nombre de valeurs manquantes - Catégories sociales", fontsize=14, pad=20)
plt.show()


# 3. DISTRIBUTIONS 

print(" Génération des histogrammes (Distributions)...")

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
axes = axes.flatten()

for i, col in enumerate(cols_cs):

    axes[i].hist(df[col].dropna(), bins=50, color="#1f77b4")
    axes[i].set_title(f"Distribution - {col}", fontsize=11)
    axes[i].set_xlabel(col, fontsize=9)
    axes[i].grid(True, linestyle='-', alpha=0.7)

plt.tight_layout()
plt.show()


# 4. VALEURS ABERRANTES 

print("Génération des boxplots (Valeurs aberrantes)...")

fig2, axes2 = plt.subplots(2, 2, figsize=(12, 6))
axes2 = axes2.flatten()

for i, col in enumerate(cols_cs):
    sns.boxplot(
        x=df[col], 
        ax=axes2[i],
        color="#1f77b4",
        flierprops={"marker": "o", "markerfacecolor": "none", "markeredgecolor": "black", "markersize": 4}
    )
    axes2[i].set_title(f"Valeurs aberrantes - {col}", fontsize=11)
    axes2[i].set_xlabel(col, fontsize=9)

plt.tight_layout()
plt.show()

print("Script terminé ")