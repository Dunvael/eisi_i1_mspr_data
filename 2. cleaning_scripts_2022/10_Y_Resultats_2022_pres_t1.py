import pandas as pd
import numpy as np
from pathlib import Path
import unicodedata
import sys

# CONFIGURATION DES CHEMINS

# Répertoire racine du projet
BASE_DIR = Path(".")

# Fichier brut des résultats présidentiels 2022
FILE_DATA = BASE_DIR / "data_raw" / "2022_raw" / "Resultat_1er_tour_2022" / "PRESIDENTIEL_T1_PAR_COM_2022.parquet"

# Référentiel des communes harmonisé
FILE_COMMUNES = BASE_DIR / "data_cleaned" / "communes_2022_cleaned.csv"

# Dossier de sortie des fichiers nettoyés
DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2022"

# Création automatique du dossier si absent
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)


# FONCTION DE SUPPRESSION DES ACCENTS

# Permet d’harmoniser les noms de communes
# et candidats pour éviter les problèmes de jointure
def remove_accents(text):

    # Vérification des valeurs manquantes
    if pd.isna(text):
        return text

    # Conversion en texte + suppression espaces
    text = str(text).strip()

    # Suppression des accents
    text = "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )

    return text


# FONCTION PRINCIPALE DE NETTOYAGE

