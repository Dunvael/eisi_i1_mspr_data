# ============================================================
# ELECTIO-ANALYTICS
# Analyse des corrélations - Heatmaps
# ============================================================

import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sqlite3


# ------------------------------------------------------------
# 1. Configuration
# ------------------------------------------------------------

# Chemin de la base SQLite
DB_PATH = "data_cleaned/Train_dataframe.db"

# Dossier de sortie des graphiques
OUTPUT_DIR = "artifacts/eda"

# Création du dossier de sortie si absent
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ------------------------------------------------------------
# 2. Connexion SQLite et chargement du dataframe
# ------------------------------------------------------------

conn = sqlite3.connect(DB_PATH)

# Lecture de la table SQL
df = pd.read_sql(
    "SELECT * FROM training_data",
    conn
)

conn.close()

print("Dataframe chargé :", df.shape)

# ------------------------------------------------------------
# 3. Fonction générique pour créer une heatmap
# ------------------------------------------------------------

def create_heatmap(dataframe, columns, title, output_file):
    """
    Crée et sauvegarde une heatmap de corrélation.

    dataframe : dataframe source
    columns : liste des colonnes à analyser
    title : titre du graphique
    output_file : nom du fichier image généré
    """

    # On garde uniquement les colonnes existantes dans le dataframe
    existing_columns = [col for col in columns if col in dataframe.columns]

    if len(existing_columns) < 2:
        print(f"Pas assez de colonnes pour générer : {title}")
        return

    # Sélection des colonnes numériques uniquement
    df_selected = dataframe[existing_columns].select_dtypes(include=["int64", "float64"])

    if df_selected.shape[1] < 2:
        print(f"Pas assez de variables numériques pour : {title}")
        return

    # Calcul de la matrice de corrélation
    corr_matrix = df_selected.corr()

    # Taille dynamique selon le nombre de variables
    plt.figure(figsize=(max(10, len(df_selected.columns) * 0.8), max(8, len(df_selected.columns) * 0.6)))

    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        linewidths=0.5
    )

    plt.title(title, fontsize=14)
    plt.xticks(rotation=90)
    plt.yticks(rotation=0)
    plt.tight_layout()

    # Sauvegarde
    path = os.path.join(OUTPUT_DIR, output_file)
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Heatmap générée : {path}")


# ------------------------------------------------------------
# 4. Heatmap générale
# ------------------------------------------------------------

# On retire les colonnes non pertinentes pour la corrélation
columns_to_drop = [
    "code_insee",
    "localisation",
    "classe_politique",
    "bloc_politique_majoritaire",
    "annee"
]

df_general = df.drop(columns=columns_to_drop, errors="ignore")

# On garde uniquement les colonnes numériques
numeric_columns = df_general.select_dtypes(include=["int64", "float64"]).columns.tolist()

create_heatmap(
    dataframe=df_general,
    columns=numeric_columns,
    title="Heatmap générale des corrélations - Electio-Analytics",
    output_file="heatmap_generale.png"
)


# ------------------------------------------------------------
# 5. Heatmaps par catégorie
# ------------------------------------------------------------

revenus_variables = [
    "pauvre",
    "moyen",
    "riche",
    "revenus_median_final",
    "taux_chomage"
]

categorie_sociale_variables = [
    "pourcentage_ouvriers",
    "pourcentage_cadres",
    "pourcentage_employes",
    "pourcentage_agri"
]

territoire_variables = [
    "population",
    "superficie_km2",
    "densite"
]

demographie_variables = [
    "pct_jeunes",
    "pct_seniors",
    "age_median",
    "taux_immigration"
]

dynamisme_local_variables = [
    "nb_associations",
    "nb_entreprises"
]

criminalite_variables = [
    "taux_degradation",
    "taux_cambriolages_logement",
    "taux_violences_intrafamiliales",
    "taux_violences_sexuelles",
    "taux_trafic_stupefiants",
    "taux_usages_stupefiants",
    "taux_vols_violents_sans_arme",
    "taux_vols_avec_armes",
    "taux_vols_vehicule"
]

resultats_electoraux_variables = [
    "droite",
    "gauche",
    "centre",
    "extreme_droite",
    "extreme_gauche"
]


create_heatmap(
    df,
    revenus_variables,
    "Corrélations - Revenus et chômage",
    "heatmap_revenus_chomage.png"
)

create_heatmap(
    df,
    categorie_sociale_variables,
    "Corrélations - Catégories sociales",
    "heatmap_categories_sociales.png"
)

create_heatmap(
    df,
    territoire_variables,
    "Corrélations - Variables territoriales",
    "heatmap_territoire.png"
)

create_heatmap(
    df,
    demographie_variables,
    "Corrélations - Démographie",
    "heatmap_demographie.png"
)

create_heatmap(
    df,
    dynamisme_local_variables,
    "Corrélations - Dynamisme local",
    "heatmap_dynamisme_local.png"
)

create_heatmap(
    df,
    criminalite_variables,
    "Corrélations - Criminalité",
    "heatmap_criminalite.png"
)

create_heatmap(
    df,
    resultats_electoraux_variables,
    "Corrélations - Résultats électoraux 2022",
    "heatmap_resultats_electoraux.png"
)


print("\nToutes les heatmaps ont été générées.")