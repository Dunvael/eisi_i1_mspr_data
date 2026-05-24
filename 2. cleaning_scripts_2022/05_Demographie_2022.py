import pandas as pd
import numpy as np
from pathlib import Path
import sys


# 1. Configuration des chemins

BASE_DIR = Path(".")

# Chemin vers le fichier brut de démographie
FILE_DATA = BASE_DIR / "data_raw" / "2022_raw" / "5_demographie_2022" / "DEMOGRAPHIE_PAR_SEXE_PAR_DEP_ET_COM_1968_TO_2022.xlsx"

# Chemin vers le référentiel communal nettoyé
FILE_COMMUNES = BASE_DIR / "data_cleaned" / "communes_2022_cleaned.csv"

# Dossier de sortie des fichiers nettoyés
DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2022"

# Création du dossier de sortie s'il n'existe pas
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)


# 2. Fonction de calcul de l'âge médian approximatif

def calcul_age_median(row, age_cols, midpoints): #row = une ligne = une commune

    # Somme de toutes les tranches d'âge
    total = row[age_cols].sum()

    # Si la commune n'a pas de population exploitable
    if total == 0:
        return np.nan

    # Seuil correspondant à 50 % de la population
    seuil = total / 2

    # Cumul progressif des tranches d'âge
    cumul = 0

    # Parcours des tranches d'âge et de leurs milieux
    for col, midpoint in zip(age_cols, midpoints):
        cumul += row[col]

        # Dès que le cumul dépasse 50 %, on retourne le milieu de la tranche
        if cumul >= seuil:
            return midpoint

    return np.nan


# 3. Nettoyage du dataset démographie

