import pandas as pd
import matplotlib
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt
import seaborn as sns
import missingno as msno

print("Analyse Exploratoire - Créations d'Entreprises 2024")


# 1. CHARGEMENT DES DONNÉES

file_path = "data_cleaned/2024/07_Entreprises/07_creations_entreprises_2024_clean.csv"

try:
    df = pd.read_csv(file_path, sep=";")
    print(f"Fichier chargé avec succès ! ({len(df)} communes analysées)")
except FileNotFoundError:
    print(f"Erreur : Le fichier {file_path} est introuvable. Vérifie ton chemin.")
    exit()

sns.set_theme(style="whitegrid")

# Colonnes ciblées
colonne_cible = 'nb_creations_entreprises_2024'


# 2. VALEURS MANQUANTES

print("Génération du graphique de complétude...")

colonnes_visibles = ['code_insee_2024', colonne_cible, 'annee']

fig_msno = plt.figure(figsize=(7, 5))
ax_msno = fig_msno.add_subplot(111)

msno.bar(df[colonnes_visibles], ax=ax_msno, fontsize=11, color=(0.4, 0.4, 0.4))
plt.title("Nombre de valeurs manquantes - Créations d'Entreprises", fontsize=14, pad=20)
plt.tight_layout()
plt.show()


# 3. DISTRIBUTION 

print("Génération de l'histogramme...")
plt.figure(figsize=(8, 5))


plt.hist(df[colonne_cible].dropna(), bins=50, range=(0, 500), color="#1f77b4")

plt.title("Distribution des créations d'entreprises par commune", fontsize=12, pad=15)
plt.xlabel("Nombre de créations (2024)", fontsize=12)
plt.ylabel("Nombre de communes", fontsize=12)

# Grille
plt.grid(True, which='both', linestyle='-', alpha=0.7)

plt.tight_layout()
plt.show()


# 4. VALEURS ABERRANTES

print("Génération du boxplot...")
plt.figure(figsize=(10, 3))

sns.boxplot(
    x=df[colonne_cible], 
    color="white", 
    flierprops={"marker": "o", "markerfacecolor": "none", "markeredgecolor": "black", "markersize": 5}
)

plt.title("Valeurs aberrantes - Créations d'entreprises", fontsize=14)
plt.xlabel("Nombre de créations (2024)", fontsize=12)

plt.tight_layout()
plt.show()

print("Script terminé avec succès !")