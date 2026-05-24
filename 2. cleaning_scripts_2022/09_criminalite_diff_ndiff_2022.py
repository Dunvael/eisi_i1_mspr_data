import pandas as pd
from pathlib import Path
import numpy as np  


# 1. Configuration des chemins

BASE_DIR = Path(".")

# Chemin vers le fichier brut de criminalité
FILE_DATA = (
    BASE_DIR / "data_raw" / "2022_raw" / "9_criminalite_2022" / "CRIMINALITE_PAR_COM_2022.parquet"
)

# Chemin vers la table de passage permettant d'harmoniser les codes INSEE
FILE_PASSAGE = (
    BASE_DIR / "data_raw" / "2022_raw" / "referentiels" / "table_passage_annuelle_2025.xlsx"
)

# Chemin vers le référentiel communal nettoyé
FILE_COMMUNES = BASE_DIR / "data_cleaned" / "communes_2022_cleaned.csv"

# Dossier de sortie des fichiers nettoyés
DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2022"

# Création du dossier de sortie s'il n'existe pas
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)


# 2. Nettoyage du dataset criminalité

def clean_criminalite_all(year):

    print(f"Nettoyage criminalité ALL {year}")


    # Étape 1 : Lecture du fichier criminalité

    # Lecture du fichier Parquet contenant les indicateurs de criminalité
    df = pd.read_parquet(FILE_DATA)

    # Normalisation du code INSEE 2025 sur 5 caractères
    df["CODGEO_2025"] = (
        df["CODGEO_2025"]
        .astype(str)
        .str.strip()
        .str.zfill(5)
    )


    # Étape 2 : Lecture de la table de passage

    # Lecture de la table de passage officielle
    # header=5 permet d'utiliser la bonne ligne d'en-tête
    passage = pd.read_excel(FILE_PASSAGE, dtype=str, header=5)

    # Nettoyage des noms de colonnes
    passage.columns = passage.columns.astype(str).str.strip()

    # Affichage des colonnes disponibles pour contrôle
    print(passage.columns.tolist())

    # Normalisation du code INSEE 2022
    passage["CODGEO_2022"] = (
        passage["CODGEO_2022"]
        .astype(str)
        .str.strip()
        .str.zfill(5)
    )

    # Normalisation du code INSEE 2025
    passage["CODGEO_2025"] = (
        passage["CODGEO_2025"]
        .astype(str)
        .str.strip()
        .str.zfill(5)
    )
    
    # Sélection des colonnes utiles dans la table de passage
    passage = passage[["CODGEO_2025", "CODGEO_2022"]].drop_duplicates()



    # Étape 3 : Harmonisation des codes INSEE 2025 vers 2022

    # Jointure avec la table de passage
    df = df.merge(
        passage,
        on="CODGEO_2025",
        how="left"
    )

    # Si un code 2022 existe, on l'utilise
    # sinon on conserve le code 2025 initial
    df["code_insee"] = df["CODGEO_2022"].fillna(df["CODGEO_2025"])

    # Normalisation du code INSEE final sur 5 caractères
    df["code_insee"] = (
        df["code_insee"]
        .astype(str)
        .str.strip()
        .str.zfill(5)
    )


    # Étape 4 : Sélection des indicateurs de criminalité

    # Liste des indicateurs conservés pour le projet
    indicateurs_gardes = [
        "Violences physiques intrafamiliales",
        "Violences sexuelles",
        "Vols avec armes",
        "Vols violents sans arme",
        "Cambriolages de logement",
        "Vols de véhicule",
        "Destructions et dégradations volontaires",
        "Usage de stupéfiants",
        "Trafic de stupéfiants"
    ]


    # Étape 5 : Filtrage de l'année et des indicateurs

    # Conservation uniquement de l'année demandée
    # et des indicateurs utiles au projet
    df = df[
        (df["annee"] == year) &
        (df["indicateur"].isin(indicateurs_gardes))
    ].copy()


    # Étape 6 : Création du taux final

    # Certains taux sont dans taux_pour_mille
    # Si cette colonne est vide, on utilise complement_info_taux
    df["taux_final"] = df["taux_pour_mille"].fillna(df["complement_info_taux"])

    # Conversion du taux final en numérique
    df["taux_final"] = pd.to_numeric(
        df["taux_final"],
        errors="coerce"
    )


    # Étape 7 : Pivot des indicateurs

    # Transformation du dataset :
    # une ligne = une commune
    # une colonne = un indicateur de criminalité
    df_pivot = df.pivot_table(
        index=["code_insee", "annee"],
        columns="indicateur",
        values="taux_final",
        aggfunc="mean"
    ).reset_index()


    # Étape 8 : Renommage des colonnes

    # Renommage des indicateurs avec des noms homogènes
    df_pivot = df_pivot.rename(columns={
        "Violences physiques intrafamiliales": "taux_violences_intrafamiliales",
        "Violences sexuelles": "taux_violences_sexuelles",
        "Vols avec armes": "taux_vols_avec_armes",
        "Vols violents sans arme": "taux_vols_violents_sans_arme",
        "Cambriolages de logement": "taux_cambriolages_logement",
        "Vols de véhicule": "taux_vols_vehicule",
        "Destructions et dégradations volontaires": "taux_degradations",
        "Usage de stupéfiants": "taux_usage_stupefiants",
        "Trafic de stupéfiants": "taux_trafic_stupefiants"
    })


    # Étape 9 : Chargement du référentiel communal

    df_ref = pd.read_csv(FILE_COMMUNES, sep=";", dtype=str)

    # Conservation uniquement des colonnes utiles à la jointure
    df_ref = df_ref[["code_insee", "nom_commune"]]

    # Normalisation du code INSEE sur 5 caractères
    df_ref["code_insee"] = df_ref["code_insee"].astype(str).str.zfill(5)

    # Suppression des doublons sur le code INSEE
    df_ref = df_ref.drop_duplicates(subset=["code_insee"])


    # Étape 10 : Jointure avec le référentiel communal

    # Ajout du nom de commune à partir du référentiel
    df_pivot = pd.merge(
        df_pivot,
        df_ref,
        on="code_insee",
        how="left"
    )


    # Étape 11 : Contrôle des communes non retrouvées

    print("Communes non trouvées :", df_pivot["nom_commune"].isna().sum())

    print(df_pivot[df_pivot["nom_commune"].isna()][["code_insee"]].head(50))


    # Étape 12 : Suppression des communes non exploitables

    # Suppression des lignes sans nom de commune
    df_pivot = df_pivot.dropna(subset=["nom_commune"]).copy()

    # Harmonisation du nom de colonne avec les autres datasets
    df_pivot = df_pivot.rename(columns={"nom_commune": "localisation"})



    # Étape 13 : Préparation de l'export

    fichier_sortie = DIR_OUTPUT / f"09_criminalite_diff_ndiff_{year}_cleaned.csv"

    # Liste des colonnes de taux à tronquer
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

    # Conversion numérique et troncature à 2 décimales
    for col in colonnes_taux:
        df_pivot[col] = pd.to_numeric(df_pivot[col], errors="coerce")
        df_pivot[col] = np.trunc(df_pivot[col] * 100) / 100


    # Étape 14 : Export du dataset nettoyé

    df_pivot.to_csv(
        fichier_sortie,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )


    # Étape 15 : Contrôles qualité finaux

    print(f"\nFichier créé : {fichier_sortie}")

    print("\nShape :")
    print(df_pivot.shape)

    print("\nHEAD :")
    print(df_pivot.head())

    print("\nNaN :")
    print(df_pivot.isna().sum())

    print("\nPourcentage NaN :")
    print((df_pivot.isna().mean() * 100).round(2))

    print("\nCodes 2025 non retrouvés dans la table de passage :")
    print(df[df["CODGEO_2022"].isna()]["CODGEO_2025"].nunique())


# Point d'entrée du script
if __name__ == "__main__":
    clean_criminalite_all(2022)