def clean_demographie(year):

    print(f"Nettoyage démographie {year}")

    # Vérification de l'existence du fichier brut
    if not FILE_DATA.exists():
        print(f" Fichier introuvable : {FILE_DATA}")
        sys.exit(1)

    # Vérification de l'existence du référentiel communal
    if not FILE_COMMUNES.exists():
        print(f"  Référentiel introuvable : {FILE_COMMUNES}")
        sys.exit(1)


    # Étape 1 : Chargement du référentiel communes

    df_ref = pd.read_csv(FILE_COMMUNES, sep=";", dtype=str)

    # Normalisation du code INSEE sur 5 caractères
    df_ref["code_insee"] = df_ref["code_insee"].astype(str).str.zfill(5)


    # Étape 2 : Lecture du fichier démographique brut

    # Lecture de la feuille COM_2022
    # skiprows=13 permet de passer les lignes d'en-tête techniques
    df = pd.read_excel(
        FILE_DATA,
        sheet_name="COM_2022",
        skiprows=13,
        dtype=str
    )

    # Nettoyage des noms de colonnes
    df.columns = df.columns.astype(str).str.strip()


    # Étape 3 : Reconstruction du code INSEE

    # Le code INSEE est reconstruit à partir du département DR et du code commune CR
    df["DR"] = df["DR"].astype(str).str.zfill(2)
    df["CR"] = df["CR"].astype(str).str.zfill(3)
    df["code_insee"] = df["DR"] + df["CR"]

    #df = df[df["STABLE"].astype(str).str.strip() == "1"] #On garde uniquement les communes STABLES (communes non fusionnées non supprimée)


    # Étape 4 : Définition des tranches d'âge

    # Dictionnaire associant chaque tranche d'âge :
    # - colonne hommes
    # - colonne femmes
    # - valeur médiane approximative de la tranche
    tranches = {
        "0_4": ("ageq_rec01s1rpop2022", "ageq_rec01s2rpop2022", 2.5),
        "5_9": ("ageq_rec02s1rpop2022", "ageq_rec02s2rpop2022", 7.5),
        "10_14": ("ageq_rec03s1rpop2022", "ageq_rec03s2rpop2022", 12.5),
        "15_19": ("ageq_rec04s1rpop2022", "ageq_rec04s2rpop2022", 17.5),
        "20_24": ("ageq_rec05s1rpop2022", "ageq_rec05s2rpop2022", 22.5),
        "25_29": ("ageq_rec06s1rpop2022", "ageq_rec06s2rpop2022", 27.5),
        "30_34": ("ageq_rec07s1rpop2022", "ageq_rec07s2rpop2022", 32.5),
        "35_39": ("ageq_rec08s1rpop2022", "ageq_rec08s2rpop2022", 37.5),
        "40_44": ("ageq_rec09s1rpop2022", "ageq_rec09s2rpop2022", 42.5),
        "45_49": ("ageq_rec10s1rpop2022", "ageq_rec10s2rpop2022", 47.5),
        "50_54": ("ageq_rec11s1rpop2022", "ageq_rec11s2rpop2022", 52.5),
        "55_59": ("ageq_rec12s1rpop2022", "ageq_rec12s2rpop2022", 57.5),
        "60_64": ("ageq_rec13s1rpop2022", "ageq_rec13s2rpop2022", 62.5),
        "65_69": ("ageq_rec14s1rpop2022", "ageq_rec14s2rpop2022", 67.5),
        "70_74": ("ageq_rec15s1rpop2022", "ageq_rec15s2rpop2022", 72.5),
        "75_79": ("ageq_rec16s1rpop2022", "ageq_rec16s2rpop2022", 77.5),
        "80_84": ("ageq_rec17s1rpop2022", "ageq_rec17s2rpop2022", 82.5),
        "85_89": ("ageq_rec18s1rpop2022", "ageq_rec18s2rpop2022", 87.5),
        "90_94": ("ageq_rec19s1rpop2022", "ageq_rec19s2rpop2022", 92.5),
        "95_plus": ("ageq_rec20s1rpop2022", "ageq_rec20s2rpop2022", 97.5),
    }

    age_cols = []
    midpoints = []


    # Étape 5 : Création des tranches d'âge agrégées

    for tranche, (col_hommes, col_femmes, milieu) in tranches.items():

        # Vérification de la présence des colonnes attendues
        if col_hommes not in df.columns or col_femmes not in df.columns:
            print(f"  Colonnes manquantes pour {tranche}")
            print(f"Attendu : {col_hommes} et {col_femmes}")
            print("Colonnes disponibles :", df.columns.tolist())
            sys.exit(1)

        # Conversion des colonnes hommes / femmes en numérique
        hommes = pd.to_numeric(df[col_hommes], errors="coerce")
        femmes = pd.to_numeric(df[col_femmes], errors="coerce")

        # Addition hommes + femmes pour obtenir la population totale de la tranche
        df[tranche] = hommes + femmes

        # Stockage des colonnes créées pour les calculs suivants
        age_cols.append(tranche)
        midpoints.append(milieu)


    # Étape 6 : Création des indicateurs démographiques

    # Population totale calculée à partir de toutes les tranches d'âge
    df["population_totale"] = df[age_cols].sum(axis=1)

    # Population des moins de 25 ans
    df["jeunes_moins_25"] = df[
        ["0_4", "5_9", "10_14", "15_19", "20_24"]
    ].sum(axis=1)

    # Population des 65 ans et plus
    df["seniors_65_plus"] = df[
        ["65_69", "70_74", "75_79", "80_84", "85_89", "90_94", "95_plus"]
    ].sum(axis=1)

    # Pourcentage de jeunes dans la population totale
    df["pct_jeunes"] = np.where(
        df["population_totale"] > 0,
        df["jeunes_moins_25"] / df["population_totale"] * 100,
        np.nan
    )

    # Pourcentage de seniors dans la population totale
    df["pct_seniors"] = np.where(
        df["population_totale"] > 0,
        df["seniors_65_plus"] / df["population_totale"] * 100,
        np.nan
    )


    # Étape 7 : Calcul de l'âge médian approximatif

    # L'âge médian est estimé avec la tranche où le cumul dépasse 50 %
    df["age_median"] = df.apply(
        lambda row: calcul_age_median(row, age_cols, midpoints),
        axis=1
    )


    # Étape 8 : Préparation du référentiel pour la jointure

    df_ref = df_ref[["code_insee", "nom_commune"]]

    # Suppression des doublons sur le code INSEE
    df_ref = df_ref.drop_duplicates(subset=["code_insee"])


    # Étape 9 : Jointure avec le référentiel communal

    # Ajout du nom de commune à partir du code INSEE
    df = pd.merge(df, df_ref, on="code_insee", how="left")

    # Renommage de la colonne nom_commune en localisation
    df = df.rename(columns={"nom_commune": "localisation"})


    # Étape 10 : Debug des communes non trouvées

    # Sélection des communes absentes du référentiel après jointure
    df_non_trouvees = df[df["localisation"].isna()].copy()

    print("\n--- COMMUNES NON TROUVÉES APRÈS MERGE ---")
    print(df_non_trouvees.shape)

    print(
        df_non_trouvees[
            ["code_insee"]
        ].head(100)
    )

    print("\nDébut des codes non trouvés :")

    print(
        df_non_trouvees["code_insee"]
        .astype(str)
        .str[:2]
        .value_counts()
        .sort_index()
    )


    # Étape 11 : Construction du dataset final

    df_final = df[
        [
            "code_insee",
            "localisation",
            "pct_jeunes",
            "pct_seniors",
            "age_median",
        ]
    ].copy()


    # Suppression des lignes sans localisation
    df_final = df_final[df_final["localisation"].notna()]

    # Suppression des localisations vides
    df_final = df_final[df_final["localisation"].astype(str).str.strip() != ""]

    # Ajout de l'année de référence
    df_final["annee"] = year


    # Étape 12 : Arrondi des variables numériques

    cols_num = ["pct_jeunes", "pct_seniors", "age_median"]

    df_final[cols_num] = df_final[cols_num].round(2)


    # Étape 13 : Export du dataset nettoyé

    fichier = DIR_OUTPUT / f"05_demographie_{year}_cleaned.csv"

    df_final.to_csv(fichier, sep=";", index=False, encoding="utf-8-sig")

    print(f" Fichier créé : {fichier}")
    print(f" Lignes sauvegardées : {len(df_final)}")


    # Étape 14 : Contrôles qualité finaux

    #DEBUG : 
    #df_null = df_final[
    #df_final["pct_jeunes"].isna() |
    #df_final["pct_seniors"].isna() |
    #df_final["age_median"].isna()]

    print("Lignes après lecture :", len(df))

    print("Communes non trouvées après merge :", df["localisation"].isna().sum())

    print(df_final.isna().sum())


    # Étape 15 : Debug complémentaire

    # Communes avec population totale nulle ou absente
    df_sans_population = df[
        df["population_totale"].isna() |
        (df["population_totale"] == 0)
    ].copy()

    # Communes non retrouvées après la jointure
    # avec le référentiel communal
    df_non_trouvees = df[
        df["localisation"].isna()
    ].copy()

    # Création de l'ensemble des codes INSEE non trouvés
    codes_non_trouvees = set(
        df_non_trouvees["code_insee"]
    )

    # Création de l'ensemble des codes INSEE sans population
    codes_sans_population = set(
        df_sans_population["code_insee"]
    )

    # Communes présentes dans les deux catégories :
    # - non trouvées dans le référentiel
    # - sans population exploitable
    codes_communs = (
        codes_non_trouvees
        .intersection(codes_sans_population)
    )

    print("\n--- COMPARAISON NON TROUVÉES / SANS POPULATION ---")

    # Nombre total de communes absentes du référentiel
    print(
        "Communes non trouvées :",
        len(codes_non_trouvees)
    )

    # Nombre total de communes sans population exploitable
    print(
        "Communes sans population :",
        len(codes_sans_population)
    )

    # Nombre de communes cumulant les deux problèmes
    print(
        "Communes à la fois non trouvées ET sans population :",
        len(codes_communs)
    )

    print(
        "\n--- COMMUNES SANS POPULATION MAIS TROUVÉES DANS LE RÉFÉRENTIEL ---"
    )

    # Communes présentes dans le référentiel
    # mais sans données démographiques exploitables
    print(
        len(
            codes_sans_population
            - codes_non_trouvees
        )
    )

    print(
        "\n--- COMMUNES NON TROUVÉES MAIS AVEC POPULATION ---"
    )

    # Communes absentes du référentiel
    # mais possédant des données de population
    print(
        len(
            codes_non_trouvees
            - codes_sans_population
        )
    )


# Point d'entrée du script
if __name__ == "__main__":
    clean_demographie(2022)