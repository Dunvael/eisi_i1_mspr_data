import pandas as pd
from pathlib import Path


# 1. Configuration des chemins

BASE_DIR = Path(".")

# Chemin vers le fichier brut de criminalité
FILE_DATA = BASE_DIR / "data_raw" / "2022_raw" / "9_criminalite_2022" / "CRIMINALITE_PAR_COM_2022.parquet"

# Dossier de sortie des fichiers nettoyés
DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2022"

# Création du dossier de sortie s'il n'existe pas
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)


# 2. Nettoyage du dataset criminalité diffusée uniquement

def clean_criminalite(year):

    print(f"Nettoyage criminalité {year}")


    # Étape 1 : Lecture du fichier brut

    # Lecture du fichier Parquet contenant les données de criminalité
    df = pd.read_parquet(FILE_DATA)


    # Étape 2 : Renommage et normalisation du code INSEE

    # Renommage du code géographique 2025 en code_insee
    df = df.rename(columns={
        "CODGEO_2025": "code_insee"
    })

    # Normalisation du code INSEE sur 5 caractères
    df["code_insee"] = df["code_insee"].astype(str).str.zfill(5)


    # Étape 3 : Sélection des indicateurs utiles

    # Liste des indicateurs de criminalité conservés pour le projet
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


    # Étape 4 : Filtrage des données

    # Conservation uniquement :
    # - de l'année demandée
    # - des indicateurs sélectionnés
    # - des données diffusées uniquement
    df = df[
        (df["annee"] == year) &
        (df["indicateur"].isin(indicateurs_gardes)) &
        (df["est_diffuse"] == "diff")
    ].copy()


    # Étape 5 : Conversion du taux

    # Conversion du taux pour mille en numérique
    df["taux_pour_mille"] = pd.to_numeric(df["taux_pour_mille"], errors="coerce")

    # Remplacement des valeurs manquantes par 0
    df["taux_pour_mille"] = df["taux_pour_mille"].fillna(0)


    # Étape 6 : Pivot des indicateurs

    # Transformation du dataset :
    # une ligne = une commune
    # une colonne = un indicateur de criminalité
    df_pivot = df.pivot_table(
        index=["code_insee", "annee"],
        columns="indicateur",
        values="taux_pour_mille",
        aggfunc="mean"
    ).reset_index()


    # Étape 7 : Renommage des colonnes

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


    # Étape 8 : Export du dataset nettoyé

    fichier_sortie = DIR_OUTPUT / f"09_criminalite_ONLY_diff_{year}_cleaned.csv"

    df_pivot.to_csv(
        fichier_sortie,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )


    # Étape 9 : Contrôles qualité finaux

    print(f"Fichier créé : {fichier_sortie}")

    print("Shape :", df_pivot.shape)

    print(df_pivot.head())

    print(df_pivot.isna().sum())


# Point d'entrée du script
if __name__ == "__main__":
    clean_criminalite(2022)