def clean_resultats_elections(year):

    print(f"Nettoyage résultats élections {year}")

    # Vérification présence fichier élections
    if not FILE_DATA.exists():
        print(f"Fichier parquet introuvable : {FILE_DATA}")
        sys.exit(1)

    # Vérification présence référentiel communes
    if not FILE_COMMUNES.exists():
        print(f"Référentiel communes introuvable : {FILE_COMMUNES}")
        sys.exit(1)

    # RÉFÉRENTIEL COMMUNES

    # Lecture du référentiel harmonisé
    df_ref = pd.read_csv(
        FILE_COMMUNES,
        sep=";",
        dtype=str,
        encoding="utf-8"
    )

    # Conservation des colonnes utiles
    df_ref = df_ref[["code_insee", "nom_commune"]].copy()

    # Normalisation des codes INSEE
    df_ref["code_insee"] = (
        df_ref["code_insee"]
        .astype(str)
        .str.zfill(5)
    )

    # LECTURE DU DATASET ÉLECTORAL

    # Lecture du parquet brut
    df = pd.read_parquet(
        FILE_DATA,
        columns=["code_commune", "nom", "voix"]
    )

    # Renommage du code commune
    df = df.rename(columns={"code_commune": "code_insee"})

    # Harmonisation des codes INSEE
    df["code_insee"] = (
        df["code_insee"]
        .astype(str)
        .str.zfill(5)
    )

    # Harmonisation des noms candidats :
    # suppression accents + majuscules + espaces
    df["nom"] = (
        df["nom"]
        .apply(remove_accents)
        .str.upper()
        .str.strip()
    )

    # Conversion du nombre de voix en numérique
    # Les valeurs invalides deviennent 0
    df["voix"] = (
        pd.to_numeric(
            df["voix"],
            errors="coerce"
        )
        .fillna(0)
    )

    # ASSOCIATION CANDIDAT → BLOC POLITIQUE

    # Regroupement des candidats
    # par orientation politique
    mapping_bloc = {

        "ARTHAUD": "extreme_gauche",
        "POUTOU": "extreme_gauche",

        "ROUSSEL": "gauche",
        "MELENCHON": "gauche",
        "HIDALGO": "gauche",
        "JADOT": "gauche",

        "MACRON": "centre",
        "LASSALLE": "centre",

        "PECRESSE": "droite",
        "DUPONT-AIGNAN": "droite",

        "LE PEN": "extreme_droite",
        "ZEMMOUR": "extreme_droite",
    }

    # Attribution du bloc politique
    df["bloc_politique"] = df["nom"].map(mapping_bloc)

    # Vérification candidats non associés
    candidats_non_associes = (
        df[df["bloc_politique"].isna()]["nom"]
        .unique()
    )

    # Arrêt du script si candidat non reconnu
    if len(candidats_non_associes) > 0:

        print("Candidats non associés à un bloc :")
        print(candidats_non_associes)

        sys.exit(1)

    # AGRÉGATION DES VOIX

    # Somme des voix par commune et bloc politique
    df_blocs = (
        df.groupby(
            ["code_insee", "bloc_politique"],
            as_index=False
        )["voix"]
        .sum()
    )

    # Calcul du total des voix exprimées par commune
    df_blocs["total_exprimes_commune"] = (
        df_blocs.groupby("code_insee")["voix"]
        .transform("sum")
    )

    # Calcul du pourcentage de chaque bloc
    df_blocs["score_bloc"] = np.where(

        df_blocs["total_exprimes_commune"] > 0,

        df_blocs["voix"] /
        df_blocs["total_exprimes_commune"] * 100,

        np.nan
    )

    # TRANSFORMATION EN FORMAT LARGE

    # Une ligne par commune
    df_scores = df_blocs.pivot_table(

        index="code_insee",

        columns="bloc_politique",

        values="score_bloc",

        fill_value=0

    ).reset_index()

    # Suppression du nom d’index des colonnes
    df_scores.columns.name = None

    # Renommage des colonnes
    df_scores = df_scores.rename(columns={

        "extreme_droite": "score_extreme_droite",

        "extreme_gauche": "score_extreme_gauche",

        "centre": "score_centre",

        "droite": "score_droite",

        "gauche": "score_gauche",
    })

    # Liste des scores attendus
    cols_scores = [

        "score_extreme_droite",

        "score_extreme_gauche",

        "score_centre",

        "score_droite",

        "score_gauche",
    ]

    # Création des colonnes manquantes si absentes
    for col in cols_scores:

        if col not in df_scores.columns:
            df_scores[col] = 0

    # Arrondi des scores à 2 décimales
    df_scores[cols_scores] = (
        df_scores[cols_scores]
        .round(2)
    )

    # VARIABLE CIBLE Y

    # Détermination de la classe politique dominante
    df_scores["classe_politique"] = (

        df_scores[cols_scores]

        .idxmax(axis=1)

        .str.replace("score_", "", regex=False)
    )

    # JOINTURE AVEC LE RÉFÉRENTIEL COMMUNES

    # Ajout du nom de commune
    df_scores = pd.merge(

        df_scores,

        df_ref,

        on="code_insee",

        how="left"
    )

    # Renommage du nom de commune
    df_scores = df_scores.rename(
        columns={"nom_commune": "localisation"}
    )

    # Suppression des accents
    df_scores["localisation"] = (
        df_scores["localisation"]
        .apply(remove_accents)
    )

    # Suppression des lignes invalides
    df_scores = df_scores.dropna(
        subset=["localisation", "classe_politique"]
    )

    # Suppression des communes vides
    df_scores = df_scores[
        df_scores["localisation"]
        .astype(str)
        .str.strip() != ""
    ]

    # CRÉATION DU FICHIER Y

    # Variable cible du modèle ML
    df_y = df_scores[
        [
            "code_insee",
            "localisation",
            "classe_politique"
        ]
    ].copy()

    # Ajout année
    df_y["annee"] = year

    # CRÉATION DU FICHIER X

    # Variables explicatives électorales
    df_x_votes = df_scores[
        [
            "code_insee",
            "localisation",
            "score_extreme_droite",
            "score_extreme_gauche",
            "score_centre",
            "score_droite",
            "score_gauche",
        ]
    ].copy()

    # Ajout année
    df_x_votes["annee"] = year

    # CHEMINS DE SORTIE

    fichier_y = (
        DIR_OUTPUT /
        f"Y_classe_politique_{year}_cleaned.csv"
    )

    fichier_x = (
        DIR_OUTPUT /
        f"X_votes_politiques_{year}_cleaned.csv"
    )

    # EXPORT CSV

    # Export du fichier cible Y
    df_y.to_csv(
        fichier_y,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    # Export du fichier X votes
    df_x_votes.to_csv(
        fichier_x,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    # AFFICHAGE DES RÉSULTATS

    print("\n--- Répartition des classes politiques ---")

    print(
        df_y["classe_politique"]
        .value_counts()
    )

    print(f"\nFichier Y créé : {fichier_y}")
    print(f"Lignes Y : {len(df_y)}")

    print(f"\nFichier X votes créé : {fichier_x}")
    print(f"Lignes X : {len(df_x_votes)}")


# POINT D’ENTRÉE DU SCRIPT

if __name__ == "__main__":

    clean_resultats_elections(2022)